import lzma

from ESFtypes import *

from ESFReader import ESFReader
from ESFWriter import ESFWriter

from ESF import ESF
from ESFSave import ESFSave

# (steam_username, faction_name, steam_id, player_offset)
DATA_INDICES = {
    "empire": (10, 11, 13, 7),
    "napoleon": (10, 11, 13, 7),
    "shogun": (10, 11, 13, 7),
    "rome": (9, 10, 13, 7),
    "attila": (9, 10, 13, 7)
}

class ESFMultiSave:
    # game: empire,napoleon,shogun,rome,attila
    def __init__(self, game="shogun"):
        self.game = game
        if(self.game != "empire" and self.game != "napoleon"):
            self.header_esf = ESF()
        else:
            self.header_esf = None
        self.main_esf = ESF()

    def read(self, esf_byte_arr):
        if(self.game != "empire" and self.game != "napoleon"):
            self.header_esf.read(esf_byte_arr)

            compressed_file = bytearray()

            compressed_info_data = self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA", "COMPRESSED_DATA_INFO"])[1]
            first_int = compressed_info_data[0][0].convert_to()

            for i in compressed_info_data[1][1]:
                compressed_file += i[0].data

            # compressed_file += first_int.to_bytes(4, "little", signed=False)
            # compressed_file += b'\x00\x00\x00\x00'
            # Putting the real size makes Windows report corrupt data for some reason
            compressed_file += b'\xff\xff\xff\xff' # Size
            compressed_file += b'\xff\xff\xff\xff'

            compressed_data = self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][1]
            for i in compressed_data:
                compressed_file += i[0].data

            decompresser = lzma.LZMADecompressor()
            save_file_bin = decompresser.decompress(compressed_file)
            # print(type(self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1]))
            self.main_esf.read(save_file_bin)
        else:
            self.main_esf.read(esf_byte_arr)
        

    def read_file(self, file_path):
        with open(file_path, mode="rb") as esf_file:
            file_data = esf_file.read()
            self.read(file_data)

    def write(self, magic_code=None):
        if(self.game != "empire" and self.game != "napoleon"):
            if(magic_code == None):
                magic_code = Magiccode.ABCA
            new_main_esf = self.main_esf.write(Magiccode.ABCA)

            compresser = lzma.LZMACompressor(format=lzma.FORMAT_ALONE)
            new_compressed_data = compresser.compress(new_main_esf)
            new_compressed_data += compresser.flush()
            new_comp_header = []
            for i in new_compressed_data[:5]:
                new_comp_header.append((UInt8(b'\x06', i.to_bytes(1, "little", signed=False)), None))

            # shogun_header_file.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][1] = new_comp_header
            compressed_info_data = self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA", "COMPRESSED_DATA_INFO"])[1]
            prev_array = compressed_info_data[1][0]
            compressed_info_data[1] = (prev_array, new_comp_header)

            file_size = len(new_main_esf)
            compressed_info_data[0] = (UInt32(b'\x08', file_size.to_bytes(4, "little", signed=False)), None)

            new_com_data = []
            for i in new_compressed_data[13:]:
                new_com_data.append((UInt8(b'\x06', i.to_bytes(1, "little", signed=False)), None))
            # print(len(new_com_data))
            prev_array = self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][0]
            # print(prev_array.node_type)
            self.header_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0] = (prev_array, new_com_data)

            return self.header_esf.write(magic_code)
        else:
            if(magic_code == None):
                magic_code = Magiccode.ABCE
            return self.main_esf.write(magic_code)

    def write_file(self, file_path, magic_code=None):
        # if(self.header_data == None):
        #     return

        with open(file_path, mode="wb") as esf_file:
            esf_file.write(self.write(magic_code))

class ESFMultiSaveConversion(ESFMultiSave):
    def __init__(self, game="shogun"):
        super().__init__()
        self.game = game

    # player number 0 and 1
    # (steam_username, faction_name, steam_id)
    def change_data(self, player, data):
        steam_username, faction_name, steam_id = data
        steam_username_index, faction_name_index, steam_id_index, player_offset = DATA_INDICES[self.game]
        if(player == 1):
            steam_username_index += player_offset
            faction_name_index += player_offset
            steam_id_index += player_offset
        
        # Change header first
        esfs = [self.main_esf]
        if(self.header_esf):
            esfs.append(self.header_esf)

        for esf in esfs:
            real_steam_username_index = esf.get_data_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"], steam_username_index)
            real_faction_name_index = esf.get_data_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"], faction_name_index)
            real_steam_id_index = esf.get_data_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"], steam_id_index)

            save_game_header = esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"])[1]

            if(steam_username != ""):
                save_game_header[real_steam_username_index] = (UniString(steam_username), None)

            if(faction_name != ""):
                if(self.game == "attila" or self.game == "rome"):
                    save_game_header[real_faction_name_index] = (ASCIIString(faction_name), None)
                else:
                    save_game_header[real_faction_name_index] = (UniString(faction_name), None)

            if(steam_id != ""):
                steam_id_data = UInt64(b'\x09', b'')
                steam_id_data.convert_from(int(steam_id))
                save_game_header[real_steam_id_index] = (steam_id_data, None)

    def multi_to_single(self, single):
        multi_env_index = self.main_esf.get_record_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")
        single_env_index = single.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")

        single_campaign = single.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME"])
        single_campaign[1][single_env_index] = self.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"])[1][multi_env_index]

    def single_to_multi(self, single):
        multi_env_index = self.main_esf.get_record_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")
        single_env_index = single.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")

        multi_campaign = self.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"])
        multi_campaign[1][multi_env_index] = single.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME"])[1][single_env_index]


### SINGLE TO MULT
# single = ESFSave()
# single.read_file("doubler.save")

# double = ESFMultiSaveConversion()
# double.read_file("lmaoer.save_multiplayer")

# double.multi_to_single(single)
# single.write_file("lore2.save")

# env_index = single.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")

# lol = ESFMultiSave()
# lol.read_file("lmaoer.save_multiplayer")
# hmm = lol.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"])[1]
# print(hmm[lol.main_esf.get_data_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "SAVE_GAME_HEADER_MULTIPLAYER"], 10)])
# # print(lol.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_SETUP_LOCAL"]))
# menv_index = lol.main_esf.get_record_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")
# hmm = lol.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"])
# hmm[1][menv_index] = single.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME"])[1][env_index]


# MULTI TO SINGLE

# env_index = single.main_esf.get_record_element_index(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")

# lol = ESFSave()
# lol.read_file("doubler.save")
# # print(lol.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_SETUP_LOCAL"]))
# menv_index = lol.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME"], "CAMPAIGN_ENV")
# hmm = lol.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME"])
# hmm[1][menv_index] = single.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME"])[1][env_index]

# lol.write_file("pls_SINGLE.save")
# FACTION = self.main_esf.get_element_by_name(["MULTIPLAYER_CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
# # print(lol.main_esf.get_element([0])[1][0][1][0][1])
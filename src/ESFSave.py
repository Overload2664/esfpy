import lzma

from ESFtypes import *

from ESFReader import ESFReader
from ESFWriter import ESFWriter

from ESF import ESF

class ESFSave:
    # game: empire,napoleon,shogun,rome,attila
    def __init__(self, game="shogun"):
        self.game = game
        if(self.game != "empire" and self.game != "napoleon"):
            self.header_esf = ESF()
        self.main_esf = ESF()

    def read(self, esf_byte_arr):
        if(self.game != "empire" and self.game != "napoleon"):
            self.header_esf.read(esf_byte_arr)

            compressed_file = bytearray()

            compressed_info_data = self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA", "COMPRESSED_DATA_INFO"])[1]
            first_int = compressed_info_data[0][0].convert_to()

            for i in compressed_info_data[1][1]:
                compressed_file += i[0].data

            compressed_file += first_int.to_bytes(4, "little", signed=False)
            compressed_file += b'\x00\x00\x00\x00'

            compressed_data = self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][1]
            for i in compressed_data:
                compressed_file += i[0].data

            decompresser = lzma.LZMADecompressor()
            save_file_bin = decompresser.decompress(compressed_file)
            # print(type(self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1]))
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

            # shogun_header_file.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][1] = new_comp_header
            compressed_info_data = self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA", "COMPRESSED_DATA_INFO"])[1]
            prev_array = compressed_info_data[1][0]
            compressed_info_data[1] = (prev_array, new_comp_header)

            file_size = len(new_main_esf)
            compressed_info_data[0] = (UInt32(b'\x08', file_size.to_bytes(4, "little", signed=False)), None)

            new_com_data = []
            for i in new_compressed_data[13:]:
                new_com_data.append((UInt8(b'\x06', i.to_bytes(1, "little", signed=False)), None))
            # print(len(new_com_data))
            prev_array = self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0][0]
            # print(prev_array.node_type)
            self.header_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "COMPRESSED_DATA"])[1][0] = (prev_array, new_com_data)

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
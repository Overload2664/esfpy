import lzma

from ESFtypes import *

from ESFReader import ESFReader
from ESFWriter import ESFWriter

from ESF import ESF
from ESFSave import ESFSave

class ESFHotseat(ESFSave):
    # game: shogun,rome,attila
    def __init__(self, game="shogun"):
        super().__init__()
        self.game = game
    
    def increment_turn(self):
        WORLD = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"])[1]
        prev_turn = WORLD[1][0].convert_to()
        prev_turn += 1
        prev_turn_byte = prev_turn.to_bytes(4, "little", signed=False)
        WORLD[1] = (UInt32(b'\x08', prev_turn_byte), None)

    def get_all_factions(self):
        faction_names = []
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            # 1 for Attila
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)
            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            faction_names.append(faction_name)

        return faction_names

    def choose_vision(self, faction_name):
        # Same thing for Attila
        CAMPAIGN_SETUP_LOCAL = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_SETUP_LOCAL"])[1]
        if(self.game == "attila"):
            CAMPAIGN_SETUP_LOCAL[0] = (ASCIIString(faction_name), None)
        else:
            CAMPAIGN_SETUP_LOCAL[0] = (UniString(faction_name), None)

    def mark_factions_as_human(self, chosen_factions, is_human):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                # 5 for Attila
                bool_human_index = 7
                if(self.game == "attila"):
                    bool_human_index = 5
                real_bool_human_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], bool_human_index)
                

                FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
                # print(FACTION[1][real_bool_human_index])
                if(is_human):
                    FACTION[1][real_bool_human_index] = (BoolTrue(b'\x12'), None)
                else:
                    FACTION[1][real_bool_human_index] = (BoolFalse(b'\x13'), None)

    def get_factions_nature(self, chosen_factions):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                bool_human_index = 7
                if(self.game == "atilla"):
                    bool_human_index = 5
                real_bool_human_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], bool_human_index)

                FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
                is_human = FACTION[1][real_bool_human_index][0]
                factions_nature.append((faction_name, is_human.convert_to()))

        return factions_nature

    def mark_factions_as_playable(self, chosen_factions, is_playable):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                # Same for Attila
                bool_playable_index = 1
                real_bool_playable_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"], bool_playable_index)

                CAMPAIGN_PLAYER_SETUP = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"])
                # print(FACTION[1][real_bool_playable_index])
                if(is_playable):
                    CAMPAIGN_PLAYER_SETUP[1][real_bool_playable_index] = (BoolTrue(b'\x12'), None)
                else:
                    CAMPAIGN_PLAYER_SETUP[1][real_bool_playable_index] = (BoolFalse(b'\x13'), None)


    def get_factions_playability(self, chosen_factions):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                bool_playable_index = 1
                real_bool_playable_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"], bool_playable_index)

                CAMPAIGN_PLAYER_SETUP = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"])

                is_playable = CAMPAIGN_PLAYER_SETUP[1][real_bool_playable_index][0]
                factions_nature.append((faction_name, is_playable.convert_to()))

        return factions_nature

    def get_shroud(self):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            for node in FACTION[1]:
                if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_SHROUD"):
                    return node

        return None

    def get_empty_shroud(self):
        old_shroud = self.get_shroud()
        if(old_shroud == None):
            return None
        
        # lol.get_shroud()[1][4][1]
        # Doing all these copies to avoid doing unnecessary reference bugs
        old_content = old_shroud[1]
        old_blocks = old_content[4][1][0]

        new_content = old_content.copy()
        new_shroud = (old_shroud[0], new_content)

        # CAMPAIGN_SHROUD_content
        record_info = new_content[4][0]
        new_blocks = (old_blocks[0], [])
        new_content[4] = (record_info, [new_blocks])

        return new_shroud

    def put_shroud(self, chosen_factions, put_empty=True):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            has_shroud = False
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                for node in FACTION[1]:
                    if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_SHROUD"):
                        has_shroud = True
                        break
                if(not has_shroud):
                    shroud = None
                    if(put_empty):
                        shroud = self.get_empty_shroud()
                    else:
                        shroud = self.get_shroud()
                    last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "MORGUE")
                    # +1 for Attila
                    new_place = last_record + 2
                    if(self.game == "attila"):
                        new_place = last_record + 2
                    FACTION[1][new_place:new_place] = [shroud]
                    # print(FACTION[1][new_place])
                    
    def get_cam_missions(self):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            for node in FACTION[1]:
                if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_MISSION_MANAGER"):
                    return node

        return None

    def get_empty_cam_missions(self):
        old_cam_missions = self.get_cam_missions()
        if(old_cam_missions == None):
            return None
        
        old_contents = old_cam_missions[1]
        new_content = []
        new_cam_missions = (old_cam_missions[0], new_content)

        # missions_record = old_contents[0][0]
        # new_missions_array = (missions_record, [])
        # new_content.append(new_missions_array)
        # old_int = old_contents[1]
        for i in old_contents:
            if(isinstance(i[0], NodeRecord) or isinstance(i[0], ArrayRecord)):
                record_record = i[0]
                record_array = (record_record, [])
                new_content.append(record_array)
            else:
                new_content.append(i)

        return new_cam_missions

    def put_cam_missions(self, chosen_factions, put_empty=True):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            has_cam_missions = False
            name_index = 2
            if(self.game == "attila"):
                name_index = 1
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                for node in FACTION[1]:
                    if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_MISSION_MANAGER"):
                        has_cam_missions = True
                        break
                if(not has_cam_missions):
                    cam_missions = None
                    if(put_empty):
                        cam_missions = self.get_empty_cam_missions()
                    else:
                        cam_missions = self.get_cam_missions()
                    # GOVERNMENT for Attila
                    last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "FAMILY")
                    new_place = last_record
                    if(self.game == "attila"):
                        last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "GOVERNMENT")
                        new_place = last_record + 1
                    FACTION[1][new_place:new_place] = [cam_missions]
    
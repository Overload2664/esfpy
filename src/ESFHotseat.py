import lzma

from ESFtypes import *

from ESFReader import ESFReader
from ESFWriter import ESFWriter

from ESF import ESF
from ESFSave import ESFSave

EMPIRE_NAME_INDEX = 1
EMPIRE_HUMAN_INDEX = 7
EMPIRE_PLAYABLE_INDEX = 1

SHOGUN_NAME_INDEX = 2
SHOGUN_HUMAN_INDEX = 7
SHOGUN_PLAYABLE_INDEX = 1

ATTILA_NAME_INDEX = 1
ATTILA_HUMAN_INDEX = 5
ATTILA_PLAYABLE_INDEX = 1
ATTILA_POLITICS_INDEX = 5

# Notes:
"""
Atilla:
Currently the way this is done recruitment isn't possible. We have to change the values at:
WORLD -> FACTION_ARRAY -> FACTION -> CAMPAIGN_PLAYER_SETUP -> CAMPAIGN_PLAYER_SETUP_MODIFIABLES
to:
-2
-2
-2
1
"""

"""
Fall of the Samurai:
Apparently the values are a little different?
"""

class ESFHotseat(ESFSave):
    # game: shogun,rome,attila
    def __init__(self, game="shogun"):
        super().__init__()
        self.game = game

    def get_name_index(self):
        if(self.game == "shogun"):
            return SHOGUN_NAME_INDEX
        elif(self.game == "attila" or self.game == "rome"):
            return ATTILA_NAME_INDEX
        elif(self.game == "empire" or self.game == "napoleon"):
            return EMPIRE_NAME_INDEX
        else:
            return None

    def get_human_index(self):
        if(self.game == "shogun"):
            return SHOGUN_HUMAN_INDEX
        elif(self.game == "attila" or self.game == "rome"):
            return ATTILA_HUMAN_INDEX
        elif(self.game == "empire" or self.game == "napoleon"):
            return EMPIRE_HUMAN_INDEX
        else:
            return None

    def get_playable_index(self):
        if(self.game == "shogun"):
            return SHOGUN_PLAYABLE_INDEX
        elif(self.game == "attila" or self.game == "rome"):
            return ATTILA_PLAYABLE_INDEX
        elif(self.game == "empire" or self.game == "napoleon"):
            return EMPIRE_PLAYABLE_INDEX
        else:
            return None

    def get_all_factions(self):
        faction_names = []
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            # 1 for Attila
            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)
            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            faction_names.append(faction_name)

        return faction_names

    # Used for Attila in multiplayer
    def get_all_factions_politics(self):
        faction_politics = []
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            politics_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"], ATTILA_POLITICS_INDEX)
            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"])[1][politics_index]
            faction_name = faction_name_tup[0].data
            faction_politics.append(faction_name)

        return faction_politics
    
    def increment_turn(self, number=1):
        WORLD = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"])[1]
        prev_turn = WORLD[1][0].convert_to()
        prev_turn += number
        prev_turn_byte = prev_turn.to_bytes(4, "little", signed=False)
        WORLD[1] = (UInt32(b'\x08', prev_turn_byte), None)

    def get_current_turn(self):
        WORLD = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"])[1]
        current_turn = WORLD[1][0].convert_to()
        return current_turn

    def change_turn(self, turn):
        WORLD = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"])[1]
        turn_byte = turn.to_bytes(4, "little", signed=False)
        WORLD[1] = (UInt32(b'\x08', turn_byte), None)

    def change_turn_order(self, factions):
        faction_element = []
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])
        faction_array_index = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"], "FACTION_ARRAY")
        WORLD = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD"])[1]

        faction_array_record = FACTION_ARRAY[0]
        faction_array_content = []

        for faction in factions:
            for i in range(len(FACTION_ARRAY[1])):
                # 1 for Attila
                name_index = self.get_name_index()
                faction_con = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i])
                
                real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)
                faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
                faction_name = faction_name_tup[0].data
                if(faction_name == faction):
                    faction_array_content.append(faction_con)
                    break

        
        new_faction_array = (faction_array_record, faction_array_content)
        WORLD[faction_array_index] = new_faction_array

    def choose_vision(self, faction_name):
        # Same thing for Attila
        CAMPAIGN_SETUP_LOCAL = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_SETUP_LOCAL"])[1]
        if(self.game == "attila" or self.game == "rome"):
            CAMPAIGN_SETUP_LOCAL[0] = (ASCIIString(faction_name), None)
        else:
            CAMPAIGN_SETUP_LOCAL[0] = (UniString(faction_name), None)

    def get_vision(self):
        CAMPAIGN_SETUP_LOCAL = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_SETUP_LOCAL"])[1]
        faction_name = CAMPAIGN_SETUP_LOCAL[0][0].data
        return faction_name

    def mark_factions_as_human(self, chosen_factions, is_human):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                # 5 for Attila
                bool_human_index = self.get_human_index()
                real_bool_human_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], bool_human_index)
                

                FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
                # print(FACTION[1][real_bool_human_index])
                if(is_human):
                    bool_true = Bool(b'\x01', b'')
                    bool_true.convert_from(True)
                    FACTION[1][real_bool_human_index] = (bool_true, None)
                else:
                    bool_false = Bool(b'\x01', b'')
                    bool_false.convert_from(False)
                    FACTION[1][real_bool_human_index] = (bool_false, None)

        # To enable recruiting
        if(self.game == "attila" or self.game == "rome"):
            self.change_modifiers(chosen_factions, is_human)

    def get_factions_nature(self, chosen_factions):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                bool_human_index = self.get_human_index()
                real_bool_human_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], bool_human_index)

                FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
                is_human = FACTION[1][real_bool_human_index][0]
                factions_nature.append((faction_name, is_human.convert_to()))

        return factions_nature

    def mark_factions_as_playable(self, chosen_factions, is_playable):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                # Same for Attila
                bool_playable_index = self.get_playable_index()
                real_bool_playable_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"], bool_playable_index)

                CAMPAIGN_PLAYER_SETUP = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP"])
                # print(FACTION[1][real_bool_playable_index])
                if(is_playable):
                    bool_true = Bool(b'\x01', b'')
                    bool_true.convert_from(True)
                    CAMPAIGN_PLAYER_SETUP[1][real_bool_playable_index] = (bool_true, None)
                else:
                    bool_false = Bool(b'\x01', b'')
                    bool_false.convert_from(False)
                    CAMPAIGN_PLAYER_SETUP[1][real_bool_playable_index] = (bool_false, None)


    def get_factions_playability(self, chosen_factions):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                bool_playable_index = self.get_playable_index()
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

    def get_shroud_index(self):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            for node_index in range(len(FACTION[1])):
                node = FACTION[1][node_index]
                if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_SHROUD"):
                    return node_index

        return None

    def get_empty_shroud(self):
        old_shroud = self.get_shroud()
        if(old_shroud == None):
            return None
        
        # lol.get_shroud()[1][4][1]
        # Doing all these copies to avoid doing unnecessary reference bugs
        if(self.game != "empire" and self.game != "napoleon"):
            old_content = old_shroud[1]
            old_blocks = old_content[4][1][0]

            new_content = old_content.copy()
            new_shroud = (old_shroud[0], new_content)

            # CAMPAIGN_SHROUD_content
            record_info = new_content[4][0]
            new_blocks = (old_blocks[0], [])
            new_content[4] = (record_info, [new_blocks])

            return new_shroud
        else:
            return old_shroud

    def put_shroud(self, chosen_factions, put_empty=True):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            has_shroud = False
            name_index = self.get_name_index()
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
                    # last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "MORGUE")
                    # +1 for Attila
                    new_place = self.get_shroud_index()
                    # if(self.game == "attila"):
                    #     new_place = last_record + 2
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

    def get_cam_missions_index(self):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            for node_index in range(len(FACTION[1])):
                node = FACTION[1][node_index]
                if(isinstance(node[0], NodeRecord) and node[0].tag_name == "CAMPAIGN_MISSION_MANAGER"):
                    return node_index

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
            name_index = self.get_name_index()
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
                    # last_record = None
                    new_place = self.get_cam_missions_index()
                    # if(self.game == "shogun"):
                    #     last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "FAMILY")
                    #     new_place = last_record
                    # elif(self.game == "attila" or self.game == "rome"):
                    #     last_record = self.main_esf.get_record_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], "GOVERNMENT")
                    #     new_place = last_record + 1
                    FACTION[1][new_place:new_place] = [cam_missions]
    
    # To be able too recruit armies in Atilla
    def change_modifiers(self, chosen_factions, to_human=True):
        FACTION_ARRAY = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY"])[1]
        factions_nature = []

        for i in range(len(FACTION_ARRAY)):
            FACTION = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])
            CAMPAIGN_PLAYER_SETUP_MODIFIABLES = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION", "CAMPAIGN_PLAYER_SETUP", "CAMPAIGN_PLAYER_SETUP_INGAME_MODIFIABLES"])

            name_index = self.get_name_index()
            real_name_index = self.main_esf.get_data_element_index(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"], name_index)

            faction_name_tup = self.main_esf.get_element_by_name(["CAMPAIGN_SAVE_GAME", "CAMPAIGN_ENV", "CAMPAIGN_MODEL", "WORLD", "FACTION_ARRAY", i, "FACTION"])[1][real_name_index]
            faction_name = faction_name_tup[0].data
            if(faction_name in chosen_factions):
                if(to_human):
                    integer = Int32(b'\x04', b'')
                    integer.convert_from(-2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][0] = (integer, None)

                    integer = Int32(b'\x04', b'')
                    integer.convert_from(-2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][1] = (integer, None)

                    integer = Int32(b'\x04', b'')
                    integer.convert_from(-2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][2] = (integer, None)

                    integer = UInt32(b'\x08', b'')
                    integer.convert_from(1)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][3] = (integer, None)
                else:
                    integer = Int32(b'\x04', b'')
                    integer.convert_from(2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][0] = (integer, None)

                    integer = Int32(b'\x04', b'')
                    integer.convert_from(2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][1] = (integer, None)

                    integer = Int32(b'\x04', b'')
                    integer.convert_from(2)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][2] = (integer, None)

                    integer = UInt32(b'\x08', b'')
                    integer.convert_from(0)
                    CAMPAIGN_PLAYER_SETUP_MODIFIABLES[1][3] = (integer, None)


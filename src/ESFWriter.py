from ESFtypes import *

from datetime import datetime
from binascii import hexlify


class ESFWriter:
    def __init__(self, ESF):
        self.ESF = ESF

    # Hope this works...
    def write_node_data(self, node_data, magic_code):
        type_code = node_data.code
        data = node_data.data
        self.byte_list += list(type_code)
        if(type_code == b'\x0e'):
            if(magic_code == Magiccode.ABCA):
                index = None
                if(data in self.UniStrings):
                    index = self.UniStrings.index(data)
                else:
                    index = len(self.UniStrings)
                    self.UniStrings.append(data)
                index_byte = index.to_bytes(4, "little", signed=False)
                self.byte_list += list(index_byte)
            else:
                size = len(data)*2
                size_byte = size.to_bytes(2, "little", signed=False)
                self.byte_list += list(size_byte)
                self.byte_list += list(data)
        elif(type_code == b'\x0f'):
            if(magic_code == Magiccode.ABCA):
                index = None
                if(data in self.ASCIIStrings):
                    index = self.ASCIIStrings.index(data)
                else:
                    index = len(self.ASCIIStrings)
                    self.ASCIIStrings.append(data)
                index_byte = index.to_bytes(4, "little", signed=False)
                self.byte_list += list(index_byte)
            else:
                size = len(data)
                size_byte = size.to_bytes(2, "little", signed=False)
                self.byte_list += list(size_byte)
                self.byte_list += list(data)
        else:       
            self.byte_list += list(node_data.data)

    def write_data_array(self, array_data, array_list, magic_code):
        array_type = array_data.get_array_type()
        self.byte_list += list(array_type)

        # Writing size/offset
        size = len(array_list) * get_data_class_and_size(array_data.node_type)[1]
        if(magic_code == Magiccode.ABCA):
            size_var_byte = to_uintvart(size)[0]
            self.byte_list += list(size_var_byte)
        else:
            offset = len(array_type) + size + 4  # 4 is the four bytes
            self.byte_list += list(offset.to_bytes(4, "little", signed=False))


        # Writing data
        for i in array_list:
            data = i.data
            if(magic_code == Magiccode.ABCA and type_code == b'\x0e'):
                index = None
                if(data in self.UniStrings):
                    index = self.UniStrings.index(data)
                else:
                    index = len(self.UniStrings)
                    self.UniStrings.append(data)
                index_byte = index.to_bytes(4, "little", signed=False)
                self.byte_list += list(index_byte)
            elif(magic_code == Magiccode.ABCA and type_code == b'\x0f'):
                index = None
                if(data in self.ASCIIStrings):
                    index = self.ASCIIStrings.index(data)
                else:
                    index = len(self.ASCIIStrings)
                    self.ASCIIStrings.append(data)
                index_byte = index.to_bytes(4, "little", signed=False)
                self.byte_list += list(index_byte)
            else:
                self.byte_list += list(data)


    def read_bodies(self, magic_code):
        while(len(self.node_bodies) > 0):
            next_node = self.node_bodies.pop()
            if(isinstance(next_node[0], NodeRecord)):
                if(magic_code == Magiccode.ABCA):
                    if(next_node[2] == 0):
                        self.byte_list += list(b'\xa0')
                        node_info = next_node[0]
                        node_content = next_node[1]

                        tag_index = None
                        if(node_info.tag_name in self.tag_names):
                            tag_index = self.tag_names.index(node_info.tag_name)
                        else:
                            tag_index = len(self.tag_names)
                            self.tag_names.append(node_info.tag_name)
                        list(tag_index.to_bytes(2, "little", signed=False))


                        version = node_info.version
                        self.byte_list += list(version.to_bytes(1, "little", signed=False))

                        size_address = len(self.byte_list)
                        self.byte_list += list(b'\x00')


                        new_node = (next_node[0], next_node[1], 1, size_address)
                        self.node_bodies.append(new_node)

                        keys = list(next_node[1].keys())[::-1]
                        values = list(next_node[1].values())[::-1]

                        for i in range(len(keys)):
                            self.node_bodies.append((keys[i], values[i], 0, 0))
                        
                    else:
                        break

                else:
                    if(next_node[2] == 0):
                        break
                    else:
                        break
            elif(isinstance(next_node[0], ArrayRecord)):
                break
            elif(isinstance(next_node[0], ArrayNode)):
                self.write_data_array(self, next_node[0], next_node[1], magic_code)
            else:
                self.write_node_data(next_node[0], magic_code)

    def write(self, magic_code):
        self.byte_list = []
        self.tag_names = []
        if(magic_code == Magiccode.ABCA or magic_code == Magiccode.ABCF):
            self.ASCIIStrings = []
            self.UniStrings = []

        # Magic code
        if(magic_code == Magiccode.ABCA):
            self.byte_list += list(b'\xca\xab\x00\x00')
        elif(magic_code == Magiccode.ABCF):
            self.byte_list += list(b'\xcf\xab\x00\x00')
        elif(magic_code == Magiccode.ABCE):
            self.byte_list += list(b'\xce\xab\x00\x00')
        elif(magic_code == Magiccode.ABCD):
            self.byte_list += list(b'\xcd\xab\x00\x00')

        # Four zero bytes
        if(magic_code != Magiccode.ABCD):
            self.byte_list += list(b'\x00\x00\x00\x00')

        # Unix time, four bytes
        if(magic_code != Magiccode.ABCD):
            unix_timestamp = int((datetime.now() - datetime(1970, 1, 1)).total_seconds())
            self.byte_list += list(unix_timestamp.to_bytes(4, "little", signed=False))

        # Offset to footer
        self.footer_adr_header = len(self.byte_list)
        self.byte_list += list(b'\x00\x00\x00\x00')

        # root node
        # root node code
        self.byte_list += list(b'\x80')

        root_node, root_content = None, None
        for key, value in self.ESF.items():
            root_node = key
            root_content = value
        tag_name = root_node.tag_name
        self.tag_names.append(tag_name)
        # Root's tag name index can always be zero
        self.byte_list += list(b'\x00\x00')
        version = root_node.version
        self.byte_list += list(version.to_bytes(1, "little", signed=False))

        self.root_node_adr = len(self.byte_list)
        if(magic_code == Magiccode.ABCA):
            self.byte_list += list(b'\x00')
        else:
            self.byte_list += list(b'\x00\x00\x00\x00')


        self.node_bodies = []
        root_children_keys = list(root_content.keys())[::-1]
        root_children_values = list(root_content.values())[::-1]
        for i in range(len(root_children_keys)):
            self.node_bodies.append((root_children_keys[i], root_children_values[i], 0, 0))

        # (NodeClass, OrderedDict, should_address: 0 not yet | 1 yes, address' address)
        self.read_bodies(magic_code)
        

        print(self.byte_list)



# if __name__ == "__main__":
#     lol = ESFWriter(32)
#     lol.write(Magiccode.ABCA)

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
            if(magic_code == Magiccode.ABCA or magic_code == Magiccode.ABCF):
                index = None
                if(data in self.UniStrings):
                    index = self.UniStrings.index(data)
                else:
                    index = len(self.UniStrings)
                    self.UniStrings.append(data)
                index_byte = index.to_bytes(4, "little", signed=False)
                self.byte_list += list(index_byte)
            else:
                size = len(data)
                size_byte = size.to_bytes(2, "little", signed=False)
                if(len(self.byte_list) == 576615):
                    print(node_data.adr)
                self.byte_list += list(size_byte)

                self.byte_list += list(data.encode('utf-16'))[2:]
        elif(type_code == b'\x0f'):
            if(magic_code == Magiccode.ABCA or magic_code == Magiccode.ABCF):
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
                self.byte_list += list(data.encode('utf-8'))
        else:       
            self.byte_list += list(node_data.data)

    def write_data_array(self, array_data, array_list, magic_code):
        array_type = array_data.get_array_type()
        type_code = array_data.node_type
        self.byte_list += list(array_type)

        # Writing size/offset
        size = len(array_list) * get_data_class_and_size(array_data.node_type)[1]
        if(magic_code == Magiccode.ABCA):
            size_var_byte = to_uintvart(size)[0]
            self.byte_list += list(size_var_byte)
        else:
            offset = len(self.byte_list) + size + 4  # 4 is the four bytes
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
            # x = 0
            # for welp in self.node_bodies:
            #     if(isinstance(welp[0], DataNode) and welp[0].code == b'\x17'):
            #         x += 1
            # print(x)

            
            next_node = self.node_bodies.pop()
            # if(isinstance(next_node[0], ArrayRecord) or isinstance(next_node[0], NodeRecord)):
            #     print(next_node[0].tag_name)  

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
                        self.byte_list += list(tag_index.to_bytes(2, "little", signed=False))


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
                        size_address = next_node[3]
                        begin_address = size_address + 1
                        current_address = len(self.byte_list)
                        size = current_address - begin_address
                        size_var, size_len = to_uintvart(size)

                        self.byte_list[size_address:size_address+1] = list(size_var)

                else:
                    if(next_node[2] == 0):
                        self.byte_list += list(b'\x80')
                        node_info = next_node[0]
                        node_content = next_node[1]

                        tag_index = None
                        if(node_info.tag_name in self.tag_names):
                            tag_index = self.tag_names.index(node_info.tag_name)
                        else:
                            tag_index = len(self.tag_names)
                            self.tag_names.append(node_info.tag_name)
                        self.byte_list += list(tag_index.to_bytes(2, "little", signed=False))


                        version = node_info.version
                        self.byte_list += list(version.to_bytes(1, "little", signed=False))

                        size_address = len(self.byte_list)
                        self.byte_list += list(b'\x00\x00\x00\x00')


                        new_node = (next_node[0], next_node[1], 1, size_address)
                        self.node_bodies.append(new_node)

                        keys = list(next_node[1].keys())[::-1]
                        values = list(next_node[1].values())[::-1]

                        for i in range(len(keys)):
                            self.node_bodies.append((keys[i], values[i], 0, 0))
                        
                    else:
                        size_address = next_node[3]
                        current_address = len(self.byte_list)

                        self.byte_list[size_address:size_address+4] = list(current_address.to_bytes(4, "little", signed=False))
            elif(isinstance(next_node[0], ArrayRecord)):
                if(magic_code == Magiccode.ABCA):
                    if(next_node[2] == 0):
                        self.byte_list += list(b'\xe0')
                        array_info = next_node[0]
                        array_content = next_node[1]

                        tag_index = None
                        if(array_info.tag_name in self.tag_names):
                            tag_index = self.tag_names.index(array_info.tag_name)
                        else:
                            tag_index = len(self.tag_names)
                            self.tag_names.append(array_info.tag_name)
                        self.byte_list += list(tag_index.to_bytes(2, "little", signed=False))


                        version = array_info.version
                        self.byte_list += list(version.to_bytes(1, "little", signed=False))

                        size_address = len(self.byte_list)
                        self.byte_list += list(b'\x00')

                        length_size = len(array_content)
                        length_size_var, _ = to_uintvart(length_size)
                        self.byte_list += list(length_size_var)


                        new_node = (next_node[0], next_node[1], 1, size_address)
                        self.node_bodies.append(new_node)

                        contents = (next_node[1])[::-1]
                        for content in contents:

                            # self.node_bodies.append((keys[i], values[i], 0, 0))



                            # content_address = len(self.byte_list)
                            # self.byte_list += list(b'\x00')

                            array_content_adr = [0]
                            array_content_end = ("ArrayContentEnd", None, None, array_content_adr)
                            self.node_bodies.append(array_content_end)

                            keys = list(content.keys())[::-1]
                            values = list(content.values())[::-1]

                            for i in range(len(keys)):

                                self.node_bodies.append((keys[i], values[i], 0, 0))

                            array_content_start = ("ArrayContentStart", None, None, array_content_adr)
                            self.node_bodies.append(array_content_start)



                        
                    else:
                        size_address = next_node[3]
                        begin_address = size_address + 1
                        current_address = len(self.byte_list)
                        size = current_address - begin_address
                        size_var, size_len = to_uintvart(size)

                        self.byte_list[size_address:size_address+1] = list(size_var)

                else:
                    if(next_node[2] == 0):
                        self.byte_list += list(b'\x81')
                        array_info = next_node[0]
                        array_content = next_node[1]

                        tag_index = None
                        if(array_info.tag_name in self.tag_names):
                            tag_index = self.tag_names.index(array_info.tag_name)
                        else:
                            tag_index = len(self.tag_names)
                            self.tag_names.append(array_info.tag_name)
                        self.byte_list += list(tag_index.to_bytes(2, "little", signed=False))


                        version = array_info.version
                        self.byte_list += list(version.to_bytes(1, "little", signed=False))

                        size_address = len(self.byte_list)
                        self.byte_list += list(b'\x00\x00\x00\x00')

                        length_size = len(array_content)
                        # length_size_var, _ = to_uintvart(length_size)
                        self.byte_list += list(length_size.to_bytes(4, "little", signed=False))


                        new_node = (next_node[0], next_node[1], 1, size_address)
                        self.node_bodies.append(new_node)

                        contents = (next_node[1])[::-1]
                        for content in contents:

                            # self.node_bodies.append((keys[i], values[i], 0, 0))



                            # content_address = len(self.byte_list)
                            # self.byte_list += list(b'\x00')

                            array_content_adr = [0]
                            array_content_end = ("ArrayContentEnd", None, None, array_content_adr)
                            self.node_bodies.append(array_content_end)

                            keys = list(content.keys())[::-1]
                            values = list(content.values())[::-1]

                            for i in range(len(keys)):

                                self.node_bodies.append((keys[i], values[i], 0, 0))

                            array_content_start = ("ArrayContentStart", None, None, array_content_adr)
                            self.node_bodies.append(array_content_start)
                        
                    else:
                        size_address = next_node[3]
                        current_address = len(self.byte_list)

                        self.byte_list[size_address:size_address+4] = list(current_address.to_bytes(4, "little", signed=False))
            # all ABCA for now
            elif(next_node[0] == "ArrayContentStart"):
                if(magic_code == Magiccode.ABCA):
                    content_address = len(self.byte_list)
                    next_node[3][0] = content_address
                    self.byte_list += list(b'\x00')
                else:
                    content_address = len(self.byte_list)
                    next_node[3][0] = content_address
                    self.byte_list += list(b'\x00\x00\x00\x00')

            elif(next_node[0] == "ArrayContentEnd"):
                if(magic_code == Magiccode.ABCA):
                    size_address = next_node[3][0]
                    begin_address = size_address + 1
                    current_address = len(self.byte_list)
                    size = current_address - begin_address
                    size_var, size_len = to_uintvart(size)

                    self.byte_list[size_address:size_address+1] = list(size_var)
                else:
                    size_address = next_node[3][0]
                    current_address = len(self.byte_list)

                    self.byte_list[size_address:size_address+4] = list(current_address.to_bytes(4, "little", signed=False))

            elif(isinstance(next_node[0], ArrayNode)):
                self.write_data_array(next_node[0], next_node[1], magic_code)
            else:
                self.write_node_data(next_node[0], magic_code)
            # else:
            #     print(next_node[0])
            #     print("ERROR")
            #     break

    def write_footer(self, magic_code):
        tag_name_size = len(self.tag_names)
        self.byte_list += list(tag_name_size.to_bytes(2, "little", signed=False))

        for tag_name in self.tag_names:
            tag_name_len = len(tag_name)
            self.byte_list += list(tag_name_len.to_bytes(2, "little", signed=False))
            self.byte_list += list(tag_name.encode('utf-8'))

        if(magic_code == Magiccode.ABCA or magic_code == Magiccode.ABCF):
            uni_string_size = len(self.UniStrings)
            self.byte_list += list(uni_string_size.to_bytes(4, "little", signed=False))
            for i in range(uni_string_size):
                uni_string = self.UniStrings[i]
                uni_string_len = len(uni_string)
                self.byte_list += list(uni_string_len.to_bytes(2, "little", signed=False))
                self.byte_list += list(uni_string.encode('utf-16'))[2:]
                self.byte_list += list(i.to_bytes(4, "little", signed=False))

            ascii_string_size = len(self.ASCIIStrings)
            self.byte_list += list(ascii_string_size.to_bytes(4, "little", signed=False))
            for i in range(ascii_string_size):
                ascii_string = self.ASCIIStrings[i]
                ascii_string_len = len(ascii_string)
                self.byte_list += list(ascii_string_len.to_bytes(2, "little", signed=False))
                self.byte_list += list(ascii_string.encode('utf-8'))
                self.byte_list += list(i.to_bytes(4, "little", signed=False))



        
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


        # Root address
        begin_address = self.root_node_adr + 1
        current_address = len(self.byte_list)


        if(magic_code == Magiccode.ABCA):
            size = current_address - begin_address
            size_var, size_len = to_uintvart(size)
            self.byte_list[self.root_node_adr:self.root_node_adr+1] = list(size_var)
        else:
            self.byte_list[self.root_node_adr:self.root_node_adr+4] = list(current_address.to_bytes(4, "little", signed=False))

        # Footer address
        current_address = len(self.byte_list)
        self.byte_list[self.footer_adr_header:self.footer_adr_header+4] = list(current_address.to_bytes(4, "little", signed=False))

        self.write_footer(magic_code)    
        with open("saves/mysave.txt", "wb") as binary_file:
            binary_file.write(bytearray(self.byte_list))



# if __name__ == "__main__":
#     lol = ESFWriter(32)
#     lol.write(Magiccode.ABCA)

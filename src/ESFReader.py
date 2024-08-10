from collections import OrderedDict
from ESFtypes import *
# from ESFtypes import Magiccode, NodeRecord, RecordType, from_uintvart, UniString, ASCIIString, Int, Bool, XYCoordinate, XYZCoordinate, Angle, ArrayRecord, ArrayNode, get_data_class_and_size


class ESFReader:
    def __init__(self, data):
        self.data = data
        self.magic_code = None
        self.current_byte = 0
        self.body = []

    def read(self):
        self.read_header()
        self.read_footer()
        self.read_body(initial_dict=self.body, is_root=True)
        return self.body

    def read_header(self):
        self.read_magic_code()
        if(self.magic_code != Magiccode.ABCD):
            # Four bytes always zeros
            self.current_byte += 4 

            self.time = self.read_bytes(4, self.current_byte)
            self.current_byte += 4

        
        footer_bytes = self.read_bytes(4, self.current_byte)
        self.footer = int.from_bytes(footer_bytes, byteorder='little', signed=False)
        self.current_byte += 4

    def read_magic_code(self):
        magic_code = self.read_bytes(2, self.current_byte)
        if(magic_code == b'\xca\xab'):
            self.magic_code = Magiccode.ABCA
        elif(magic_code == b'\xcf\xab'):
            self.magic_code = Magiccode.ABCF
        elif(magic_code == b'\xce\xab'):
            self.magic_code = Magiccode.ABCE
        elif(magic_code == b'\xcd\xab'):
            self.magic_code = Magiccode.ABCD
        else:
            raise "File format not supported."

        self.current_byte += 4

    def read_footer(self):
        self.read_tag_names()

        if(self.magic_code == Magiccode.ABCA or self.magic_code == Magiccode.ABCF):
            self.read_unicode_strings()
            self.read_ascii_strings()

    def read_tag_names(self):
        self.tag_names = []
        self.current_footer = self.footer
        tag_names_size_byte = self.read_bytes(2, self.current_footer)
        tag_names_size = int.from_bytes(tag_names_size_byte, byteorder='little', signed=False)
        self.current_footer += 2

        for i in range(tag_names_size):
            tag_name_size_byte = self.read_bytes(2, self.current_footer)
            tag_name_size = int.from_bytes(tag_name_size_byte, byteorder='little', signed=False)
            self.current_footer += 2

            tag_name = self.read_bytes(tag_name_size, self.current_footer).decode("utf-8")
            self.tag_names.append(tag_name)
            self.current_footer += tag_name_size

    def read_unicode_strings(self):
        self.unicode_strings = {}
        self.read_bytes(4, self.current_footer)
        unicode_strings_size_byte = self.read_bytes(4, self.current_footer)
        unicode_strings_size = int.from_bytes(unicode_strings_size_byte, byteorder='little', signed=False)
        self.current_footer += 4

        for i in range(unicode_strings_size):
            unicode_string_size_byte = self.data[self.current_footer:self.current_footer+2]
            unicode_string_size = int.from_bytes(unicode_string_size_byte, byteorder='little', signed=False)
            self.current_footer += 2

            unicode_string = self.read_bytes(unicode_string_size*2, self.current_footer).decode("utf-16")
            self.current_footer += unicode_string_size*2

            unicode_string_index_byte = self.read_bytes(4, self.current_footer)
            unicode_string_index = int.from_bytes(unicode_string_index_byte, byteorder='little', signed=False)
            self.current_footer += 4

            self.unicode_strings[unicode_string_index] = unicode_string

    def read_ascii_strings(self):
        self.ascii_strings = {}
        ascii_strings_size_byte = self.read_bytes(4, self.current_footer)
        ascii_strings_size = int.from_bytes(ascii_strings_size_byte, byteorder='little', signed=False)
        self.current_footer += 4

        for i in range(ascii_strings_size):
            ascii_string_size_byte = self.data[self.current_footer:self.current_footer+2]
            ascii_string_size = int.from_bytes(ascii_string_size_byte, byteorder='little', signed=False)
            self.current_footer += 2

            ascii_string = self.read_bytes(ascii_string_size, self.current_footer).decode("utf-8")
            self.current_footer += ascii_string_size

            ascii_string_index_byte = self.read_bytes(4, self.current_footer)
            ascii_string_index = int.from_bytes(ascii_string_index_byte, byteorder='little', signed=False)
            self.current_footer += 4

            self.ascii_strings[ascii_string_index] = ascii_string

    def read_data_node(self, type_code, stack_dict):
        if(type_code == b'\x01'):
            bool_byte = self.read_bytes(1, self.current_byte)
            self.current_byte += 1

            bool_data = Bool(type_code, bool_byte)
            stack_dict[-1].append((bool_data, None))
            return

        if(type_code == b'\x02'):
            size = 1
            signed = True
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = Int8(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x03'):
            size = 2
            signed = True
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = Int16(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x04'):
            size = 4
            signed = True
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = Int32(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x05'):
            size = 8
            signed = True
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = Int64(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x06'):
            size = 1
            signed = False
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = UInt8(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x07'):
            size = 2
            signed = False
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = UInt16(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x08'):
            size = 4
            signed = False
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = UInt32(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x09'):
            size = 8
            signed = False
            int_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            int_data = UInt64(type_code, int_byte)
            stack_dict[-1].append((int_data, None))
            return

        if(type_code == b'\x0a'):
            size = 4
            float_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            float_data = Float32(type_code, float_byte)
            stack_dict[-1].append((float_data, None))
            return

        if(type_code == b'\x0b'):
            size = 8
            float_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            float_data = Float64(type_code, float_byte)
            stack_dict[-1].append((float_data, None))
            return

        if(type_code == b'\x0c'):
            size = 4*2

            floatXY_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            XYCoord_data = XYCoordinate(floatXY_byte)
            stack_dict[-1].append((XYCoord_data, None))
            return

        if(type_code == b'\x0d'):
            size = 4*3

            floatXYZ_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            XYZCoord_data = XYZCoordinate(floatXYZ_byte)
            stack_dict[-1].append((XYZCoord_data, None))
            return

        if(type_code == b'\x0e'):
            size = 4
            string_index_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            string_index = int.from_bytes(string_index_byte, byteorder='little', signed=False)
            string = self.unicode_strings[string_index]
            string_data = UniString(string)

            stack_dict[-1].append((string_data, None))
            return

        if(type_code == b'\x0f'):
            size = 4
            string_index_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            string_index = int.from_bytes(string_index_byte, byteorder='little', signed=False)
            string = self.ascii_strings[string_index]
            string_data = ASCIIString(string)

            stack_dict[-1].append((string_data, None))
            return

        if(type_code == b'\x10'):
            size = 2
            signed = False
            angle_byte = self.read_bytes(size, self.current_byte)
            self.current_byte += size

            angle_data = Angle(angle_byte)
            stack_dict[-1].append((angle_data, None))
            return

        if(self.magic_code == Magiccode.ABCA):
            if(type_code == b'\x12'):
                bool_data = BoolTrue(type_code)
                stack_dict[-1].append((bool_data, None))
                return

            if(type_code == b'\x13'):
                bool_data = BoolFalse(type_code)
                stack_dict[-1].append((bool_data, None))
                return
    
            if(type_code == b'\x14'):
                size = 4
                signed = False

                int_data = UInt32_zero(type_code)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x15'):
                size = 4
                signed = False

                int_data = UInt32_one(type_code)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x16'):
                real_size = 4
                compact_size = 1
                signed = False
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = UInt8(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x17'):
                real_size = 4
                compact_size = 2
                signed = False
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = UInt16(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x18'):
                real_size = 4
                compact_size = 3
                signed = False
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = UInt24be(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x19'):
                size = 4
                signed = True

                int_data = Int32_zero(type_code)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x1a'):
                real_size = 4
                compact_size = 1
                signed = True
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = Int8(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x1b'):
                real_size = 4
                compact_size = 2
                signed = True
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = Int16(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x1c'):
                real_size = 4
                compact_size = 3
                signed = True
                int_byte = self.read_bytes(compact_size, self.current_byte)
                self.current_byte += compact_size

                int_data = Int24be(type_code, int_byte)
                stack_dict[-1].append((int_data, None))
                return

            if(type_code == b'\x1d'):
                size = 4

                float_data = Float32_zero(type_code)
                stack_dict[-1].append((float_data, None))
                return

    def read_body(self, initial_dict, is_root, initial_offset=None):
        stack_offest = None
        stack_dict = None
        if(is_root):
            stack_offest = []
            stack_dict = []
            root_code = self.read_bytes(1, self.current_byte)
            self.current_byte += 1
            if root_code != b'\x80':
                raise "That's not supposed to happen"

            tag_name_byte_index = self.read_bytes(2, self.current_byte)
            tag_name_index = int.from_bytes(tag_name_byte_index, byteorder='little', signed=False)
            tag_name = self.tag_names[tag_name_index]
            self.current_byte += 2

            version_byte = self.read_bytes(1, self.current_byte)
            version = int.from_bytes(version_byte, byteorder='little', signed=False)
            self.current_byte += 1

            root_record = None

            if(self.magic_code == Magiccode.ABCA):
                size_byte = self.read_bytes(5, self.current_byte)
                size, byte_len = from_uintvart(size_byte)
                self.current_byte += byte_len
                root_record = NodeRecord(RecordType.ROOT, tag_name, version, size)
                stack_offest.append(self.current_byte + size)
            else:
                offset_byte = self.read_bytes(4, self.current_byte)
                offset = int.from_bytes(offset_byte, byteorder='little', signed=False)
                self.current_byte += 4
                size = offset - self.current_byte - 1
                root_record = NodeRecord(RecordType.ORIG, tag_name, version, size)
                stack_offest.append(offset - 1)

            # self.body
            initial_list = []
            initial_dict.append((root_record, initial_list))
            # initial_dict[root_record] = OrderedDict()
            stack_dict.append(initial_list)
        else:
            stack_offest = [initial_offset]
            stack_dict = [initial_dict]


        while(len(stack_offest) > 0):
            if(self.current_byte >= stack_offest[-1]):
                stack_offest.pop(-1)
                stack_dict.pop(-1)
                continue

            type_code = self.read_bytes(1, self.current_byte)
            
            self.current_byte += 1
            # Record nodes
            if(self.magic_code != Magiccode.ABCA):
                if(type_code == b'\x80'):
                    tag_name_index_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2

                    tag_name_index = int.from_bytes(tag_name_index_byte, byteorder='little', signed=False)
                    tag_name = self.tag_names[tag_name_index]

                    version_byte = self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    version = int.from_bytes(version_byte, byteorder='little', signed=False)

                    offset_byte = self.read_bytes(4, self.current_byte)
                    offset = int.from_bytes(offset_byte, byteorder='little', signed=False)
                    self.current_byte += 4
                    size = offset - self.current_byte - 1
                    record = NodeRecord(RecordType.ORIG, tag_name, version, size)
                    stack_offest.append(offset - 1)

                    record_list = []
                    stack_dict[-1].append((record, record_list))
                    stack_dict.append(record_list)
                    continue
            else:
                if(type_code == b'\xa0'):
                    tag_name_index_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2
                    tag_name_index = int.from_bytes(tag_name_index_byte, byteorder='little', signed=False)
                    tag_name = self.tag_names[tag_name_index]

                    version_byte = self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    version = int.from_bytes(version_byte, byteorder='little', signed=False)

                    size_byte = self.read_bytes(5, self.current_byte)
                    size, byte_len = from_uintvart(size_byte)
                    self.current_byte += byte_len
                    record = NodeRecord(RecordType.TRAD, tag_name, version, size)
                    stack_offest.append(self.current_byte + size)

                    record_list = []
                    stack_dict[-1].append((record, record_list))
                    stack_dict.append(record_list)
                    continue
                elif((type_code[0] & 0b11100000) == 0x80):
                    record_field = type_code + self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    record_field_int = int.from_bytes(record_field, byteorder='big', signed=False)

                    tag_name_index = record_field_int & (0b0000000111111111)
                    tag_name = self.tag_names[tag_name_index]

                    version = (record_field[0] & 0b00011110) >> 1
                    
                    size_byte = self.read_bytes(5, self.current_byte)
                    size, byte_len = from_uintvart(size_byte)
                    self.current_byte += byte_len
                    record = NodeRecord(RecordType.COMP, tag_name, version, size)
                    stack_offest.append(self.current_byte + size)

                    record_list = []
                    stack_dict[-1].append((record, record_list))
                    stack_dict.append(record_list)
                    continue

            if(type_code == b'\x0e'):
                if(self.magic_code == Magiccode.ABCA or self.magic_code == Magiccode.ABCF):
                    string_index_byte = self.read_bytes(4, self.current_byte)
                    self.current_byte += 4

                    string_index = int.from_bytes(string_index_byte, byteorder='little', signed=False)
                    string = self.unicode_strings[string_index]
                    string_data = UniString(string)

                    stack_dict[-1].append((string_data, None))
                    continue
                else:
                    size_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2

                    size = int.from_bytes(size_byte, byteorder='little', signed=False)
                    string = self.read_bytes(size*2, self.current_byte).decode("utf-16")
                    self.current_byte += size*2

                    string_data = UniString(string)

                    stack_dict[-1].append((string_data, None))
                    continue

            if(type_code == b'\x0f'):
                if(self.magic_code == Magiccode.ABCA or self.magic_code == Magiccode.ABCF):
                    string_index_byte = self.read_bytes(4, self.current_byte)
                    self.current_byte += 4

                    string_index = int.from_bytes(string_index_byte, byteorder='little', signed=False)
                    string = self.ascii_strings[string_index]
                    string_data = ASCIIString(string)

                    stack_dict[-1].append((string_data, None))
                    continue
                else:
                    size_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2

                    size = int.from_bytes(size_byte, byteorder='little', signed=False)
                    string = self.read_bytes(size, self.current_byte).decode("utf-8")
                    self.current_byte += size

                    string_data = ASCIIString(string)

                    stack_dict[-1].append((string_data, None))
                    continue

            # data node
            if(int.from_bytes(type_code, byteorder='little', signed=False) >= 0x1 and
                int.from_bytes(type_code, byteorder='little', signed=False) <= 0x1d):
                self.read_data_node(type_code, stack_dict)
                continue

            

            # data array (not tested)
            if(int.from_bytes(type_code, byteorder='little', signed=False) >= 0x41 and
                int.from_bytes(type_code, byteorder='little', signed=False) <= 0x5f):
                data_type = int.from_bytes(type_code, byteorder='little', signed=False) - 0x40
                data_type_byte = data_type.to_bytes(1, "little", signed=False)
                if(self.magic_code == Magiccode.ABCA):
                    array_size_byte = self.read_bytes(5, self.current_byte)
                    array_size, byte_len = from_uintvart(array_size_byte)
                    self.current_byte += byte_len

                    array_length = (array_size // get_data_class_and_size(data_type_byte)[1])
                    array_node = ArrayNode(data_type_byte)

                    array_list = []
                    stack_dict[-1].append((array_node, array_list))
                    stack_dict.append(array_list)

                    for i in range(array_length):
                        self.read_data_node(data_type_byte, stack_dict)

                    stack_dict.pop(-1)
                else:
                    offset_byte = self.read_bytes(4, self.current_byte)
                    offset = int.from_bytes(offset_byte, byteorder='little', signed=False)
                    self.current_byte += 4
                    array_size = offset - self.current_byte - 1

                    array_length = (array_size // get_data_class_and_size(data_type_byte)[1]) + 1
                    array_node = ArrayNode(data_type_byte)
                    array_list = []
                    stack_dict[-1].append((array_node, array_list))
                    stack_dict.append(array_list)

                    for i in range(array_length):
                        self.read_data_node(data_type_byte, stack_dict)

                    stack_dict.pop(-1)


                continue

            # last thing remaining: Record Arrays...
            # This little maneuver is going to cost us 51 years
            if(self.magic_code != Magiccode.ABCA):
                if(type_code == b'\x81'):
                    tag_name_index_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2

                    tag_name_index = int.from_bytes(tag_name_index_byte, byteorder='little', signed=False)
                    tag_name = self.tag_names[tag_name_index]

                    version_byte = self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    version = int.from_bytes(version_byte, byteorder='little', signed=False)

                    offset_byte = self.read_bytes(4, self.current_byte)
                    offset = int.from_bytes(offset_byte, byteorder='little', signed=False)
                    self.current_byte += 4
                    size = offset - self.current_byte - 1

                    elements_number_byte = self.read_bytes(4, self.current_byte)
                    elements_number = int.from_bytes(elements_number_byte, byteorder='little', signed=False)
                    self.current_byte += 4

                    array_record = ArrayRecord(type_code, tag_name, version)
                    # stack_dict[-1][array_record] = []
                    array_list = []
                    stack_dict[-1].append((array_record, array_list))
                    # stack_dict.append(array_list)

                    # A small bug may appear here...
                    # while(self.current_byte < offset - 1):
                    for i in range(elements_number):
                        offset_byte = self.read_bytes(4, self.current_byte)
                        offset = int.from_bytes(offset_byte, byteorder='little', signed=False)
                        self.current_byte += 4
                        size = offset - self.current_byte - 1

                        new_list = []
                        self.read_body(new_list, is_root=False, initial_offset=offset)
                        array_list.append(new_list)
                        # stack_dict[-1][array_record].append(new_dict)

                    

                    # record = ArrayRecord(type_code, tag_name, version)
                    # stack_offest.append(offset - 1)

                    # stack_dict[-1][record] = OrderedDict()
                    # stack_dict.append(stack_dict[-1][record])
                    continue
            else:
                if(type_code == b'\xe0'):
                    tag_name_index_byte = self.read_bytes(2, self.current_byte)
                    self.current_byte += 2

                    tag_name_index = int.from_bytes(tag_name_index_byte, byteorder='little', signed=False)
                    tag_name = self.tag_names[tag_name_index]

                    version_byte = self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    version = int.from_bytes(version_byte, byteorder='little', signed=False)

                    size_byte = self.read_bytes(5, self.current_byte)
                    size, byte_len = from_uintvart(size_byte)
                    self.current_byte += byte_len

                    elements_number_byte = self.read_bytes(5, self.current_byte)
                    elements_number, byte_len = from_uintvart(elements_number_byte)
                    self.current_byte += byte_len

                    array_record = ArrayRecord(type_code, tag_name, version)
                    array_list = []
                    stack_dict[-1].append((array_record, array_list))
                    # stack_dict.append(array_list)

                    # A small bug may appear here...
                    # while(self.current_byte < offset - 1):
                    for i in range(elements_number):
                        size_byte = self.read_bytes(5, self.current_byte)
                        size, byte_len = from_uintvart(size_byte)
                        self.current_byte += byte_len
                        offset = size + self.current_byte
                        # size = offset - self.current_byte - 1 # -> offset = size + self.current_byte + 1

                        new_list = []
                        self.read_body(new_list, is_root=False, initial_offset=offset)
                        array_list.append(new_list)

                    
                    continue
                    # tag_name_index_byte = self.read_bytes(2, self.current_byte)
                    # self.current_byte += 2
                    # tag_name_index = int.from_bytes(tag_name_index_byte, byteorder='little', signed=False)
                    # tag_name = self.tag_names[tag_name_index]

                    # version_byte = self.read_bytes(1, self.current_byte)
                    # self.current_byte += 1
                    # version = int.from_bytes(version_byte, byteorder='little', signed=False)

                    # size_byte = self.read_bytes(5, self.current_byte)
                    # size, byte_len = from_uintvart(size_byte)
                    # self.current_byte += byte_len
                    # record = NodeRecord(RecordType.TRAD, tag_name, version, size)
                    # stack_offest.append(self.current_byte + size)

                    # stack_dict[-1][record] = OrderedDict()
                    # stack_dict.append(stack_dict[-1][record])
                    # continue
                elif((type_code[0] & 0b11100000) == 0xc0):
                    record_field = type_code + self.read_bytes(1, self.current_byte)
                    self.current_byte += 1
                    record_field_int = int.from_bytes(record_field, byteorder='big', signed=False)

                    tag_name_index = record_field_int & (0b0000000111111111)
                    tag_name = self.tag_names[tag_name_index]

                    version = (record_field[0] & 0b00011110) >> 1
                    
                    size_byte = self.read_bytes(5, self.current_byte)
                    size, byte_len = from_uintvart(size_byte)
                    self.current_byte += byte_len

                    elements_number_byte = self.read_bytes(5, self.current_byte)
                    elements_number, byte_len = from_uintvart(elements_number_byte)
                    self.current_byte += byte_len

                    array_record = ArrayRecord(type_code, tag_name, version)
                    array_list = []
                    stack_dict[-1].append((array_record, array_list))
                    # stack_dict.append(array_list)

                    # A small bug may appear here...
                    # while(self.current_byte < offset - 1):
                    for i in range(elements_number):
                        size_byte = self.read_bytes(5, self.current_byte)
                        size, byte_len = from_uintvart(size_byte)
                        self.current_byte += byte_len
                        offset = size + self.current_byte
                        # size = offset - self.current_byte - 1 # -> offset = size + self.current_byte + 1

                        new_list = []
                        self.read_body(new_list, is_root=False, initial_offset=offset)
                        array_list.append(new_list)
                    continue

            # This is good, it simply means that we didn't face an unsupported type code
            print("ERROR")
            break
            

    def read_bytes(self, byte_count, position):
        return self.data[position:position + byte_count]
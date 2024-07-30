from enum import Enum
from collections import OrderedDict
import struct

class Magiccode(Enum):
    ABCD = 1
    ABCE = 2
    ABCF = 3
    ABCA = 4

class RecordType(Enum):
    ORIG = 1
    ROOT = 2
    TRAD = 3
    COMP = 4

def from_uintvart(byte_array):
    # data = int.to_integer(byte_array)
    result = 0
    i = 0
    while(byte_array[i] & 0x80):
        result = (result << 7) | (byte_array[i] & 0x7f)
        i += 1
    result = (result << 7) | (byte_array[i] & 0x7f)
    i += 1

    return (result, i)

def to_uintvart(integer):
    uintvart = b''
    uintvart += int.to_bytes(integer & 0x7f, 1, "little")
    integer = integer >> 7 

    for i in range(4):
        uintvart = int.to_bytes((integer & 0x7f) | 0x80, 1, "little") + uintvart
        integer = integer >> 7 

    return uintvart

# if __name__ == "__main__":
#     xd = to_uintvart(255)
#     print(from_uintvart(xd))

class Bool:
    def __init__(self, data):
        self.data = data
        self.size = 1

    def convert_to(self):
        return bool.from_bytes(self.data, "little")

    def convert_from(self, value):
        if(value == 0):
            self.data = b'\x00'
        else:
            self.data = b'\x01'

    def __str__(self):
        if(self.convert_to()):
            return "Bool: True"
        else:
            return "Bool: False"

class Int:
    def __init__(self, code, data, size, signed, endian="little"):
        self.code = code
        self.data = data
        self.size = size
        self.signed = signed
        self.endian = endian

    def convert_to(self):
        return int.from_bytes(self.data, self.endian, signed=self.signed)

    def convert_from(self, value):
        self.data = value.to_bytes(self.size, self.endian, signed=self.signed)

    def to_little(self):
        self.data = self.convert_to().to_bytes(self.size, "little", signed=self.signed)
        self.endian = "little"

    def __str__(self):
        data_type = "int"
        if(self.signed == False):
            data_type = "u" + data_type
        data_type += str(self.size*8)
        if(self.endian == "big"):
            data_type += "be"

        return data_type + ": " + str(self.convert_to())


class Float:
    def __init__(self, code, data, size):
        self.code = code
        self.data = data
        self.size = size
        if(self.size == 4):
            self.type = "<f"
        elif(self.size == 8):
            self.type = "<d"
        else:
            raise "No such float data type"

    def convert_to(self):
        return struct.unpack(self.type, self.data)

    def convert_from(self, value):
        self.data = struct.pack(self.type, self.data)

class XYCoordinate:
    def __init__(self, data):
        self.code = "\x0c"
        self.data = data
        self.size = 8
    
    def convert_to(self):
        return (struct.unpack("<f", self.data[0:4]), struct.unpack("<f", self.data[4:8]))

    def convert_from(self, value):
        new_data = b''
        new_data += struct.pack("<f", value[0])
        new_data += struct.pack("<f", value[1])
        self.data = new_data

class XYZCoordinate:
    def __init__(self, data):
        self.code = "\x0d"
        self.data = data
        self.size = 12
    
    def convert_to(self):
        return (struct.unpack("<f", self.data[0:4]), struct.unpack("<f", self.data[4:8]),
                struct.unpack("<f", self.data[8:12]))

    def convert_from(self, value):
        new_data = b''
        new_data += struct.pack("<f", value[0])
        new_data += struct.pack("<f", value[1])
        new_data += struct.pack("<f", value[2])
        self.data = new_data

class Angle:
    def __init__(self, data):
        self.code = "\x10"
        self.data = data
        self.size = 2
    
    def convert_to(self):
        return int.from_bytes(self.data, "little", signed=False)

    def convert_from(self, value):
        self.data = value.to_bytes(self.size, "little", signed=False)

class UniString:
    def __init__(self, data):
        self.code = "\x0e"
        self.data = data
        self.size = len(data)*2

    def convert_to(self):
        return self.data.decode("utf-16")

    def __str__(self):
        return "Unicode: " + self.data

class ASCIIString:
    def __init__(self, data):
        self.code = "\x0f"
        self.data = data
        self.size = len(data)

    def convert_to(self):
        return self.data.decode("utf-8")

class ArrayNode:
    def __init__(self, node_type):
        self.node_type = node_type

    # def append(self, node):
    #     self.array.append(node)

    # def remove(self, index):
    #     pass

    # def __getitem__(self, index):
    #     return self.array[index]

    # # Doing it like this for legacy reasons
    # def __setitem__(self, node, arg):
    #     self.append(node)

    def __str__(self):
        data_name = get_data_class_and_size(self.node_type)[0].__name__
        return "Array Node: " + data_name

class NodeRecord:
    def __init__(self, record_type, tag_name, version, size):
        self.record_type = record_type
        self.tag_name = tag_name
        self.version = version
        self.size = size


    def __hash__(self):
        return hash(self.tag_name)

    def __eq__(self, tag_name):
        if(self.tag_name == tag_name):
            return True
        else:
            return False

    def __str__(self):
        return "Record: " + self.tag_name

class ArrayRecord:
    def __init__(self, type_code, tag_name, version):
        self.type_code = type_code
        self.tag_name = tag_name
        self.version = version

    def __hash__(self):
        return hash(self.tag_name)

    def __eq__(self, tag_name):
        if(self.tag_name == tag_name):
            return True
        else:
            return False

    def __str__(self):
        return "Record Array: " + self.tag_name

# Return: (Class, wri_size: int, real_size: int)
def get_data_class_and_size(type_code):
    if(type_code == b'\x01'):
        return (Bool, 1, 1)

    if(type_code == b'\x02'):
        return (Int, 1, 1)

    if(type_code == b'\x03'):
        return (Int, 2, 2)

    if(type_code == b'\x04'):
        return (Int, 4, 4)

    if(type_code == b'\x05'):
        return (Int, 8, 8)

    if(type_code == b'\x06'):
        return (Int, 1, 1)

    if(type_code == b'\x07'):
        return (Int, 2, 2)

    if(type_code == b'\x08'):
        return (Int, 4, 4)

    if(type_code == b'\x09'):
        return (Int, 8, 8)

    if(type_code == b'\x0a'):
        return (Float, 4, 4)

    if(type_code == b'\x0b'):
        return (Float, 8, 8)

    if(type_code == b'\x0c'):
        return (XYCoordinate, 8, 8)

    if(type_code == b'\x0d'):
        return (XYZCoordinate, 12, 12)

    if(type_code == b'\x10'):
        return (Angle, 2, 2)

    if(type_code == b'\x12'):
        return (Bool, 0, 1)

    if(type_code == b'\x13'):
        return (Bool, 0, 1)

    if(type_code == b'\x14'):
        return (Int, 0, 4)

    if(type_code == b'\x15'):
        return (Int, 0, 4)

    if(type_code == b'\x16'):
        return (Int, 1, 4)

    if(type_code == b'\x17'):
        return (Int, 2, 4)

    if(type_code == b'\x18'):
        return (Int, 3, 4)

    if(type_code == b'\x19'):
        return (Int, 0, 4)

    if(type_code == b'\x1a'):
        return (Int, 1, 4)

    if(type_code == b'\x1b'):
        return (Int, 2, 4)

    if(type_code == b'\x1c'):
        return (Int, 3, 4)

    if(type_code == b'\x1d'):
        return (Float, 0, 4)
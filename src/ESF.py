from ESFtypes import *

from ESFReader import ESFReader
from ESFWriter import ESFWriter

class ESF:
    def __init__(self):
        self.data = None

    def read(self, esf_byte_arr):
        esf_reader = ESFReader(esf_byte_arr)
        self.data = esf_reader.read()

    def read_file(self, file_path):
        with open(file_path, mode="rb") as esf_file:
            file_data = esf_file.read()
            self.read(file_data)

    def write(self, magic_code):
        if(self.data == None):
            return
        
        esf_writer = ESFWriter(self.data)
        return esf_writer.write(magic_code)

    def write_file(self, file_path, magic_code):
        if(self.data == None):
            return

        with open(file_path, mode="wb") as esf_file:
            esf_file.write(self.write(magic_code))

    def get_element(self, indcies):
        current_data = self.data
        for index in indcies[:-1]:
            current_data = current_data[index][1]

        return current_data[indcies[-1]]

    def get_element_name(self, indices):
        return self.get_element(indices)[0]

    def get_element_data(self, indices):
        return self.get_element(indices)[1]

    def get_element_by_name(self, indices):
        current_data = self.data
        # print(current_data)
        for i in indices[:-1]:
            if(isinstance(i, str)):
                for j in current_data:
                    
                    if(isinstance(j[0], NodeRecord) and j[0].tag_name == i):
                        current_data = j[1]
                        break
                    elif(isinstance(j[0], ArrayRecord) and j[0].tag_name == i):
                        current_data = j[1]
                        break
            elif(isinstance(i, int)):
                try:
                    current_data = current_data[i]
                except:
                    return None
        final_index = indices[-1]
        if(isinstance(final_index, str)):
            # print("lol")
            for j in current_data:
                if(isinstance(j[0], NodeRecord) and j[0].tag_name == final_index):
                    return j
                elif(isinstance(j[0], ArrayRecord) and j[0].tag_name == final_index):
                    return j
            return None
        elif(isinstance(final_index, int)):
            # print(current_data)
            try:
                return current_data[final_index]
            except:
                return None
        else:
            return None

    def get_data_element_index(self, indices, index):
        element_data = self.get_element_by_name(indices)[1]
        ele_index = 0
        for i in range(len(element_data)):
            if(not isinstance(element_data[i][0], NodeRecord) and not isinstance(element_data[i][0], ArrayRecord)):
                if(ele_index == index):
                    return i
                else:
                    ele_index += 1

        return None

    def get_record_element_index(self, indices, name):
        element_data = self.get_element_by_name(indices)[1]
        ele_index = 0
        for i in range(len(element_data)):
            if(isinstance(element_data[i][0], NodeRecord) or isinstance(element_data[i][0], ArrayRecord)):
                if(element_data[i][0].tag_name == name):
                    return i
                else:
                    ele_index += 1

        return None    


    # def change_element_data(self, new_element, indices):





    # def get_data_element(self, index):
    #     for i in 

    


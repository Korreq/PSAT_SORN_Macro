import os

class FileHandler:

    def __init__(self):
        pass


    def delete_files_from_directory(self, directory, string):

        for file_name in os.listdir(directory):

            if string in file_name:

                os.remove(directory + "/" + file_name)


    
    #Left for possible implementation
    def get_data_from_file(self, file_path):

        data = []

        with open(file_path, "r") as file:

            lines = file.readlines()

            for line in lines:

                pass
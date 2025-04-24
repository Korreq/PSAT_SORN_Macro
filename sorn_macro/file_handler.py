import os
from time_manager import TimeManager

class FileHandler:

    def __init__(self):
        pass


    def delete_files_from_directory(self, directory, string):

        for file_name in os.listdir(directory):

            if string in file_name:

                os.remove(directory + "/" + file_name)


    def create_directory(self, path, string, add_timestamp):

        if not string:
            return path

        timestamp = TimeManager().get_current_utc_time()

        if add_timestamp:
            directory_path = f'{path}/{timestamp}_{string}'

        else:
            directory_path = path + '/' + string

        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        return directory_path
    

    #Left for possible implementation
    def get_data_from_file(self, file_path):

        data = []

        with open(file_path, "r") as file:

            lines = file.readlines()

            for line in lines:

                pass

    
    def create_info_file(self, file_path, text):

        with open(file_path + '/info.txt', "w") as file:

            file.write(text)
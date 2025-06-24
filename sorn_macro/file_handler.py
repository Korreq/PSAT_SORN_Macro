import os
from time_manager import TimeManager

class FileHandler:

    # Deletes all files with specifed text in it within directory
    def delete_files_from_directory(self, directory, string):

        for file_name in os.listdir(directory):
            if string in file_name:
                os.remove(directory + "/" + file_name)

    # Creates directory in specifed path, with selected name, and if true with timestamp
    def create_directory(self, path, string, add_timestamp):

        if not string:
            return path

        timestamp = TimeManager().get_current_utc_time()

        # Asign directory_path with specifed path, string and if selected timestamp
        if add_timestamp:
            directory_path = f'{path}/{timestamp}_{string}'

        else:
            directory_path = path + '/' + string

        # Create directory if it dosen't exists
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        return directory_path
    
    # Creates info.txt file in specifed path and fills it with text
    def create_info_file(self, file_path, text):

        with open(f"{file_path}", "w") as file:
            file.write(text)
   
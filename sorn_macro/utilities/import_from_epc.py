from core.psat_functions import PsatFunctions
from handlers.file_handler import FileHandler

class ImportFromEPC:

    def __init__(self):
        self.psat = PsatFunctions()
       

    def import_epc(self, directory: str, model_name: str):
        ''' Import an EPC file from the specified directory and convert it to PFB format. '''
        
        file_path = FileHandler.find_file_in_directory(directory, model_name)
        if file_path:
            self.psat.import_epc(file_path)
            return f"Updated pfb file with: {file_path}"

        return f"Used original file: {model_name}"
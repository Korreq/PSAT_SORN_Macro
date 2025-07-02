from configparser import ConfigParser

class IniHandler:

    # Read config file on instance creation
    def __init__(self, ini_file):
        self.ini_parser = ConfigParser()
        self.ini_parser.read(ini_file)

    # Get config data by 2d list 
    def get_config_file(self):
        return self.ini_parser

    # Get specifed config by section, value_name and it's type.
    def get_data(self, section, value_name, value_type):

        match value_type:

            case "string":
                return self.ini_parser.get(section, value_name)
        
            case "boolean":
                return self.ini_parser.getboolean(section, value_name)

            case "float":
                return self.ini_parser.getfloat(section, value_name)
            
            case "int":
                return self.ini_parser.getint(section, value_name)

    

from configparser import ConfigParser

''' Variables that need to be in .ini file

    if bus is connected
    if elements are on
    if generators mvar min is not same as max
    if transformer is changeable
    #minimum generators max_mw
    #transformer_ratio_margin (currently 0.05)
    #kv change value (default: 1 and -1)
    #remove node notation from name
    #psat install location
    #model path
    #model name
    #results save location
    #rounding precission for results / calculation
    #results file prefix
    create results files, create folder, add timestamp
    #subsystem
'''

class IniHandler:

    def __init__(self, ini_file):
        self.ini_parser = ConfigParser()
        self.ini_parser.read(ini_file)

    
    def get_config_file(self):

        return self.ini_parser


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

    

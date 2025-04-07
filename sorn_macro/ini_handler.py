import sys
from configparser import ConfigParser

''' Variables that need to be in .ini file

    if bus is connected
    if elements are on
    if generators mvar min is not same as max
    if transformer is changeable
    minimum generators max_mw
    transformer_ratio_margin (currently 0.05)
    kv change value (default: 1 and -1)
    remove node notation from name
    psat install location
    model path
    model name
    results save location
    rounding precission for results / calculation
    results file prefix
    create results files, create folder, add timestamp
    subsystem
'''







class IniHandler:

    def __init__(self, ini_file):
        self.ini_parser = ConfigParser()
        self.ini_file = ini_file






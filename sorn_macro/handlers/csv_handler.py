import csv

from elements.functions import ElementsFunctions
from core.psat_functions import PsatFunctions

class CsvFile:
 
    # Set file save location, name formating for every csv file and create csv dialect with semicolon as a delimiter
    def __init__(self, path, timestamp='', prefix=''):

        self.functions = ElementsFunctions()

        self.psat = PsatFunctions()

        self.path = path

        self.name_addons = ''

        if timestamp:
            self.name_addons += timestamp + '_' 

        if prefix:
            self.name_addons += prefix + '_'

        csv.register_dialect('excel-semicolon','excel', delimiter=';')

    # Write header and rows to file using dialect and name set in init 
    def write_to_file(self, name, header, rows):

        full_path = self.path + "/" + self.name_addons + name + ".csv"

        with open(full_path, 'w', newline='') as file:

            writer = csv.writer(file, dialect="excel-semicolon")

            writer.writerow(header)

            writer.writerows(rows)


    def write_buses_file(self, buses):

        header = ["Name", "Type", "KV"]

        rows = []

        for bus in buses:

            rows.append( [ bus.name[:-4].strip(), self.functions.get_bus_type(bus), self.functions.get_bus_changed_kv_vmag(bus,0)[1] ] )
          
        self.write_to_file("buses", header, rows)


    def write_gens_file(self, generators):

        header = ["Bus", "Name", "MW min", "Current MW", "MW max", "Mvar min", "Current Mvar", "Mvar max"]
      
        rows = []

        for gen in generators:

            rows.append( [ self.functions.get_bus_name_from_id(gen.bus), gen.eqname, gen.mwmin, gen.mw, gen.mwmax, 
                 gen.mvarmin, gen.mvar, gen.mvarmax ] )
            
        self.write_to_file("generators", header, rows)


    def write_shunts_file(self, shunts):

        header = ["Bus", "Name", "Status", "Nominal MW", "MW", "Nominal Mvar", "Mvar"]

        rows = []

        for shunt in shunts:

            rows.append( [ self.functions.get_bus_name_from_id(shunt.bus), shunt.eqname, shunt.status, shunt.nommw, 
                          shunt.mw, shunt.nommvar, shunt.mvar ] )

        self.write_to_file("shunts", header, rows)

    
    def wrtie_trfs_file(self, transformers, margin):

        header = ["From Bus", "To Bus", "Name", "Current tap", "Max tap"]

        rows = []

        for trf in transformers:

            beg_bus = self.psat.get_bus_data(trf.frbus)
            end_bus = self.psat.get_bus_data(trf.tobus)

            current_tap, max_tap = self.functions.get_transformer_ratios(trf, beg_bus.basekv, end_bus.basekv, margin, True)

            rows.append( [ self.functions.get_bus_name_from_id(trf.frbus), self.functions.get_bus_name_from_id(trf.tobus), 
                          trf.name, current_tap, max_tap ] )
            
        self.write_to_file("transformers", header, rows)
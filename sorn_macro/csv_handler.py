import csv

from elements_functions import ElementsFunctions


class CsvFile:
    '''
    # Creates results file when created as instance, adds timestamp and prefix if specifed, 
    # fills file with header data and rows data
    def __init__(self, path, filename, header, rows, timestamp='', prefix=''):
        
        full_name = filename

        if prefix:
            full_name = prefix + '_' + full_name

        if timestamp:
            full_name = timestamp + '_' + full_name 
        
        self.full_path = path + '/' + full_name

        with open(self.full_path, 'w', newline='') as file:

            writer = csv.writer(file, dialect="excel-tab")

            writer.writerow(header)

            writer.writerows(rows)
    '''

    def __init__(self, path, timestamp='', prefix=''):

        self.functions = ElementsFunctions()

        self.path = path

        self.name_addons = ''

        if timestamp:
            self.name_addons += timestamp + '_' 

        if prefix:
            self.name_addons += prefix + '_'

       
    def write_to_file(self, name, header, rows):

        full_path = self.path + "/" + self.name_addons + name + ".csv"

        with open(full_path, 'w', newline='') as file:

            writer = csv.writer(file, dialect="excel-tab")

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

        header = ["From Bus", "To Bus", "Name", "Current tap", "Max tap", "Tap position"]

        rows = []

        for trf in transformers:

            max_tap, current_tap = self.functions.get_transformer_taps(trf, margin)[1:3]

            rows.append( [ self.functions.get_bus_name_from_id(trf.frbus), self.functions.get_bus_name_from_id(trf.tobus), 
                          trf.name, current_tap, max_tap, trf.ctlside ] )
            
        self.write_to_file("transformers", header, rows)
import csv
import locale
from pathlib import Path 

from elements.functions import ElementsFunctions
from core.psat_functions import PsatFunctions

csv.register_dialect('excel-semicolon','excel', delimiter=';')

class CsvFile:
    """
    Handles writing semicolon-delimited CSV exports for PSAT data.
    """
    
    def __init__(self, path: str | Path, timestamp: str='', prefix: str=''):
        self.functions = ElementsFunctions()
        self.psat = PsatFunctions()

        self.path = Path(path)

        # Build name addons: "timestamp_prefix_" or "" if none
        parts = (timestamp, prefix)
        self.name_addons = '_'.join(p for p in parts if p)
        if self.name_addons:
            self.name_addons += '_'
       
    # Write header and rows to file using dialect and name set in init 
    def write_to_file(self, name: str, header: list[str], rows: list[list[str | float]]) :
        """
        Write header and rows into 
        path / "{name_addons}{name}.csv".
        """
        file_path = self.path / f"{self.name_addons}{name}.csv"

        with file_path.open('w', newline='') as fp:
            writer = csv.writer(fp, dialect="excel-semicolon")
            writer.writerow(header)
            writer.writerows(rows)

    def write_buses_file(self, buses: list):
        header = ["Name", "Type", "KV"]
        rows: list[list[str]] = []

        for bus in buses:
            name = bus.name[:-4].strip()
            bus_type = self.functions.get_bus_type(bus)
            kv = locale.format_string('%G', self.functions.get_bus_changed_kv_vmag(bus,0)[1])
            rows.append([name, bus_type, kv])
            
        self.write_to_file("buses", header, rows)

    def write_gens_file(self, generators: list):
        header = ["Bus", "Name", "MW min", "Current MW", "MW max", "Mvar min", "Current Mvar", "Mvar max"]
        rows: list[list[str]] = []

        for gen in generators:
            rows.append( [ 
                self.functions.get_bus_name_from_id(gen.bus), 
                gen.eqname, 
                locale.format_string('%G', gen.mwmin), 
                locale.format_string('%G', gen.mw), 
                locale.format_string('%G', gen.mwmax), 
                locale.format_string('%G', gen.mvarmin), 
                locale.format_string('%G', gen.mvar), 
                locale.format_string('%G', gen.mvarmax) 
            ] )
            
        self.write_to_file("generators", header, rows)


    def write_shunts_file(self, shunts: list):
        header = ["Bus", "Name", "Status", "Nominal MW", "MW", "Nominal Mvar", "Mvar"]
        rows: list[list[str]] = []

        for shunt in shunts:
            rows.append( [ 
                self.functions.get_bus_name_from_id(shunt.bus), 
                shunt.eqname, 
                shunt.status, 
                locale.format_string('%G', shunt.nommw), 
                locale.format_string('%G', shunt.mw), 
                locale.format_string('%G', shunt.nommvar), 
                locale.format_string('%G', shunt.mvar) 
            ] )

        self.write_to_file("shunts", header, rows)

    
    def write_trfs_file(self, transformers: list, margin):
        header = ["From Bus", "To Bus", "Name", "Current tap", "Max tap"]
        rows: list[list[str | float]] = []

        for trf in transformers:
            beg_bus = self.psat.get_bus_data(trf.frbus)
            end_bus = self.psat.get_bus_data(trf.tobus)

            current_tap, max_tap = self.functions.get_transformer_ratios(
                trf, 
                beg_bus.basekv, 
                end_bus.basekv, 
                margin, 
                True
            )
            rows.append( [ 
                self.functions.get_bus_name_from_id(trf.frbus), 
                self.functions.get_bus_name_from_id(trf.tobus), 
                trf.name, 
                current_tap, 
                max_tap 
            ] )
            
        self.write_to_file("transformers", header, rows)
import sys
sys.path.append('C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\sorn_macro')
sys.path.append('C:\\DSATools_24-SL\\Psat\\bin\\python')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from csv_handler import CsvFile

'''
TODO:

    *Decide what to do, if there are multiple generators on the same node
    *How to change transformers tap
    *Add comments
    *Result files for all changed elements in model

'''
psat = PsatFunctions()
elements = ElementsLists()

model = "C:\\Users\\ien\\Documents\\Models\\model.psp"
save_path = "C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\files"

psat.load_model(model)

generators = elements.get_generators_with_buses()
buses_base_kv = elements.get_bus_base_kv()

psat.calculate_powerflow()

header = ['ID', 'Elements', 'Difference']
rows = []
first_pass = True

for element in generators:

    row = []

    generator_bus = element[0]
    generator = element[1]

    if generator.mw < 300 :
        continue

    bus_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    bus_new_kv = bus_kv + 1
    changed_kv_vmag = bus_new_kv / float(generator_bus.basekv)
    
    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator.bus, generator.id, generator)       

    psat.calculate_powerflow()
    generator_bus = psat.get_bus_data(generator_bus.number)

    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    kv_difference = round( bus_new_kv - bus_kv, 2)

    row = [ generator.bus, generator.eqname, kv_difference ]

    buses = psat.get_element_list('bus')

    for bus in buses:

        for bus_base_kv in buses_base_kv:

            if bus_base_kv[0] == bus.number:

                if first_pass:
                    header.append( bus.name )
                
                bus_kv = round( float(bus.basekv) * float(bus.vmag), 2)
                bus_kv_change = round( bus_kv - bus_base_kv[1], 2)

                row.append( bus_kv_change )

    psat.print( f"\nDone {generator.eqname}\n" )

    first_pass = False

    rows.append(row)

    psat.load_model(model)

results = CsvFile(f"{save_path}\\result.csv", header, rows)
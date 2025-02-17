import sys
sys.path.append('C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\sorn_macro')
sys.path.append('C:\\DSATools_24-SL\\Psat\\bin\\python')
from psat_functions import PsatFunctions
from elements_lists import ElementsLists


psat = PsatFunctions()
elements = ElementsLists()


model = "C:\\Users\\ien\\Documents\\Models\\model.psp"
psat.load_model(model)

generators = elements.get_generators_with_buses()
buses_base_pu = elements.get_bus_base_pu()

psat.calculate_powerflow()

for element in generators:

    bus = element[0]
    generator = element[1]

    if generator.mw < 300 :
        continue

    bus_kv = float(bus.basekv) * float(bus.vmag)

    bus_new_kv = bus_kv + 10
    changed_kv_vmag = bus_new_kv / float(bus.basekv)

    psat.print( f"{generator.id}: {generator.eqname}, {generator.bus}, {generator.vhi} - {generator.vlo}" )
    psat.print( f"{bus.number}: {bus.name}, {bus.vmag}, {bus.vang}, {bus_kv}" )

    generator.vhi = generator.vlo = changed_kv_vmag
        
    psat.set_generator_data(generator.bus, generator.id, generator)       

    psat.calculate_powerflow()

    psat.print( f"{generator.id}: {generator.eqname}, {generator.bus}, {generator.vhi} - {generator.vlo}" )
    psat.print( f"{bus.number}: {bus.name}, {bus.vmag}, {bus.vang}, {bus_kv}\n" )

    buses = psat.get_element_list('bus')

    for sub_bus in buses:

        for bus_base_pu in buses_base_pu:

            if bus_base_pu[0] == sub_bus.number and bus_base_pu[1] != sub_bus.vmag:

                sub_bus_pu_change = round( sub_bus.vmag - bus_base_pu[1], 6)

                if sub_bus_pu_change == 0:
                    sub_bus_pu_change = 0

                sub_bus_kv = float(sub_bus.basekv) * float(sub_bus.vmag)
            
                psat.print( f"{sub_bus.number}: {sub_bus.name}, {sub_bus.vmag}, {sub_bus.vang}, {sub_bus_kv}, diff: {sub_bus_pu_change:f}" )

    psat.print( f"\nDone {generator.eqname}\n" )

    psat.load_model(model)
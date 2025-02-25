import sys
sys.path.append('C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\sorn_macro')
sys.path.append('C:\\DSATools_24-SL\\Psat\\bin\\python')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from csv_handler import CsvFile

'''
TODO:

    *Finish tranformer base mvar function
    *Add transformers to result files
    *Add comments
    *Result files for all changed elements in model

'''
psat = PsatFunctions()
elements = ElementsLists()

model = "C:\\Users\\ien\\Documents\\Models\\model.psp"
save_path = "C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\files"

psat.load_model(model)

generators = elements.get_generators_with_buses()
buses_base_kv = elements.get_buses_base_kv()
gens_base_mvar = elements.get_generators_base_mvar()
changed_generators = psat.get_element_list('generator')
transformers = psat.get_element_list('adjustable_transformer')


psat.calculate_powerflow()

v_header = ['ID', 'Elements', 'Difference']
q_header = ['ID', 'Elements', 'Difference']
v_rows = [] 
q_rows = []
base_mvar = []
first_pass = True

'''
for element in generators:

    v_row = [] 
    q_row = []

    generator_bus = element[0]
    generator = element[1]

    bus_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    bus_new_kv = bus_kv + 5
    changed_kv_vmag = bus_new_kv / float(generator_bus.basekv)
    
    mvar = float(generator.mvar)

    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator.bus, generator.id, generator)       

    for changed_generator in changed_generators:

        if changed_generator.bus == generator.bus and changed_generator.id != generator.id:

            changed_generator.vhi = changed_generator.vlo = changed_kv_vmag
            psat.set_generator_data(changed_generator.bus, changed_generator.id, changed_generator)

    psat.calculate_powerflow()

    generator_bus = psat.get_bus_data(generator_bus.number)
    generator_new_q = psat.get_generator_data(generator.bus, generator.id)

    mvar_difference = round( float(generator_new_q.mvar) - mvar, 2 )

    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    kv_difference = round( bus_new_kv - bus_kv, 2 )

    v_row = [ generator.bus, generator.eqname, kv_difference ]
    q_row = [ generator.bus, generator.eqname, mvar_difference ]

    changed_generators_q = psat.get_element_list("generator")
    
    for changed_generator_q in changed_generators_q:

        for gen_base_mvar in gens_base_mvar:

            if gen_base_mvar[0] == changed_generator_q.bus and gen_base_mvar[2] == changed_generator_q.id:

                if first_pass:
                    q_header.append( changed_generator_q.eqname )

                gen_q_change = round( float(changed_generator_q.mvar ) - float( gen_base_mvar[1] ) ,2 )

                q_row.append( gen_q_change )

    buses = psat.get_element_list('bus')

    for bus in buses:

        for bus_base_kv in buses_base_kv:

            if bus_base_kv[0] == bus.number:

                if first_pass:
                    v_header.append( bus.name )
                
                bus_kv = round( float(bus.basekv) * float(bus.vmag), 2)
                bus_kv_change = round( bus_kv - bus_base_kv[1], 2)

                v_row.append( bus_kv_change )

    psat.print( f"\nDone {generator.eqname}\n" )

    first_pass = False

    v_rows.append(v_row)
    q_rows.append(q_row)

    psat.load_model(model)
'''

for transformer in transformers:

    beg_bus = psat.get_bus_data(transformer.frbus)
    end_bus = psat.get_bus_data(transformer.tobus)

    trf_from_side = transformer.fsratio * beg_bus.basekv
    trf_to_side = transformer.tsratio * end_bus.basekv

    trf_max =  ( transformer.maxratio * beg_bus.basekv ) / trf_to_side
    trf_min =  ( transformer.minratio * beg_bus.basekv ) / trf_to_side
    
    trf_step_plans =  transformer.stepratio * beg_bus.basekv 

    trf_step =  (transformer.stepratio * beg_bus.basekv) / trf_to_side 

    trf_current_ratio =  round( trf_from_side / trf_to_side, 4)

    trf_max_tap = 0
    trf_current_tap = 0
    trf_changed_tap = 0
    down_change = True
    trf_pass = trf_min

    while trf_pass < trf_max:

        if( round(trf_pass, 4) == trf_current_ratio ):
            trf_current_tap = trf_max_tap

            if(trf_pass + trf_step <= trf_max):
                trf_changed_tap = trf_max_tap + 1
            else:
                trf_changed_tap = trf_max_tap - 1
                down_change = False

        trf_max_tap += 1

        trf_pass += trf_step

    trf_current_tap = trf_max_tap - trf_current_tap
    trf_changed_tap = trf_max_tap - trf_changed_tap

    if(down_change):

        transformer.fsratio += transformer.stepratio

    else:

        transformer.fsratio -= transformer.stepratio

    psat.set_transformer_data(transformer)

    psat.calculate_powerflow()

    changed_transformer = psat.get_transformer_data(transformer.frbus, transformer.tobus, transformer.id, transformer.sec)

    psat.print( f"{transformer.name}: {transformer.frbus} - {transformer.tobus}, tap: {trf_current_tap} / {trf_max_tap}" )





    psat.load_model(model)

    break

'''

CsvFile(f"{save_path}\\v_result.csv", v_header, v_rows)
CsvFile(f"{save_path}\\q_result.csv", q_header, q_rows)

'''
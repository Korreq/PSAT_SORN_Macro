import sys
sys.path.append('C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\sorn_macro')
sys.path.append('C:\\DSATools_24-SL\\Psat\\bin\\python')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from csv_handler import CsvFile

'''
TODO:

    *Add comments
    *Result files for all changed elements in model
    *Fix problem with generators on same node, where one of the generators is not able to match it's new voltage to other one
    (Need to check if limits are set even when generator can't achive them, if yes then compare it agains it's calculated kv)
    *Fix transformer tap change logic ( check if set margins will not overlap neigbouring taps )
    *Change the way of finding matching element from loop in a loop to one loop with range (if both arrays are sorted and same lenght) 

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
trfs_base_mvar = elements.get_transformers_base_mvar()


#psat.calculate_powerflow()

v_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
q_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
v_rows = [] 
q_rows = []
base_mvar = []
first_pass = True


# Iterating through each generator, changeing it's voltage and 
# adding bus voltage difference, generator mvar difference and transformer difference to results arrays
for element in generators:

    v_row = [] 
    q_row = []

    generator_bus = element[0]
    generator = element[1]

    if generator.mwmax < 60:
        continue

    bus_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    bus_new_kv = bus_kv + 1
    changed_kv_vmag = bus_new_kv / float(generator_bus.basekv)
    
    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator.bus, generator.id, generator)       

    '''
    Change this loop to fix problem when some of neigbouring gen can't match new set voltage
    '''

    
    for changed_generator in changed_generators:

        # Check if generator has neigbours on the same node
        if changed_generator.bus == generator.bus and changed_generator.id != generator.id:

            # Change generators lower and upper limit to new calculated kv_vmag and apply changes to model
            changed_generator.vhi = changed_generator.vlo = changed_kv_vmag
            psat.set_generator_data(changed_generator.bus, changed_generator.id, changed_generator)

    # Calculate powerflow after changes to generator and it's neigbours 
    psat.calculate_powerflow()
    
    # Get generators bus with new calculated values
    generator_bus = psat.get_bus_data(generator_bus.number)

    # Calculate buse's new kv and it's kv difference before changes 
    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    kv_difference = round( bus_new_kv - bus_kv, 2 )

    # Set generator bus number, generator's eqname and it's bus kv difference to row of the result files
    v_row = [ generator.bus, "-", generator.eqname, kv_difference ]
    q_row = [ generator.bus, "-", generator.eqname, kv_difference ]

    # Getting changed mvar on each generator and transformer
    changed_generators = psat.get_element_list("generator")
    changed_transformers = psat.get_element_list("adjustable_transformer")

    for changed_generator in changed_generators:

        for gen_base_mvar in gens_base_mvar:

            if gen_base_mvar[0] == changed_generator.bus and gen_base_mvar[2] == changed_generator.id:

                if first_pass:
                    q_header.append( changed_generator.eqname )

                gen_q_change = round( float( changed_generator.mvar ) - float( gen_base_mvar[1] ) ,2 )

                q_row.append( gen_q_change )

    for changed_transformer in changed_transformers:

        for trf_base_mvar in trfs_base_mvar:

            if trf_base_mvar[0] == changed_transformer.frbus and trf_base_mvar[1] == changed_transformer.tobus and trf_base_mvar[2] == changed_transformer.id:

                if first_pass:
                    q_header.append( changed_transformer.name )

                trf_mvar = changed_transformer.qfr if changed_transformer.meter == "F" else changed_transformer.qto
                trf_q_change = round( float( trf_mvar ) - float( trf_base_mvar[3] ) ,2 )

                q_row.append( trf_q_change )


    # Getting changed voltage on each node

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


for transformer in transformers:

    v_row = [] 
    q_row = []

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

        if( 
            round(trf_pass, 4) >= trf_current_ratio - (0.05 * trf_current_ratio) and
            round(trf_pass, 4) <= trf_current_ratio + (0.05 * trf_current_ratio)  
        ):
            trf_current_tap = trf_max_tap

            if(trf_pass + trf_step <= trf_max):
                trf_changed_tap = trf_max_tap - 1
            else:
                trf_changed_tap = trf_max_tap + 1
                down_change = False

        trf_max_tap += 1
        trf_pass += trf_step

    trf_current_tap = trf_max_tap - trf_current_tap
    trf_changed_tap = trf_max_tap - trf_changed_tap

    psat.print(f"{transformer.name}| Curr: {trf_current_tap}, Changed: {trf_changed_tap}, Max: {trf_max_tap}")

    trf_tap_difference = trf_changed_tap - trf_current_tap

    if(down_change):

        transformer.fsratio += transformer.stepratio
    else:

        transformer.fsratio -= transformer.stepratio

    psat.set_transformer_data(transformer)

    psat.calculate_powerflow()

    changed_transformer = psat.get_transformer_data(transformer.frbus, transformer.tobus, transformer.id, transformer.sec)

    
    v_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]
    q_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]

    # Getting changed mvar on each generator and transformer

    changed_generators = psat.get_element_list("generator")
    changed_transformers = psat.get_element_list("adjustable_transformer")

    for changed_generator in changed_generators:

        for gen_base_mvar in gens_base_mvar:

            if gen_base_mvar[0] == changed_generator.bus and gen_base_mvar[2] == changed_generator.id:

                gen_q_change = round( float( changed_generator.mvar ) - float( gen_base_mvar[1] ) ,2 )

                q_row.append( gen_q_change )


    for changed_transformer in changed_transformers:

        for trf_base_mvar in trfs_base_mvar:

            if trf_base_mvar[0] == changed_transformer.frbus and trf_base_mvar[1] == changed_transformer.tobus and trf_base_mvar[2] == changed_transformer.id:

                trf_mvar = changed_transformer.qfr if changed_transformer.meter == "F" else changed_transformer.qto
                trf_q_change = round( float( trf_mvar ) - float( trf_base_mvar[3] ) ,2 )

                q_row.append( trf_q_change )

    # Getting buses with changed values 
    buses = psat.get_element_list('bus')

    
    '''
        If buses and buses_base_kv arrays are same lenght, then change from 2 loops to one with range
    '''

    for bus in buses:

        for bus_base_kv in buses_base_kv:

            if bus_base_kv[0] == bus.number:

                if first_pass:
                    v_header.append( bus.name )
                
                bus_kv = round( float(bus.basekv) * float(bus.vmag), 2)
                bus_kv_change = round( bus_kv - bus_base_kv[1], 2)

                v_row.append( bus_kv_change )


    psat.print( f"\nDone {transformer.name}\n" )

    v_rows.append(v_row)
    q_rows.append(q_row)

    psat.load_model(model)


CsvFile(f"{save_path}\\v_result.csv", v_header, v_rows)
CsvFile(f"{save_path}\\q_result.csv", q_header, q_rows)

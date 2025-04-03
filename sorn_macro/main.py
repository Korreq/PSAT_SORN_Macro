import sys
sys.path.append('C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\sorn_macro')
sys.path.append('C:\\DSATools_24-SL\\Psat\\bin\\python')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from elements_functions import ElementsFunctions
from csv_handler import CsvFile

'''
TODO:

    *Add comments
    *Result files for all changed elements in model 
    *Create input file where you can decide which nodes and elements to use
    *Change iterating from generators to nodes ( Add indication in results file, 
    if there was multiple generators in same node)
'''



psat = PsatFunctions()
elements_lists = ElementsLists()
elements_func = ElementsFunctions()

model = "C:\\Users\\ien\\Documents\\Models\\model.pfb"
tmp_model = "C:\\Users\\ien\\Documents\\Models\\tmp.pfb"
save_path = "C:\\Users\\ien\\Documents\\Github\\PSAT_SORN_Macro\\files"

psat.load_model(model)

psat.calculate_powerflow()
psat.save_as_tmp_model(tmp_model)


generators = elements_lists.get_generators_with_buses()
buses_base_kv = elements_lists.get_buses_base_kv()
gens_base_mvar = elements_lists.get_generators_base_mvar()
all_generators = psat.get_element_list('generator')
transformers = psat.get_element_list('adjustable_transformer')
trfs_base_mvar = elements_lists.get_transformers_base_mvar()

generators_from_bus = elements_lists.get_generators_bus()
generators_from_bus_base_mvar = elements_lists.get_generators_from_bus_base_mvar()


v_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
q_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
v_rows = [] 
q_rows = []
base_mvar = []
first_pass = True


for element in generators_from_bus:

    v_row = [] 
    q_row = []

    generator_bus = element[0]
    generator = element[1]

    changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, 1)

    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator.bus, generator.id, generator)       

    neighbouring_generators = [generator]

    for changed_generator in all_generators:

        # Check if generator has neighbours on the same node
        if changed_generator.bus == generator.bus and changed_generator.id != generator.id:

            neighbouring_generators.append(changed_generator)

            # Change generators lower and upper limit to new calculated kv_vmag and apply changes to model
            changed_generator.vhi = changed_generator.vlo = changed_kv_vmag
            psat.set_generator_data(changed_generator.bus, changed_generator.id, changed_generator)

    psat.calculate_powerflow()

    # Check if each generator reached changed_kv_mag and set flag to false if not
    is_matching_desired_v = True
    for neighbouring_generator in neighbouring_generators:

        neighbouring_generator_bus = psat.get_bus_data(neighbouring_generator.bus)

        if round( neighbouring_generator_bus.vmag, 4 ) < round( changed_kv_vmag, 4 ):
            is_matching_desired_v = False
            break

    # Set new changed_kv_vmag, if flag is set to false and apply it to generators
    if is_matching_desired_v == False:

        changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, -1)

        for neighbouring_generator in neighbouring_generators:

            neighbouring_generator.vhi = neighbouring_generator.vlo = changed_kv_vmag
            psat.set_generator_data(neighbouring_generator.bus, neighbouring_generator.id, neighbouring_generator)

        psat.calculate_powerflow()
    

    # Get generator bus with new calculated values
    generator_bus = psat.get_bus_data(generator_bus.number)

    # Calculate bus new kv and it's kv difference before changes 
    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    kv_difference = round( bus_new_kv - bus_kv, 2 )

    # Set generator bus number, generator's eqname and it's bus kv difference to row of the result files
    v_row = [ generator.bus, "-", generator.eqname.split("-")[0], kv_difference ]
    q_row = [ generator.bus, "-", generator.eqname.split("-")[0], kv_difference ]

   
    # Getting changed mvar on each generator and transformer
    changed_transformers = psat.get_element_list("adjustable_transformer")
    #changed_generators = elements_lists.get_generators_with_buses()
    changed_generators_from_bus = elements_lists.get_generators_bus()

    '''
    for i in range( len(changed_generators) ):

        if first_pass:
            q_header.append( changed_generators[i].eqname )

        gen_q_change = round( float( changed_generators[i].mvar ) - float( gens_base_mvar[i][1] ), 2 )

        q_row.append( gen_q_change )
    '''
    for i in range( len(changed_generators_from_bus) ):

        if first_pass:

            q_header.append( changed_generators_from_bus[i][1].eqname.split("-")[0] )

        gen_q_change = round( float( changed_generators_from_bus[i][1].mvar ) - float( generators_from_bus_base_mvar[i][1] ), 2 )

        q_row.append( gen_q_change )


    for i in range( len(changed_transformers) ):

        if first_pass:

            q_header.append( changed_transformers[i].name )

            trf_mvar = changed_transformers[i].qfr if changed_transformers[i].meter == "F" else changed_transformers[i].qto
            trf_q_change = round( float( trf_mvar ) - float( trfs_base_mvar[i][3] ), 2 )

            q_row.append( trf_q_change )

  
    # Getting changed voltage on each node

    buses = psat.get_element_list('bus')

    for i in range( len(buses) ):

        if first_pass:
            v_header.append( buses[i].name )

        bus_kv = round( float(buses[i].basekv) * float(buses[i].vmag), 2 )
        bus_kv_change = round( bus_kv - buses_base_kv[i][1], 2 )

        v_row.append( bus_kv_change )
   
    #psat.print( f"\nDone {generator.eqname}\n" )

    first_pass = False

    v_rows.append(v_row)
    q_rows.append(q_row)

    psat.load_model(tmp_model)


'''
# Iterating through each generator, changeing it's voltage and 
# adding bus voltage difference, generator mvar difference and transformer difference to results arrays
for element in generators:

    v_row = [] 
    q_row = []

    generator_bus = element[0]
    generator = element[1]

    # Need to be change into desired elements/nodes input file
    """if generator.mwmax < 60:
        continue
    """
    changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, 1)

    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator.bus, generator.id, generator)       

    neighbouring_generators = [generator]

    for changed_generator in all_generators:

        # Check if generator has neighbours on the same node
        if changed_generator.bus == generator.bus and changed_generator.id != generator.id:

            neighbouring_generators.append(changed_generator)

            # Change generators lower and upper limit to new calculated kv_vmag and apply changes to model
            changed_generator.vhi = changed_generator.vlo = changed_kv_vmag
            psat.set_generator_data(changed_generator.bus, changed_generator.id, changed_generator)

    psat.calculate_powerflow()

    # Check if each generator reached changed_kv_mag and set flag to false if not
    is_matching_desired_v = True
    for neighbouring_generator in neighbouring_generators:

        neighbouring_generator_bus = psat.get_bus_data(neighbouring_generator.bus)

        if round( neighbouring_generator_bus.vmag, 4 ) < round( changed_kv_vmag, 4 ):
            is_matching_desired_v = False
            break

    # Set new changed_kv_vmag, if flag is set to false and apply it to generators
    if is_matching_desired_v == False:

        changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, -1)

        for neighbouring_generator in neighbouring_generators:

            neighbouring_generator.vhi = neighbouring_generator.vlo = changed_kv_vmag
            psat.set_generator_data(neighbouring_generator.bus, neighbouring_generator.id, neighbouring_generator)

        psat.calculate_powerflow()
    

    # Get generator bus with new calculated values
    generator_bus = psat.get_bus_data(generator_bus.number)

    # Calculate bus new kv and it's kv difference before changes 
    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    kv_difference = round( bus_new_kv - bus_kv, 2 )

    # Set generator bus number, generator's eqname and it's bus kv difference to row of the result files
    v_row = [ generator.bus, "-", generator.eqname, kv_difference ]
    q_row = [ generator.bus, "-", generator.eqname, kv_difference ]

   
    # Getting changed mvar on each generator and transformer
    changed_transformers = psat.get_element_list("adjustable_transformer")
    changed_generators = elements_lists.get_generators_with_buses()
    
    for i in range( len(changed_generators) ):

        if first_pass:
            q_header.append( changed_generators[i].eqname )

        gen_q_change = round( float( changed_generators[i].mvar ) - float( gens_base_mvar[i][1] ), 2 )

        q_row.append( gen_q_change )
 

    for i in range( len(changed_transformers) ):

        if first_pass:

            q_header.append( changed_transformers[i].name )

            trf_mvar = changed_transformers[i].qfr if changed_transformers[i].meter == "F" else changed_transformers[i].qto
            trf_q_change = round( float( trf_mvar ) - float( trfs_base_mvar[i][3] ), 2 )

            q_row.append( trf_q_change )

  
    # Getting changed voltage on each node

    buses = psat.get_element_list('bus')

    for i in range( len(buses) ):

        if first_pass:
            v_header.append( buses[i].name )

        bus_kv = round( float(buses[i].basekv) * float(buses[i].vmag), 2 )
        bus_kv_change = round( bus_kv - buses_base_kv[i][1], 2 )

        v_row.append( bus_kv_change )
   
    #psat.print( f"\nDone {generator.eqname}\n" )

    first_pass = False

    v_rows.append(v_row)
    q_rows.append(q_row)

    psat.load_model(tmp_model)
'''

for transformer in transformers:

    v_row = [] 
    q_row = []
   
    down_change = elements_func.get_transformer_taps(transformer)[0]

    if(down_change):

        transformer.fsratio += transformer.stepratio
    else:

        transformer.fsratio -= transformer.stepratio

    psat.set_transformer_data(transformer)

    psat.calculate_powerflow()

    changed_transformer = psat.get_transformer_data(transformer.frbus, transformer.tobus, transformer.id, transformer.sec)

    down_change, trf_max_tap, trf_current_tap, trf_changed_tap = elements_func.get_transformer_taps(changed_transformer) 
    trf_tap_difference = trf_changed_tap - trf_current_tap

    v_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]
    q_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]

    # Getting changed mvar on each generator and transformer

    changed_transformers = psat.get_element_list("adjustable_transformer")
    #changed_generators = elements_lists.get_generators_with_buses()
    changed_generators_from_bus = elements_lists.get_generators_bus()
    
    for i in range( len(changed_generators_from_bus) ):

        if first_pass:

            q_header.append( changed_generators_from_bus[i][1].eqname.split("-")[0] )

        gen_q_change = round( float( changed_generators_from_bus[i][1].mvar ) - float( generators_from_bus_base_mvar[i][1] ), 2 )

        q_row.append( gen_q_change )


    '''
    for i in range( len(changed_generators) ):

        gen_q_change = round( float( changed_generators[i].mvar ) - float( gens_base_mvar[i] ), 2 )

        q_row.append( gen_q_change )

    '''
    '''
    for changed_generator in all_generators:

        for gen_base_mvar in gens_base_mvar:

            if gen_base_mvar[0] == changed_generator.bus and gen_base_mvar[2] == changed_generator.id:

                gen_q_change = round( float( changed_generator.mvar ) - float( gen_base_mvar[1] ) ,2 )

                q_row.append( gen_q_change )
    '''
    for i in range( len( changed_transformers ) ):

        trf_mvar = changed_transformers[i].qfr if changed_transformers[i].meter == "F" else changed_transformers[i].qto
        trf_q_change = round( float( trf_mvar ) - float( trfs_base_mvar[i][3] ), 2 )

        q_row.append( trf_q_change )
    '''
    for changed_transformer in changed_transformers:

        for trf_base_mvar in trfs_base_mvar:

            if trf_base_mvar[0] == changed_transformer.frbus and trf_base_mvar[1] == changed_transformer.tobus and trf_base_mvar[2] == changed_transformer.id:

                trf_mvar = changed_transformer.qfr if changed_transformer.meter == "F" else changed_transformer.qto
                trf_q_change = round( float( trf_mvar ) - float( trf_base_mvar[3] ) ,2 )

                q_row.append( trf_q_change )
    '''

    # Getting buses with changed values 
    buses = psat.get_element_list('bus')

    for i in range( len(buses) ):

        bus_kv = round( float(buses[i].basekv) * float(buses[i].vmag), 2 )
        bus_kv_change = round( bus_kv - buses_base_kv[i][1], 2 )

        v_row.append( bus_kv_change )

    '''
    for bus in buses:

        for bus_base_kv in buses_base_kv:

            if bus_base_kv[0] == bus.number:

                if first_pass:
                    v_header.append( bus.name )
                
                bus_kv = round( float(bus.basekv) * float(bus.vmag), 2)
                bus_kv_change = round( bus_kv - bus_base_kv[1], 2)

                v_row.append( bus_kv_change )
    '''

    #psat.print( f"\nDone {transformer.name}\n" )

    v_rows.append(v_row)
    q_rows.append(q_row)

    psat.load_model(tmp_model)


CsvFile(f"{save_path}\\v_result.csv", v_header, v_rows)
CsvFile(f"{save_path}\\q_result.csv", q_header, q_rows)

psat.load_model(model)
'''
    Run in terminal from Psat\bin:

        PSAT "model.location" autopython "this\file.location"
        
'''


import sys
script_path = 'C:/Users/ien/Documents/Github/PSAT_SORN_Macro'
sys.path.append(script_path + '/sorn_macro')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from elements_functions import ElementsFunctions
from csv_handler import CsvFile
from file_handler import FileHandler
from ini_handler import IniHandler
from time_manager import TimeManager

'''
TODO:

    *Add missing comments
    *Result files for all elements in model 
    *Create input file where you can decide which nodes and elements to use ( Stashed for now, looking into using database for it )
    *Change iterating from generators to nodes ( Add gens id in results file, 
    if there was multiple generators in same node)
'''

#Load configuration file
ini_handler = IniHandler(script_path + '/files/config.ini')
config = ini_handler.get_config_file()

#Add psat isntall loacation to enviromental variables
sys.path.append( config['psat']['psat_installation_path'] + "/bin/python" )

psat = PsatFunctions()
elements_lists = ElementsLists()
elements_func = ElementsFunctions()
f_handler = FileHandler()
time_mgr = TimeManager()

#Assign paths and file names to main model and for temporary file
model_path = config['psat']['psat_model_path']
model = config['psat']['psat_model_name']
save_path = config['results']['results_save_path']
subsystem = config['psat']['subsystem']
tmp_model = "tmp.pfb"
start_timestamp = time_mgr.get_current_utc_time()

# Load model, calculate it's powerflow and save changed model as temporary model
#psat.load_model(model_path + '/' + model)
psat.calculate_powerflow()
psat.save_as_tmp_model(model_path + '/' + tmp_model)


# Get arrays with all generators and transformers in loaded model
all_generators = psat.get_element_list('generator', subsystem)
transformers = psat.get_element_list('adjustable_transformer', subsystem)
# Get arrays with base values for buses, transformers, buses with connected suitable generators
buses_base_kv = elements_lists.get_buses_base_kv(subsystem)
trfs_base_mvar = elements_lists.get_transformers_base_mvar(subsystem)
generators_from_bus_base_mvar = elements_lists.get_generators_from_bus_base_mvar(
    ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
# Get arrays with buses that have suitable generator connected and filtred shunts 
generators_from_bus = elements_lists.get_generators_bus( 
    ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
shunts = elements_lists.get_shunts(
    ini_handler.get_data('calculations','shunt_minimal_abs_mvar_value','int'), subsystem)


v_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference/State']
q_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference/State']
v_rows = [] 
q_rows = []
tmp_row = []
tmp_header = []
first_pass = True

# Iterate through each node, that has sutaible generator directly connected  
for element in generators_from_bus:

    v_row = [] 
    q_row = []

    generator_bus = element[0]
    generator = element[1]
                                                                                    
    # Getting new kv change from base value and calculated bus kv
    changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, ini_handler.get_data('calculations','node_kv_change_value', 'int') )

    # Setting changed kv value to generator's lower and upper limits 
    generator.vhi = generator.vlo = changed_kv_vmag
    psat.set_generator_data(generator)       

    # Searching throgh all generators in model for generators connected to same node
    neighbouring_generators = [generator]
    for changed_generator in all_generators:

        # If generator is on the same node and has different id, then add it to neigbours array and change it's limits 
        if changed_generator.bus == generator.bus and changed_generator.id != generator.id:
            neighbouring_generators.append(changed_generator)

            # Setting changed kv value to generator's lower and upper limits 
            changed_generator.vhi = changed_generator.vlo = changed_kv_vmag
            psat.set_generator_data(changed_generator)

    psat.calculate_powerflow()

    # Check if each generator reached changed_kv_mag and set flag to false if not
    is_matching_desired_v = True
    for neighbouring_generator in neighbouring_generators:

        neighbouring_generator_bus = psat.get_bus_data(neighbouring_generator.bus)

        if round( neighbouring_generator_bus.vmag, 4 ) < round( changed_kv_vmag, 4 ):
            is_matching_desired_v = False
            break


    if is_matching_desired_v == False:

        # Getting new kv change from base value and calculated bus kv
        changed_kv_vmag, bus_kv = elements_func.get_bus_changed_kv_vmag(generator_bus, - ini_handler.get_data('calculations','node_kv_change_value', 'int') )

        # Apply new kv changed value to all generators connected to bus
        for neighbouring_generator in neighbouring_generators:

            # Setting changed kv value to generator's lower and upper limits 
            neighbouring_generator.vhi = neighbouring_generator.vlo = changed_kv_vmag
            psat.set_generator_data(neighbouring_generator)

        psat.calculate_powerflow()
    

    # Get generator bus with new calculated values
    generator_bus = psat.get_bus_data(generator_bus.number)

    # Calculate bus new kv and it's kv change from base value 
    bus_new_kv = float(generator_bus.basekv) * float(generator_bus.vmag)
    
    kv_difference = round( bus_new_kv - bus_kv, ini_handler.get_data('results','rounding_precission', 'int') )

    # Set generator bus number, generator's eqname and it's bus kv difference to row of the result files
    v_row = [ generator.bus, "-", generator.eqname.split("-")[0], kv_difference ]
    q_row = [ generator.bus, "-", generator.eqname.split("-")[0], kv_difference ]

   
    # Getting changed values on each transformers, generators and buses
    changed_transformers = psat.get_element_list("adjustable_transformer", subsystem)
    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
    buses = psat.get_element_list('bus', subsystem)


    # Get row and header filled with generators changes for q_result file 
    tmp_row, tmp_header = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, first_pass, 
                                                                            ini_handler.get_data('results','rounding_precission', 'int') )
    q_row.extend( tmp_row )
    if tmp_header:
        q_header.extend( tmp_header )

    # Get row and header filled with transformers changes for q_result file
    tmp_row, tmp_header = elements_func.get_changed_transformers_results(changed_transformers, trfs_base_mvar, first_pass, 
                                                                         ini_handler.get_data('results','rounding_precission', 'int'))
    q_row.extend( tmp_row )
    if tmp_header:
        q_header.extend( tmp_header )

    # Get row and header filled with buses changes for v_result file
    tmp_row, tmp_header = elements_func.get_changed_buses_results(buses, buses_base_kv, first_pass, ini_handler.get_data('results','rounding_precission', 'int'), 
                                                                  ini_handler.get_data('results', 'node_notation_next_to_bus_name', 'boolean'))
    v_row.extend( tmp_row )
    if tmp_header:
        v_header.extend( tmp_header )

    # Change add headers to files flag and add generator's changed row to v_rows and q_rows  
    first_pass = False
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)


# Iterate through each suitable transformer 
for transformer in transformers:

    v_row = [] 
    q_row = []
    
    # If able change tap down, if not change tap up 
    down_change = elements_func.get_transformer_taps(transformer, ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float') )[0]
    if(down_change):
        transformer.fsratio += transformer.stepratio
    else:
        transformer.fsratio -= transformer.stepratio

    # Set changed ratio corresponding for tap change 
    psat.set_transformer_data(transformer)
    psat.calculate_powerflow()

    # Get updated transformer's data
    changed_transformer = psat.get_transformer_data(transformer.frbus, transformer.tobus, transformer.id, transformer.sec)
    down_change, trf_max_tap, trf_current_tap, trf_changed_tap = elements_func.get_transformer_taps(
        changed_transformer, ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float') 
    ) 
    trf_tap_difference = trf_changed_tap - trf_current_tap

    v_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]
    q_row = [ transformer.frbus, transformer.tobus, transformer.name, trf_tap_difference ]

    # Getting changed values on each transformers, generators and buses
    changed_transformers = psat.get_element_list("adjustable_transformer")
    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
    buses = psat.get_element_list('bus', subsystem)

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, 
                                                                0, ini_handler.get_data('results','rounding_precission', 'int'))[0]
    q_row.extend( tmp_row )
    
    # Get row filled with transformers changes for q_result file
    tmp_row = elements_func.get_changed_transformers_results(changed_transformers, trfs_base_mvar, 
                                                             0, ini_handler.get_data('results','rounding_precission', 'int'))[0]
    q_row.extend( tmp_row )

    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(buses, buses_base_kv, 0, ini_handler.get_data('results','rounding_precission', 'int'),
                                                    ini_handler.get_data('results', 'node_notation_next_to_bus_name', 'boolean'))[0]
    v_row.extend( tmp_row )
   
    # Add transformer's changed row to v_rows and q_rows  
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)


# Iterate through each suitable shunts
for shunt in shunts:

    v_row = []
    q_row = []

    # Set fliped shunt status 
    shunt.status = 0 if shunt.status == 1 else 1
    psat.set_fixed_shunt_data(shunt)
    psat.calculate_powerflow()

    # Get updated shunt
    shunt = psat.get_fixed_shunt_data(shunt.bus, shunt.id)

    v_row = [ shunt.bus, "-", shunt.eqname, shunt.status ]
    q_row = [ shunt.bus, "-", shunt.eqname, shunt.status ]

    # Getting changed values on each transformers, generators and buses 
    changed_transformers = psat.get_element_list("adjustable_transformer")
    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
    buses = psat.get_element_list('bus', subsystem)

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, 
                                                                0, ini_handler.get_data('results','rounding_precission', 'int'))[0]
    q_row.extend( tmp_row )
    
    # Get row filled with transformers changes for q_result file
    tmp_row = elements_func.get_changed_transformers_results(changed_transformers, trfs_base_mvar, 
                                                             0, ini_handler.get_data('results','rounding_precission', 'int'))[0]
    q_row.extend( tmp_row )

    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(buses, buses_base_kv, 0, ini_handler.get_data('results','rounding_precission', 'int'),
                                                    ini_handler.get_data('results', 'node_notation_next_to_bus_name', 'boolean'))[0]
    v_row.extend( tmp_row )
   
    # Add transformer's changed row to v_rows and q_rows  
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)


# If set to true in config, create a results folder
if ini_handler.get_data('results','create_results_folder','boolean'):

    save_path = f_handler.create_directory(save_path, config['results']['folder_name'] , 
                                           ini_handler.get_data('results','add_timestamp_to_folder','boolean'))

# If set to true in config, add timestamp to result files
if ini_handler.get_data('results','add_timestamp_to_files','boolean'):
    timestamp = time_mgr.get_current_utc_time()

else:
    timestamp = ''

# Save filled rows and headers to corresponding result files
CsvFile( save_path, 'v_result.csv', v_header, v_rows, timestamp, config['results']['files_prefix'] )
CsvFile( save_path, 'q_result.csv', q_header, q_rows, timestamp, config['results']['files_prefix'] )

# Load original model and delete all temporary model files
psat.close_model(model_path + '/' + tmp_model)
#psat.load_model(model_path + '/' + model)
f_handler.delete_files_from_directory(model_path,"tmp")

# Show whole duration of program run
duration = time_mgr.elapsed_time()
psat.print(f"Elapsed time: {duration}")

# Create info file of results
info_text = f"""Model: {model}\nSubsystem: {subsystem}\nDate: {start_timestamp}\nDuration: {duration}\n\n
Minimum upper generated MW limit for generators: {ini_handler.get_data('calculations','minimum_max_mw_generators','int')}\n
Node KV +/- change: {ini_handler.get_data('calculations','node_kv_change_value', 'int')}\n
Transformer ratio precission error margin: {ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float')}\n
Shunt minumum absolute mvar value: {ini_handler.get_data('calculations', 'shunt_minimal_abs_mvar_value', 'int')}\n"""
f_handler.create_info_file(save_path, info_text)

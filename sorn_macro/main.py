"""
    To start this macro start it by running run.py in terminal from sorn_macro directory:

        python run.py
        
"""

import locale
import os
import sys

sys.path.append(os.environ["SORN_WORKING_DIRECTORY"] + '/sorn_macro')

from psat_functions import PsatFunctions
from elements_lists import ElementsLists
from elements_functions import ElementsFunctions
from csv_handler import CsvFile
from file_handler import FileHandler
from ini_handler import IniHandler
from time_manager import TimeManager

'''
TODO:

    *Optimize changing transformers tap
    *Result files for all elements in model
    *Add missing data to info file
    *Add missing comments
    *Create input file where you can decide which nodes and elements to use ( Stashed for now, looking into using database for it )
'''

#Set locale based on system's locale
locale.setlocale(locale.LC_ALL, '')

#Load configuration file using system variable, then unset said variable and get config file's dictionary 
ini_handler = IniHandler(os.environ["SORN_WORKING_DIRECTORY"] + '/files/config.ini')
os.environ.pop("SORN_WORKING_DIRECTORY")
config = ini_handler.get_config_file()

#Add psat isntall loacation to enviromental variables
sys.path.append( config['psat']['psat_installation_path'] + "/python" )

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

# If set to true in config, add timestamp to result files
timestamp = start_timestamp if ini_handler.get_data('results','add_timestamp_to_files','boolean') else ''

# If set to true in config, create a results folder
if ini_handler.get_data('results','create_results_folder','boolean'):
    save_path = f_handler.create_directory(save_path, config['results']['folder_name'] , 
    ini_handler.get_data('results','add_timestamp_to_folder','boolean'))

# Initialize csv files handler
csv = CsvFile(save_path, timestamp, config['results']['files_prefix'])

# Calculate powerflow and save changed model as temporary model
psat.calculate_powerflow()
psat.save_as_tmp_model(model_path + '/' + tmp_model)

# Get arrays with all generators 
# and 400,220,110 buses in loaded model
all_generators = psat.get_element_list('generator', subsystem)
buses = psat.get_element_list('bus', subsystem)
# Get arrays with base values for buses, transformers, buses with connected suitable generators
buses_base_kv = elements_lists.get_buses_base_kv(subsystem)
generators_from_bus_base_mvar = elements_lists.get_generators_from_bus_base_mvar(
    ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
# Get arrays with buses that have suitable generator connected, filtred shunts and filtred transformers
generators_from_bus = elements_lists.get_generators_bus( 
    ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem)
shunts = elements_lists.get_shunts(
    ini_handler.get_data('calculations','shunt_minimal_abs_mvar_value','int'), subsystem)
transformers = elements_lists.get_transformers(
    ini_handler.get_data('calculations','keep_transformers_without_connection_to_400_bus','boolean'), subsystem)

# Create files for model's elements
csv.write_buses_file(buses)
csv.write_gens_file(all_generators)
csv.write_shunts_file(shunts)
csv.wrtie_trfs_file(transformers, ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float') )

v_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference/State']
q_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference/State']
v_rows = [] 
q_rows = []
tmp_row = []
tmp_header = []
first_pass = True

# Iterate through each node, that has sutaible generator directly connected  
for bus_number_key in generators_from_bus:

    row = elements_func.set_new_generators_bus_kv_value( bus_number_key, generators_from_bus[bus_number_key], 
        ini_handler.get_data('calculations','node_kv_change_value', 'int'), 
        ini_handler.get_data('results','rounding_precission', 'int')   )

    # Set generator bus number, generator's eqname and it's bus kv difference to row of the result files
    v_row = row
    q_row = row
    
    # Getting changed values on each transformers, generators and buses
    changed_transformers = elements_lists.get_transformers(
    ini_handler.get_data('calculations','keep_transformers_without_connection_to_400_bus','boolean'), subsystem)
    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem, False)
    buses = psat.get_element_list('bus', subsystem)

    # Get row and header filled with generators changes for q_result file 
    tmp_row, tmp_header = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, first_pass)
    q_row.extend( tmp_row )
    if tmp_header:
        q_header.extend( tmp_header )

    # Get row and header filled with buses changes for v_result file
    tmp_row, tmp_header = elements_func.get_changed_buses_results(buses, buses_base_kv, first_pass)
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
    down_change = elements_func.get_transformer_taps(transformer, 
                        ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float') )[0]
    
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
    changed_transformers = elements_lists.get_transformers(
    ini_handler.get_data('calculations','keep_transformers_without_connection_to_400_bus','boolean'), subsystem)

    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem, False)
    buses = psat.get_element_list('bus', subsystem)

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, 0)[0]
    q_row.extend( tmp_row )

    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(buses, buses_base_kv, 0)[0]
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
    shunt.status = int( not shunt.status )
    psat.set_fixed_shunt_data(shunt)
    psat.calculate_powerflow()

    # Get updated shunt
    shunt = psat.get_fixed_shunt_data(shunt.bus, shunt.id)

    v_row = [ shunt.bus, "-", shunt.eqname, shunt.status ]
    q_row = [ shunt.bus, "-", shunt.eqname, shunt.status ]

    # Getting changed values on each transformers, generators and buses 
    changed_transformers = elements_lists.get_transformers(
    ini_handler.get_data('calculations','keep_transformers_without_connection_to_400_bus','boolean'), subsystem)

    changed_generators_from_bus = elements_lists.get_generators_bus( 
        ini_handler.get_data('calculations','minimum_max_mw_generators','int'), subsystem, False)
    buses = psat.get_element_list('bus', subsystem)

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_changed_generator_buses_results(changed_generators_from_bus, generators_from_bus_base_mvar, 0)[0]
    q_row.extend( tmp_row )
    
    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(buses, buses_base_kv, 0)[0]
    v_row.extend( tmp_row )
   
    # Add transformer's changed row to v_rows and q_rows  
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)

# Save filled rows and headers to corresponding result files
csv.write_to_file("v_result", v_header, v_rows)
csv.write_to_file("q_result", q_header, q_rows)

# Close model and delete all temporary model files
psat.close_model()
f_handler.delete_files_from_directory(model_path,"tmp")

# Show whole duration of program run
duration = time_mgr.elapsed_time()
psat.print(f"Elapsed time: {duration}")

# Create info file of results
info_text = f"""Model: {model}\nSubsystem: {subsystem}\nDate: {start_timestamp}\nDuration: {duration}\n
Minimum upper generated MW limit for generators: {ini_handler.get_data('calculations','minimum_max_mw_generators','int')}
Node KV +/- change: {ini_handler.get_data('calculations','node_kv_change_value', 'int')}
Transformer ratio precission error margin: {ini_handler.get_data('calculations', 'transformer_ratio_margins', 'float')}
Shunt minimum absolute mvar value: {ini_handler.get_data('calculations', 'shunt_minimal_abs_mvar_value', 'int')}
Keep transformers not connected to 400 bus: {ini_handler.get_data('calculations','keep_transformers_without_connection_to_400_bus','boolean')}\n
"""
f_handler.create_info_file(save_path, info_text)


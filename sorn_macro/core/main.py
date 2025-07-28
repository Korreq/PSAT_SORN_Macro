"""
    Start this script by running run.py in terminal from sorn_macro directory:

        python scripts/run.py
        
"""

import locale
import os
import sys

sys.path.append(os.environ["SORN_WORKING_DIRECTORY"] + '/sorn_macro')

from core.psat_functions import PsatFunctions
from elements.filters import ElementsLists
from elements.functions import ElementsFunctions
from elements.raport import RaportHandler
from elements.model_modifier import ModelModifier
from handlers.csv_handler import CsvFile
from handlers.file_handler import FileHandler
from handlers.ini_handler import IniHandler
from handlers.json_handler import JsonHandler
from utilities.time_manager import TimeManager

'''
TODO:
    *Result files for all elements in model ~
    *Add missing data to info file ~
    *Add missing comments ~ 

'''

#Set locale based on system's locale
locale.setlocale(locale.LC_ALL, '')

#Load configuration file using system variable, then unset said variable and get config file's dictionary 
ini_handler = IniHandler(os.environ["SORN_WORKING_DIRECTORY"] + '/configuration/config.ini')
os.environ.pop("SORN_WORKING_DIRECTORY")
config = ini_handler.get_config_file()

#Add psat isntall loacation to enviromental variables
sys.path.append( config['psat']['psat_installation_path'] + "/python" )

input_settings = [
    ini_handler.get('input', 'use_input_for_buses', bool),
    ini_handler.get('input', 'use_input_for_transformers', bool),
    ini_handler.get('input', 'use_input_for_generators', bool),
    ini_handler.get('input', 'use_input_for_shunts', bool)
]
input_handler = JsonHandler(config['input']['input_file_path']) if any(input_settings) else None
input_dict = input_handler.get_input_dict() if input_handler else {}
model_modifier = ModelModifier(input_dict) if input_handler else None
model_modifier.modify_model(config['psat']['subsystem']) if model_modifier else None

psat = PsatFunctions()


elements_func = ElementsFunctions()
time_mgr = TimeManager()





start_timestamp = TimeManager.get_current_utc_time()

# If set to true in config, add timestamp to result files
timestamp = start_timestamp if ini_handler.get('results','add_timestamp_to_files',bool) else ''

# If set to true in config, create a results folder
if ini_handler.get('results','create_results_folder',bool):
    save_path = FileHandler.create_directory(save_path, config['results']['folder_name'] , 
    ini_handler.get('results','add_timestamp_to_folder',bool))

#Assign paths and file names to main model and for temporary file
model_path = config['psat']['psat_model_path']
model = config['psat']['psat_model_name']
save_path = config['results']['results_save_path']
subsystem = config['psat']['subsystem']

minimum_max_mw_generated = ini_handler.get('calculations','minimum_max_mw_generators',int)

tmp_model = "tmp.pfb"

elements_lists = ElementsLists(input_settings, config['input']['input_file_path'])

# Initialize csv files handler
csv = CsvFile(save_path, timestamp, config['results']['files_prefix'])

# Calculate powerflow and save changed model as temporary model
psat.calculate_powerflow()
psat.save_as_new_model(f"{model_path}/{tmp_model}")

filtered_buses = elements_lists.get_buses(subsystem)
filtered_generators = elements_lists.get_generators(minimum_max_mw_generated, subsystem)
filtered_shunts = elements_lists.get_shunts(ini_handler.get('calculations','shunt_minimal_abs_mvar_value',int), subsystem)
filtered_transformers = elements_lists.get_transformers(subsystem)

generators_with_buses = elements_lists.get_generators_with_buses()

buses_base_kv = elements_lists.get_buses_base_kv()
generators_base_mvar = elements_lists.get_generators_base_mvar()

# Create files and write them elements from model
csv.write_buses_file( filtered_buses )
csv.write_gens_file( filtered_generators )
csv.write_shunts_file( filtered_shunts )
csv.write_trfs_file( filtered_transformers, ini_handler.get('calculations', 'transformer_ratio_margins', float) )

if True in input_settings:
    raport = RaportHandler(elements_lists.get_found_elements_dict(), 
        elements_lists.get_input_elements_dict(), elements_lists.get_model_elements_dict()).get_raport_data()

    FileHandler.create_info_file( save_path/"raport.txt", raport)

v_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
q_header = ['From_bus_ID', 'To_bus_ID', 'Elements', 'Difference']
v_rows, q_rows, tmp_row, tmp_header = [], [], [], []
first_pass = True

# Iterate through each node, that has sutaible generator directly connected  
for bus_number_key in generators_with_buses:

    count = 0
    for generator_label in generators_with_buses[ bus_number_key ]:
        if generator_label[1] == "outside_filter":
            count += 1

    if len( generators_with_buses[ bus_number_key ] ) <= count:
        continue

    # Try to change generators bus kv value up or down, recalculate power flow and return row with bus number, bus name, change difference
    row = elements_func.set_new_generators_bus_kv_value( bus_number_key, generators_with_buses[ bus_number_key ],
        model_path + '/' + tmp_model, ini_handler.get('calculations','node_kv_change_value', int) )
    v_row = row.copy()
    q_row = row.copy()
    
    updated_generators = elements_lists.update_filtered_generators()
    updated_buses = elements_lists.update_filtered_buses()

    # Get row and header filled with generators changes for q_result file 
    tmp_row, tmp_header = elements_func.get_generators_mvar_differrence_results(updated_generators, generators_base_mvar, first_pass)
    q_row.extend( tmp_row )
    if tmp_header:
        q_header.extend( tmp_header )

    # Get row and header filled with buses changes for v_result file
    tmp_row, tmp_header = elements_func.get_changed_buses_results(updated_buses, buses_base_kv, first_pass)
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
for transformer in filtered_transformers:

    row = elements_func.set_transformer_new_tap(transformer, ini_handler.get('calculations', 'transformer_ratio_margins', float) )

    v_row = row.copy()
    q_row = row.copy()

    updated_generators = elements_lists.update_filtered_generators()
    updated_buses = elements_lists.update_filtered_buses()

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_generators_mvar_differrence_results(updated_generators, generators_base_mvar, 0)[0]
    q_row.extend( tmp_row )

    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(updated_buses, buses_base_kv, 0)[0]
    v_row.extend( tmp_row )
   
    # Add transformer's changed row to v_rows and q_rows  
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)

# Iterate through each suitable shunts
for shunt in filtered_shunts:

    v_row = []
    q_row = []

    # Set fliped shunt status 
    old_shunt_status = shunt.status
    shunt.status = int( not shunt.status )
    psat.set_fixed_shunt_data(shunt)
    psat.calculate_powerflow()

    # Get updated shunt
    shunt = psat.get_fixed_shunt_data(shunt.bus, shunt.id)

    v_row = [ shunt.bus, "-", shunt.eqname, shunt.status - old_shunt_status ]
    q_row = [ shunt.bus, "-", shunt.eqname, shunt.status - old_shunt_status ]

    updated_generators = elements_lists.update_filtered_generators()
    updated_buses = elements_lists.update_filtered_buses()

    # Get row filled with generators changes for q_result file 
    tmp_row = elements_func.get_generators_mvar_differrence_results(updated_generators, generators_base_mvar, 0)[0]
    q_row.extend( tmp_row )
    
    # Get row filled with buses changes for v_result file
    tmp_row = elements_func.get_changed_buses_results(updated_buses, buses_base_kv, 0)[0]
    v_row.extend( tmp_row )
   
    # Add transformer's changed row to v_rows and q_rows  
    v_rows.append(v_row)
    q_rows.append(q_row)

    # Load temporary model
    psat.load_model(model_path + '/' + tmp_model)


# Save filled rows and headers to corresponding result files
csv.write_to_file("v_sensitivity", v_header, v_rows)
csv.write_to_file("q_sensitivity", q_header, q_rows)

# Close model and delete all temporary model files
psat.close_model()
FileHandler.delete_files_from_directory(model_path,"tmp")

# Show whole duration of program run
duration = time_mgr.elapsed_time()
psat.print(f"Elapsed time: {duration}")

# Create info file of results
info_text = f"""Model: {model}
Subsystem: {subsystem}
Date: {start_timestamp}
Duration: {duration}\n
Using input file for: 
buses: {input_settings[0]}
transformers: {input_settings[1]}
generators: {input_settings[2]}
shunts: {input_settings[3]}\n
Minimum upper generated MW limit for generators: {ini_handler.get('calculations','minimum_max_mw_generators',int)}
Node KV +/- change: {ini_handler.get('calculations','node_kv_change_value', int)}
Transformer ratio precission error margin: {ini_handler.get('calculations', 'transformer_ratio_margins', float)}
Shunt minimum absolute mvar value: {ini_handler.get('calculations', 'shunt_minimal_abs_mvar_value', int)}
Keep transformers not connected to 400 bus: {ini_handler.get('calculations','keep_transformers_without_connection_to_400_bus',bool)}\n
"""
FileHandler.create_info_file( save_path/"info.txt", info_text)

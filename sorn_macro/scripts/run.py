import os
import sys

if __name__ == '__main__':

    # Add the base directory to the system path
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    sys.path.append(base_dir)

    from sorn_macro.handlers.ini_handler import IniHandler

    # Load the configuration file
    # Assuming the config.ini is located in a 'configuration' directory
    ini_handler = IniHandler(os.path.join(base_dir, 'configuration', 'config.ini'))
    config = ini_handler.get_config_file()

    # Set the working directory environment variable
    os.environ["SORN_WORKING_DIRECTORY"] = base_dir

    # Run the PSAT automation script using data from the config
    psat = config['psat']['psat_installation_path']    
    model_with_path = os.path.join(config['psat']['psat_model_path'], config['psat']['psat_model_name'])
    main_path = os.path.join(os.path.dirname(os.path.dirname( __file__ )), 'core', 'main.py')

    os.system(f'cd {psat} && PSAT {model_with_path} autopython {main_path} ')

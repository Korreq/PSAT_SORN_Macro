
import os

from ini_handler import IniHandler

if __name__ == '__main__':

    ini_handler = IniHandler(os.getcwd() + '/files/config.ini')
    config = ini_handler.get_config_file()

    os.environ["SORN_WORKING_DIRECTORY"] = os.getcwd()

    psat = config['psat']['psat_installation_path']    
    model_with_path = config['psat']['psat_model_path'] + "/" + config['psat']['psat_model_name']
    main_path = os.getcwd() + '/sorn_macro/main.py'

    os.system(f'cd {psat} && PSAT {model_with_path} autopython {main_path} ')

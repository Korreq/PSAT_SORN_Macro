import os

from ini_handler import IniHandler

if __name__ == '__main__':

    base_dir = os.path.dirname(os.path.dirname(__file__))
    ini_handler = IniHandler(base_dir + '/files/config.ini')
    config = ini_handler.get_config_file()

    os.environ["SORN_WORKING_DIRECTORY"] = base_dir

    psat = config['psat']['psat_installation_path']    
    model_with_path = config['psat']['psat_model_path'] + "/" + config['psat']['psat_model_name']
    main_path = os.path.dirname( __file__ ) + '/main.py'

    os.system(f'cd {psat} && PSAT {model_with_path} autopython {main_path} ')

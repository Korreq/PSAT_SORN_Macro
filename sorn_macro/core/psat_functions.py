from psat_python311 import * # type: ignore


class PsatFunctions:

    def __init__(self):
        self.error = psat_error() # type: ignore


    def get_element_list( self, element_type_string, subsys="mainsub" ):

        elements = []

        # Match element name to it's PSAT type and coresponding function
        match( element_type_string ):

            case 'bus':
                element_type = ctype.bs # type: ignore
                element_func = get_bus_dat # type: ignore

            case 'generator':
                element_type = ctype.gen # type: ignore
                element_func = get_gen_dat # type: ignore

            case 'load':
                element_type = ctype.ld # type: ignore
                element_func = get_load_dat # type: ignore

            case 'line':
                element_type = ctype.ln # type: ignore
                element_func = get_line_dat # type: ignore

            case 'adjustable_transformer':
                element_type = ctype.ultc # type: ignore
                element_func = get_2w_trans_dat # type: ignore

            case 'fixed_shunt':
                element_type = ctype.fxsh # type: ignore
                element_func = get_fx_shunt_dat # type: ignore

            case 'area':
                element_type = ctype.ar # type: ignore
                element_func = get_area_dat # type: ignore

            case 'zone':
                element_type = ctype.zn # type: ignore
                element_func = get_zone_dat # type: ignore

        # Get first component of matched element and get next one from specified subsystem
        component = psat_comp_id( element_type, 1, '' ) # type: ignore
        next_component = get_next_comp( subsys, component, self.error ) # type: ignore

        # Until there is next component available add element to array
        while next_component:
            element = element_func(component, self.error)
            next_component = get_next_comp( subsys, component, self.error ) # type: ignore

            elements.append(element)

        return elements

    
    def load_model(self, full_path):
        '''Close current model without saving, open new one in given path'''
        psat_command('CloseProject:NoSave', self.error) # type: ignore
        psat_command(f'OpenPowerflow:"{full_path}"', self.error) # type: ignore

    
    def close_model(self):
        '''Close current model without saving'''
        psat_command('CloseProject:NoSave', self.error) # type: ignore

    
    def save_as_new_model(self, full_path):
        '''Save current model as one in given path'''
        psat_command(f'SavePowerflowAs:"{full_path}"', self.error) # type: ignore


    def calculate_powerflow(self):
        psat_command('Solve', self.error) # type: ignore


    @staticmethod
    def print(message: str):
        psat_msg( message ) # type: ignore

    
    def set_generator_data(self, generator_object):
        '''Set generator based on given generator object.'''
        set_gen_dat(generator_object.bus, generator_object.id, generator_object, self.error) # type: ignore

    
    def set_transformer_data(self, transformer_object):
        '''Set transformer based on given transformer object.'''
        set_2w_trans_dat(transformer_object.frbus, transformer_object.tobus, transformer_object.id, transformer_object.sec, transformer_object, self.error) # type: ignore


    def set_fixed_shunt_data(self, shunt_object):
        '''Set shunt based on given shunt object.'''
        set_fx_shunt_dat(shunt_object.bus, shunt_object.id, shunt_object, self.error) # type: ignore


    def get_bus_data(self, bus_id):
        '''Get bus object with given bus id, return error if not found.'''
        return get_bus_dat(bus_id, self.error) # type: ignore
    

    def get_transformer_data(self, from_bus_id, to_bus_id, transformer_id, transformer_section):
        '''Get adjuctable transformer object with given data, throws psat error if not found.'''
        return get_2w_trans_dat(from_bus_id, to_bus_id, transformer_id, transformer_section, self.error) # type: ignore


    def get_generator_data(self, bus_id, generator_id):
        '''Get generator object with given bus id and generator id, throws psat error if not found'''
        return get_gen_dat(bus_id, generator_id, self.error) # type: ignore
    

    def get_fixed_shunt_data(self, bus_id, shunt_id):
        '''Get shunt object with given bus id and shunt id, throws psat error if not found'''
        return get_fx_shunt_dat(bus_id, shunt_id, self.error) # type: ignore
    

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

        # Until there is next component available and element is sutaible add it to array
        while next_component:
            element = element_func(component, self.error)

            next_component = get_next_comp( subsys, component, self.error ) # type: ignore

            if element_type == ctype.bs: # type: ignore
                if element.type == 4:
                    continue

            if element_type not in [ctype.ar, ctype.zn, ctype.bs, ctype.fxsh]: # type: ignore
                if element.status == 0:
                    continue

                if element_type == ctype.ultc: # type: ignore
                    if element.minratio == element.maxratio:
                        continue

            elements.append(element)

        return elements

    # Closes opened project without saving, opens new one
    def load_model(self, name):

        psat_command('CloseProject:NoSave', self.error) # type: ignore

        psat_command(f'OpenPowerflow:"{name}"', self.error) # type: ignore

    # Closes opened project without saving
    def close_model(self):

        psat_command('CloseProject:NoSave', self.error) # type: ignore

    # Save current model as new one
    def save_as_tmp_model(self, name):

        psat_command(f'SavePowerflowAs:"{name}"', self.error) # type: ignore


    def calculate_powerflow(self):

        psat_command('Solve', self.error) # type: ignore


    def print(self, message):

        psat_msg( message ) # type: ignore

    # Set generator data, requires bus number, generator id and generator object
    def set_generator_data(self, object):

        set_gen_dat(object.bus, object.id, object, self.error) # type: ignore

    # Set transformer data, requires from and to bus number, transformer id, transformer section and transformer object
    def set_transformer_data(self, object):

        set_2w_trans_dat(object.frbus, object.tobus, object.id, object.sec, object, self.error) # type: ignore

    # Set shunt data, requires bus id, shunt id and shunt object
    def set_fixed_shunt_data(self, object):

        set_fx_shunt_dat(object.bus, object.id, object, self.error) # type: ignore

    # Get bus data by it's number
    def get_bus_data(self, id):

        return get_bus_dat(id, self.error) # type: ignore
    
    # Get transformer data, requires from and to bus number, transformer id, transformer section
    def get_transformer_data(self, bus1, bus2, id, sect):

        return get_2w_trans_dat(bus1, bus2, id, sect, self.error) # type: ignore

    # Get generator data, requires bus number, generator id 
    def get_generator_data(self, busid, genid):

        return get_gen_dat(busid, genid, self.error) # type: ignore
    
    #Get fixed shunt data, requires bus number, shunt id
    def get_fixed_shunt_data(self, busid, shuntid):

        return get_fx_shunt_dat(busid, shuntid, self.error) # type: ignore
    

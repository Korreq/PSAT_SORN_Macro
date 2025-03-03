from psat_python311 import *


class PsatFunctions:

    def __init__(self):
        self.error = psat_error()


    def get_element_list( self, element_type_string, subsys="mainsub" ):

        elements = []

        match( element_type_string ):

            case 'bus':

                element_type = ctype.bs
                element_func = get_bus_dat

            case 'generator':

                element_type = ctype.gen
                element_func = get_gen_dat

            case 'load':

                element_type = ctype.ld
                element_func = get_load_dat

            case 'line':

                element_type = ctype.ln
                element_func = get_line_dat

            case 'adjustable_transformer':

                element_type = ctype.ultc
                element_func = get_2w_trans_dat

            case 'fixed_shunt':

                element_type = ctype.fxsh
                element_func = get_fx_shunt_dat

            case 'area':

                element_type = ctype.ar
                element_func = get_area_dat

            case 'zone':

                element_type = ctype.zn
                element_func = get_zone_dat

        component = psat_comp_id( element_type, 1, '' )
        next_component = get_next_comp( subsys, component, self.error )

        while next_component:

            element = element_func(component, self.error)

            next_component = get_next_comp( subsys, component, self.error )

            if element_type == ctype.bs:
                if element.type == 4:
                    continue

            if element_type not in [ctype.ar, ctype.zn, ctype.bs]:

                if element.status == 0:
                    continue

                if element_type == ctype.gen:
                    if float(element.mvarmin + 0.1 ) > element.mvarmax or element.mvar == element.mvarmax:
                        continue

               

            elements.append(element)

        return elements


    def load_model(self, name):

        psat_command('CloseProject:NoSave', self.error)

        psat_command(f'OpenPowerflow:"{name}"', self.error)


    def calculate_powerflow(self):

        psat_command('Solve', self.error)


    def print(self, message):

        psat_msg( message )


    def set_generator_data(self, bus, id, object):

        set_gen_dat(bus, id, object, self.error)


    def set_transformer_data(self, object):

        set_2w_trans_dat(object.frbus, object.tobus, object.id, object.sec, object, self.error)


    def get_bus_data(self, id):

        return get_bus_dat(id, self.error)
    
    
    def get_transformer_data(self, bus1, bus2, id, sect):

        return get_2w_trans_dat(bus1, bus2, id, sect, self.error)


    def get_generator_data(self, busid, genid):

        return get_gen_dat(busid, genid, self.error)
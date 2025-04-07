from psat_python311 import *


class PsatFunctions:

    def __init__(self):
        self.error = psat_error()


    def get_element_list( self, element_type_string, subsys="mainsub" ):

        elements = []

        # Match element name to it's PSAT type and coresponding function
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

        # Get first component of matched element and get next one from specified subsystem
        component = psat_comp_id( element_type, 1, '' )
        next_component = get_next_comp( subsys, component, self.error )

        # Until there is next component available and element is sutaible add it to array
        while next_component:
            element = element_func(component, self.error)

            next_component = get_next_comp( subsys, component, self.error )

            if element_type == ctype.bs:
                if element.type == 4:
                    continue

            if element_type not in [ctype.ar, ctype.zn, ctype.bs]:
                if element.status == 0:
                    continue

                '''if element_type == ctype.gen:
                    if float( element.mvarmin + ( 0.05 * element.mvarmin ) ) >= element.mvarmax or element.mvar == element.mvarmax:
                        continue
                '''
                if element_type == ctype.ultc:
                    if element.minratio == element.maxratio:
                        continue

            elements.append(element)

        return elements

    # Closes opened project without saveing, opens new one
    def load_model(self, name):

        psat_command('CloseProject:NoSave', self.error)

        psat_command(f'OpenPowerflow:"{name}"', self.error)

    # Save current model as new one
    def save_as_tmp_model(self, name):

        psat_command(f'SavePowerflowAs:"{name}"', self.error)


    def calculate_powerflow(self):

        psat_command('Solve', self.error)


    def print(self, message):

        psat_msg( message )

    # Set generator data, requires bus number, generator id and generator object
    def set_generator_data(self, bus, id, object):

        set_gen_dat(bus, id, object, self.error)

    # Set transformer data, requires from and to bus number, transformer id, transformer section and transformer object
    def set_transformer_data(self, object):

        set_2w_trans_dat(object.frbus, object.tobus, object.id, object.sec, object, self.error)

    # Get bus data by it's number
    def get_bus_data(self, id):

        return get_bus_dat(id, self.error)
    
    # Get transformer data, requires from and to bus number, transformer id, transformer section
    def get_transformer_data(self, bus1, bus2, id, sect):

        return get_2w_trans_dat(bus1, bus2, id, sect, self.error)

    # Get generator data, requires bus number, generator id 
    def get_generator_data(self, busid, genid):

        return get_gen_dat(busid, genid, self.error)
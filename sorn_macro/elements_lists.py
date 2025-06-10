from psat_functions import PsatFunctions
from json_handler import JsonHandler

class ElementsLists:

    def __init__(self, input_settings, input_file=""):
        self.psat = PsatFunctions()
    
        self.filtered_buses = []
        self.filtered_generators = []
        self.filtered_transformers = []
        self.filtered_shunts = []

        if not input_file:
            self.use_input_file = False
        else:
            self.json = JsonHandler(input_file)
            self.input_settings = input_settings
        
   
    def get_buses_new(self, subsys):

        filtred_buses, buses_filter_list = [], []
        buses = self.psat.get_element_list("bus", subsys)

        if self.use_input_file and self.input_settings[0]:
            buses_filter_list = self.json.get_buses()

        for bus in buses:

            if buses_filter_list:
                if bus.name[:-4].strip() in buses_filter_list:
                    filtred_buses.append(bus)
                    break

            elif bus.basekv in [110,220,400]:
                filtred_buses.append(bus)

        self.filtered_buses = filtred_buses
        return filtred_buses


    def get_transformers_new(self, subsys):

        filtered_transformers, transformers_filter_list = [], []
        transformers = self.psat.get_element_list("adjustable_transformer",subsys)

        if self.use_input_file and self.input_settings[1]:
            transformers_filter_list = self.json.get_transformers()

        for transformer in transformers:

            from_bus, to_bus = self.psat.get_bus_data(transformer.frbus), self.psat.get_bus_data(transformer.tobus)
            if transformers_filter_list:
                if transformer.name in transformers_filter_list:
                    filtered_transformers.append(transformer)
                    break

            else:
                if (( from_bus.basekv != 400 or to_bus.basekv != 400 ) and 
                    ( from_bus.basekv not in [110,220] or to_bus.basekv not in [110,220] )):
                    continue

                for bus in self.filtered_buses:
                    if from_bus.name == bus.name or to_bus.name == bus.name:
                        filtered_transformers.append(transformer)
                        break

            self.filtered_transformers = filtered_transformers
            return filtered_transformers

 
    def get_shunts_new(self, abs_minimum, subsys):

        filtered_shunts, shunts_filter_list = [], []
        shunts = self.psat.get_element_list("fixed_shunt", subsys)

        if self.use_input_file and self.input_settings[3]:
            shunts_filter_list = self.json.get_shunts()

        for shunt in shunts:
            if shunts_filter_list:
                if shunt.name in shunts_filter_list:
                    filtered_shunts.append(shunt)
                    break

            else:
                shunt_bus = self.psat.get_bus_data(shunt.bus)

                if abs(shunt.nommvar) < abs_minimum:
                    continue

                for bus in self.filtered_buses:
                    if shunt_bus.name == bus.name:
                        filtered_shunts.append(shunt)
                        break

            self.filtered_shunts = filtered_shunts
            return filtered_shunts

        








 


    def get_buses_base_kv_new(self):

        buses_kv = []
        for bus in self.filtered_buses:
            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )
            buses_kv.append( bus_kv )

        return buses_kv


     # Get from every bus in model it's current kv value
    def get_buses_base_kv(self, subsys="mainsub"):

        buses_kv = []
        buses = self.get_filtred_buses(subsys)

        for bus in buses:
            
            #Skip if bus base kv is not 110,220 or 400
            if bus.basekv not in [110,220,400]:
                continue

            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )
            buses_kv.append( bus_kv )

        return buses_kv



    # Get buses that have directly connected generators. Can filter buses based on maximum MW generated on generator, 
    # bus will be added if there's at least one generator fitting requirements
    def get_generators_bus(self, mw_min, subsys="mainsub"):

        added_buses_with_gens_id = {}
        generators = self.psat.get_element_list("generator", subsys)

        for generator in generators:

            bus = self.psat.get_bus_data(generator.bus)

            # Skip generator if max mw is not enough and if generator's bus base kv is not 110,220 or 400
            if generator.mwmax < mw_min or bus.basekv not in [110,220,400]:
                continue

            if bus.number not in added_buses_with_gens_id:
                added_buses_with_gens_id[bus.number] = [generator.id]

            else:
                gens_id = added_buses_with_gens_id.get( bus.number )
                gens_id.append( generator.id )

                added_buses_with_gens_id[bus.number] = gens_id

        return added_buses_with_gens_id
        

    def get_filtred_generators(self, mw_min, subsys="mainsub"):

        filtred_generators = []
        generators = self.psat.get_element_list("generator", subsys)

        for generator in generators:

            bus = self.psat.get_bus_data(generator.bus)

            # Skip generator if max mw is not enough and if generator's bus base kv is not 110,220 or 400
            if generator.mwmax < mw_min or bus.basekv not in [110,220,400]:
                continue

            filtred_generators.append( generator )

        return filtred_generators


    def get_filtred_buses(self, subsys="mainsub"):

        filtred_buses = []
        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            #Skip if bus base kv is not 110,220 or 400
            if bus.basekv not in [110,220,400]:
                continue

            filtred_buses.append(bus)

        return filtred_buses

   
    
    # Get from filtred buses with directly connected generators their mvar values
    def get_generators_base_mvar(self, mw_min, subsys="mainsub"):

        generators_base_bus_mvar = []
        generators = self.get_filtred_generators(mw_min, subsys)

        for generator in generators:
            generators_base_bus_mvar.append( generator.mvar )

        return generators_base_bus_mvar

   # Get transformers, if filter set to true, 
    # return only transformers connected to/from 400 base kv buses to/from 220/110 base kv buses 
    def get_transformers(self, keep_transformers_without_connection_to_400=True, subsys="mainsub"):

        filtred_transformers = []
        transformers = self.psat.get_element_list("adjustable_transformer",subsys)

        for transformer in transformers:

            from_bus_kv, to_bus_kv = self.psat.get_bus_data(transformer.frbus).basekv, self.psat.get_bus_data(transformer.tobus).basekv

            if not keep_transformers_without_connection_to_400:
                if ( from_bus_kv == 400 or to_bus_kv == 400 ) and ( from_bus_kv in [110,220] or to_bus_kv in [110,220] ):
                    filtred_transformers.append(transformer)

            else:
                filtred_transformers.append(transformer)
           
        return filtred_transformers

 
    # Get shunts, that absolute of nominal mvar value isn't less than specifed 
    def get_shunts(self, abs_minimum=0 ,subsys="mainsub"):

        filtred_shunts = []
        shunts = self.psat.get_element_list("fixed_shunt", subsys)

        for shunt in shunts:
            if abs(shunt.nommvar) < abs_minimum:
                continue

            filtred_shunts.append(shunt)

        return filtred_shunts

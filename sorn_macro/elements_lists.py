from psat_functions import PsatFunctions
from json_handler import JsonHandler


"""

    Create a list for all filtered elements in model, change updates to update using correct list

"""

class ElementsLists:

    def __init__(self, input_settings, input_file=""):
        self.psat = PsatFunctions()
    
        self.filtered_buses = []
        self.filtered_generators = []
        self.filtered_transformers = []
        self.filtered_shunts = []

        self.use_input_file = False

        if input_file:
            self.use_input_file = True
            self.json = JsonHandler(input_file)
            self.input_settings = input_settings
        
            self.found_elements = {
                "buses": [],
                "transformers": [],                
                "generators": [],              
                "shunts": []                          
            }
   
    def get_buses(self, subsys):

        filtred_buses, buses_filter_list = [], []
        buses = self.psat.get_element_list("bus", subsys)

        if self.use_input_file and self.input_settings[0]:
            buses_filter_list = self.json.get_buses()

        for bus in buses:

            bus_name = bus.name[:-4].strip()

            if buses_filter_list:
                if bus_name in buses_filter_list:
                    filtred_buses.append(bus)

                    if bus_name not in self.found_elements["buses"]:
                        self.found_elements["buses"].append(bus_name)

            elif bus.basekv in [110,220,400]:
                filtred_buses.append(bus)

        self.filtered_buses = filtred_buses
        return filtred_buses


    def get_transformers(self, subsys):

        filtered_transformers, transformers_filter_list = [], []
        transformers = self.psat.get_element_list('adjustable_transformer',subsys)

        if self.use_input_file and self.input_settings[1]:
            transformers_filter_list = self.json.get_transformers()

        for transformer in transformers:

            from_bus, to_bus = self.psat.get_bus_data(transformer.frbus), self.psat.get_bus_data(transformer.tobus)
            if transformers_filter_list:
                if transformer.name in transformers_filter_list:
                    filtered_transformers.append(transformer)

                    if transformer.name not in self.found_elements["transformers"]:
                        self.found_elements["transformers"].append(transformer.name)
            else:
                # if transformers are not 220 - 110, 400 - 220 , 400 - 110 then continue
                if (( from_bus.basekv == to_bus.basekv ) or 
                    ( from_bus.basekv or to_bus.basekv not in [110,220,400] )):
                    continue

                for bus in self.filtered_buses:
                    if from_bus.name == bus.name or to_bus.name == bus.name:
                        filtered_transformers.append(transformer)
                        break

        self.filtered_transformers = filtered_transformers
        return filtered_transformers

 
    def get_shunts(self, abs_minimum, subsys):

        filtered_shunts, shunts_filter_list = [], []
        shunts = self.psat.get_element_list("fixed_shunt", subsys)

        if self.use_input_file and self.input_settings[3]:
            shunts_filter_list = self.json.get_shunts()

        for shunt in shunts:
            if shunts_filter_list:
                if shunt.name in shunts_filter_list:
                    filtered_shunts.append(shunt)

                    if shunt.name not in self.found_elements["shunts"]:
                        self.found_elements["shunts"].append(shunt.name)

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


    def get_generators(self, mw_min, subsys):

        filtred_generators, generators_filter_list = [], []
        generators = self.psat.get_element_list("generator", subsys)

        if self.use_input_file and self.input_settings[2]:
            generators_filter_list = self.json.get_generators()

        for generator in generators:
            if generators_filter_list:
                if generator.name in generators_filter_list:
                    filtred_generators.append(generator)

                    if generator.name not in self.found_elements["generators"]:
                        self.found_elements["generators"].append(generator.name)
            else:
                generator_bus = self.psat.get_bus_data(generator.bus)

                # Skip generator if max mw is not enough
                if generator.mwmax < mw_min:
                    continue

                for bus in self.filtered_buses:
                    if generator_bus.name == bus.name:
                        filtred_generators.append(generator)
                        break

        self.filtered_generators = filtred_generators
        return filtred_generators       


    def get_generators_with_buses(self):

        buses_with_gens_id = {}

        for generator in self.filtered_generators:
            bus = self.psat.get_bus_data(generator.bus)

            if bus.number not in buses_with_gens_id:
                buses_with_gens_id[bus.number] = [generator.id]

            else:
                gens_id = buses_with_gens_id.get( bus.number )
                gens_id.append( generator.id )
                buses_with_gens_id[bus.number] = gens_id

        return buses_with_gens_id


    def get_buses_base_kv(self):

        buses_kv = []
        for bus in self.filtered_buses:
            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )
            buses_kv.append( bus_kv )

        return buses_kv


    def get_generators_base_mvar(self):

        generators_mvar = []
        for generator in self.filtered_generators:
            generators_mvar.append( generator.mvar )

        return generators_mvar


    def update_filtered_buses(self):

        for i, bus in enumerate(self.filtered_buses):
            bus = self.psat.get_bus_data(bus.number)
            self.filtered_buses[i] = bus
        
        return self.filtered_buses


    def update_filtered_generators(self):

        for i, generator in enumerate(self.filtered_generators):
            generator = self.psat.get_generator_data(generator.bus, generator.id)
            self.filtered_generators[i] = generator

        return self.filtered_generators
    

    def get_found_elements_dict(self):

        return self.found_elements
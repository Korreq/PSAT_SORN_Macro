from core.psat_functions import PsatFunctions
from handlers.json_handler import JsonHandler


class ElementsLists:

    def __init__(self, input_settings, input_file=""):
        self.psat = PsatFunctions()

        self.filtered_buses = []
        self.filtered_generators = []
        self.filtered_transformers = []
        self.filtered_shunts = []

        self.all_generators_in_buses = []

        self.use_input_file = False

        if input_file:
            self.use_input_file = True
            self.json = JsonHandler(input_file)
            self.input_settings = input_settings
        
            self.input_dict = self.json.get_input_dict()

            self.found_elements = {
                "buses": [],
                "transformers": [],                
                "generators": [],              
                "shunts": []                          
            }

            self.model_elements = {
                "buses": [],
                "transformers": [],                
                "generators": [],              
                "shunts": []               
            }

   
    def get_buses(self, subsys):
        filtered_buses, buses_filter_list = [], []
        buses = self.psat.get_element_list("bus", subsys)

        if self.use_input_file and self.input_settings[0]:
            buses_filter_list = self.input_dict["buses"]

        for bus in buses:
            bus_name = bus.name[:-4].strip()

            if buses_filter_list:
                if bus_name in buses_filter_list:
                    filtered_buses.append(bus)

                    if bus_name not in self.found_elements["buses"]:
                        self.found_elements["buses"].append(bus_name)

            if bus.basekv in [110,220,400]:
                if buses_filter_list:
                    if bus_name not in self.model_elements["buses"]:
                        self.model_elements["buses"].append(bus_name)
                else:
                    filtered_buses.append(bus)

        self.filtered_buses = filtered_buses
        return filtered_buses


    def get_transformers(self, subsys):
        filtered_transformers, transformers_filter_list = [], []
        transformers = self.psat.get_element_list('adjustable_transformer',subsys)

        if self.use_input_file and self.input_settings[1]:
            transformers_filter_list = self.input_dict["transformers"]

        for transformer in transformers:
            from_bus, to_bus = self.psat.get_bus_data(transformer.frbus), self.psat.get_bus_data(transformer.tobus)

            if transformers_filter_list:
                if transformer.name in transformers_filter_list:
                    filtered_transformers.append(transformer)

                    if transformer.name not in self.found_elements["transformers"]:
                        self.found_elements["transformers"].append(transformer.name)
            
            # if transformers are 220 - 110, 400 - 220 , 400 - 110 then find if transformer is connected to filtered buses
            if (( from_bus.basekv != to_bus.basekv ) and 
                ( to_bus.basekv in [110,220,400] or from_bus.basekv in [110,220,400] )):
                for bus in self.filtered_buses:
                    if from_bus.name == bus.name or to_bus.name == bus.name:
                        if transformers_filter_list: 
                            if transformer.name not in self.model_elements["transformers"]:
                                self.model_elements["transformers"].append(transformer.name)
                        else:
                            filtered_transformers.append(transformer)
                        break

        self.filtered_transformers = filtered_transformers
        return filtered_transformers

 
    def get_shunts(self, abs_minimum, subsys):
        filtered_shunts, shunts_filter_list = [], []
        shunts = self.psat.get_element_list("fixed_shunt", subsys)

        if self.use_input_file and self.input_settings[3]:
            shunts_filter_list = self.input_dict["shunts"]

        for shunt in shunts:
            shunt_bus = self.psat.get_bus_data(shunt.bus)

            if shunts_filter_list:
                if shunt.name in shunts_filter_list:
                    filtered_shunts.append(shunt)

                    if shunt.name not in self.found_elements["shunts"]:
                        self.found_elements["shunts"].append(shunt.name)

            if abs(shunt.nommvar) >= abs_minimum:
                for bus in self.filtered_buses:
                    if shunt_bus.name == bus.name:
                        if shunts_filter_list:
                            if shunt.name not in self.model_elements["shunts"]:
                                self.model_elements["shunts"].append(shunt.name)
                        else:
                            filtered_shunts.append(shunt)
                        break    

        self.filtered_shunts = filtered_shunts
        return filtered_shunts


    def get_generators(self, mw_min, subsys):
        all_generators_in_buses, filtered_generators, generators_filter_list = [], [], []
        generators = self.psat.get_element_list("generator", subsys)

        if self.use_input_file and self.input_settings[2]:
            generators_filter_list = self.input_dict["generators"]

        for generator in generators:
            generator_bus = self.psat.get_bus_data(generator.bus)

            for bus in self.filtered_buses:
                if generator_bus.name == bus.name:
                    if generators_filter_list:
                        all_generators_in_buses.append(generator)

                        if generator.eqname in generators_filter_list:
                            filtered_generators.append(generator)

                            if generator.eqname not in self.found_elements["generators"]:
                                self.found_elements["generators"].append(generator.eqname)

                        if generator.mwmax >= mw_min and generator.eqname not in self.model_elements["generators"]:
                            self.model_elements["generators"].append(generator.eqname)

                    elif generator.mwmax >= mw_min:
                        filtered_generators.append(generator)
                    break

        self.all_generators_in_buses = all_generators_in_buses

        '''

        for generator in generators:
            generator_bus = self.psat.get_bus_data(generator.bus)

            if generators_filter_list:
                if generator.eqname in generators_filter_list:
                    filtered_generators.append(generator)

                    if generator.eqname not in self.found_elements["generators"]:
                        self.found_elements["generators"].append(generator.eqname)
            
            # If generator's max mw is enough then find if it's connected to filtered buses
            if generator.mwmax >= mw_min:
                for bus in self.filtered_buses:
                    if generator_bus.name == bus.name:
                        if generators_filter_list:
                            if generator.eqname not in self.model_elements["generators"]:
                                self.model_elements["generators"].append(generator.eqname)
                        else:
                            filtered_generators.append(generator)
                        break
        '''  
        self.filtered_generators = filtered_generators
        return filtered_generators       


    def get_generators_with_buses(self):
        buses_with_gens_id = {}

        if self.use_input_file and self.input_settings[2]:
            generator_list = self.all_generators_in_buses
        else:
            generator_list = self.filtered_generators

        for generator in generator_list:
            bus = self.psat.get_bus_data(generator.bus)

            label = ""

            is_found = False

            if self.use_input_file and self.input_settings[2]:
                for filtered_gen in self.filtered_generators:
                    if generator.eqname == filtered_gen.eqname:
                        is_found = True
                        break
            
                if is_found:
                    label = "in_filter"
                else:
                    label = "outside_filter"

            if bus.number not in buses_with_gens_id:
                buses_with_gens_id[bus.number] = [[generator.id, label]]

            else:
                gens_id = buses_with_gens_id.get( bus.number )
                gens_id.append( [generator.id, label] )
                buses_with_gens_id[bus.number] = gens_id

        '''
        for generator in self.filtered_generators:
            bus = self.psat.get_bus_data(generator.bus)

            if bus.number not in buses_with_gens_id:
                buses_with_gens_id[bus.number] = [generator.id]

            else:
                gens_id = buses_with_gens_id.get( bus.number )
                gens_id.append( generator.id )
                buses_with_gens_id[bus.number] = gens_id
        '''

        return buses_with_gens_id


    def get_buses_base_kv(self):
        buses_kv = []
        for bus in self.filtered_buses:
            bus_kv = bus.basekv * bus.vmag
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
    

    def get_model_elements_dict(self):
        return self.model_elements
    
    
    def get_input_elements_dict(self):
        return self.input_dict
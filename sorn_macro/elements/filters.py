from core.psat_functions import PsatFunctions
from handlers.json_handler import JsonHandler

'''
TODO: Change saving to model_elements dictonary, to add every element from model not only connected to filtered buses
'''

class ElementsLists:

    def __init__(self, input_settings, input_file):
        self.psat = PsatFunctions()
        self.input_settings = input_settings
        self.use_input_file = bool(input_file)

        # Initialize all element lists
        self.filtered_buses = []
        self.filtered_generators = []
        self.filtered_transformers = []
        self.filtered_shunts = []
        self.all_generators_in_buses = []

        # Prepare input file structures if needed
        if self.use_input_file:
            self.json = JsonHandler(input_file)
            self.input_dict = self.json.get_input_dict()
        else:
            self.input_dict = {}

        # Initialize found input elements and all elements in model lists 
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
        '''Retrieve and filter bus elements from given model in given subsystem. Can filter buses based on input file or 
        exclude buses with base kv other than 110, 220 and 400.'''
        buses = self.psat.get_element_list("bus", subsys)
        filter_list = (
            self.input_dict.get("buses", [])
            if self.use_input_file and self.input_settings[0]
            else []
        )

        filtered_elements = []
        for bus in buses:
            # Normalize bus name by trimming last 4 characters and whitespaces
            name = bus.name[:-4].strip()
            is_turned_off = (bus.type == 4)

            # Filter buses by input file if filter list is present. Record elements from the model found in input file.
            if filter_list and name in filter_list:
                if not is_turned_off:
                    filtered_elements.append(bus)

                if name not in self.found_elements["buses"]:
                    self.found_elements["buses"].append(name)

            # Filter buses by it's basekv value. Record every element found in the model if filter list is present
            if bus.basekv in (110, 220, 400):
                if filter_list:
                    if name not in self.model_elements["buses"]:
                        self.model_elements["buses"].append(name)
                elif not is_turned_off:
                    filtered_elements.append(bus)

        self.filtered_buses = filtered_elements
        return filtered_elements
    

    def get_transformers(self, subsys):
        '''Retrive and filter adjustable transformers from given model in given subsystem. Can filter transformers
        based on input file or exclude transformers if basekv on both sides are not in 110, 220, 400 or are the same.'''
        transformers = self.psat.get_element_list('adjustable_transformer',subsys)
        filter_list = (
            self.input_dict.get("transformers", [])
            if self.use_input_file and self.input_settings[1]
            else []
        )

        filtered_elements = []
        target_kv = {110, 220, 400}
        for transformer in transformers:
            name = transformer.name
            in_service = (transformer.status != 0)
            movable_tap = (transformer.minratio != transformer.maxratio)

            # Filter transformers by input file if filter list is present. Record elements from the model found in input file.
            if filter_list and name in filter_list:
                if in_service and movable_tap:
                    filtered_elements.append(transformer)
                
                if name not in self.found_elements["transformers"]:
                    self.found_elements["transformers"].append(name)

            # Filter transformers if basekv on both sides are in 110, 220, 400 and not the same. 
            # Record every element found in the model if filter list is present
            from_bus = self.psat.get_bus_data(transformer.frbus)
            to_bus = self.psat.get_bus_data(transformer.tobus)
            kv_mismatch = (from_bus.basekv != to_bus.basekv)
            connects_key_kv = bool({from_bus.basekv, to_bus.basekv} & target_kv)

            if kv_mismatch and connects_key_kv:
                # Check connection to any previously filtered bus
                for bus in self.filtered_buses:
                    if bus.name in (from_bus.name, to_bus.name):
                        if filter_list:
                            if name not in self.model_elements["transformers"]:
                                self.model_elements["transformers"].append(name)
                        elif in_service and movable_tap:
                            filtered_elements.append(transformer)
                        break
            
        self.filtered_transformers = filtered_elements
        return filtered_elements

 
    def get_shunts(self, abs_minimum, subsys):
        '''Retrive and filter shunts from given model in given subsystem. Can filter shunts
        based on input file or exclude shunts if the absolute value of nominal mvar is less than specified.'''
        shunts = self.psat.get_element_list("fixed_shunt", subsys)
        filter_list = (
            self.input_dict.get("shunts", [])
            if self.use_input_file and self.input_settings[3]
            else []
        )

        filtered_elements = []
        for shunt in shunts:
            name = shunt.name
            rating_ok = abs(shunt.nommvar) >= abs_minimum
            shunt_bus = self.psat.get_bus_data(shunt.bus)

            # Filter shunt by input file if filter list is present. Record elements from the model found in input file.
            if filter_list and name in filter_list:
                filtered_elements.append(shunt)

                if name not in self.found_elements["shunts"]:
                    self.found_elements["shunts"].append(name)

            for bus in self.filtered_buses:
                if bus.name == shunt_bus.name:
                    if filter_list:
                        if name not in self.model_elements["shunts"]:
                            self.model_elements["shunts"].append(name)
                    
                    elif rating_ok:
                        filtered_elements.append(shunt)
                    break

        self.filtered_shunts = filtered_elements
        return filtered_elements


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

                        if generator.status != 0:
                            all_generators_in_buses.append(generator)

                        if generator.eqname in generators_filter_list:
                            filtered_generators.append(generator)

                            if generator.eqname not in self.found_elements["generators"]:
                                self.found_elements["generators"].append(generator.eqname)

                        if generator.mwmax >= mw_min and generator.eqname not in self.model_elements["generators"]:
                            self.model_elements["generators"].append(generator.eqname)

                    elif generator.mwmax >= mw_min and generator.status != 0:
                        filtered_generators.append(generator)
                    break

        self.all_generators_in_buses = all_generators_in_buses  
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
            
                label = "in_filter" if is_found else "outside_filter"

            if bus.number not in buses_with_gens_id:
                buses_with_gens_id[bus.number] = [[generator.id, label]]

            else:
                gens_id = buses_with_gens_id.get( bus.number )
                gens_id.append( [generator.id, label] )
                buses_with_gens_id[bus.number] = gens_id

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
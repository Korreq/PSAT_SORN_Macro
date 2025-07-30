from core.psat_functions import PsatFunctions
from handlers.json_handler import JsonHandler

from collections import defaultdict

'''
TODO: Change saving to model_elements dictonary, to add every element from model not only connected to filtered buses.

      Make filter list make changes to elements status in model.

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
            in_service = (bus.type != 4)
            zone = bus.zone
            filter_name = f'{name[:3]}**{zone}'

            # Filter buses by input file if filter list is present. Record elements from the model found in input file.
            if filter_list:
                for filter_bus in filter_list:
                    if filter_bus["name"] in name and zone == filter_bus.get("zone", 0):

                        if in_service:
                            filtered_elements.append(bus)
                        
                        if filter_name not in self.found_elements["buses"]:
                            self.found_elements["buses"].append(filter_name)
                
            # Filter buses by it's basekv value. Record every element found in the model if filter list is present
            if bus.basekv in (110, 220, 400):
                if filter_list:
                    if filter_name not in self.model_elements["buses"]:
                        self.model_elements["buses"].append(filter_name)

                elif in_service:
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
        found_transformers = []
        target_kv = {110, 220, 400}
        for transformer in transformers:
            name = transformer.name
            in_service = (transformer.status != 0)
            movable_tap = (transformer.minratio != transformer.maxratio)

            # Filter transformers by input file if filter list is present. Record elements from the model found in input file.
            if filter_list:
                if name not in self.model_elements["transformers"]:
                    self.model_elements["transformers"].append(name)

                if name in filter_list:
                    if in_service and movable_tap:
                        filtered_elements.append(transformer)
                
                    if name not in self.found_elements["transformers"]:
                        self.found_elements["transformers"].append(name)

            else:
                # Filter transformers if basekv on both sides are in 110, 220, 400 and not the same. 
                # Record every element found in the model if filter list is present
                from_bus = self.psat.get_bus_data(transformer.frbus)
                to_bus = self.psat.get_bus_data(transformer.tobus)
                kv_mismatch = (from_bus.basekv != to_bus.basekv)
                connects_key_kv = bool({from_bus.basekv, to_bus.basekv} & target_kv)

                if kv_mismatch and connects_key_kv:
                    # Check connection to any previously filtered bus
                    for bus in self.filtered_buses:
                        if bus.name in (from_bus.name, to_bus.name) and name not in found_transformers and in_service and movable_tap:
                            filtered_elements.append(transformer)
                            found_transformers.append(name)
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
            rating_ok = (abs(shunt.nommvar) >= abs_minimum)
            shunt_bus = self.psat.get_bus_data(shunt.bus)

            # Filter shunt by input file if filter list is present. Record elements from the model found in input file.
            if filter_list:
                if name not in self.model_elements["shunts"]:
                    self.model_elements["shunts"].append(name)

                if name in filter_list:
                    filtered_elements.append(shunt)

                    if name not in self.found_elements["shunts"]:
                        self.found_elements["shunts"].append(name)
            else:
                for bus in self.filtered_buses:
                    if bus.name == shunt_bus.name and rating_ok:
                        filtered_elements.append(shunt)
                        break

        self.filtered_shunts = filtered_elements
        return filtered_elements


    def get_generators(self, mw_min, subsys):
        '''Retrive and filter generators from given model in given subsystem. Can filter generators
        based on input file or exclude generators if the max possible generated MW is less than specified.'''
        generators = self.psat.get_element_list("generator", subsys)
        filter_list = (
            self.input_dict.get("generators", [])
            if self.use_input_file and self.input_settings[2]
            else []
        )

        filtered_elements = []
        all_elements = []
        for generator in generators:
            eq_name = generator.eqname
            rating_ok = (generator.mwmax >= mw_min)
            in_service = (generator.status != 0)
            generator_bus = self.psat.get_bus_data(generator.bus)

            if filter_list and eq_name not in self.model_elements["generators"]:
                self.model_elements["generators"].append(eq_name)

            for bus in self.filtered_buses:
                if bus.name == generator_bus.name:

                    if filter_list:
                        
                        for filter_gen in filter_list:
                            if eq_name in filter_gen["name"]:
                                if in_service and generator_bus.type == 2:
                                    filtered_elements.append(generator)

                                if eq_name not in self.found_elements["generators"]:
                                    self.found_elements["generators"].append(eq_name)

                        if in_service:
                            all_elements.append(generator)

                    elif rating_ok and in_service and generator_bus.type == 2:
                        filtered_elements.append(generator)

                    break

        self.all_generators_in_buses = all_elements
        self.filtered_generators = filtered_elements
        return filtered_elements

      
    def get_generators_with_buses(self):
        '''Retrieve generators with their connected buses. If input file is used, label generators as "in_filter" or "outside_filter".'''
        use_input = self.use_input_file and self.input_settings[2]

        # Pick the correct source of generators
        generator_list = (
            self.all_generators_in_buses
            if use_input
            else self.filtered_generators
        )

        if use_input:
            buses_of_filtered_generators = {
                generator.bus
                for generator in self.filtered_generators
            } 

        buses_with_gens = defaultdict(list)
        for generator in generator_list:
            if generator.bus not in buses_of_filtered_generators:
                continue

            bus = self.psat.get_bus_data(generator.bus)
            buses_with_gens[bus.number].append(generator.id)

        return dict(buses_with_gens)

     
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
        input_generators = []
        input_buses = []
        input_shunts = []
        input_transformers = []

        for bus in self.input_dict.get("buses", []):
            converted_name = f'{bus["name"]}**{bus.get("zone", "?")}'
            input_buses.append(converted_name)

        for generator in self.input_dict.get("generators", []):
            input_generators.append(generator["name"])

        for transformer in self.input_dict.get("transformers", []):
            input_transformers.append(transformer["name"])

        for shunt in self.input_dict.get("shunts", []):
            input_shunts.append(shunt["name"])

        input_elements = {
            "buses": input_buses,
            "transformers": input_transformers,
            "generators": input_generators,
            "shunts": input_shunts
        }

        return input_elements
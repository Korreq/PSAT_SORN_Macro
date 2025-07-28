from core.psat_functions import PsatFunctions

from typing import Dict, List

'''
    Add option to turn off model elements only found in input file or in whole model

'''

class ModelModifier:
    def __init__(self, input_dict: Dict[str, List[dict]]):
        self.psat = PsatFunctions()
        self.input_dict = input_dict


    def modify_model(self, subsys: str):
        
        buses = self.psat.get_element_list("bus", subsys)
        generators = self.psat.get_element_list("generator", subsys)

        bus_filter_list = self.input_dict.get("buses", [])
        generator_filter_list = self.input_dict.get("generators", [])        

    
        for bus in buses:
            generators_in_bus = []

            bus_name = bus.name[:-4].strip()
            for bus_filter in bus_filter_list:
                if bus_name in bus_filter["name"]:
                    if bus_filter.get("enable", 0) == 0:
                        bus.type = 4
                        self.psat.set_bus_data(bus)
                        continue
                else:
                    bus.type = 4
                    self.psat.set_bus_data(bus)
                    continue

            for generator in generators:
                if generator.bus == bus.number:
                    generator_name = generator.eqname
                    label = "dynamic"
                    for gen_filter in generator_filter_list:
                        if generator_name in gen_filter["name"]:
                            if gen_filter.get("enable", 0) == 0:
                                label = "static"

                    generators_in_bus.append([generator, label])
                   

            if len(generators_in_bus) == 1:
                generator, label = generators_in_bus[0]
                if label == "static":
                    bus.type = 1
                    self.psat.set_bus_data(bus)
                    continue

            for generator, label in generators_in_bus:
                if label == "static":
                    generator.mvarmax = generator.mvarmin = generator.mvar
                    self.psat.set_generator_data(generator)
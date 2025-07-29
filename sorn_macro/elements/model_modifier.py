from core.psat_functions import PsatFunctions
from handlers.json_handler import JsonHandler


class ModelModifier:
    def __init__(self, input_file_path, change_for_whole_network: bool = False):
        self.psat = PsatFunctions()
        self.json = JsonHandler(input_file_path)

        self.input_dict = self.json.get_input_dict()
        self.change_for_whole_network = change_for_whole_network


    def modify_model(self, subsys: str):
        '''Modify the model based on the input dictionary and settings.'''        
        buses = self.psat.get_element_list("bus", subsys)
        generators = self.psat.get_element_list("generator", subsys)

        bus_filter_list = self.input_dict.get("buses", [])
        generator_filter_list = self.input_dict.get("generators", [])        

        for bus in buses:
            generators_in_bus = []
            found_bus = False


            bus_name = bus.name[:-4].strip()
            for bus_filter in bus_filter_list:
                if bus_filter["name"] in bus_name and bus.zone == bus_filter.get("zone", 0):
                    found_bus = True
                    if int(bus_filter.get("enabled", 1)) == 0:
                        bus.type = 1
                        self.psat.set_bus_data(bus)
                        break


            if not found_bus and self.change_for_whole_network and bus.type == 2:
                bus.type = 1
                self.psat.set_bus_data(bus)
                continue


            for generator in generators:
                found_generator = False

                if generator.bus == bus.number:
                    generator_name = generator.eqname
                    label = "dynamic"
                    for gen_filter in generator_filter_list:
                        if generator_name in gen_filter["name"]:
                            found_generator = True

                            if int(gen_filter.get("enabled", 1)) == 0:
                                label = "static"
                                break
                    if not found_generator:
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
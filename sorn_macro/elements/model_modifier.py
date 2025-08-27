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

        generator_filter_list = self.input_dict.get("generators", [])        
        bus_filter_list = self.input_dict.get("buses", [])

        for bus in buses:
            generators_in_bus = []

            # Normalize bus name by trimming last 4 characters and whitespaces
            bus_name = bus.name[:-4].strip()
            # Assumes station name is first 3 characters plus any charcters until first digit
            station_name = bus_name[:3]
            for c in bus_name[3:]:
                if c.isdigit():
                    break
                station_name += c
            zone = bus.zone

            # Skip if bus is in area 99 (usually used for external grid)
            if bus.area == 99:
                continue

            if not self.change_for_whole_network:
                found_bus = False

                for bus_filter in bus_filter_list:
                        
                        if int(bus_filter.get("enabled", 1)) == 0:
                            continue

                        if bus_filter["name"] == station_name and zone == bus_filter.get("zone", 0):
                            found_bus = True
                            break

                if not found_bus:
                    continue

            for generator in generators:
                found_generator = False

                # Check if generator is connected to the bus
                if generator.bus == bus.number:
                    generator_name = generator.eqname
                    label = "dynamic"

                    # Check if generator is in the input filter list
                    for gen_filter in generator_filter_list:
                        if generator_name in gen_filter["name"]:
                            found_generator = True

                            if int(gen_filter.get("enabled", 1)) == 0:
                                label = "static"
                                break

                    if not found_generator:
                        label = "static"
                            
                    generators_in_bus.append([generator, label])
                   
            # Check if all generators in the bus have label "static"
            if generators_in_bus and all(label == "static" for _, label in generators_in_bus):
                bus.type = 1
                self.psat.set_bus_data(bus)
            else:
                for generator, label in generators_in_bus:
                    if label == "static":
                        generator.mvarmax = generator.mvar
                        generator.mvarmin = generator.mvar
                        self.psat.set_generator_data(generator)
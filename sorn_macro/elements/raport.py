from core.psat_functions import PsatFunctions

class RaportHandler:

    def __init__(self, found_elements, input_elements, model_elements):
        self.psat = PsatFunctions()
        self.found_elements = found_elements
        self.input_elements = input_elements
        self.model_elements = model_elements

  
    def _get_missing_elements(self, source, reference):
        ''' Compare two dictionaries of elements and return a dictionary
        with keys from the source and lists of items that are not in the reference.
        For buses, compare by station name and zone if flag is set. '''

        missing = {key: [] for key in source}
        for key, items in source.items():
            ref_items = reference.get(key, [])

            if key == "buses":

                # Build set of (station_name, zone) from reference buses
                ref_bus_keys = set()
                for bus_entry in ref_items:
                    # model/found bus id
                    if isinstance(bus_entry, int):  
                        bus = self.psat.get_bus_data(bus_entry)
                        bus_name = bus.name[:-4].strip()

                        # Assumes station name is first 3 characters plus any charcters until first digit
                        station_name = bus_name[:3]
                        for c in bus_name[3:]:
                            if c.isdigit():
                                break
                            station_name += c
                        bus_zone = str(bus.zone)

                    # input bus entry
                    else:  
                        station_name, bus_zone = bus_entry.split("_")[:2]
                    ref_bus_keys.add((station_name, bus_zone))

                # Compare source buses by (station_name, zone)
                for bus_entry in items:

                    # model/found bus id
                    if isinstance(bus_entry, int):  
                        bus = self.psat.get_bus_data(bus_entry)
                        bus_name = bus.name[:-4].strip()

                        # Assumes station name is first 3 characters plus any charcters until first digit
                        station_name = bus_name[:3]
                        for c in bus_name[3:]:
                            if c.isdigit():
                                break
                            station_name += c
                        bus_zone = str(bus.zone)

                    # input bus entry
                    else:  
                        station_name, bus_zone = bus_entry.split("_")[:2]

                    text = f"Name: {station_name} Zone: {bus_zone}"  
                    if (station_name, bus_zone) not in ref_bus_keys and text not in missing[key]:
                        missing[key].append(f"Name: {station_name} Zone: {bus_zone}")
            else:
                # Default comparison for other element types
                missing[key] = [item for item in items if item not in ref_items]
        return missing


    def _format_section(self, title: str, elements_dict):
        ''' Format a section of the report with a title and elements. '''

        section = f"\n{title}:\n"
        for element_type, items in elements_dict.items():
            section += f"\n{element_type}:\n"
            section += "\n".join(str(item) for item in items) + "\n"
        return section
    

    def get_raport_data(self):
        ''' Create data for raport file. '''
        not_in_model = self._get_missing_elements(self.input_elements, self.found_elements)
        only_in_model = self._get_missing_elements(self.model_elements, self.input_elements)

        raport_data = ""
        raport_data += self._format_section("Elements not found in model", not_in_model)
        raport_data += self._format_section("Elements only found in model", only_in_model)

        return raport_data

class RaportHandler:

    def __init__(self, found_elements, input_elements, model_elements):
        self.found_elements = found_elements
        self.input_elements = input_elements
        self.model_elements = model_elements


    def _get_missing_elements(self, source, reference):
        missing = {key: [] for key in source}
        for key, items in source.items():
            ref_items = reference.get(key, [])
            missing[key] = [item for item in items if item not in ref_items]
        return missing


    def _format_section(self, title: str, elements_dict):
        section = f"\n{title}:\n"
        for element_type, items in elements_dict.items():
            section += f"\n{element_type}:\n"
            section += "\n".join(str(item) for item in items) + "\n"
        return section
    

    def get_raport_data(self):
        not_in_model = self._get_missing_elements(self.input_elements, self.found_elements)
        only_in_model = self._get_missing_elements(self.model_elements, self.input_elements)

        raport_data = ""
        raport_data += self._format_section("Elements not found in model", not_in_model)
        raport_data += self._format_section("Elements only found in model", only_in_model)

        return raport_data

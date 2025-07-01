class RaportHandler:

    def __init__(self, found_elements, input_elements, model_elements):
        self.found_elements = found_elements
        self.input_elements = input_elements
        self.model_elements = model_elements


    def get_raport_data(self):
        raport_data = ""
        is_found = False

        not_in_model = {
            "buses": [],
            "transformers": [],                
            "generators": [],              
            "shunts": []              
        }

        only_in_model = {
            "buses": [],
            "transformers": [],                
            "generators": [],              
            "shunts": []        
        }

        for element in self.input_elements:
            for input in self.input_elements[element]:
                is_found = False

                for found in self.found_elements[element]:
                    if input == found:
                        is_found = True
                        break

                if not is_found:
                    not_in_model[element].append( input )


        for element in self.model_elements:
            for model in self.model_elements[element]:
                is_found = False

                for input in self.input_elements[element]:
                    if input == model:
                        is_found = True
                        break
                
                if not is_found:
                    only_in_model[element].append(model)

       
        for type in not_in_model:

            raport_data += f"\n{type} not found in model:\n"

            for element in not_in_model[type]:
                raport_data += f"{element}\n"


        for type in only_in_model:

            raport_data += f"\n{type} only found in model:\n"

            for element in only_in_model[type]:
                raport_data += f"{element}\n"

        return raport_data
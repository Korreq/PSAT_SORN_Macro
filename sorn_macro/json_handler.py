import json

class JsonHandler:

    def __init__(self, input_file):
        
        with open(f'{input_file}', 'r') as file:
            self.data = json.load(file)            


    def get_transformers(self):

        transformers_names = []

        for transformer in self.data["transformers"]:
            transformer_name = transformer["name"]
            transformers_names.append(transformer_name)

        transformers_names.sort()
        return transformers_names
    

    def get_buses(self):

        buses_names = []

        for bus in self.data["buses"]:
            bus_name = bus["name"]
            buses_names.append(bus_name)

        buses_names.sort()
        return buses_names
    

    def get_generators(self):

        generators_names = []

        for generator in self.data["generators"]:
            generator_name = generator["name"]
            generators_names.append(generator_name)

        generators_names.sort()
        return generators_names
    

    def get_shunts(self):

        shunts_names = []

        for shunt in self.data["shunts"]:
            shunt_name = shunt["name"]
            shunts_names.append(shunt_name)

        shunts_names.sort()
        return shunts_names
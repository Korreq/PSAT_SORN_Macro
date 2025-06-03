from psat_functions import PsatFunctions

class ElementsLists:

    def __init__(self):
        self.psat = PsatFunctions()
        
    # Get buses that have directly connected generators. Can filter buses based on maximum MW generated on generator, 
    # bus will be added if there's at least one generator fitting requirements
    def get_generators_bus(self, mw_min, subsys="mainsub"):

        added_buses_with_gens_id = {}
        generators = self.psat.get_element_list("generator", subsys)

        for generator in generators:

            bus = self.psat.get_bus_data(generator.bus)

            # Skip generator if max mw is not enough and if generator's bus base kv is not 110,220 or 400
            if generator.mwmax < mw_min or bus.basekv not in [110,220,400]:
                continue

            if bus.number not in added_buses_with_gens_id:
                added_buses_with_gens_id[bus.number] = [generator.id]

            else:
                gens_id = added_buses_with_gens_id.get( bus.number )
                gens_id.append( generator.id )

                added_buses_with_gens_id[bus.number] = gens_id

        return added_buses_with_gens_id
        

    def get_filtred_generators(self, mw_min, subsys="mainsub"):

        filtred_generators = []
        generators = self.psat.get_element_list("generator", subsys)

        for generator in generators:

            bus = self.psat.get_bus_data(generator.bus)

            # Skip generator if max mw is not enough and if generator's bus base kv is not 110,220 or 400
            if generator.mwmax < mw_min or bus.basekv not in [110,220,400]:
                continue

            filtred_generators.append( generator )

        return filtred_generators


    def get_filtred_buses(self, subsys="mainsub"):

        filtred_buses = []
        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            #Skip if bus base kv is not 110,220 or 400
            if bus.basekv not in [110,220,400]:
                continue

            filtred_buses.append(bus)

        return filtred_buses

    # Get from every bus in model it's current kv value
    def get_buses_base_kv(self, subsys="mainsub"):

        buses_kv = []
        buses = self.get_filtred_buses(subsys)

        for bus in buses:
            
            #Skip if bus base kv is not 110,220 or 400
            if bus.basekv not in [110,220,400]:
                continue

            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )
            buses_kv.append( bus_kv )

        return buses_kv
    
    # Get from filtred buses with directly connected generators their mvar values
    def get_generators_base_mvar(self, mw_min, subsys="mainsub"):

        generators_base_bus_mvar = []
        generators = self.get_filtred_generators(mw_min, subsys)

        for generator in generators:
            generators_base_bus_mvar.append( generator.mvar )

        return generators_base_bus_mvar
  
    # Get shunts, that absolute of nominal mvar value isn't less than specifed 
    def get_shunts(self, abs_minimum=0 ,subys="mainsub"):

        filtred_shunts = []
        shunts = self.psat.get_element_list("fixed_shunt", subys)

        for shunt in shunts:
            if abs(shunt.nommvar) < abs_minimum:
                continue

            filtred_shunts.append(shunt)

        return filtred_shunts
    
    # Get transformers, if filter set to true, 
    # return only transformers connected to/from 400 base kv buses to/from 220/110 base kv buses 
    def get_transformers(self, keep_transformers_without_connection_to_400=True, subsys="mainsub"):

        filtred_transformers = []
        transformers = self.psat.get_element_list("adjustable_transformer",subsys)

        for transformer in transformers:

            from_bus_kv, to_bus_kv = self.psat.get_bus_data(transformer.frbus).basekv, self.psat.get_bus_data(transformer.tobus).basekv

            if not keep_transformers_without_connection_to_400:
                if ( from_bus_kv == 400 or to_bus_kv == 400 ) and ( from_bus_kv in [110,220] or to_bus_kv in [110,220] ):
                    filtred_transformers.append(transformer)

            else:
                filtred_transformers.append(transformer)
           
        return filtred_transformers
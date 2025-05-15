from psat_functions import PsatFunctions

class ElementsLists:

    def __init__(self):
        self.psat = PsatFunctions()
        
    # Get buses that have directly connected generators. Can filter buses based on maximum MW generated on generator, 
    # bus will be added if there's at least one generator fitting requirements
    def get_generators_bus(self, mw_min=0 ,subsys="mainsub", skip_generators_on_same_bus=True):

        generators_bus = []
        added_buses = []

        generators = self.psat.get_element_list("generator", subsys)
        

        for generator in generators:

            if generator.mwmax < mw_min:

                continue

            bus = self.psat.get_bus_data(generator.bus)

            # If not already added, add bus and first found connected generator to list   
            if bus.number not in added_buses or not skip_generators_on_same_bus:

                generators_bus.append( [ bus, generator ] )
                
                added_buses.append(bus.number)

        return generators_bus

    # Get from every bus in model it's current kv value
    def get_buses_base_kv(self, subsys="mainsub"):

        buses_kv = []

        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )

            buses_kv.append( bus_kv )

        return buses_kv
    
    # Get from filtred buses with directly connected generators their mvar values
    def get_generators_from_bus_base_mvar(self, mw_min=0, subsys="mainsub"):

        generators_from_bus_mvar = []

        buses_with_generators = self.get_generators_bus(mw_min, subsys, False)

        for buses in buses_with_generators:

            generators_from_bus_mvar.append( buses[1].mvar )

        return generators_from_bus_mvar
  
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
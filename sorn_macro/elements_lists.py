from psat_functions import PsatFunctions


class ElementsLists:

    def __init__(self):
        self.psat = PsatFunctions()

    
    def get_generators_with_buses(self, subsys="mainsub"):

        generators_with_buses = []

        generators = self.psat.get_element_list("generator", subsys)
        buses = self.psat.get_element_list("bus", subsys)

        for generator in generators:

            for bus in buses:

                if( generator.bus == bus.number ):

                    generators_with_buses.append( [bus, generator] )            
        
        return generators_with_buses


    def get_buses_base_kv(self, subsys="mainsub"):

        buses_kv = []

        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )

            buses_kv.append( [bus.number, bus_kv] )

        return buses_kv
    

    def get_generators_base_mvar(self, subsys="mainsub"):

        gens_mvar = []

        gens = self.psat.get_element_list("generator", subsys)

        for gen in gens:

            if gen.mw < 300:
                continue

            gens_mvar.append( [gen.bus, gen.mvar, gen.id] ) 

        return gens_mvar
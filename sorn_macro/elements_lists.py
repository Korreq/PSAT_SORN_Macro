from psat_functions import PsatFunctions


class ElementsLists:

    def __init__(self):
        self.psat = PsatFunctions()

    
    def get_generators_with_buses(self, subsys="mainsub"):

        generators_with_buses = []

        generators = self.psat.get_element_list("generator", subsys)
        buses = self.psat.get_element_list("bus", subsys)

        for generator in generators:

            if generator.mwmax < 200:

                continue

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
        buses = self.psat.get_element_list("bus", subsys)

        for gen in gens:

            if gen.mwmax < 200:

                continue

            for bus in buses:

                if( gen.bus == bus.number ):
                    
                    gens_mvar.append( [gen.bus, gen.mvar, gen.id] ) 

        return gens_mvar
    
    # Need to look into from which side is controled and to take base_mvar from that
    def get_transformers_base_mvar(self, subsys="mainsub"):

        trfs_mvar = []

        trf_mvar = None

        trfs = self.psat.get_element_list("adjustable_transformer", subsys)

        for trf in trfs:

            trf_mvar = trf.qfr if trf.meter == "F" else trf.qto

            trfs_mvar.append( [trf.frbus, trf.tobus, trf.id, trf_mvar ] )

        return trfs_mvar
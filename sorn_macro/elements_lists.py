from psat_functions import PsatFunctions


class ElementsLists:

    def __init__(self):
        self.psat = PsatFunctions()


    def get_generators_bus(self, subsys="mainsub"):

        generators_bus = []
        added_buses = []

        generators = self.psat.get_element_list("generator", subsys)
        
        for generator in generators:

            if generator.mwmax < 200:

                continue

            bus = self.psat.get_bus_data(generator.bus)
           
            if bus.number not in added_buses:

                generators_bus.append( [ bus, generator ] )
                
                added_buses.append(bus.number)

        return generators_bus


    def get_buses_base_kv(self, subsys="mainsub"):

        buses_kv = []

        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            bus_kv = round( float(bus.basekv) * float(bus.vmag), 2 )

            buses_kv.append( bus_kv )

        return buses_kv
    
  
    def get_generators_from_bus_base_mvar(self, subsys="mainsub"):

        generators_from_bus_mvar = []

        buses_with_generators = self.get_generators_bus(subsys)

        for buses in buses_with_generators:

            generators_from_bus_mvar.append( buses[1].mvar )

        return generators_from_bus_mvar


    # Need to look into from which side is controled and to take base_mvar from that
    def get_transformers_base_mvar(self, subsys="mainsub"):

        trfs_mvar = []

        trf_mvar = None

        trfs = self.psat.get_element_list("adjustable_transformer", subsys)

        for trf in trfs:

            trf_mvar = trf.qfr if trf.meter == "F" else trf.qto

            trfs_mvar.append( trf_mvar )

        return trfs_mvar
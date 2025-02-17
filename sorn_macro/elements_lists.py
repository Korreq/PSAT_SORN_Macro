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


    def get_bus_base_pu(self, subsys="mainsub"):

        buses_pu = []

        buses = self.psat.get_element_list("bus", subsys)

        for bus in buses:

            buses_pu.append( [bus.number, bus.vmag] )

        return buses_pu
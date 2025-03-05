from psat_functions import PsatFunctions

class ElementsFunctions:

    def __init__(self):
        self.psat = PsatFunctions()


    def get_transformer_taps(self, transformer):

        down_change = True

        beg_bus = self.psat.get_bus_data(transformer.frbus)
        end_bus = self.psat.get_bus_data(transformer.tobus)

        trf_from_side = transformer.fsratio * beg_bus.basekv
        trf_to_side = transformer.tsratio * end_bus.basekv

        trf_current_ratio =  round( trf_from_side / trf_to_side, 4)

        trf_max =  ( transformer.maxratio * beg_bus.basekv ) / trf_to_side
        trf_min =  ( transformer.minratio * beg_bus.basekv ) / trf_to_side
        trf_step =  (transformer.stepratio * beg_bus.basekv) / trf_to_side 

       

        trf_max_tap = trf_current_tap = trf_changed_tap = 0
        trf_pass = trf_min

        while trf_pass < trf_max:

            if( 
                round(trf_pass, 4) >= round( trf_current_ratio - (0.05 * trf_current_ratio), 4 ) and
                round(trf_pass, 4) <= round( trf_current_ratio + (0.05 * trf_current_ratio), 4 )  
            ):
                trf_current_tap = trf_max_tap

                if(trf_pass + trf_step <= trf_max):
                    trf_changed_tap = trf_max_tap - 1
                else:
                    trf_changed_tap = trf_max_tap + 1
                    down_change = False

            trf_max_tap += 1
            trf_pass += trf_step

        trf_current_tap = trf_max_tap - trf_current_tap
        trf_changed_tap = trf_max_tap - trf_changed_tap

        return down_change, trf_max_tap, trf_current_tap, trf_changed_tap
    
    def get_bus_changed_kv_vmag(self, bus, value):

        bus_kv = float(bus.basekv) * float(bus.vmag)
        bus_new_kv = bus_kv + value
        changed_kv_vmag = bus_new_kv / float(bus.basekv)
        
        return changed_kv_vmag, bus_kv
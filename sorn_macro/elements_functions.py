from psat_functions import PsatFunctions
import locale

class ElementsFunctions:

    def __init__(self):
        self.psat = PsatFunctions()
        
    # Get transformer's current tap, max tap, change_tap value and if it was a tap change down 
    def get_transformer_taps(self, transformer, transformer_ratio_margin=0.05):

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
                round(trf_pass, 4) >= round( 
                    trf_current_ratio - (transformer_ratio_margin * trf_current_ratio), 4 ) and
                round(trf_pass, 4) <= round( 
                    trf_current_ratio + (transformer_ratio_margin * trf_current_ratio), 4 )  
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
    
    # Get changed kv value by specified value and it's multiplier from base value 
    def get_bus_changed_kv_vmag(self, bus, value):

        bus_kv = float(bus.basekv) * float(bus.vmag)
        bus_new_kv = bus_kv + value
        changed_kv_vmag = bus_new_kv / float(bus.basekv)
        
        return changed_kv_vmag, bus_kv
    
    # For each updated generator bus get differrence from base mvar and append it to q_row list. 
    # If first pass, then add bus name to q_header list 
    def get_changed_generator_buses_results(self, changed_generators, base_generators_mvar , first_pass):

        q_header = []
        q_row = []

        for i in range( len( changed_generators ) ):

            if first_pass:
                q_header.append( changed_generators[i][1].eqname )
        
            bus_q_change = locale.format_string('%G', float( changed_generators[i][1].mvar ) 
                                                      - float( base_generators_mvar[i] ), grouping=True )

            q_row.append( bus_q_change )

        return q_row, q_header
        
    # For each updated buses get differrence from base kv and append it to v_row list.
    # If first pass, then add nodes name to v_row list 
    def get_changed_buses_results(self, changed_buses, base_buses_kv, first_pass):

        v_header = []
        v_row = []

        for i in range( len( changed_buses ) ):

            if first_pass:
                v_header.append( changed_buses[i].name[:-4].strip() )

            bus_kv = float(changed_buses[i].basekv) * float(changed_buses[i].vmag)
    
            bus_kv_change = locale.format_string('%G', bus_kv - base_buses_kv[i], grouping=True)

            v_row.append( bus_kv_change )

        return v_row, v_header
       
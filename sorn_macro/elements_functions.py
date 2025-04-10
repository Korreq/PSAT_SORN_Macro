from psat_functions import PsatFunctions

class ElementsFunctions:

    def __init__(self):
        self.psat = PsatFunctions()

    "Fix missing config arguments in main file"       

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
    

    def get_bus_changed_kv_vmag(self, bus, value):

        bus_kv = float(bus.basekv) * float(bus.vmag)
        bus_new_kv = bus_kv + value
        changed_kv_vmag = bus_new_kv / float(bus.basekv)
        
        return changed_kv_vmag, bus_kv
    

    def get_changed_generator_buses_results(self, changed_generators, base_generators_mvar , first_pass, rounding_precission=2):

        q_header = []
        q_row = []

        for i in range( len( changed_generators ) ):

            if first_pass:
                q_header.append( changed_generators[i][1].eqname.split("-")[0] )

            generator_q_change = round( float( changed_generators[i][1].mvar ) 
                                       - float( base_generators_mvar[i] ), rounding_precission )

            q_row.append( generator_q_change )

        return q_row, q_header
        

    def get_changed_transformers_results(self, changed_transformers, base_transformers_mvar, first_pass, rounding_precission=2):

        q_header = []
        q_row = []

        for i in range( len( changed_transformers ) ):

            if first_pass:
                q_header.append( changed_transformers[i].name )

            trf_mvar = changed_transformers[i].qfr if changed_transformers[i].meter == "F" else changed_transformers[i].qto
            trf_q_change = round( float( trf_mvar ) 
                                 - float( base_transformers_mvar[i] ), rounding_precission )

            q_row.append( trf_q_change )

        return q_row, q_header
        

    def get_changed_buses_results(self, changed_buses, base_buses_kv, first_pass, rounding_precission=2, node_notation_next_to_bus_name=False):

        v_header = []
        v_row = []

        for i in range( len( changed_buses ) ):

            if first_pass:

                if node_notation_next_to_bus_name:
                    v_header.append( changed_buses[i].name )

                else:
                    v_header.append( changed_buses[i].name.split("  ")[0] )

            bus_kv = round( float(changed_buses[i].basekv) * float(changed_buses[i].vmag), 2 )
            bus_kv_change = round( bus_kv - base_buses_kv[i], rounding_precission )

            v_row.append( bus_kv_change )

        return v_row, v_header
       
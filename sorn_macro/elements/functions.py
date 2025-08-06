import locale

from core.psat_functions import PsatFunctions


class ElementsFunctions:

    def __init__(self):
        self.psat = PsatFunctions()
        
        
    def set_new_generators_bus_kv_value( self, generator_bus_number, generators_id, tmp_model_path, node_kv_change_value=1 ):
        generator_bus = self.psat.get_bus_data( generator_bus_number )

        # Getting new kv change from base value and calculated bus kv
        changed_kv_vmag, bus_kv = self.get_bus_changed_kv_vmag( generator_bus, node_kv_change_value )

        # Apply new kv changed value to all generators connected to bus
        self.set_generators_kv_limits( generator_bus_number, generators_id, changed_kv_vmag )
        self.psat.calculate_powerflow()

        # Get generator bus with new calculated values
        generator_bus = self.psat.get_bus_data( generator_bus_number )
        
        # Check if generators bus reached changed_kv_mag, if not try to change in opposite direction
        if round(generator_bus.vmag, 4) < round(changed_kv_vmag, 4):

            # Get old kv_difference
            kv_difference =  ( generator_bus.basekv * generator_bus.vmag )  - bus_kv
            self.psat.load_model(tmp_model_path)

            # Getting new kv change from base value and calculated bus kv
            changed_kv_vmag, bus_kv = self.get_bus_changed_kv_vmag( generator_bus, - node_kv_change_value )

            # Apply new kv changed value to all generators connected to bus
            self.set_generators_kv_limits( generator_bus_number, generators_id, changed_kv_vmag )
            self.psat.calculate_powerflow()

            # Get generator bus with new calculated values
            generator_bus = self.psat.get_bus_data( generator_bus.number )
         
            # Use kv change, that have higger difference value  
            if abs(  ( generator_bus.basekv * generator_bus.vmag )  - bus_kv ) <= abs( kv_difference ):
                self.psat.load_model(tmp_model_path)

                # Getting new kv change from base value and calculated bus kv
                changed_kv_vmag, bus_kv = self.get_bus_changed_kv_vmag( generator_bus, node_kv_change_value )

                # Apply new kv changed value to all generators connected to bus
                self.set_generators_kv_limits( generator_bus_number, generators_id, changed_kv_vmag )
                self.psat.calculate_powerflow()

                # Get generator bus with new calculated values
                generator_bus = self.psat.get_bus_data( generator_bus.number )

        # Calculate bus new kv and it's kv change from base value 
        kv_difference =  ( generator_bus.basekv * generator_bus.vmag )  - bus_kv

        # Return generator's bus number, generator's bus name and it's bus kv difference in array form
        return [ generator_bus.number, "-", generator_bus.name[:-4].strip(), locale.format_string('%G',kv_difference) ]


    def set_transformer_new_tap( self, transformer, transformer_ratio_margin=0.05 ):
        beg_bus = self.psat.get_bus_data(transformer.frbus)
        end_bus = self.psat.get_bus_data(transformer.tobus)

        trf_current_tap, trf_current, trf_max, trf_step = self.get_transformer_ratios(transformer, beg_bus.basekv, end_bus.basekv, transformer_ratio_margin)

        # Change one tap down if possible, otherwise change tap up
        if( trf_current + trf_step <= trf_max ):
            transformer.fsratio += transformer.stepratio
        else:
            transformer.fsratio -= transformer.stepratio

        self.psat.set_transformer_data(transformer)
        self.psat.calculate_powerflow()

        updated_transformer = self.psat.get_transformer_data( transformer.frbus, transformer.tobus, transformer.id, transformer.sec )

        #Get updated current tap 
        trf_updated_current_tap = self.get_transformer_ratios(updated_transformer, beg_bus.basekv, 
                                                              end_bus.basekv, transformer_ratio_margin)[0]

        return [ transformer.frbus, transformer.tobus, transformer.name, trf_updated_current_tap - trf_current_tap ]


    def get_transformer_ratios( self, transformer, beg_bus_base_kv, end_bus_base_kv, transformer_ratio_margin, get_data_for_elements_file=False ):
        trf_from_side = transformer.fsratio * beg_bus_base_kv
        trf_to_side = transformer.tsratio * end_bus_base_kv

        trf_current =  round( trf_from_side / trf_to_side, 4)

        trf_max = ( transformer.maxratio * beg_bus_base_kv ) / trf_to_side
        trf_min = ( transformer.minratio * beg_bus_base_kv ) / trf_to_side
        trf_step = ( transformer.stepratio * beg_bus_base_kv ) / trf_to_side 

        trf_max_tap = trf_current_reversed_tap = 0
        trf_pass = trf_min
        while trf_pass < trf_max:
            if( 
                round(trf_pass, 4) > round( trf_current - (transformer_ratio_margin * trf_current), 4 ) and
                round(trf_pass, 4) < round( trf_current + (transformer_ratio_margin * trf_current), 4 )  
            ):
                trf_current_reversed_tap = trf_max_tap
                
            trf_max_tap += 1
            trf_pass += trf_step

        trf_current_tap = trf_max_tap - trf_current_reversed_tap

        if get_data_for_elements_file:
            return trf_current_tap, trf_max_tap
        
        return trf_current_tap, trf_current, trf_max, trf_step

    # Find generators by their id number and bus number, set their kv bus limit if mvar min and max are not the same and apply changes
    def set_generators_kv_limits(self, bus_number, generators_id, changed_kv_vmag):
        for generator_id in generators_id:
            generator = self.psat.get_generator_data(bus_number, generator_id)
            
            if generator.mvarmax != generator.mvarmin:
                generator.vhi = generator.vlo = changed_kv_vmag
                self.psat.set_generator_data(generator)    

    # Get changed kv value by specified value and it's multiplier from base value 
    def get_bus_changed_kv_vmag(self, bus, value):
        bus_kv = bus.basekv * bus.vmag
        bus_new_kv = bus_kv + value
        changed_kv_vmag = bus_new_kv / bus.basekv
        
        return changed_kv_vmag, bus_kv
    
    # Get bus type name depending on it's type number
    def get_bus_type(self, bus):
        types = ["Load","Generator","Swing","Out of service"]

        if bus.type > 0 and bus.type < 5:
            name = types[ bus.type - 1 ]
        else:
            name = "Unknown"

        return name

    # Get formated bus name from bus id
    def get_bus_name_from_id(self, id):
        bus = self.psat.get_bus_data(id)
        return bus.name[:-4].strip()

    # For each updated generator bus get differrence from base mvar and append it to q_row list. 
    # If first pass, then add bus name to q_header list 
    def get_generators_mvar_differrence_results(self, changed_generators, base_generators_mvar, first_pass):
        q_header = []
        q_row = []

        for i in range( len( changed_generators ) ):
            if first_pass:
                q_header.append( changed_generators[i].eqname )
        
            bus_q_change = locale.format_string('%G', changed_generators[i].mvar - base_generators_mvar[i])

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

            bus_kv = changed_buses[i].basekv * changed_buses[i].vmag
            bus_kv_change = locale.format_string('%G', bus_kv - base_buses_kv[i])

            v_row.append( bus_kv_change )

        return v_row, v_header
    
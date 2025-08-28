import locale

from core.psat_functions import PsatFunctions


class ElementsFunctions:

    def __init__(self):
        self.psat = PsatFunctions()
        
        
    def set_new_generators_bus_kv_value( self, generator_bus_number, generators_id, tmp_model_path, node_kv_change_value=1 ):
        ''' Try to set generators' bus new kv value by set kv change value up or down. When not able to achive such change, 
        change it said direction which allows for bigger change. '''

        # Get bus object from generator's bus number 
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

            # Get old kv_difference and reload model
            kv_difference = ( generator_bus.basekv * generator_bus.vmag ) - bus_kv
            self.psat.load_model(tmp_model_path)

            # Update generator bus with base values
            generator_bus = self.psat.get_bus_data( generator_bus_number )

            # Getting new kv change from base value and calculated bus kv
            changed_kv_vmag, bus_kv = self.get_bus_changed_kv_vmag( generator_bus, - node_kv_change_value )

            # Apply new kv changed value to all generators connected to bus
            self.set_generators_kv_limits( generator_bus_number, generators_id, changed_kv_vmag )
            self.psat.calculate_powerflow()

            # Get generator bus with new calculated values
            generator_bus = self.psat.get_bus_data( generator_bus.number )
         
            # Use kv change, that have higger difference value  
            if abs(  ( generator_bus.basekv * generator_bus.vmag ) - bus_kv ) <= abs( kv_difference ):

                # Reload model
                self.psat.load_model(tmp_model_path)

                # Update generator bus with base values
                generator_bus = self.psat.get_bus_data( generator_bus_number )

                # Getting new kv change from base value and calculated bus kv
                changed_kv_vmag, bus_kv = self.get_bus_changed_kv_vmag( generator_bus, node_kv_change_value )

                # Apply new kv changed value to all generators connected to bus
                self.set_generators_kv_limits( generator_bus_number, generators_id, changed_kv_vmag )
                self.psat.calculate_powerflow()

                # Get generator bus with new calculated values
                generator_bus = self.psat.get_bus_data( generator_bus.number )

        # Calculate bus new kv and it's kv change from base value 
        kv_difference = ( generator_bus.basekv * generator_bus.vmag ) - bus_kv

        # Return generator's bus number, generator's bus name and it's bus kv difference in array form
        return [ generator_bus.number, "-", generator_bus.name[:-4].strip(), locale.format_string('%G',kv_difference) ]


    def set_transformer_new_tap( self, transformers, transformer_ratio_margin=0.05 ):
        ''' Set all transformers with same buses taps based on theirs' direction to connected buses'''

        transformers_names = []
        first_transformer_tap_difference = 0

        first_transformer = transformers[0]
        first_beg_number = first_transformer.frbus

        for i, transformer in enumerate(transformers):
            transformer_name = transformer.name
            beg_bus = self.psat.get_bus_data(transformer.frbus)
            end_bus = self.psat.get_bus_data(transformer.tobus)

            trf_current_tap, trf_current, trf_max, trf_step = self.get_transformer_ratios(
                transformer, beg_bus.basekv, end_bus.basekv, transformer_ratio_margin
            )

            # Tap change direction logic
            if i > 0 and first_beg_number != transformer.frbus:
                # Reverse direction
                if trf_current + trf_step <= trf_max:
                    transformer.fsratio += transformer.stepratio
                else:
                    transformer.fsratio -= transformer.stepratio

            else:
                # Normal direction
                if trf_current - trf_step >= 0:
                    transformer.fsratio -= transformer.stepratio
                else:
                    transformer.fsratio += transformer.stepratio
       
            self.psat.set_transformer_data(transformer)
            self.psat.calculate_powerflow()

            # Update transformer after changes
            updated_transformer = self.psat.get_transformer_data( 
                transformer.frbus, transformer.tobus, transformer.id, transformer.sec 
            )
            #Get updated current tap    
            trf_updated_current_tap = self.get_transformer_ratios(
                updated_transformer, beg_bus.basekv, end_bus.basekv, transformer_ratio_margin
            )[0]

            if i == 0:
                first_transformer_tap_difference = trf_updated_current_tap - trf_current_tap

            transformers_names.append( transformer_name )

        transformers_names_str = '#'.join(transformers_names)
        return [ first_transformer.frbus, first_transformer.tobus, transformers_names_str, first_transformer_tap_difference ]

    
    def get_transformer_ratios( self, transformer, beg_bus_base_kv, end_bus_base_kv, transformer_ratio_margin, get_data_for_elements_file=False ):
        ''' Get transformer's current tap, max tap, last tap ratio and step ratio between taps. '''
        
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


    def set_generators_kv_limits(self, bus_number, generators_id, changed_kv_vmag):
        ''' Find generators by their id number and bus number, set their kv bus limit if mvar min and max are not 
        the same and apply changes'''

        for generator_id in generators_id:
            generator = self.psat.get_generator_data(bus_number, generator_id)
            
            generator.vhi = generator.vlo = changed_kv_vmag
            self.psat.set_generator_data(generator)    

    def get_bus_changed_kv_vmag(self, bus, value):
        ''' Get changed kv value by specified value and it's multiplier from base value '''
        
        bus_kv = bus.basekv * bus.vmag
        bus_new_kv = bus_kv + value
        changed_kv_vmag = bus_new_kv / bus.basekv
        
        return changed_kv_vmag, bus_kv
    
    
    def get_bus_type(self, bus):
        ''' Get bus type name depending on it's type number '''
        
        types = ["Load","Generator","Swing","Out of service"]

        if bus.type > 0 and bus.type < 5:
            name = types[ bus.type - 1 ]
        else:
            name = "Unknown"

        return name


    def get_bus_name_from_id(self, id):
        ''' Get formated bus name from bus id '''
        
        bus = self.psat.get_bus_data(id)
        return bus.name[:-4].strip()


    def get_generators_mvar_differrence_results(self, changed_generators, base_generators_mvar, first_pass):
        '''For each updated generator bus get differrence from base mvar and append it to q_row list. 
        If first pass, then add bus name to q_header list '''
        
        q_header = []
        q_row = []

        for i in range( len( changed_generators ) ):
            if first_pass:
                q_header.append( changed_generators[i].eqname )
        
            bus_q_change = locale.format_string('%G', changed_generators[i].mvar - base_generators_mvar[i])

            q_row.append( bus_q_change )

        return q_row, q_header
        

    def get_changed_buses_results(self, changed_buses, base_buses_kv, first_pass):
        ''' For each updated buses get differrence from base kv and append it to v_row list. 
        If first pass, then add nodes name to v_row list '''

        v_header = []
        v_row = []

        for i in range( len( changed_buses ) ):
            if first_pass:
                v_header.append( changed_buses[i].name[:-4].strip() )

            bus_kv = changed_buses[i].basekv * changed_buses[i].vmag
            bus_kv_change = locale.format_string('%G', bus_kv - base_buses_kv[i])

            v_row.append( bus_kv_change )

        return v_row, v_header
    
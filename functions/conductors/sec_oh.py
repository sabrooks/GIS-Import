from conductor_general import conductor_init, LINES, SIZE_MATERIAL

SEC_OH_COND_INFO = lambda x: x['properties']['SecOHConductorObjectID']

SEC_OH = {'SecOHElectricLineSegment':
          {'prefix':'OHSec_', 'section_type':1, 'funcs':LINES,
            'init': lambda gdb: 
                    conductor_init(gdb, 'SECOHCONDUCTORINFO',
                                   SEC_OH_COND_INFO, SIZE_MATERIAL)}}
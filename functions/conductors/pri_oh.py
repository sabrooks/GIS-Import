from conductor_general import conductor_init, LINES, SIZE_MATERIAL



PRI_OH_COND_INFO = lambda x: x['properties']['PriOHConductorObjectID']

PRI_OH = {'PriOHElectricLineSegment':
          {'prefix':'OH_', 'section_type':1, 'funcs':LINES,
            'init': lambda gdb: 
                    conductor_init(gdb, 'PRIOHCONDUCTORINFO',
                    PRI_OH_COND_INFO, SIZE_MATERIAL)}}

from conductor_general import conductor_init, LINES, SIZE_WIRE

PRI_UG_COND_INFO = lambda x: x['properties']['PriUGConductorObjectID']

PRI_UG = {'PriUGElectricLineSegment':
          {'prefix':'UG_', 'section_type':3, 'funcs':LINES,
            'init': lambda gdb: 
                    conductor_init(gdb, 'PRIUGCONDUCTORINFO',
                                   PRI_UG_COND_INFO, SIZE_WIRE)}}
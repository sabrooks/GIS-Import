from conductor_general import conductor_init, LINES, SIZE_MATERIAL

SEC_UG_COND_INFO = lambda x: x['properties']['SecUGConductorObjectID']

SEC_UG = {'SecUGElectricLineSegment':
          {'prefix':'UGSec_', 'section_type':3, 'funcs':LINES,
            'init': lambda gdb: 
                    conductor_init(gdb, 'SECUGCONDUCTORINFO',
                                   SEC_UG_COND_INFO, SIZE_MATERIAL)}}
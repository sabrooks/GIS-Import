'Functions and dicts to construct conductor layers'
import fiona

def conductor_configuration(conductor):
    'For segments - check first, if no value, assumes "HOR" '
    try:
        return conductor['properties']['ConductorConfiguration']
    except:
        return "HOR"

def conductor_init(gdb, layer, pkey):
    'Return a dict of conductor keys and conductor names'
    def conductor_lookup(detail, pkey=pkey):
        'Creates key, value pairing'
        try:
            return detail[pkey], detail['ConductorSize'] + detail['ConductorMaterial']
        except:
            try:
                return detail[pkey], detail['ConductorSize'] + detail['WireType']
            except:
                return None, None
        looked = (conductor_lookup(detail) for detail in fiona.open(gdb, layer=layer))
        return {key: value for key, value in looked if key and value}

LINES = {'F14': lambda raw, out, _: {**out, 'F14': conductor_configuration(raw)},
         'F34': lambda raw, out, _: {**out, 'F34':1}}

CONDUCTOR = {'PriOHElectricLineSegment':
             {'prefix':'OH_', 'section_type':1, 'funcs':LINES,
             'init': lambda gdb: conductor_init(gdb, 'PRIOHCONDUCTORINFO', 'PriOHConductorObjectID')},
             'PriUGElectricLineSegment':
             {'prefix':'UG_', 'section_type':3, 'funcs':LINES,
             'init': lambda gdb: conductor_init(gdb, 'PRIUGCONDUCTORINFO', 'PriUGConductorObjectID')},
             'SecOHElectricLineSegment':{'prefix':'OHSec_', 'section_type':1, 'funcs': LINES,
             'init': lambda gdb: conductor_init(gdb, 'SECOHCONDUCTORINFO', 'SecOHConductorObjectID')},
             'SecUGElectricLineSegment':{'prefix':'UGSec_', 'section_type':3, 'funcs': LINES,
             'init': lambda gdb: conductor_init(gdb, 'SECUGCONDUCTORINFO', 'SecUGConductorObjectID')},
             'BusBar':{'prefix':'UGB_', 'section_type':1, 'funcs': LINES}}

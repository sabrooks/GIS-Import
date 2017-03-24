'Functions and dicts to construct conductor layers'

def conductor_configuration(conductor):
    'For segments - check first, if no value, assumes "HOR" '
    try:
        return conductor['properties']['ConductorConfiguration']
    except:
        return "HOR"

LINES = {'F14': lambda raw, out, _: {**out, 'F14': conductor_configuration(raw)},
         'F34': lambda raw, out, _: {**out, 'F34':1}}

CONDUCTOR = {'PriOHElectricLineSegment':{'prefix':'OH_', 'section_type':1, 'funcs':LINES},
             'PriUGElectricLineSegment':{'prefix':'UG_', 'section_type':3, 'funcs':LINES},
             'SecOHElectricLineSegment':{'prefix':'OHSec_', 'section_type':1, 'funcs': LINES},
             'SecUGElectricLineSegment':{'prefix':'UGSec_', 'section_type':3, 'funcs': LINES},
             'BusBar':{'prefix':'UGB_', 'section_type':1, 'funcs': LINES}}

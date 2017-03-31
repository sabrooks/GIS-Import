"""General imports for conductors"""
import fiona

LINES = {'F14': lambda raw, out, _: {**out, 'F14': conductor_configuration(raw)},
         'F34': lambda raw, out, _: {**out, 'F34':1}}

SIZE_MATERIAL = lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['ConductorMaterial'])
SIZE_WIRE = lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['WireType'])

def conductor_init(gdb, layer, key, value):
    'Creates a dict of GDB layer based of a function to access key and value'
    return {key(element):value(element) for element in fiona.open(gdb, layer=layer)}

def conductor_configuration(conductor):
    'For segments - check first, if no value, assumes "HOR" '
    try:
        return conductor['properties']['ConductorConfiguration']
    except:
        return "HOR"
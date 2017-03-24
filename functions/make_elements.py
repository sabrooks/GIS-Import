'Constructs a default layer and element processing'

from collections import OrderedDict
from functools import reduce
import fiona

def make_init(G)

def make_layer(gdb, layer, *, kwds):
    'Function calls make element on all elements in a layer'
    functions = make_function_stack(kwds)
    return [make_element(element, functions, kwds)
            for element in fiona.open(gdb, layer=layer)]

def make_element(element, functions, kwds):

    return reduce(lambda prev, func: func(element, prev, kwds),
                  [function for _, function in functions.items()], {})

def get_material(raw, init, kwds):
    try:
        return {'material': init[int(raw['id'])]}
    except:
        return {'material': None}

def make_function_stack(kwds):
    '''Constructs function stack as ordered dict'''
    functions = OrderedDict(
        [('material', get_material), # start with material
         ('geometry', lambda raw, out, _: {**out, 'geometry': raw['geometry']}), # Store for geo processing
         ('section_name', lambda raw, out, kwds: {**out, 'SectionName':kwds['prefix'] + str(raw['id'])}),
         ('section_type', lambda raw, out, kwds: {**out, 'SectionType': kwds['section_type']}),
         ('section_phase_config', get_section_phase_config),
         ('phase_spread', get_spread_phases),
         ('guid', lambda raw, out, _: {**out, 'F50':raw['properties']['GlobalID']}),
         ('coordinates', get_coordinates)])

    # Overwrite standard functions with specific functions passed in as a dictionary
    for func_name, func in kwds['funcs'].items():
        functions[func_name] = func
        
    return functions

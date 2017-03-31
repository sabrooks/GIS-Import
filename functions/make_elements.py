'Constructs a default layer and element processing'

from collections import OrderedDict
from functools import reduce
from general import *
import fiona

def make_init(gdb, **kwargs):
    '''Makes the init dict for detail lookup if needed.
    If details are needed, a function is passed.
    The details are used to init the feature processing.
    Assumes a different layer specified in function.'''
    kwargs['details'] = kwargs['init'](gdb)
    import pdb; pdb.set_trace()
    return kwargs

def make_layer(gdb, layer, kwds):
    'Function calls make element on all elements in a layer'
    functions = make_function_stack(kwds)
    return [make_element(element, functions, kwds)
            for element in fiona.open(gdb, layer=layer)]

def make_element(element, functions, kwds):
    details = kwds.pop('details', None)
    init = {'details':details} if details else {}
    return reduce(lambda prev, func: func(element, prev, kwds),
                  [function for _, function in functions.items()], init)

def get_material(raw, init, kwds):
    return init

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

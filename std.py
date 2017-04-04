'Functions for exporting the STD and MPT files from a GDB'

from collections import OrderedDict, defaultdict
import csv
from functools import reduce
from multiprocessing.dummy import Pool as ThreadPool
import fiona
from std_layers import ELEMENTS


def make_function_stack(kwargs):
    '''Constructs function stack as ordered dict'''
    def get_coordinates(raw, out, kwargs):
        "Appends coordinates to output dict"
        geo = raw['geometry']
        coordinates = geo['coordinates']
        coords = {}
        coords['Xcoord'], coords['Ycoord'] = coordinates if geo['type'] == 'Point' else coordinates[0][-1]
        try:
            coords['F32'], coords['F33'] = coordinates[0][0]
        except:
            pass
        try:
            coords['F13'] = raw['properties']['Shape_Length']
        except:
            pass
        return {**out, **coords}

    def get_section_phase_config(raw, out, kwargs):
        'Appends section phase config to output dict'
        SECTION_PHASE = {1:'C', 2:'B', 3:'BC', 4:'A', 5:'AC', 6:'AB', 7:'ABC'}
        try:
            phase = raw['properties']['PhaseDesignation']
            section_phase_config = SECTION_PHASE[phase]
        except:
            section_phase_config = 'ABC'
        return {**out, 'SectionPhaseConfig':section_phase_config}

    def get_spread_phases(raw, out, kwargs):
        detail = kwargs.pop('detail', None)
        phase_cells = kwargs.pop('phase_cells', ['F9', 'F10', 'F11'])
        detail_cells = kwargs.pop('detail_cells', ['F12'])
        if detail:
            for phase, cell in zip(['A', 'B', 'C'], phase_cells):
                if phase in out['SectionPhaseConfig']:
                    out[cell] = detail
            for cell in detail_cells:
                out[cell] = detail
        return out


    functions = OrderedDict(
        [('geometry', lambda r, o, _: {**o, 'geometry': r['geometry']}), # Store for geo processing
         ('section_name', lambda r, o, k: {**o, 'SectionName':k['prefix'] + str(r['id'])}),
         ('section_type', lambda r, o, k: {**o, 'SectionType': k['section_type']}),
         ('section_phase_config', get_section_phase_config),
         ('phase_spread', get_spread_phases),
         ('guid', lambda r, o, k: {**o, 'F50':r['properties']['GlobalID']}),
         ('coordinates', get_coordinates)])

    # Overwrite standard functions with specific functions passed in as a dictionary
    custom_functions = kwargs.pop('functions', {})
    for func_name, func in custom_functions.items():
        functions[func_name] = func
    return functions

def initialize(gdb, **kwargs):
    'If init included in kwargs, builds detail dict'
    init = kwargs.pop('init', None)
    if init:
        table = init.get('table')
        f_key = init.get('f_key')
        f_value = init.get('f_value')
        detail_map = lambda x: (f_key(x), f_value(x))
        kwargs['details'] = dict((detail_map(detail) for detail in fiona.open(gdb, layer=table)))
    return kwargs


def make_element(element, layer_functions, **kwargs):
    details = kwargs.pop('details', None)
    f_detail = kwargs.pop('f_detail', lambda x: int(x['id'])) # ID is default 
    if details:
        detail = details.get(f_detail(element), None)
    elif f_detail:
        detail = f_detail(element)
    else:
        detail = kwargs.pop('detail', None)
    kwargs['detail'] = detail
    return reduce(lambda prev, func: func(element, prev, kwargs),
                  [function for _, function in layer_functions.items()], {})

def make_layer(gdb, layer, **kwargs):
    layer_functions = make_function_stack(kwargs)
    return [make_element(element, layer_functions, **kwargs) for element in fiona.open(gdb, layer=layer)]


def find_endpoint(element, end_points):
    def find_prior(element_geo, possible_priors):
        if len(possible_priors) == 1:
            return possible_priors[0]
        else:
            try:
                return [p for p in possible_priors if p['type'] != element_geo['type']][0]
            except:
                print('check element' + element['SectionName'])
                return possible_priors[0]

    geo = element['geometry']
    start = geo['coordinates'] if geo['type'] == 'Point' else geo['coordinates'][0][0]
    if end_points.get(start):
        possible = end_points.get(start)
        parent = find_prior(geo, possible)
        element['PriorSection'] = parent.get('name')
        element['F51'] = parent.get('guid')
    return element

def make_std_mpt(gdb, elements, export='Export'):
    'Function to make and export std and mpt files'
    pools = ThreadPool(8)
    layers = pools.map(lambda x: make_layer(gdb=x[0], layer=x[1], **x[2]),
                       ((gdb, layer, initialize(gdb, **kwargs)) for layer, kwargs in elements.items()))

    end_points = defaultdict(list)

    for layer in layers:
        for element in layer:
            key = (element['Xcoord'], element['Ycoord'])
            value = {'name':element['SectionName'], 'guid': element['F50'], 'type': element['geometry']['type']}
            end_points[key].append(value)

    std_elements = pools.map(lambda x: find_endpoint(x, end_points), (element for layer in layers for element in layer))

    std_fields = ['SectionName', 'SectionType', 'SectionPhaseConfig', 'PriorSection',
                  'MapNumber', 'Xcoord', 'Ycoord', 'UserTag',
                  *['F' + str(num) for num in range(9, 53)]]

    with open(export + '.std', 'w') as f:
        std = ([element.get(field, None) for field in std_fields]
               for element in std_elements)
        writer = csv.writer(f)
        writer.writerows(list(std))


    with open('MPT.mpt', 'w') as f:
        mpt_elements = (element for layer in layers for element in layer if element['geometry']['type'] != 'Point')
        mpt_lines = [[element['SectionName'], x, y, element['F50']]
                     for element in mpt_elements for  i, (x, y) in enumerate(element['geometry']['coordinates'][0]) if i > 0]
        writer = csv.writer(f)
        writer.writerows(mpt_lines)

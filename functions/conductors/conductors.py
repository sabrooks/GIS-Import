from collections import OrderedDict
import csv
from functools import reduce
from multiprocessing.dummy import Pool as ThreadPool
import fiona


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

def conductor_configuration(conductor):
    'For segments - check first, if no value, assumes "HOR" '
    try:
        return conductor['properties']['ConductorConfiguration']
    except:
        return "HOR"

def phasing(raw, out, kwargs):
    phases = {cell: (1 if phase in out['SectionPhaseConfig'] else 2)
              for cell, phase in zip(['F12', 'F13', 'F14'], ['A', 'B', 'C'])}
    return {**out, **phases}

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

GDB = 'GDB/Export_Feb01.gdb'

LINES = {'F14': lambda raw, out, _: {**out, 'F14': conductor_configuration(raw)},
         'F34': lambda raw, out, _: {**out, 'F34':1}}

POINTS = {'section_name': lambda r, o, k: {**o, 'SectionName': k['prefix'] + str(r['properties']['FacilityID'])},
          'map_number': lambda r, o, k: {**o, 'MapNumber': r['properties'].get('FacilityID')}}
ENABLED = {0:'O', 1:'C'}
SWITCHES = {'F9': lambda r, o, k: {**o, 'F9':ENABLED[r['properties']['Enabled']]},
            'partner': lambda r, o, k: {**o, 'F11': k['prefix'] + str(r['properties']['FacilityID']) + '-B'}}
SUBS = {'section_name': lambda r, o, k: {**o, 'SectionName': r['properties']['Name']},
        'map_number': lambda r, o, k: {**o, 'MapNumber': None}}
OPEN_POINTS = {'partner': lambda r, o, k: {**o, 'F11':o['section_name']}}
RECLOSERS = {'protection': lambda r, o, k: {**o,**{cell: r['properties']['FacilityID'] for cell in ['F9', 'F10', 'F11']}},
             'phasing': phasing,
             'F17': lambda r, o, k: {**o, 'F17': 0}}
CAPACITORS = {'F12-13': lambda r, o, k:{**o, 'F12':0, 'F13':0},
              'Enabled': lambda r, o, k: {**o, 'F20':r['properties']['Enabled']}}
METERS = {'section_name': lambda r, o, _: {**o, 'section_name':str(r['properties']['AccountNumber'])},
          'F24': lambda r, o, k: {**o, 'F24': 0},
          'F23': lambda r, o, k: {**o, 'F23':1} if r['properties']['Status'] == 'A' else o}
LIGHTS = {'F234':lambda r, o, k: {**o, 'F23':1, 'F24':8}}
FUSE_TYPE = {1:'CL', 2:'EXP', 3:'UGEXP', 4:'V'}
FUSES = {'F17': lambda r, o, k: {**o, 'F17':0},
         'UserTag': lambda r, o, k: {**o, 'UserTag': r['properties']['Tag']},
         'phasing': phasing}

PRI_OH = {'PriOHElectricLineSegment':
          {'prefix':'OH_', 'section_type':1, 'functions':LINES,
           'f_detail': lambda x: int(x['id']),
            'init': {'table':'PRIOHCONDUCTORINFO',
                     'f_key': lambda x: x['properties']['PriOHConductorObjectID'],
                     'f_value': lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['ConductorMaterial'])}}}

PRI_UG = {'PriUGElectricLineSegment':
          {'prefix':'UG_', 'section_type':3, 'functions':LINES,
           'f_detail': lambda x: int(x['id']),
            'init': {'table':'PRIUGCONDUCTORINFO',
                     'f_key': lambda x: x['properties']['PriUGConductorObjectID'],
                     'f_value': lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['WireType'])}}}

BUSBAR = {'BusBar':
          {'prefix':'UGB_', 'section_type':1, 'functions':LINES,
           'detail': 'BUS'}}

SEC_UG = {'SecUGElectricLineSegment':
          {'prefix':'UGSec_', 'section_type':3, 'functions':LINES,
           'f_detail': lambda x: int(x['id']),
           'init': {'table': 'SECUGCONDUCTORINFO',
                    'f_key': lambda x: x['properties']['SecUGConductorObjectID'],
                    'f_value': lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['ConductorMaterial'])}}}

SEC_OH = {'SecOHElectricLineSegment':
          {'prefix':'OHSec_', 'section_type':1, 'functions':LINES,
           'f_detail': lambda x: int(x['id']),
           'init': {'table': 'SECUGCONDUCTORINFO',
                    'f_key': lambda x: x['properties']['SecUGConductorObjectID'],
                    'f_value': lambda x: str(x['properties']['ConductorSize']) + str(x['properties']['ConductorMaterial'])}}}

SWITCH = {'Switch':{'prefix': 'SW_', 'section_type': 6, 'functions': {**POINTS, **SWITCHES}}}
OPEN_POINT = {'OpenPoint':{'prefix':'OP_', 'section_type':6, 'functions': {**POINTS, **SWITCHES}}}
ELECTRIC_STATION = {'ElectricStation':{'prefix': '', 'section_type':9, 'functions': {**POINTS, **SUBS}}}
DYNAMIC_PROTECTION_DEVICE = {'DynamicProtectiveDevice':
                             {'prefix': 'REC_', 'section_type':10, 'functions': {**POINTS, **RECLOSERS}}}
PF_CORRECTING_EQUIPMENT = {'PFCorrectingEquipment':
                           {'prefix': 'CAP_', 'section_type':2, 'functions': {**POINTS, **CAPACITORS},
                            'f_detail': lambda x: int(x['id']),
                            'init': {'table':'CAPACITORUNIT',
                            'f_key':lambda x: x['properties']['CapacitorBankObjectID'],
                            'f_value': lambda x: x['properties']['KVAR']}}}
VOLTAGE_REGULATOR = {'VoltageRegulator':{'prefix': 'REG_', 'section_type': 4, 'functions': POINTS}}

SERVICEPOINT = {'ServicePoint':{'prefix':'', 'section_type':13, 'functions': {**POINTS, **METERS}}}
STREETLIGHT = {'Streetlight':{'prefix': 'L', 'section_type':13,
                              'functions': {**POINTS, **LIGHTS}}}
TRANSFORMER = {'Transformer':{'prefix': 'XFMR_', 'section_type': 5,
                              'functions': {**POINTS},
                              'phase_cells':['F20', 'F21', 'F22'],
                              'init':{'table':'TRANSFORMERUNIT',
                              'f_key': lambda x: x['properties']['TransformerObjectID'],
                              'f_value': lambda x: x['properties']['RatedKVA']}}}
FUSE = {'Fuse':{'prefix':'FUS_', 'section_type':10, 'functions': {**POINTS, **FUSES},
                'f_detail':lambda x: str(x['properties']['Tag']) + ' ' + FUSE_TYPE.get(int(x['properties']['SubtypeCD']), ''),
                'phasing': phasing,
                'detail_cells':[]}}
POOLS = ThreadPool(8)
CONDUCTORS = {**PRI_OH, **PRI_UG, **BUSBAR, **SEC_UG, **SEC_OH, **SWITCH, **ELECTRIC_STATION,
              **OPEN_POINT, **DYNAMIC_PROTECTION_DEVICE, **PF_CORRECTING_EQUIPMENT, **VOLTAGE_REGULATOR,
              **SERVICEPOINT, **STREETLIGHT, **TRANSFORMER, **FUSE}

LAYER = POOLS.map(lambda x: make_layer(gdb=x[0], layer=x[1], **x[2]),
                  ((GDB, layer, initialize(GDB, **kwargs)) for layer, kwargs in CONDUCTORS.items()))
STD_FIELDS = ['SectionName', 'SectionType', 'SectionPhaseConfig', 'PriorSection',
              'MapNumber', 'Xcoord', 'Ycoord', 'UserTag',
              *['F' + str(num) for num in range(9, 53)]]

with open('STD.std', 'w') as f:
    STD = ([element.get(field, None) for field in STD_FIELDS]
           for layer in LAYER for element in layer)
    WRITER = csv.writer(f)
    WRITER.writerows(list(STD))



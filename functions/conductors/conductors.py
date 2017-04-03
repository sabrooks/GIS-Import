from collections import OrderedDict, defaultdict
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

def sub_protection(raw, out, kwargs):
    sub = {}
    feeder = raw['properties']['FeederID']
    if raw['properties'].get('SubtypeCD') == 3:
        for cell in ['F12', 'F13', 'F14', 'F15','F17']:
            sub[cell] = 1 # 1 values
        for cell in ['F9', 'F10', 'F11']:
            sub[cell] = feeder
        sub['SectionName'] = 'FDR_' + raw['properties'].get('FacilityID')
    return {**out, **sub}

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

def xfmr_phase(raw, out, kwargs):
    'Appends section phase config to output dict'
    XFMR_TYPE = {1:"NETWORK", 2:'1PH OH', 3:'1PH UG', 4:"2PH OH", 5:'2PH UG', 6:'3PH OH', 7:'3PH UG',
               8:"STEP", 9:'POWER'}
    size_phases = {cell: kwargs['detail']
              for cell, phase in zip(['F20', 'F21', 'F22'], ['A', 'B', 'C']) if phase in out['SectionPhaseConfig']}
    name_phases = {cell: str(kwargs['detail']) + ' KVA ' + XFMR_TYPE[raw['properties']['SubtypeCD']]
              for cell, phase in zip(['F25', 'F26', 'F27'], ['A', 'B', 'C']) if phase in out['SectionPhaseConfig']}
    return {**out, **size_phases, **name_phases}

def regulator_spread(raw, out, kwargs):
    phases = {cell: 'Reg_' + str(kwargs['detail']) for cell, phase in zip(['F12', 'F13', 'F14'], ['A', 'B', 'C'])}
    return {**out, **phases}

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
             'F17': lambda r, o, k: {**o, 'F17': 0} if 'F17' not in o.keys() else o,
             'sub protection': sub_protection}
CAPACITORS = {'F12-13': lambda r, o, k:{**o, 'F12':0, 'F13':0},
              'Enabled': lambda r, o, k: {**o, 'F20':r['properties']['Enabled']}}
METERS = {'section_name': lambda r, o, _: {**o, 'SectionName':str(r['properties']['AccountNumber'])},
          'F24': lambda r, o, k: {**o, 'F24': 0},
          'F23': lambda r, o, k: {**o, 'F23':1} if r['properties']['Status'] == 'A' else o}
LIGHTS = {'F234':lambda r, o, k: {**o, 'F23':1, 'F24':8}}
FUSE_TYPE = {1:'CL', 2:'EXP', 3:'UGEXP', 4:'V'}
FUSES = {'F17': lambda r, o, k: {**o, 'F17':0},
         'UserTag': lambda r, o, k: {**o, 'UserTag': r['properties']['Tag']},
         'phasing': phasing}
XFMR = {'phase_spread': xfmr_phase} 

REGULATORS = {'phase_spread': regulator_spread,
              'F10-F23': lambda r, o, k: {**o, 'F10':0, 'F23':0}}        

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
VOLTAGE_REGULATOR = {'VoltageRegulator':{'prefix': 'REG_', 'section_type': 4,
                                         'functions': {**POINTS, **REGULATORS},
                                         'init':{'table':'VOLTAGEREGULATORUNIT',
                                         'f_key': lambda x: x['properties']['VoltageRegulatorObjectID'],
                                         'f_value': lambda x: x['properties']['RatedKVA']}}}

SERVICEPOINT = {'ServicePoint':{'prefix':'', 'section_type':13, 'functions': {**POINTS, **METERS}}}
STREETLIGHT = {'Streetlight':{'prefix': 'L', 'section_type':13,
                              'functions': {**POINTS, **LIGHTS}}}

TRANSFORMER = {'Transformer':{'prefix': 'XFMR_', 'section_type': 5,
                              'functions': {**POINTS, **XFMR},
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

END_POINTS = defaultdict(list)
for layer in LAYER:
    for element in layer:
        key = (element['Xcoord'], element['Ycoord'])
        value = {'name':element['SectionName'], 'guid': element['F50'], 'type': element['geometry']['type']}
        END_POINTS[key].append(value)

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

STD_ELEMENTS = POOLS.map(lambda x: find_endpoint(x, END_POINTS), (element for layer in LAYER for element in layer))


STD_FIELDS = ['SectionName', 'SectionType', 'SectionPhaseConfig', 'PriorSection',
              'MapNumber', 'Xcoord', 'Ycoord', 'UserTag',
              *['F' + str(num) for num in range(9, 53)]]

with open('STD.std', 'w') as f:
    STD = ([element.get(field, None) for field in STD_FIELDS]
           for element in STD_ELEMENTS)
    WRITER = csv.writer(f)
    WRITER.writerows(list(STD))


with open('MPT.mpt', 'w') as f:
    MPT_ELEMENTS = (element for layer in LAYER for element in layer if element['geometry']['type'] != 'Point')
    MPT_LINES = [[element['SectionName'], x, y, element['F50']] 
                 for element in MPT_ELEMENTS for  i, (x,y) in enumerate(element['geometry']['coordinates'][0]) if i > 0]
    WRITER = csv.writer(f)
    WRITER.writerows(MPT_LINES)

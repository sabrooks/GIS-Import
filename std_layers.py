
def conductor_configuration(conductor):
    'For segments - check first, if no value, assumes "HOR" '
    try:
        return conductor['properties']['ConductorConfiguration']
    except:
        return "HOR"


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

def phasing(raw, out, kwargs):
    phases = {cell: (1 if phase in out['SectionPhaseConfig'] else 2)
              for cell, phase in zip(['F12', 'F13', 'F14'], ['A', 'B', 'C'])}
    return {**out, **phases}

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

ELEMENTS  = {**PRI_OH, **PRI_UG, **BUSBAR, **SEC_UG, **SEC_OH, **SWITCH, **ELECTRIC_STATION,
             **OPEN_POINT, **DYNAMIC_PROTECTION_DEVICE, **PF_CORRECTING_EQUIPMENT, **VOLTAGE_REGULATOR,
             **SERVICEPOINT, **STREETLIGHT, **TRANSFORMER, **FUSE}


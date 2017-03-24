'Constructor functions for point elements'
import fiona

def point_init(gdb, layer, pkey, prop):
    '''Creates initial dict for points'''
    def point_lookup(detail, pkey=pkey):
        'Creates key, value pairing'
        try:
            return detail['properties'][pkey], prop(detail)
        except:
            return None, None
        looked = (point_lookup(detail) for detail in fiona.open(gdb, layer=layer))
        return {key: value for key, value in looked if key and value}

def active_meter(raw, out, kwds):
    if raw['properties']['Status'] == 'A':
        return {**out, 'F23':1}
    else:
        return out

def fuse_phase(raw, out, kwds):
    tag = raw['properties']['Tag']
    out['UserTag'] = tag
    phasing = {cell: str(tag) +  ' ' + FUSE[raw['properties']['SubtypeCD']]
               for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
               if phase in out['SectionPhaseConfig']}
    return {**out, **phasing}


def xfmr_phase(raw, out, kwds):
    phasing = out['SectionPhaseConfig']
    tag = out['details'][raw['id']]
    tx_type = TRANSFORMER_LABELS[raw['properties']['SubtypeCD']]
    phasing = {cell: str(tag) +  'KVA' + tx_type
               for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
               if phase in out['SectionPhaseConfig']}
    return {**out, **phasing}

TRANSFORMER_LABELS = {1:"NETWORK", 2:'1PH OH', 3:'1PH UG', 4:"2PH OH", 5:'2PH UG', 6:'3PH OH', 7:'3PH UG',
               8:"STEP", 9:'POWER'}

METER_FUNCS = {'section_name': lambda raw, out, _:
                          {**out, 'section_name':str(raw['properties']['AccountNumber'])},
          'F24': lambda raw, out, kwds:
                 {**out, 'F24':0},
          'F23': active_meter}

FACILITYID = {'section_name':
              lambda raw, out, kwds:
              {**out, 'section_name': kwds['prefix'] + str(raw['properties']['FacilityID'])}}

LIGHT_FUNCS = {'F234':lambda raw, out, kwds:
                      {**out, 'F23':1, 'F24':8}}

XFMR_FUNCS = {'xfmr_phase': xfmr_phase}

POINT_FUNCS = {**FACILITYID}

FUSES = {'F17': lambda raw, out, kwds: {**out, 'F17':0},
         'phase_spread': fuse_phase}

FUSE = {'Fuse':{'prefix':'FUS_', 'section_type':10, 'funcs': POINT_FUNCS}}
SERVICEPOINT = {'ServicePoint':{'prefix':'', 'section_type':13,
                'funcs': {**POINT_FUNCS, **METER_FUNCS}}}
TRANSFORMER = {'Transformer':
               {'prefix': 'XFMR_', 'section_type': 5,
                'funcs': {**POINT_FUNCS, **XFMR_FUNCS}},
                'init': lambda gdb: point_init(gdb, 'TRANSFORMERUNIT', 'TransformerObjectID',
                                               prop=lambda x: x['properties']['RatedKVA']) }
STREETLIGHT = {'Streetlight':{'prefix': 'L', 'section_type':13,
                              'funcs': {**POINT_FUNCS, **LIGHT_FUNCS}}}
SWITCH = {'Switch':{'prefix': 'SW_', 'section_type': 6, 'funcs': POINT_FUNCS}}
VOLTAGE_REGULATOR = {'VoltageRegulator':{'prefix': 'REG_', 'section_type': 4, 'funcs': POINT_FUNCS}}
ELECTRIC_STATION = {'ElectricStation':{'prefix': '', 'section_type':9, 'funcs': POINT_FUNCS}}
DYNAMIC_PROTECTION_DEVICE = {'DynamicProtectiveDevice':
                             {'prefix': 'REC_', 'section_type':10, 'funcs': POINT_FUNCS}}
PF_CORRECTING_EQUIPMENT = {'PFCorrectingEquipment':
                           {'prefix': 'CAP_', 'section_type':2, 'funcs': POINT_FUNCS}}

POINTS = {**FUSE, **SERVICEPOINT, **TRANSFORMER, **STREETLIGHT, **SWITCH, **VOLTAGE_REGULATOR,
          **ELECTRIC_STATION, **DYNAMIC_PROTECTION_DEVICE, **PF_CORRECTING_EQUIPMENT}
    
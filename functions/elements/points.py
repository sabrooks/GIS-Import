'Constructor functions for point elements'

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

TRANSFORMER = {1:"NETWORK", 2:'1PH OH', 3:'1PH UG', 4:"2PH OH", 5:'2PH UG', 6:'3PH OH', 7:'3PH UG',
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
POINT_FUNCS = {**FACILITYID}

FUSES = {'F17': lambda raw, out, kwds: {**out, 'F17':0},
         'phase_spread': fuse_phase}

FUSE = {'Fuse':{'prefix':'FUS_', 'section_type':10, 'funcs': POINT_FUNCS}}
SERVICEPOINT = {'ServicePoint':{'prefix':'', 'section_type':13, 'funcs': {**POINT_FUNCS, **METER_FUNCS}}}
TRANSFORMER = {'Transformer':{'prefix': 'XFMR_', 'section_type': 5, 'funcs': POINT_FUNCS}}
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
    
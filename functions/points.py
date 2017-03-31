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





def xfmr_phase(raw, out, kwds):
    phasing = out['SectionPhaseConfig']
    tag = out['details'][int(raw['id'])]
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



XFMR_FUNCS = {'xfmr_phase': xfmr_phase}

POINT_FUNCS = {**FACILITYID}

FUSES = {'F17': lambda raw, out, kwds: {**out, 'F17':0},
         'phase_spread': fuse_phase}

FUSE = {'Fuse':{'prefix':'FUS_', 'section_type':10, 'funcs': POINT_FUNCS}}

TRANSFORMER = {'Transformer':
               {'prefix': 'XFMR_', 'section_type': 5,
                'funcs': {**POINT_FUNCS, **XFMR_FUNCS},
                'init': lambda gdb: {element['properties']['TransformerObjectID']: element['properties']['RatedKVA']
                          for element in fiona.open(gdb, layer='TRANSFORMERUNIT')}}}



    
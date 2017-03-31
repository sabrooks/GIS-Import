from points_general import POINT_FUNCS

METER_FUNCS = {'section_name': lambda raw, out, _:
                          {**out, 'section_name':str(raw['properties']['AccountNumber'])},
          'F24': lambda raw, out, kwds:
                 {**out, 'F24':0},
          'F23': active_meter}

def active_meter(raw, out, kwds):
    if raw['properties']['Status'] == 'A':
        return {**out, 'F23':1}
    else:
        return out


SERVICEPOINT = {'ServicePoint':{'prefix':'', 'section_type':13,
                'funcs': {**POINT_FUNCS, **METER_FUNCS}}}
from points_general import POINT_FUNCS
LIGHT_FUNCS = {'F234':lambda raw, out, kwds:
                      {**out, 'F23':1, 'F24':8}}

STREETLIGHT = {'Streetlight':{'prefix': 'L', 'section_type':13,
                              'funcs': {**POINT_FUNCS, **LIGHT_FUNCS}}}
                              
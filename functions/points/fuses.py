from points_general import POINT_FUNCS

FUSE_TYPE = {1:'CL', 2:'EXP', 3:'UGEXP', 4:"V"}

def fuse_phase(raw, out, kwds):
    tag = raw['properties']['Tag']
    out['UserTag'] = tag
    phasing = {cell: str(tag) +  ' ' + FUSE_TYPE[raw['properties']['SubtypeCD']]
               for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
               if phase in out['SectionPhaseConfig']}
    return {**out, **phasing}

FUSES_FUNC = {'F17': lambda raw, out, kwds: {**out, 'F17':0},
              'phase_spread': fuse_phase}

FUSES = {'Fuse':{'prefix':'FUS_', 'section_type':10,
                'funcs': {**POINT_FUNCS, **FUSES_FUNC}}}

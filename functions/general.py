

def get_coordinates(raw, out, kwds):
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



def get_spread_phases(raw, out, kwds):
    try:
        phasing = {cell:out['material'] for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
                   if phase in out['section_phase_config']}
        return {**out, **phasing}
    except:
        return out

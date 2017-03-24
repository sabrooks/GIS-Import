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

def get_section_phase_config(raw, out, kwds):
    'Appends section phase config to output dict'
    try:
        phase = raw['properties']['PhaseDesignation']
        section_phase_config = SECTION_PHASE[phase]
    except:
        section_phase_config = 'ABC'
    return {**out, 'SectionPhaseConfig':section_phase_config}

def get_spread_phases(raw, out, kwds):
    try:
        phasing = {cell:out['material'] for phase, cell in zip(['A', 'B', 'C'], ['F9', 'F10', 'F11'])
                   if phase in out['section_phase_config']}
        return {**out, **phasing}
    except:
        return out

def make_layer(gdb, layer, *, kwds):
    'Function calls make element on all elements in a layer'
    functions = make_function_stack(kwds)
    return [make_element(element, functions, kwds)
            for element in fiona.open(gdb, layer=layer)]
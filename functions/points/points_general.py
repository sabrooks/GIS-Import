FACILITYID = {'section_name':
              lambda raw, out, kwds:
              {**out, 'section_name': kwds['prefix'] + str(raw['properties']['FacilityID'])}}


POINT_FUNCS = {**FACILITYID}
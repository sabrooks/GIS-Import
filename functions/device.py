import fiona
from elements import make_element
#def make_devices(gdb, layer, prefix, detail, detail_join, detail_accessor, section_type):
#
#    def make_device(device, details, prefix, section_type):
#        made_element = make_element(device, section_type)
#        out = {}
#        out['SectionName'] = prefix + str(device['properties'['FacilityID']])
#
#        return {**made_element, **out}
#
#    # Make the dict of device details for lookup
#    details = fiona.open(gdb, layer=detail)
#    device_details = {: get_device_details(details)
#                      for device in details}
#
#    return [make_device(device, device_details, prefix, section_type)
#            for device in fiona.open(gdb, layer=layer)]
#
#MAKE_XFMRS = lambda gdb: make_devices(gdb, layer='Transformer',
#                                    prefix='XFMR_', detail='TRANSFORMERUNIT',
#                                    detail_join=lambda x: x['id']
#                                    detail_accessor=lambda x: x['properties']['RatedKVA'],
#                                    section_type=5)
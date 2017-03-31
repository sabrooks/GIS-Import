from points_general import POINT_FUNCS

SWITCH = {'Switch':{'prefix': 'SW_', 'section_type': 6, 'funcs': POINT_FUNCS}}
ELECTRIC_STATION = {'ElectricStation':{'prefix': '', 'section_type':9, 'funcs': POINT_FUNCS}}
DYNAMIC_PROTECTION_DEVICE = {'DynamicProtectiveDevice':
                             {'prefix': 'REC_', 'section_type':10, 'funcs': POINT_FUNCS}}
PF_CORRECTING_EQUIPMENT = {'PFCorrectingEquipment':
                           {'prefix': 'CAP_', 'section_type':2, 'funcs': POINT_FUNCS}}
VOLTAGE_REGULATOR = {'VoltageRegulator':{'prefix': 'REG_', 'section_type': 4, 'funcs': POINT_FUNCS}}

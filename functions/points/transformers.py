from functions import POINT_FUNCS, FACILITYID
import fiona

XFMR_INIT = lambda gdb: {element['properties']['TransformerObjectID']: element['properties']['RatedKVA']
                         for element in fiona.open(gdb, layer='TRANSFORMERUNIT')}


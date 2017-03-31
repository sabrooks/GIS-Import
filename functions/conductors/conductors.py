from pri_oh import PRI_OH
from pri_ug import PRI_UG
from sec_oh import SEC_OH
from sec_ug import SEC_UG
from busbar import BUSBAR


CONDUCTORS = {**PRI_OH, **PRI_UG, **SEC_OH, **SEC_UG, **BUSBAR}

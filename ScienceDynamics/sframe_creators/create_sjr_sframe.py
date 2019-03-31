import turicreate as tc
import os
import re
from configs import *

def create_sjr_sframe():
    """
    Createing the SJR SFrame from CSV files
    :note: please notice that each file name contains the SJR report year
    """
    sjr_sf = tc.SFrame()
    for p in os.listdir(DATASETS_SJR_DIR):
        if not p.endswith(".csv"):
            continue
        y = int(re.match(r'.*([1-3][0-9]{3})', p.split(os.path.sep)[-1]).group(1))
        sf = tc.SFrame.read_csv("%s/%s" % (DATASETS_SJR_DIR, p))
        sf['Year'] = y
        sf = sf.rename({"Total Docs. (%s)" % y : "Total Docs."})
        extra_cols = ["Categories"]
        for c in extra_cols:
            if c not in sf.column_names():
                sf[c] = ''
        sjr_sf = sjr_sf.append(sf)

    r_issn = re.compile('(\\d{8})')
    sjr_sf['Issn'] = sjr_sf['Issn'].apply(lambda  i: r_issn.findall(i))
    sjr_sf = sjr_sf.stack('Issn', new_column_name='ISSN')
    sjr_sf.save(SJR_SFRAME)
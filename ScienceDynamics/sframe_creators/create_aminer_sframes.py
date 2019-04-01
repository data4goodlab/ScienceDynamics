import sys

from ScienceDynamics.config.configs import AMINER_PAPERS_SFRAME, AMINER_TXT_FILES, AMINER_MAG_JOIN_SFRAME, \
    EXTENDED_PAPERS_SFRAME, SJR_SFRAME
from ScienceDynamics.config.log_config import logger

import turicreate as tc
import turicreate.aggregate as agg
import os
import re

sys.path.extend([".."])


def create_aminer_sframe():
    """
    Create AMiner Papers sFrame from the AMiner text files. After creating the SFrame, it is save to AMINER_PAPERS_SFRAME
    """
    logger.info("Creating AMiner Papers SFrame")
    if os.path.isdir(AMINER_PAPERS_SFRAME):
        return

    sf = tc.SFrame.read_json(AMINER_TXT_FILES, orient='lines')
    sf.save(AMINER_PAPERS_SFRAME)


def create_aminer_mag_links_by_doi_sframe():
    """
    Create Links Sframe that match papers from the MAG dataset with papers from the AMiner dataset based on the papers
    DOI
    :return:
    """
    if os.path.isdir(AMINER_MAG_JOIN_SFRAME):
        return
    sf = tc.load_sframe(EXTENDED_PAPERS_SFRAME)
    g1 = sf.groupby('Paper Document Object Identifier (DOI)', {'Count': agg.COUNT()})
    s1 = set(g1[g1['Count'] > 1]['Paper Document Object Identifier (DOI)'])
    sf = sf[sf['Paper Document Object Identifier (DOI)'].apply(lambda doi: doi not in s1)]
    sf.materialize()

    sf2 = tc.load_sframe(AMINER_PAPERS_SFRAME)
    g2 = sf2.groupby('doi', {'Count': agg.COUNT()})
    s2 = set(g2[g2['Count'] > 1]['doi'])
    sf2 = sf2[sf2['doi'].apply(lambda doi: doi not in s2)]
    sf2.materialize()

    j = sf.join(sf2, {'Paper Document Object Identifier (DOI)': 'doi'})
    j['title_len'] = j['title'].apply(lambda t: len(t))
    j['title_len2'] = j['Original paper title'].apply(lambda t: len(t))
    j = j[j['title_len'] > 0]
    j = j[j['title_len2'] > 0]

    j = j.rename({"Paper ID": "MAG Paper ID", "id": "Aminer Paper ID"})
    j = j.remove_columns(['title_len', 'title_len2'])
    j.save(AMINER_MAG_JOIN_SFRAME)


def create_aminer_mag_sjr_sframe(year):
    """
    Creates a unified SFrame of AMiner, MAG, and the SJR datasets
    :param year: year to use for SJR data
    :return: SFrame with AMiner, MAG, and SJR data
    :rtype: tc.SFrame
    """
    sf = tc.load_sframe(AMINER_MAG_JOIN_SFRAME)
    sf = sf[sf['issn'] != None]
    sf = sf[sf['issn'] != 'null']
    sf.materialize()
    r = re.compile(r"(\d+)-(\d+)")
    sf['issn_str'] = sf['issn'].apply(lambda i: "".join(r.findall(i)[0]) if len(r.findall(i)) > 0 else None)
    sf = sf[sf['issn_str'] != None]
    sjr_sf = tc.load_sframe(SJR_SFRAME)
    sjr_sf = sjr_sf[sjr_sf['Year'] == year]
    return sf.join(sjr_sf, on={'issn_str': "ISSN"})

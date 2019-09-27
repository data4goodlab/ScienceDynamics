from ScienceDynamics.config.configs import VenueType
import turicreate.aggregate as agg
from collections import Counter

from ScienceDynamics.sframe_creators.create_mag_sframes import get_papers_sframe


class VenuesAnalyzer(object):
    def __init__(self, min_ref_num=5, venue_type=VenueType.journal):
        self._min_ref_num = min_ref_num
        self._venue_col_name = VenuesAnalyzer._get_venue_col_name(venue_type)

    @staticmethod
    def _get_venue_col_name(venue_type):
        col_name = "Journal ID mapped to venue name"
        if venue_type == VenueType.conference:
            col_name = "Conference ID mapped to venue name"
        return col_name

    def get_venues_papers_ids(self, end_year):
        p_sf = get_papers_sframe(min_ref_num=self._min_ref_num, end_year=end_year)
        return p_sf.groupby(self._venue_col_name, {'papers_list': agg.CONCAT('Paper ID')})

    def get_venues_authors_ids(self, end_year):
        p_sf = get_papers_sframe(min_ref_num=self._min_ref_num, end_year=end_year)
        a_sf = get_authors_sframe(min_ref_num=self._min_ref_num, end_year=end_year)
        sf = a_sf.join(p_sf, on="Paper ID")

        return sf.groupby(self._venue_col_name, {'authors_list': agg.CONCAT('Author ID')})

    def get_venue_features(self, end_year):
        p_sf = self.get_venue_features(end_year=end_year)
        a_sf = self.get_venue_features(end_year=end_year)
        sf = p_sf.join(a_sf, on=self._venue_col_name)
        sf['authors_dict'] = sf['authors_list'].apply(lambda l: dict(Counter(l)))
        sf['unique_authors'] = sf['authors_dict'].apply(lambda d: len(d.keys()))
        sf['total_authors'] = sf['authors_list'].apply(lambda l: len(l))
        sf['total_papers'] = sf['papers_list'].apply(lambda l: len(l))

        return sf

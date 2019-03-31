from configs import *
from papers_collection_analyer import *
import json, os
import math


class Venue(PapersCollection):
    VENUE_FEATURES_LIST = ('papers_number', 'authors_number', 'authors_average_age', 'authors_median_age',
                           'first_authors_average_age', 'first_authors_median_age',
                           'last_authors_average_age', 'last_authors_median_age',
                           'percentage_of_papers_with_authors_that_publish_before_in_the_same_venue',
                           "percentage_of_papers_with_first_authors_that_publish_before_in_the_same_venue",
                           "percentage_of_papers_with_last_authors_that_publish_before_in_the_same_venue",
                           "first_avg_female_probability", "last_avg_female_probability", "top_keywords",
                           "papers_average_length"
                           )

    def __init__(self, venue_id=None, venue_name=None, issn_list=(), venue_type=VenueType.journal, papers_ids=None,
                 papers_list=None, papers_filter_func=None, papers_type='MAG', venue_fetcher=VENUE_FETCHER):
        """
        Create a venue object with the venue features
        :param venue_id: the venue id (optional)
        :param venue_name: the venue name (optional)
        :param issn_list: the venue issn list ((optional)
        :param venue_type: the venue type
        :param papers_ids: contains papers ids (optional)
        :param papers_ids: contains papers list
        :param papers_filter_func: filter function to filter the papers accordingly
        :param papers_type: MAG for MAG dataset papers or 'Join' for AMinerMag Datasets papers
        :param venue_fetcher: a venue fetcher object
        :note if papers_ids is None then the class will fetch the papers ids based on the input parameters
        """
        if venue_id is None and venue_name is None and len(issn_list) == 0:
            raise Exception("Cannot consturct venue venue_id, venue_name, and issn list are empty")
        logger.info(
            "Consturcting a Venue object with the following params venue_id=%s, venue_name=%s, issn_list=%s " % (
                venue_id, venue_name, issn_list))
        self._venue_id = venue_id
        self._name = venue_name
        self._venue_type = venue_type
        self._papers_type = papers_type
        if papers_ids is None and papers_list is None:
            _paper_ids_dict = venue_fetcher.get_papers_ids_dict(venue_id, venue_name, venue_type, issn_list)
            papers_ids = _paper_ids_dict['papers_ids']
            if papers_type == 'Join':
                papers_ids = _paper_ids_dict['join_papers_ids']

        if papers_list is not None:
            super(Venue, self).__init__(papers_list=papers_list, papers_filter_func=papers_filter_func)
            logger.info("Consturcted a Venue object with %s papers" % len(papers_list))
        else:
            super(Venue, self).__init__(papers_ids=papers_ids, papers_filter_func=papers_filter_func)
            logger.info("Consturcted a Venue object with %s papers" % len(papers_ids))

        if venue_name is not None or len(issn_list) > 0:
            self._sjr_features = VENUE_FETCHER.get_sjr_dict(venue_name, issn_list)
        self._issn_list = issn_list
        self._features = {}


    def _calculate_venue_features_over_time(self, features_list, start_year, end_year):
        """
        The function calcualte the venue features given in the features list
        :param features_list: list of valid venue features (see for example VENUE_FEATURES_LIST)
        :param start_year: the start year
        :param end_year: the end year
        :return: a dict with the venue features over given as input in the features_list
        """
        t = ""
        if self.venue_type is VenueType.journal:
            t = 'journal'
        if self.venue_type is VenueType.conference:
            t = 'conference'

        d = {"name": self.name, "id": self.venue_id, "issn": self._issn_list, 'papers_type': self._papers_type,
             "type": t, 'start_year': self.min_publication_year, "end_year": self.max_publication_year, 'features': {}}

        for f in features_list:
            logger.info("Calculating venue=%s feature=%s" % (self.name, f))
            d['features'][f] = self.calculate_feature_over_time(f, start_year, end_year)
        return d

    @property
    def venue_id(self):
        return self._venue_id

    @property
    def venue_type(self):
        return self._venue_type

    @property
    def name(self):
        return self._name

    @property
    def features_dict(self):
        """
        Calcualtes the venue features dict over time using the features in the VENUE_FEATURES_LIST
        :return: dict with the venue features over time
        """
        start_year = self.min_publication_year
        end_year = self.max_publication_year

        if not self._features:  # dict is empty
            self._features = self._calculate_venue_features_over_time(self.VENUE_FEATURES_LIST,
                                                                      start_year=start_year, end_year=end_year)

        return self._features


if __name__ == "__main__":
    import json
    import traceback
    min_ref_number = 5
    min_journal_papers_num = 100
    sf = VENUE_FETCHER.get_valid_venues_papers_ids_sframe_from_mag(min_ref_number=min_ref_number,
                                                                   min_journal_papers_num=min_journal_papers_num)
    sf = sf.sort("Count")
    for d in sf:
        j_id = d['Journal ID mapped to venue name']
        path = "/data/journals/%s.json" % j_id
        n = d['Journal name'].replace('ieee', 'IEEE').replace('acm', 'ACM').title()
        logger.info('Getting %s (%s) venue features' % (j_id, n))
        if os.path.isfile(path):
            continue
        try:
            papers_data_list = PAPERS_FETCHER.get_journal_papers_data(j_id)
            papers_list = [Paper(j['Paper ID'], json_data=j) for j in papers_data_list]
            papers_list = [p for p in papers_list if p.references_count >= min_ref_number ]

            logger.info('Created %s paper objects for %s venue' % (len(papers_list), j_id))
            v = Venue(venue_id=j_id, venue_name=n, papers_list=papers_list, papers_filter_func=lambda p:p.publish_year >= 2015)
            f = v.features_dict
            json.dump(f, file(path, "w"))
        except Exception, e:
            logger.error("Failed to get features of %s\n - %s\n\n%s" % (j_id, e.message, traceback.format_exc()))


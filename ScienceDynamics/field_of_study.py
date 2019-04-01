from ScienceDynamics.config.configs import FIELDS_OF_STUDY_FETCHER
from ScienceDynamics.config.log_config import logger
from ScienceDynamics.papers_collection_analyer import PapersCollection
import turicreate as tc


class FieldOfStudy(PapersCollection):
    """Calls for analyzing field of study papers """

    FIELD_FEATURES_LIST = ('papers_number', 'authors_number', 'authors_average_age', 'authors_median_age',
                           'first_authors_average_age', 'first_authors_median_age',
                           'last_authors_average_age', 'last_authors_median_age',
                           "first_avg_female_probability", "last_avg_female_probability", "top_keywords",
                           "papers_average_length"
                           )

    def __init__(self, field_id, papers_filter_func=None, field_of_study_fetcher=FIELDS_OF_STUDY_FETCHER):
        """
        Construct a FieldOfStudyAnalyzer object
        :param field_id: field of study id
        :param papers_filter_func: paper filter function
        :param field_of_study_fetcher: FieldOfStudyFetcher object (optional)
        """
        self._id = field_id
        self._field_of_study_fetcher = field_of_study_fetcher
        self._name = self._field_of_study_fetcher.get_field_name(field_id)
        self._level = self._field_of_study_fetcher.get_field_level(field_id)

        paper_ids = self._field_of_study_fetcher.get_field_paper_ids(field_id)

        super(FieldOfStudy, self).__init__(papers_ids=paper_ids, papers_filter_func=papers_filter_func)
        if len(self.papers_ids) > self.MAX_PAPERS:
            logger.warn(
                "There are high number of papers -- %s -- in field %s (%s) , please consider to use better filter func for optimal results" % (
                    self.papers_number, self._name, field_id))

    def features_dict(self, cited_max_year=2015, add_field_features_over_time=False):
        """
        Get's field features as dict object which includes the field meta information including the most cited papers
         in each year
        :param add_field_features_over_time:
        :param cited_max_year:
        :return: dict with the field of study information including the most cited papers in each year
        :rtype: dict
        """
        start_year = self.min_publication_year
        end_year = self.max_publication_year
        d = {"field_id": self._id, "name": self.name, "level": self.level, "papers_number": len(self.papers_ids),
             "start_year": start_year, "end_year": end_year, "features": {}}
        p = self.max_citations_paper(self.max_publication_year, include_self_citations=True)
        d["max_cited_paper"] = {"year": p.publish_year, "title": p.title,
                                "citation_number": p.total_citations_number_by_year(cited_max_year,
                                                                                    include_self_citation=True),
                                "venue_name": p.venue_name,
                                "venue_tyoe": str(p.venue_type)}

        if add_field_features_over_time:
            for f in self.FIELD_FEATURES_LIST:
                d["features"][f] = self.calculate_feature_over_time(f, start_year, end_year)

        return d

    def print_fields_features(self):
        d = self.features_dict()
        print(f"Field ID {d['field_id']}: ")
        print(f"Field Name {d['name']}: ")
        print(f"Field Level {d['level']}: ")
        print(f"Field Papers Number {d['papers_number']}")
        sf = tc.SFrame(d["yearly_most_cited_papers"])
        sf = sf.sort("year", ascending=False)
        sf.print_rows(len(sf))

    @property
    def name(self):
        return self._name

    @property
    def level(self):
        return self._level

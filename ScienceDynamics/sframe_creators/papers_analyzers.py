import turicreate as tc
import turicreate.aggregate as agg

from ScienceDynamics.configs import PAPERS_ORDERED_AUTHORS_LIST_SFRAME, PAPER_REFERENCES_SFRAME, PAPER_KEYWORDS_SFRAME, \
    JOURNALS_DETAILS_SFRAME, logger
from ScienceDynamics.sframe_creators.create_mag_sframes import get_papers_sframe


class PapersAnalyzer(object):
    """
    Creates papers features using SFrame object
    """

    def __init__(self, start_year, end_year, min_ref_num=5):
        self._papers_sf = get_papers_sframe(min_ref_num=min_ref_num, start_year=start_year, end_year=end_year)

    def papers_add_features(self):
        """Add paper fetures """
        self._add_authors_features()
        self._add_references_count()
        self._add_title_tf_ids()
        self._add_title_bag_of_words()
        self._add_keywords()
        self._add_fields_of_study()

    def _add_authors_features(self):
        """  Update papers SFrame with the number of authors and a list of authors sorted by author's order
        """
        logger.info("Adding authors info")
        g = tc.load_sframe(PAPERS_ORDERED_AUTHORS_LIST_SFRAME)
        self._papers_sf = self._papers_sf.join(g, how="left")
        self._papers_sf['Authors Number'] = self._papers_sf['Authors List Sorted'].apply(lambda l: len(l))

    def _add_references_count(self):
        """
        Update paper's references count
        """
        logger.info("Adding references info")
        papers_refrences_sf = tc.load_sframe(PAPER_REFERENCES_SFRAME)
        ref_count_sf = papers_refrences_sf.groupby("Paper ID", {"References Count": agg.COUNT()})
        self._papers_sf = self._papers_sf.join(ref_count_sf, on="Paper ID", how="left")

    def _add_title_tf_ids(self):
        """
        Add title TF-IDF
        """
        logger.info("Adding title TF-IDS")
        self._papers_sf["Title Tf-Idf"] = self._papers_sf["Original paper title"].apply(lambda t: t.lower())
        self._papers_sf['Title Tf-Idf'] = tc.text_analytics.tf_idf(self._papers_sf["Title Tf-Idf"])
        self._papers_sf['Title Tf-Idf'] = self._papers_sf['Title Tf-Idf'].dict_trim_by_keys(
            tc.text_analytics.stop_words(), True)

    def _add_title_bag_of_words(self):
        """
        Add title bag of word
        """
        logger.info("Adding title Bag of Words")
        self._papers_sf["Title Bag of Words"] = tc.text_analytics.count_ngrams(self._papers_sf["Original paper title"],
                                                                               1)
        self._papers_sf["Title Bag of Words"] = self._papers_sf["Title Bag of Words"].dict_trim_by_keys(
            tc.text_analytics.stop_words(), True)

    def _add_keywords(self):
        """
        Add papers_keywords
        """
        logger.info("Adding keywords")
        k_sf = tc.load_sframe(PAPER_KEYWORDS_SFRAME)
        g = k_sf.groupby("Paper ID", {"Keywords List": tc.aggregate.CONCAT("Keyword name")})
        self._papers_sf = self._papers_sf.join(g, how="left")

    def _add_journal_details(self):
        """
        Add the journal details JSR if the journal original name match a journal name on JSR
        :return:
        """
        logger.info('Adding journal details')
        j_sf = tc.load_sframe(JOURNALS_DETAILS_SFRAME)
        j_sf['Title'] = j_sf['Title'].apply(lambda t: t.lower())
        j_sf['Year'] = j_sf['Year'].astype(int)
        self._papers_sf['Original venue name'] = self._papers_sf['Original venue name'].apply(lambda s: s.lower())
        sf = self._papers_sf.join(j_sf, how='left', on={'Original venue name': 'Title', 'Paper publish year': 'Year'})
        return sf

    def _add_fields_of_study(self):
        g = self.get_paper_fields_of_study()

    def _add_citation_number(self):
        """
        Add the paper's total citation number
        """
        sf = tc.load_sframe(PAPER_REFERENCES_SFRAME)
        g = sf.groupby("Paper reference ID", {"Citation Number": agg.COUNT()})
        g.rename({"Paper reference ID": "Paper ID"})
        self._papers_sf = self._papers_sf.join(g, on="Paper Id", how="left")
        self._papers_sf = self._papers_sf.fillna("Citation Number", 0)

    def get_papers_basic_features(self, venues_set=None):
        sf = self._papers_sf
        if venues_set is not None:
            sf['filter'] = sf.apply(lambda r: r['Journal ID mapped to venue name'] in venues_set or
                                              r['Conference ID mapped to venue name'] in venues_set)
            sf = sf[sf['filter']]
            sf.remove_column('filter')
        # client = MongoClient('mongodb://%s:%s@127.0.0.1' % (MONGO_USER, MONGO_PASSWORD))
        basic_features = ['Paper ID', 'Journal ID mapped to venue name', 'Conference ID mapped to venue name',
                          'Ref Count', 'Authors Number', 'Title Bag of Words', 'Keywords List']
        return sf[basic_features]

    def filter_papers(self, min_reference_count=5):
        """
        Filter paper with number of reference lower the min_reference_count
        :param min_reference_count: minimal references count
        :return: filter SFrame without paper with too few references
        :rtype: tc.SFrame
        """
        sf = self._papers_sf[self._papers_sf["References Count"] >= min_reference_count]
        sf = sf[sf['Paper Document Object Identifier (DOI)'] != '']
        return sf

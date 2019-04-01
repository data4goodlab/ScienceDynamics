import os

from ScienceDynamics.config.configs import VenueType, JOURNALS_PAPERS_SFRAMES_DIR, CONFERENCES_PAPERS_SFRAMES_DIR, \
    JOURNAL_AUTHORS_ACADEMIC_BIRTHYEAR_PKL, CONFERENCE_AUTHORS_ACADEMIC_BIRTHYEAR_PKL, FIELDS_OF_STUDY_SFRAME, \
    FIELDS_OF_STUDY_HIERARCHY_SFRAME, PAPERS_SFRAME, EXTENDED_PAPERS_SFRAME, PAPER_AUTHOR_AFFILIATIONS_SFRAME, \
    PAPER_KEYWORDS_SFRAME, PAPER_REFERENCES_SFRAME, CO_AUTHORSHIP_LINK_SFRAME, L3_FIELD_PAPERS_LIST_SFRAME, \
    JOURNALS_SFRAME, CONFERENCES_SAME
from ScienceDynamics.config.log_config import logger
from ScienceDynamics.utils import filter_sframe_by_func
import itertools
from collections import Counter
import pickle
import numpy as np
import json
from datetime import datetime
import turicreate as tc
import turicreate.aggregate as agg


class VenueAnalyzer(object):
    def __init__(self, venue_id, venue_type=VenueType.journal, academic_birthday_dict=None):
        """
        Construct a VenueAnalyzer object
        :param venue_id: the venue ID as appear in Microsoft Academic Graph dataset
        :param venue_type: the venue type of VenueType
        @type venue_type: VenueType
        :param academic_birthday_dict: dict with all the authors academic birthdays (the year in which they publish their
        first paper)
        """

        self._venue_id = venue_id
        self._venue_type = venue_type
        self._name = self._get_venue_name()
        self._all_papers_sf = self._get_all_papers_sframe()
        self._academic_birthyear_dict = academic_birthday_dict
        self._l3_papers_dict = None
        self._co_authors_links = None

    def _get_venue_name(self):
        """
        Return the venue full name
        :return: string with the venue full name
        :rtype: str
        """
        if self.venue_type == VenueType.journal:
            sf = self.journals_sframe
            sf = sf[sf["Journal ID"] == self.venue_id]
            if len(sf) != 0:
                return sf[0]["Journal name"]
        elif self.venue_type == VenueType.conference:
            sf = self.confrences_sframe
            sf = sf[sf["Conference ID"] == self.venue_id]
            if len(sf) != 0:
                return sf[0]["Full Name"]
        return None

    def _get_all_papers_sframe(self):
        """
        Return SFrame with all the papers published in the venue
        :return: Papers SFrame with all the papers details that were published in the venue
        :rtype tc.SFrame
        @note: The SFrame object was created by academic_parser.create_venue_papers_sframe
        """
        if self.venue_type == VenueType.journal:
            return tc.load_sframe("%s/%s.sframe" % (JOURNALS_PAPERS_SFRAMES_DIR, self._venue_id))
        elif self.venue_type == VenueType.conference:
            return tc.load_sframe("%s/%s.sframe" % (CONFERENCES_PAPERS_SFRAMES_DIR, self._venue_id))

    def _get_papers_sframe(self, filter_func=None):
        """
        Filter all the papers according to the filter function and return filtered Papers SFrame object
        :param filter_func: filter function
        :return: Filtered Papers SFrame object
        :rtype: tc.SFrame
        """
        if filter_func is None:
            return self._all_papers_sf
        return filter_sframe_by_func(self._all_papers_sf, filter_func)

    def get_papers_sframe_by_year(self, start_year, end_year):
        """
        Get venue papers between input years
        :param start_year: start year
        :param end_year: end year
        :return: SFrame with all the papers between the input years
        :rtype: tc.SFrame
        @note: the start_year/end_year can be equal None
        """
        f = None
        if start_year is None and end_year is None:
            return self._all_papers_sf
        elif start_year is not None and end_year is not None:
            f = lambda r: end_year >= r['Paper publish year'] >= start_year
        elif end_year is None:
            f = lambda r: r['Paper publish year'] >= start_year
        elif start_year is None:
            f = lambda r: end_year >= r['Paper publish year']

        return self._get_papers_sframe(f)

    def get_papers_ids_set(self, start_year=None, end_year=None):
        """ Returns all the venue papers ids between years
        :param start_year: start year
        :param end_year:  end year
        :return: set with all papers ids between the input years
        :rtype: Set()
        """
        sf = self.get_papers_sframe_by_year(start_year, end_year)
        return set(sf["Paper ID"])

    def get_venue_authors_sframe(self, start_year=None, end_year=None):
        """
        Returns a SFrame object with all the venue's authors details who publish papers in the venue between the
         input years
        :param start_year: start year
        :param end_year: end year
        :return: SFrame with the authors details
        :rtype: tc.SFrame
        """
        sf = self.paper_author_affiliations_sframe
        p_ids = self.get_papers_ids_set(start_year, end_year)
        return sf[sf['Paper ID'].apply(lambda pid: pid in p_ids)]

    def get_venue_authors_ids_list(self, start_year=None, end_year=None, authors_seq_list=None):
        """
        Returns a list with all the author ids that publish in the venue between the input years.
        :param start_year: start year
        :param end_year: end year
        :param authors_seq_list: author sequence in the paper's authors list. For example, authors_seq_list=[0] will return
        only the authors ids who where the first authors, while authors_seq_list=[-1] will return only the authors ids
         who were the last authors.
        :return: list of authors ids
        :rtype: list
        @note: an author id can appear multiple times, each time for each paper the author publish in the venue
        """
        sf = self.get_papers_sframe_by_year(start_year, end_year)
        if authors_seq_list is None:
            selected_authors_list = sf["Authors List Sorted"]
        else:
            selected_authors_list = sf["Authors List Sorted"].apply(lambda l: [l[i] for i in authors_seq_list])
        return list(itertools.chain.from_iterable(selected_authors_list))

    def get_venue_authors_affiliations_list(self, start_year=None, end_year=None):
        """
        Returns a list of venue authors' affiliations
        :param start_year: start year
        :param end_year: end year
        :return: a list of venue authors' affiliations with repeats
        :rtype: list
        """
        sf = self.get_venue_authors_sframe(start_year, end_year)
        return list(sf["Normalized affiliation name"])

    def get_authors_papers_count(self):
        """
        Calculate the number of papers each author published in the venue
        :return: Counter object in which keys are the venue's author ids and the values are the number of times
         each author published a paper in the venue
        :rtype: Counter
        """
        l = self.get_venue_authors_ids_list()
        return Counter(l)

    def get_percentage_of_new_authors(self, year):
        """
        Get the perecentage of new authors that publish paper's in the venue in specific year
        :param year: year
        :return: returns percentage of new authors, and the total number of authors in a specific year as a tuple
        :rtyoe: dict with the new authrors percentage and total authors value
        """
        s1 = set(self.get_venue_authors_ids_list(start_year=self.min_year, end_year=year - 1))
        s2 = set(self.get_venue_authors_ids_list(start_year=year, end_year=year))
        if len(s2) == 0:
            return None
        return {'new_authors_percentage': len(s2 - s1) / float(len(s2)), 'total_authors': len(s2)}

    def get_percentage_of_new_authors_over_time(self):
        """
        Get the percentage of new authors by year
        :return: a dict with the percentage of new authors in each year, and the total number of authors in each year
        :rtyoe: dict
        """
        return {i: self.get_percentage_of_new_authors(i) for i in range(self.min_year + 1, self.max_year + 1)}

    def get_percentage_papers_by_new_authors(self, year, authors_seq_list):
        """
        Get the percentage of new authors, in specific sequence,  in specific year
        :param year: year
        :param authors_seq_list: authors sequence list
        :return: the percentage of new authors in specific sequence, and the number of new papers in the year
        :rtyoe: dict with the percentage of new authors and the total number of new papers
        """
        all_previous_authors_set = set(self.get_venue_authors_ids_list(start_year=self.min_year, end_year=year - 1))
        year_papers_sf = self.get_papers_sframe_by_year(year, year)
        if len(year_papers_sf) == 0:
            return None
        if authors_seq_list is None:
            year_papers_sf["Selected Authors"] = year_papers_sf["Authors List Sorted"]
        else:
            year_papers_sf["Selected Authors"] = year_papers_sf["Authors List Sorted"].apply(
                lambda l: [l[i] for i in authors_seq_list])

        year_papers_sf['New Paper'] = year_papers_sf["Selected Authors"].apply(
            lambda l: 1 if len(set(l) & all_previous_authors_set) == 0 else 0)

        return {"new_authors_papers_percentage": year_papers_sf['New Paper'].sum() / float(len(year_papers_sf)),
                "total_papers": len(year_papers_sf)}

    def get_yearly_percentage_of_papers_with_new_authors_dict(self, authors_seq_list):
        return {i: self.get_percentage_papers_by_new_authors(i, authors_seq_list) for i in
                range(self.min_year + 1, self.max_year + 1)}

    def get_venue_median_number_of_authors_by_year(self):
        sf = self._all_papers_sf.groupby("Paper publish year", {'Authors Number List': agg.CONCAT("Authors Number")})
        return {r["Paper publish year"]: np.median(r['Authors Number List']) for r in sf}

    def get_number_of_papers_by_year(self):
        sf = self._all_papers_sf.groupby("Paper publish year", {"Count": agg.COUNT()})
        return {r["Paper publish year"]: r["Count"] for r in sf}

    def average_and_median_academic_age(self, year, authors_seq_list):
        """
        Calculate venue authors average/median academic ages, i.e. number of years since the year the published their first paper,
         in specific year
        :param year: year
        :param authors_seq_list: authors sequence
        :return: dict with the average and median academic age values
        """
        authors_list = self.get_venue_authors_ids_list(year, year, authors_seq_list)
        # remove papers with too many authors
        academic_birthyears_list = [year - self.authors_academic_birthyear_dict[a] for a in authors_list if
                                    a in self.authors_academic_birthyear_dict]
        if len(academic_birthyears_list) == 0:
            return {'average': 0, 'median': 0}
        return {'average': np.average(academic_birthyears_list), 'median': np.median(academic_birthyears_list)}

    def get_average_and_median_academic_age_dict(self, authors_seq_list=None):
        return {i: self.average_and_median_academic_age(i, authors_seq_list) for i in
                range(self.min_year + 1, self.max_year + 1)}

    def get_authors_publications_number_in_year_range(self, authors_set, start_year, end_year, authors_seq=None):
        d = {}

        for y in range(start_year, end_year + 1):
            p_sf = self.get_papers_sframe_by_year(y, y)
            if authors_seq is not None:
                p_sf['Selected Authors'] = p_sf["Authors List Sorted"].apply(lambda l: [l[i] for i in authors_seq])
            else:
                p_sf['Selected Authors'] = p_sf["Authors List Sorted"]
            p_sf['published'] = p_sf['Selected Authors'].apply(lambda l: 1 if len(set(l) & authors_set) > 0 else 0)
            d[y] = p_sf['published'].sum()
        return d

    def get_venue_stats(self):
        features_dict = {"name": self.name, "id": self.venue_id,
                         "min_year": self._all_papers_sf['Paper publish year'].min(),
                         "max_year": self._all_papers_sf['Paper publish year'].max(),
                         "total_authors_number": len(set(self.get_venue_authors_ids_list())),
                         "total_papers_number": len(self.get_papers_ids_set()),
                         "percentage_of_papers_with_all_new_authors": self.get_yearly_percentage_of_papers_with_new_authors_dict(
                             None),
                         "percentage_of_papers_new_first_authors": self.get_yearly_percentage_of_papers_with_new_authors_dict(
                             [0]),
                         "percentage_of_papers_new_last_authors": self.get_yearly_percentage_of_papers_with_new_authors_dict(
                             [-1]),
                         "percentage_of_papers_new_first_and_last_authors": self.get_yearly_percentage_of_papers_with_new_authors_dict(
                             [0, -1]),
                         "avg_median_academic_age_first_authors": self.get_average_and_median_academic_age_dict([0]),
                         "avg_median_academic_age_last_authors": self.get_average_and_median_academic_age_dict([-1]),
                         "avg_median_academic_age_all_authors": self.get_average_and_median_academic_age_dict(None),
                         "median_number_of_authors_by_year": self.get_venue_median_number_of_authors_by_year()}
        return features_dict

    def update_venue_stats(self):
        j = json.load(open(f"/data/json/journals/{self.name} ({self.venue_id}).json", "r"))
        logger.info(f"update features of {self.name}")
        j["median_number_of_authors_by_year"] = self.get_venue_median_number_of_authors_by_year()
        j["number_of_papers_in_a_year"] = self.get_number_of_papers_by_year()
        json.dump(j, open(f"/data/json/journals/{self.name} ({self.venue_id}).json", "w"))

    @property
    def name(self):
        return self._name

    @property
    def venue_id(self):
        return self._venue_id

    @property
    def venue_type(self):
        return self._venue_type

    @property
    def min_year(self):
        return self._all_papers_sf['Paper publish year'].min()

    @property
    def max_year(self):
        return self._all_papers_sf['Paper publish year'].max()

    @property
    def papers_with_new_first_authors_dict(self):
        return self.get_yearly_percentage_of_papers_with_new_authors_dict([0])

    @property
    def papers_with_new_last_authors_dict(self):
        return self.get_yearly_percentage_of_papers_with_new_authors_dict([-1])

    @property
    def authors_academic_birthyear_dict(self):
        if self._academic_birthyear_dict is not None:
            return self._academic_birthyear_dict

        if self.venue_type == VenueType.journal:
            p = JOURNAL_AUTHORS_ACADEMIC_BIRTHYEAR_PKL
        else:
            p = CONFERENCE_AUTHORS_ACADEMIC_BIRTHYEAR_PKL
        d = pickle.load(open(p, "rb"))
        self._academic_birthyear_dict = d

        return self._academic_birthyear_dict

    def get_venue_authors_timeseries(self):

        p = self._all_papers_sf["Paper ID", "Paper publish year"]
        a = self.authors_affilations_sframe["Paper ID", "Author ID"]
        sf = p.join(a, on="Paper ID")["Author ID", "Paper publish year"]
        sf = sf.groupby("Author ID", {"mindate": agg.MIN("Paper publish year"),
                                      "maxdate": agg.MAX("Paper publish year")})
        sf.rename({"Author ID": "v_id"})
        sf["mindate"] = sf["mindate"].apply(lambda y: datetime(year=y, month=1, day=1))
        sf["maxdate"] = sf["maxdate"].apply(lambda y: datetime(year=y, month=1, day=1))

        if sf.num_rows() == 0:
            return None

        return tc.TimeSeries(sf, index="mindate")

    def get_venue_authors_links_timeseries(self):
        a = self.authors_affilations_sframe["Paper ID", "Author ID"]

        a = self._all_papers_sf.join(a, on="Paper ID")
        a = a['datetime', 'Author ID', 'Paper publish year', 'Paper ID']
        links_sf = a.join(a, on="Paper ID")
        p = self.papers_sframe["Paper ID", "Paper publish year"]

        links_sf.rename({'Author ID': 'src_id', 'Author ID.1': 'dst_id'})
        links_sf = links_sf["src_id", "dst_id", "datetime"]
        links_sf = links_sf[links_sf["src_id"] != links_sf[
            "dst_id"]]  # because this is a direct network we keep for each link both (u,v) and (v,u)
        return tc.TimeSeries(links_sf, index="datetime")

    def create_timeseries(self, outpath):
        v_ts = self.get_venue_authors_timeseries()
        v_ts.save(f"{outpath}/{self._venue_id}.vertices.timeseries")
        i_ts = self.get_venue_authors_links_timeseries()
        i_ts.save(f"{outpath}/{self._venue_id}.interactions.timeseries")

    # -------------------------#
    #   SFrame Properties     #
    # -------------------------#
    @property
    def fields_of_study_sframe(self):
        if os.path.isdir(FIELDS_OF_STUDY_SFRAME):
            return tc.load_sframe(FIELDS_OF_STUDY_SFRAME)
        return tc.load_sframe(FIELDS_OF_STUDY_S3_SFRAME)

    @property
    def fields_of_study_hierarchy_sframe(self):
        if os.path.isdir(FIELDS_OF_STUDY_HIERARCHY_SFRAME):
            return tc.load_sframe(FIELDS_OF_STUDY_HIERARCHY_SFRAME)
        return tc.load_sframe(FIELDS_OF_STUDY_HIERARCHY_S3_SFRAME)

    @property
    def papers_sframe(self):
        if os.path.isdir(PAPERS_SFRAME):
            return tc.load_sframe(PAPERS_SFRAME)
        return tc.load_sframe(PAPERS_S3_SFRAME)

    @property
    def extended_papers_sframe(self):
        if os.path.isdir(EXTENDED_PAPERS_SFRAME):
            return tc.load_sframe(EXTENDED_PAPERS_SFRAME)
        return tc.load_sframe(EXTENDED_PAPERS_S3_SFRAME)

    @property
    def paper_author_affiliations_sframe(self):
        if os.path.isdir(PAPER_AUTHOR_AFFILIATIONS_SFRAME):
            return tc.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)
        return tc.load_sframe(PAPER_AUTHOR_AFFILIATIONS_S3_SFRAME)

    @property
    def paper_keywords_sframe(self):
        if os.path.isdir(PAPER_KEYWORDS_SFRAME):
            return tc.load_sframe(PAPER_KEYWORDS_SFRAME)
        return tc.load_sframe(PAPER_KEYWORDS_S3_SFRAME)

    @property
    def paper_references_sframe(self):
        if os.path.isdir(PAPER_REFERENCES_SFRAME):
            return tc.load_sframe(PAPER_REFERENCES_SFRAME)
        return tc.load_sframe(PAPER_REFERENCES_S3_SFRAME)

    @property
    def authors_affilations_sframe(self):
        if os.path.isdir(PAPER_AUTHOR_AFFILIATIONS_SFRAME):
            return tc.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)
        return tc.load_sframe(PAPER_AUTHOR_AFFILIATIONS_S3_SFRAME)

    @property
    def coauthors_links_sframe(self):
        if self._co_authors_links is not None:
            return self._co_authors_links
        if os.path.isdir(CO_AUTHORSHIP_LINK_SFRAME):
            self._co_authors_links = tc.load_sframe(CO_AUTHORSHIP_LINK_SFRAME)
        else:
            self._co_authors_links = tc.load_sframe(CO_AUTHORSHIP_LINK_S3_SFRAME)
        return self._co_authors_links

    @property
    def l3_field_papers_sframe(self):
        if os.path.isdir(L3_FIELD_PAPERS_LIST_SFRAME):
            return tc.load_sframe(L3_FIELD_PAPERS_LIST_SFRAME)
        return tc.load_sframe(L3_FIELD_PAPERS_LIST_S3_SFRAME)

    @property
    def journals_sframe(self):
        if os.path.isdir(JOURNALS_SFRAME):
            return tc.load_sframe(JOURNALS_SFRAME)
        return tc.load_sframe(JOURNALS_S3_SFRAME)

    @property
    def confrences_sframe(self):
        if os.path.isdir(CONFERENCES_SAME):
            return tc.load_sframe(CONFERENCES_SAME)
        return tc.load_sframe(CONFRENCES_S3_SFRAME)

    @property
    def l3_papers_dict(self):
        if self._l3_papers_dict is None:
            sf = self.l3_field_papers_sframe
            self._l3_papers_dict = {r["Field of study ID"]: r["Papers List"] for r in sf}
        return self._l3_papers_dict


def update_journals_features():
    for i in os.listdir("/data/sframes/journals"):
        try:
            logger.info(f"Updating {i}")
            jid = i.split(".sframe")[0]
            va = VenueAnalyzer(jid, VenueType.journal, None)
            va.update_venue_stats()
        except Exception as e:
            print(e.message)
            logger.error(e.message)


def get_all_journals_features():
    academic_birthyear_dict = pickle.load(open(JOURNAL_AUTHORS_ACADEMIC_BIRTHYEAR_PKL, "rb"))
    for i in os.listdir("/data/sframes/journals"):
        logger.info(f"Analyzing {i}")
        try:
            jid = i.split(".sframe")[0]
            va = VenueAnalyzer(jid, VenueType.journal, academic_birthyear_dict)
            j = va.get_venue_stats()
            json.dump(j, open(f"/data/json/journals/{va.name} ({va.venue_id}).json", "w"))
        except Exception as e:
            print(e.message)
            logger.error(e.message)


def create_all_timeseries():
    for i in os.listdir("/data/sframes/journals"):
        jid = i.split(".sframe")[0]
        print(f"Createing {jid} timeseries")
        va = VenueAnalyzer(jid, VenueType.journal, None)
        p = f"/data/timeseries/journals/{jid}"
        if os.path.isdir(p):
            continue
        os.mkdir(p)
        va.create_timeseries(p)


if __name__ == "__main__":
    va = VenueAnalyzer("08364228")  # Nature 08364228 Science 003B355D PNAS 077EDC2F

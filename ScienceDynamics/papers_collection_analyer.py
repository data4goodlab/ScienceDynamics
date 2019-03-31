import itertools
import math
import random
from collections import Counter
from functools import lru_cache

import numpy as np
import turicreate as tc

from ScienceDynamics.authors_list_analyzer import AuthorsListAnalyzer
from ScienceDynamics.configs import AUTHORS_FETCHER, PAPERS_FETCHER, VenueType, logger
from ScienceDynamics.paper import Paper


class PapersCollection(object):
    MAX_PAPERS = 500000

    def __init__(self, papers_ids=None, papers_list=None, papers_filter_func=None, papers_fetcher=PAPERS_FETCHER,
                 authors_fetcher=AUTHORS_FETCHER):
        """
        Consturct a paper collection object using a list of paper ids or a list of Paper object
        :param papers_ids: papers ids list
        :param papers_list: Paper object list (optional)
        :param papers_filter_func:  a filter function to filter the papers. For example, the filter fucntion
            "lambda p: p.reference_count < 5" will filter out papeprs with less than 5 references (optional)
        :param papers_fetcher: a PapersFetcher object (optional)
        :param authors_fetcher:  an AuthorsFetcher object (optional)
        """
        self._authors_fetcher = authors_fetcher
        self._papers_fetcher = papers_fetcher

        if papers_list is None:
            papers_list = []
        self.__papers_list = papers_list  # type: list[Paper]
        self.__papers_ids = papers_ids  # type: list[str]
        self._min_year = None
        self._max_year = None

        if papers_ids is None and len(papers_list) > 0:
            self.__papers_ids = [p.paper_id for p in papers_list]
        if papers_filter_func is not None:
            self.__filter_papers(papers_filter_func)
        if len(self.__papers_list) > self.MAX_PAPERS:
            logger.warn(
                "PapersCollection contains over maximal number of papers %s.\n Randomly selecting %s papers\b" % (
                    len(self.__papers_list), self.MAX_PAPERS))
            self.__randomly_select_papers(self.MAX_PAPERS)

    def __filter_papers(self, filter_func=lambda p: p):
        """
        Filtering the papers according to the filter func
        :param filter_func: input filter function, all papers in the collection in which filter_func(p) == True will be
         filtered
        :note the function update both the self.__papers_list and the self.__papers_ids vars
        :warning: due to caching issues calling this function outside the the class constructor can have
        unexcpected reults
        """
        self.__papers_list = [p for p in self.papers_list if not filter_func(p)]
        self.__papers_ids = [p.paper_id for p in self.__papers_list]

    def __randomly_select_papers(self, n):
        """
        Randomly select n papers
        :param n: number of paper to select
        :warning: due to caching issues calling this function outside the the class constructor can have
        unexcpected reults
        """
        self.__papers_list = random.shuffle(self.__papers_list)[:n]
        self.__papers_ids = [p.paper_id for p in self.__papers_list]

    def first_authors_list(self, year):
        """
        Get papers' first authors list in a specific year
        :param year: year
        :return: a list of first authors
        :rtyoe: list<Author>
        """
        return [p.first_author for p in self.papers_published_in_year_list(year)]

    def last_authors_list(self, year):
        """
        Get papers' last authors list in a specific year
        :param year: year
        :return: a list of last authors
        :rtyoe: list<Author>
        """
        return [p.last_author for p in self.papers_published_in_year_list(year)]

    @lru_cache(maxsize=100)
    def all_authors_in_year_list(self, year):
        """
        Get authors list of papers that were published in a specific year
        :param year: year
        :return: a list of all authors
        :rtyoe: list<Author>
        """
        l = [p.authors_list for p in self.papers_published_in_year_list(year)]
        return list(itertools.chain.from_iterable(l))

    @lru_cache(maxsize=100)
    def papers_published_in_year_list(self, year):
        """
        Return papers list  of papers in collection that were published in specific year
        :param year:  input year
        :return: list of Papers that were published in the input year
        :rtype: list<Paper>
        """
        return [p for p in self.papers_list if p.publish_year == year]

    @lru_cache(maxsize=100)
    def papers_between_years_list(self, start_year=None, end_year=None):
        """
        Return papers list  of papers in collection that were published in year range
        :param start_year: start year
        :param end_year: end year
        :return: list of Papers that were published between start_year and end_year
        :rtype: list<Paper>
        """
        if start_year is None:
            start_year = 0
        if end_year is None:
            end_year = float("inf")

        return [p for p in self.papers_list if end_year >= p.publish_year >= start_year]

    def papers_ranks_list(self, year):
        """
        Return list of collection's papers ranks in input year
        :param year: input year
        :return: list of collection ranks
        :rtype: list<int>
        """
        return [p.rank() for p in self.papers_published_in_year_list(year)]

    def papers_length_list(self, year):
        """
        Return list of collection's papers length in input year
        :param year: input year
        :return: list of collection ranks
        :rtype: list<int>
        """
        return [p.paper_length for p in self.papers_published_in_year_list(year) if p.paper_length is not None]

    def papers_total_citations_after_years(self, publication_year, after_years, include_self_citations):
        """
        Return the total citations of collection's papers that were published in the input publication after after_years
        :param publication_year: a publication year
        :param after_years: year after publication
        :param include_self_citations: if True include self citation otherwise don't include self citations
        :return: the total number of citation of papers  that were published in published_years after
            after_years
        :rtype: float
        """
        return sum([i[1] for i in
                    self.papers_citations_after_years_list(publication_year, after_years, include_self_citations)])

    def paper_with_max_citation_after_years(self, publication_year, after_years, include_self_citations):
        l = self.papers_citations_after_years_list(publication_year, after_years, include_self_citations)
        l = sorted(l, key=lambda x: x[1], reverse=True)
        return l[0]

    @lru_cache(maxsize=100)
    def papers_citations_after_years_list(self, publication_year, after_years, include_self_citations):
        """
        Return the list with the total citations of collection's papers that were published in the input publication
        after after_years
        :param publication_year: a publication year
        :param after_years: year after publication
        :param include_self_citations: if True include self citation otherwise don't include self citations
        :return: List of the total number of citation of papers that were published in published_years after
            after_years
        :rtype: list<Paper,int>
        """
        l = self.papers_published_in_year_list(publication_year)
        return [
            (p, p.total_citation_number_after_years_from_publication(after_years, include_self_citations)) for p in l]

    def papers_total_citations_in_year(self, year, include_self_citations):
        """
        Returns the papers' total number of citations in a specfici year
        :param year: year
        :param include_self_citations: if True include self citation otherwise don't include self citations
        :return: the total number of papers' citations in a specific year
        :rtype: int
        """
        l = self.papers_between_years_list(None, year)
        return sum([p.get_total_citations_number_in_year(year, include_self_citations) for p in l])

    def get_yearly_most_cited_papers_sframe(self, citation_after_year, max_publish_year):
        """
        Returns SFrame, with the most cited in each year papers details
        :param max_publish_year:
        :param citation_after_year: number of years to check the number of citations after paper publication year
        :param: max_publish_year: the maximal publish year
        :return: SFrame with the most cited paper details in each year
        :rtype: tc.SFrame
        """
        m = {"ids": [], "year": [], "title": [], "citation_number": [], "venue_type": [], "venue_name": []}
        for y, p in self.get_yearly_most_cited_paper_dict(citation_after_year, True,
                                                          self.max_publication_year).iteritems():
            if p.publish_year > max_publish_year:
                continue
            m["ids"].append(p.paper_id)

            m["year"].append(p.publish_year)
            m["title"].append(p.title)
            m["citation_number"].append(p.total_citations_number_by_year(p.publish_year + citation_after_year,
                                                                         include_self_citation=True))
            m["venue_name"].append(p.venue_name)
            t = ""
            if p.venue_type == VenueType.journal:
                t = "journal"
            elif p.venue_type == VenueType.conference:
                t = "conference"

            m["venue_type"].append(t)
        sf = tc.SFrame(m)

        return sf.sort("year", ascending=False)

    def papers_in_which_authors_published_in_venue_list(self, year=None):
        """
        Return the papers list of only papers in which one of their authors published in the venue in the past
        :param year: input year or None for all papers
        :return: list of papers in which one of the authors published before in the same venue the paper was published
        :rtype: list<Paper>
        """
        if year is not None:
            papers_list = self.papers_published_in_year_list(year)
        else:
            papers_list = self.papers_list
        return [p for p in papers_list if p.did_authors_publish_before_in_venue()]

    def papers_in_which_authors_not_published_in_venue(self, year=None):
        """
        Return the papers list of only papers in which  their authors didn't publish in the venue in the past
        :param year: input year or None for all papers
        :return: list of papers in which one the papers' authors didn't publish before in the same venue the paper was
            published
        :rtype: list<Paper>
        """
        if year is not None:
            papers_list = self.papers_published_in_year_list(year)
        else:
            papers_list = self.papers_list
        return [p for p in papers_list if not p.did_authors_publish_before_in_venue()]

    # <editor-fold desc="Papers Collection Properties">

    def papers_number(self, year):
        """
        Return the papers number
        :param year: input year
        :return: the number of papers in the collection that where published in the input list
        :rtype: int
        """
        return len(self.papers_published_in_year_list(year))

    def authors_number(self, year, unique=True):
        """
        The total number of authors who wrote the collections papers in a specific year
        :param year: input year
        :param unique: if True count each author only once, otherwise each author can be count multiple times
        :return: the number of authors who wrote the collection paper
        """
        l = self.all_authors_in_year_list(year)
        if unique:
            l = list(set(l))
        return len(l)

    @property
    def papers_ids(self):
        """
        Returns a list with the papers ids
        :return: returns a list with the papers ids
        :rtype: list<str>
        """
        return self.__papers_ids

    @property
    def papers_list(self):
        """
        Returns a list of the collection's paper objects
        :return: list of papers objects
        :rtype: list<Paper>
        """
        if len(self.__papers_list) == 0:
            self.__papers_list = [Paper(i, self._papers_fetcher, self._authors_fetcher) for i in self.papers_ids]

        return self.__papers_list

    @property
    def max_publication_year(self):
        """
        Returns the maximal publication year among all the collections papers
        :return: maximal publication year
        :rtype: int
        """
        if self._max_year is None:
            self._max_year = max([p.publish_year for p in self.papers_list if p.publish_year is not None])
        return self._max_year

    @property
    def min_publication_year(self):
        """
        Returns the minimal publication year among all the collections papers
        :return: minimal publication year
        :rtype: int
        """
        if self._min_year is None:
            self._min_year = min([p.publish_year for p in self.papers_list if p.publish_year is not None])
        return self._min_year

    def max_citations_paper(self, by_year, include_self_citations):
        """
        Returns the paper with the maximal number of citations by the input year
        :param by_year: input year
        :param include_self_citations: to include or to not include self-citation ion the calculations
        :return: Paper with maximal number of citation
        :rtype: Paper
        """
        l = [(p, p.total_citations_number_by_year(by_year, include_self_citations)) for p in self.papers_list]
        l = sorted(l, key=lambda k: k[1], reverse=True)
        return l[0][0]

    def authors_full_names(self, year, unique=True):
        """
        Returns the full authors names for authors who publish paper in specific years
        :param year: input
        :param unique: if True return list with unique names otherwise return the full list
        :return: a list with the authors full names for authors
        :rtype: list<str>
        """
        authors_names = list(
            itertools.chain.from_iterable([p.authors_fullnames_list for p in self.papers_published_in_year_list(year)]))
        if unique:
            authors_names = list(set(authors_names))
        return authors_names

        # </editor-fold>

        # <editor-fold desc="Authors Age">

    def authors_average_age(self, at_year):
        """
        Returns the papers' authors average age in a specific year
        :param at_year: year
        :return: the average authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.all_authors_in_year_list(at_year))
        return a.get_average_age(at_year)

    def authors_median_age(self, at_year):
        """
        Returns the papers' authors average age in a specific year
        :param at_year: year
        :return: the average authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.all_authors_in_year_list(at_year))
        return a.get_median_age(at_year)

    def first_authors_average_age(self, at_year):
        """
        Returns the papers' first authors average age in a specific year
        :param at_year: year
        :return: the average first authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.first_authors_list(at_year))
        return a.get_average_age(at_year)

    def first_authors_median_age(self, at_year):
        """
        Returns the papers' first authors median age in a specific year
        :param at_year: year
        :return: the median first authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.first_authors_list(at_year))
        return a.get_median_age(at_year)

    def last_authors_average_age(self, at_year):
        """
        Returns the papers' last authors average age in a specific year
        :param at_year: year
        :return: the average last authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.last_authors_list(at_year))
        return a.get_average_age(at_year)

    def last_authors_median_age(self, at_year):
        """
        Returns the papers' last authors median age in a specific year
        :param at_year: year
        :return: the median last authors age at the input year
        :rtype: float
        """
        a = AuthorsListAnalyzer(self.last_authors_list(at_year))
        return a.get_average_age(at_year)

    @staticmethod
    def _percentage_of_papers_authors_publish_before(papers_list, author_type):
        """
        Return the percentage of papers in which authors published in the venue before
        :param papers_list: a paper list
        :param author_type: author type all/first/last
        :return: the percentage of papers which their authors published in the venue before
        :rtype: float
        """
        if len(papers_list) == 0:
            return None
        if author_type is "all":
            l = [p for p in papers_list if p.did_authors_publish_before_in_venue()]
        elif author_type == "first":
            l = [p for p in papers_list if p.did_first_author_publish_in_venue()]
        elif author_type == "last":
            l = [p for p in papers_list if p.did_last_author_publish_in_venue()]
        else:
            raise Exception("Invalid author type - %s" % author_type)
        return len(l) / float(len(papers_list))

    def percentage_of_papers_with_authors_that_publish_before_in_the_same_venue(self, year):
        """
        Returns the percentage of papers in which authors publish a paper before in the venue
        :param year: year
        :return: the percentage of papers in which authors already published in the venue before
        :rtype: float
        """
        return PapersCollection._percentage_of_papers_authors_publish_before(self.papers_published_in_year_list(year),
                                                                             "all")

    def percentage_of_papers_with_first_authors_that_publish_before_in_the_same_venue(self, year):
        """
        Returns the percentage of papers in which first authors publish a paper before in the venue
        :param year: year
        :return: the percentage of papers in which first authors already published in the venue before
        :rtype: float
        """
        return PapersCollection._percentage_of_papers_authors_publish_before(self.papers_published_in_year_list(year),
                                                                             "first")

    def percentage_of_papers_with_last_authors_that_publish_before_in_the_same_venue(self, year):
        """
        Returns the percentage of papers in which last authors publish a paper before in the venue
        :param year: year
        :return: the percentage of papers in which last authors already published in the venue before
        :rtype: float
        """
        return PapersCollection._percentage_of_papers_authors_publish_before(self.papers_published_in_year_list(year),
                                                                             "last")

    # </editor-fold>

    # <editor-fold desc="Gender Stats ">
    def authors_avg_female_probability(self, at_year):
        """
        Return the avg female probabilites of the authors' first names of all the authors who published paper at
        the input year
        :param at_year: year
        :return: gender statistics of the all the papers' authors
        :rtype:dict
        """
        a = AuthorsListAnalyzer(self.all_authors_in_year_list(at_year))
        return a.get_avg_female_probabilities()

    def first_avg_female_probability(self, at_year):
        """
        Return the gender statistics of all the first authors who published paper at the input year
        :param at_year: year
        :return: gender statistics of the all the papers' first authors
        :rtype:dict
        """
        a = AuthorsListAnalyzer(self.first_authors_list(at_year))
        return a.get_avg_female_probabilities()

    def last_avg_female_probability(self, at_year):
        """
        Return the gender statistics of all the last authors who published paper at the input year
        :param at_year: year
        :return: gender statistics of the all the papers' last authors
        :rtype:dict
        """
        a = AuthorsListAnalyzer(self.last_authors_list(at_year))
        return a.get_avg_female_probabilities()

    # </editor-fold>

    def papers_median_rank(self, year):
        """
        Returns the papers median rank for papers publish in the input year
        :param year: input year
        :return: the median value of papers rank for papers publish in input year
        """
        return np.median(self.papers_ranks_list(year))

    def papers_average_rank(self, year):
        """
        Returns the papers average rank for papers publish in the input year
        :param year: input year
        :return: the median value of papers rank for papers publish in input year
        """
        return np.average(self.papers_ranks_list(year))

    def papers_average_length(self, year):
        """
        Returns the average paper length and the number of paper with lentgh
        :return: tupe in which the first element is the average paper length and the second element is the number of papers
            with length
        """
        l = self.papers_length_list(year)
        if len(l) > 0:
            return np.average(l), len(l)
        return None

    def papers_median_citations_after_years(self, publish_year, after_years, include_self_citations):
        """
        Returns the median number of citations after input years for papers that were published in a specific year
        :param publish_year: papers publish year
        :param after_years: after years from publication
        :param include_self_citations: if True count each author only once, otherwise each author can be count multiple
            times
        :return: the median number of citations after the input year for papers that were published in a specific year
        """
        return np.median([c for p, c in self.papers_citations_after_years_list(publish_year, after_years,
                                                                               include_self_citations=include_self_citations)])

    def papers_average_citations_after_years(self, publish_year, after_years, include_self_citations):
        """
        Returns the average number of citations after input years for papers that were published in a specific year
        :param publish_year: papers publish year
        :param after_years: after years from publication
        :param include_self_citations: if True count each author only once, otherwise each author can be count multiple
            times
        :return: the average number of citations after the input year for papers that were published in a specific year
        """
        return np.average([c for p, c in self.papers_citations_after_years_list(publish_year, after_years,
                                                                                include_self_citations=include_self_citations)])

    def top_keywords(self, year, top_keywords_number=20):
        """
        Returns a dict with the most common keywords in the input papers
        :param year: input year
        :param top_keywords_number: the number of top keywords to return
        :return: a dict with the most common keywords among the papers in the collection which where published in a
            specific year
        :rtype: dict<str,int>
        """
        papers_list = self.papers_published_in_year_list(year)
        if papers_list is None or len(papers_list) == 0:
            return {}
        l = list(itertools.chain.from_iterable(
            [p.keywords_list for p in papers_list if p.keywords_list is not None and len(p.keywords_list) > 0]))
        if len(l) == 0:
            return {}
        c = Counter(l)
        return dict(c.most_common(top_keywords_number))

    def get_citations_number_after_years_dict(self, after_years, include_self_citations):
        """
        Create dict of the papers citation number of papers that were published in specific year after the input years
        :param after_years: a number of year after publication
        :param include_self_citations: if True include self citation otherwise the citation number would be calculate
            without self-citations
        :return: dict in which each key is a year and each value is a list of papers and their corresponding citation
            number after "after_years" years
        :rtype: dict<int,list<(Paper, int)>>
        """

        min_year = self.min_publication_year
        max_year = self.max_publication_year
        d = {}
        for y in range(min_year, max_year + 1):
            d[y] = self.papers_citations_after_years_list(y, after_years, include_self_citations)
        return d

    def get_yearly_most_cited_paper_dict(self, after_years, include_self_citations, max_year):
        """
        Return the most cited paper after X years in each year
        :param after_years: a number of years
        :param include_self_citations: if True include self-citations otherwise the citation number will be without self
            citations
        :param max_year: max year to do the calculation for
        :return: dict in which each key is a year and each value is a the most cited paper that was published in the key
            year after after_years
        :rtype: dict<int,Paper>
        """
        d = self.get_citations_number_after_years_dict(after_years, include_self_citations)
        d = {k: v for k, v in d.iteritems() if v != []}

        for y, papers_list in d.items():
            if y > max_year or len(papers_list) == 0:
                continue

            papers_list = sorted(papers_list, key=lambda k: k[1], reverse=True)

            p = papers_list[0][0]
            d[y] = p

        return d

    def calculate_feature_over_time(self, feature_name, start_year, end_year):
        """
        Returns the feature values over the years from start_year to end_year
        :param feature_name: input feature name that is valud PapersCollection function
        :param start_year: start year
        :param end_year: end year
        :return: dict with the input feature values from start year to the end year
        :rtype: dict
        """
        d = {}
        if feature_name not in dir(PapersCollection):
            raise Exception("Invalid PaperCollection function - %s" % feature_name)
        for y in range(start_year, end_year + 1):
            f_value = eval(f"self.{feature_name}({y})")
            if f_value is None or str(f_value) == 'nan' or (type(f_value) is float and math.isnan(f_value)):
                continue
            if feature_name not in d:
                d[feature_name] = {}
            d[feature_name][y] = f_value

        return d

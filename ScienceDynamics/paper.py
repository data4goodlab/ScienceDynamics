from ScienceDynamics.config.configs import VenueType, PAPERS_FETCHER, AUTHORS_FETCHER
from ScienceDynamics.author import Author
from functools import lru_cache


class Paper(object):
    def __init__(self, paper_id, papers_fetcher=PAPERS_FETCHER, authors_fetcher=AUTHORS_FETCHER, json_data=None):
        """
        Construct a paper object
        :param paper_id: paper id
        :param papers_fetcher: papers fetcher object
        :param authors_fetcher: authors fetcher object
        :param json_data: paper's json_data
        """
        self._id = paper_id
        self._authors_fetcher = authors_fetcher
        self._json_data = json_data
        if json_data is None:
            self._json_data = papers_fetcher.get_paper_data(paper_id)

    def _get_data_value(self, k):
        """
        Returns a paper feature value by name, if the key exists otherwise returns None
        :param k: feature name
        :return: the feature value if exists or None otherwise
        """
        if k in self._json_data:
            return self._json_data[k]
        return None

    # ------------------------------------#
    # Times Authors Published in Venue    #
    # ------------------------------------#
    def times_list_authors_published_in_venue(self):
        """
        A list of time each paper's author published in venue until the year before the paper publication
        :return: list of time each paper's publist in venue
        :rtype: list of int
        """
        return [
            a.times_published_in_venue(self.venue_id, self.venue_type, start_year=None, end_year=self.publish_year - 1)
            for a in self.authors_list]

    def did_authors_publish_before_in_venue(self):
        """
        Return True if one of the paper's author published in venue until a year before this paper publication, or
            False otherwise
        :return: True if one of the authors published in venue false otherwise
        :rtype: bool
        """
        if self.total_number_of_times_authors_published_in_venue > 0:
            return True
        return False

    def _did_author_published_in_venue(self, a):
        """
        Check if an input author published in the paper's venue in the past
        :param a: author object
        :type a: Author
        :return: True if the author published in the venue before, or False otherwise
        :rtype: bool
        """
        return a.times_published_in_venue(self.venue_id, self.venue_type, start_year=None,
                                          end_year=self.publish_year - 1) > 0

    def did_first_author_publish_in_venue(self):
        """
        Return True if the paper's first author published in venue until a year before this paper publication, or
            false otherwise
        :return: True if the first published in venue false otherwise
        :rtype: bool
        """
        return self._did_author_published_in_venue(self.first_author)

    def did_last_author_publish_in_venue(self):
        """
        Return True if the paper's last author published in venue until a year before this paper publication, or
            false otherwise
        :return: True if the last published in venue false otherwise
        :rtype: bool
        """
        return self._did_author_published_in_venue(self.last_author)

    # </editor-fold>

    # <editor-fold desc="Citations Related Functions">
    # -----------------------------------#
    # Citations Related Functions        #
    # -----------------------------------#
    @lru_cache(maxsize=2)
    def get_total_citation_number_by_year_dict(self, include_self_citation):
        """
        Returns dict with the number of citation the paper received by a specific year
        :param include_self_citation:  if True include also self citations
        :return: dict in which each key is the year and each value is the total number of citations the paper received by the
            input year
        :rtype: dict<int,int>
        """
        n = "Total Citations by Year"
        if not include_self_citation:
            n = "Total Citations by Year without Self Citations"
        d = self._get_data_value(n)  # type: dict

        if d is not None:
            d = {int(y): v for y, v in d.items()}
        return d

    @lru_cache(maxsize=400)
    def get_total_citations_number_in_year(self, year, include_self_citation=True):
        """
        Get the number of citations in a specific year
        :param year: input year
        :param include_self_citation: to include self-citations or not
        :return: the number of citations in a specific year
        :note: in case the year is out of range the function will return 0
        """
        d = self.get_total_citation_number_by_year_dict(include_self_citation)
        if year not in d:
            return 0
        # calculating the previous year with citations
        years = [y for y in d.keys() if y < year]
        if len(years) == 0:
            return d[year]
        year_before = max(years)
        return d[year] - d[year_before]

    def total_self_citations_in_year(self, year):
        """
        Return the total number of self citation in a year
        :param year: input year
        :return: the total number of self citations in a year
        :rtype: int
        """
        return (
                self.get_total_citations_number_in_year(year, True) - self.get_total_citations_number_in_year(year,
                                                                                                              False))

    def get_max_citations_number_in_year(self, include_self_citation=True):
        """
        Returns citation maximal number
        :param include_self_citation: to include or not include self-citations
        :return: the maximal number of citations in a year since the paper's publication
        :rtype: int
        """
        d = self.get_total_citation_number_by_year_dict(include_self_citation)
        start_year = min(d.keys())
        end_year = max(d.keys())
        l = [self.get_total_citations_number_in_year(y, include_self_citation) for y in range(start_year, end_year + 1)]
        return max(l)

    def total_citations_number_by_year(self, end_year, include_self_citation):
        """
        Returns the papers total citations number by input year
        :param end_year: end year
        :param include_self_citation:  if True include also self citations
        :return: the total number of paper citation by year
        """
        d = self.get_total_citation_number_by_year_dict(include_self_citation)
        if d is None or d == {}:
            return 0
        if end_year in d:
            return d[end_year]
        years_keys = [y for y in d.keys() if y <= end_year]
        if len(years_keys) == 0:
            return 0
        return d[max(years_keys)]

    def total_citation_number_after_years_from_publication(self, years_num, include_self_citation):
        """
        Return the number of total citations after input years since publication
        :param years_num: the number of years after publication
        :param include_self_citation:  if True include also self citations
        :return: return the total number of citations after input number of years
        :rtype: int
        """
        return self.total_citations_number_by_year(self.publish_year + years_num, include_self_citation)

    # </editor-fold>

    # <editor-fold desc="Paper's Properties">
    @property
    def paper_id(self):
        """
        Return paper id
        :return: the paper id
        :rtype: str
        """
        return self._id

    @property
    def venue_type(self):
        """
        Returns the paper's venue type if one exists or None otherwise
        :return: Venue type
        :rtype: VenueType
        """
        n = self._get_data_value('Journal ID mapped to venue name')
        if n is not None and n != '':
            return VenueType.journal

        self._get_data_value('Conference ID mapped to venue name')
        if n is not None and n != '':
            return VenueType.conference

        return None

    @property
    def venue_id(self):
        """
        Returns the venue id
        :return: returns the venue id
        :rtype: str
        """
        if self.venue_type == VenueType.journal:
            return self._get_data_value(u'Journal ID mapped to venue name')

        if self.venue_type == VenueType.conference:
            return self._get_data_value(u'Conference ID mapped to venue name')

        return None

    @property
    def venue_name(self):
        """
        Returns the venue's name
        :return: the venue name
        :rtype: str
        """
        return self._get_data_value('Original venue name')

    @property
    def references_count(self):
        """
        Returns the paper references number
        :return: the paper's references number
        :rtype: int
        """
        return self._get_data_value('Ref Number')

    @property
    def publish_year(self):
        """
        Returns the paper's publish year
        :return: the paper's publish year
        :rtype: int
        """
        return self._get_data_value('Paper publish year')

    @property
    def rank(self):
        """
        Returns the paper's rank
        :return: paper
        """
        return self._get_data_value("Paper rank")

    @property
    def total_number_of_times_authors_published_in_venue(self):
        """
        The total number of times the authros published in venue
        :return: the total times all authors publish in venue
        :rtype: int
        :note: there can be double count of each paper
        """
        return sum(self.times_list_authors_published_in_venue())

    # <editor-fold desc="Paper's Authors Properties">

    @property
    def author_ids_list(self):
        """
        The paper's author ids list
        :return: the papers authors ids list
        :rtype: list of str
        """
        return self._get_data_value('Authors List Sorted')

    @property
    def authors_number(self):
        """
        Paper authors number
        :return: return the number of authros
        :rtype: int
        """
        return self._get_data_value('Authors Number')

    @property
    def first_author(self):
        """
        Return first author Author object
        :return: First author object
        :rtype: Author
        """
        if self.first_author_id is None:
            return None
        return Author(author_id=self.first_author_id, authors_fetcher=self._authors_fetcher)

    @property
    def last_author(self):
        """
        Return last author Author object
        :return: Last author object
        :rtype: Author
        """
        if self.last_author_id is None:
            return None
        return Author(self.last_author_id, self._authors_fetcher)

    @property
    def authors_list(self):
        """
        Return the papers author object list
        :return: Return the papers author object list
        :rtype: list of Author
        """
        if self.author_ids_list is None:
            return []
        return [Author(i, self._authors_fetcher) for i in self.author_ids_list]

    @property
    def first_author_id(self):
        """
        Return first author id
        :return: first author id
        :rtype: str
        """
        if self.author_ids_list is None:
            return None
        return self.author_ids_list[0]

    @property
    def last_author_id(self):
        """
        Return last author id
        :return: last author id
        :rtype: str
        """
        if self.author_ids_list is None:
            return None
        return self.author_ids_list[-1]

    @property
    def authors_fullnames_list(self):
        """
        Returns authors full names
        :return: return a list with paper's authors full names
        :rtype: list<str>
        """
        return [a.fullname for a in self.authors_list]


    @property
    def title(self):
        return self._get_data_value("Original paper title")

    @property
    def paper_norm_title(self):
        return self._get_data_value('Normalized paper title')

    @property
    def keywords_list(self):
        """
        Return the papers keyworkds
        :return: paper's keywords list
        :rtype: list of str
        """
        return self._get_data_value('Keywords List')

    @property
    def title_bag_of_words(self):
        """
        Returns the title bag of words dict
        :return: the title bag-of-words dict
        :rtype: dict
        """
        return self._get_data_value('Title Bag of Words')


    @property
    def paper_length(self):
        """
        Returns the paper length in pages if possible
        :return: the paper's number of pages
        :rtype: int
        :note: this is estimation to the paper's length
        """
        start = self._get_data_value('page_start')
        end = self._get_data_value('page_end')
        if start is None or end is None:
            return None
        try:
            length = int(end) - int(start) + 1
        except:
            return None
        return length

    @property
    def abstract(self):
        """
        Returns the paper's abstract if possible
        :return: paper's abstract
        :rtype: str
        """
        return self._get_data_value('abstract')

    @property
    def issn(self):
        """
        Returns the paper's publication ISSN if possible
        :return: the paper's ISSN
        :rtype: str
        """
        return self._get_data_value('issn')

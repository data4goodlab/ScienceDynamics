from ScienceDynamics.config.configs import VenueType
from ScienceDynamics.config.configs import AUTHORS_FETCHER
from ScienceDynamics.utils import join_all_lists
from ScienceDynamics.papers_collection_analyer import PapersCollection
from collections import Counter


class Author(object):
    def __init__(self, author_id, fullname=None, authors_fetcher=AUTHORS_FETCHER):
        """
        Construct an Author object that contains the authors features
        :param author_id: an author id
        :param authors_fetcher: an authors fetcher object
        :type author_id: str
        :param fullname: author name
        :type authors_fetcher: AuthorsFetcher
        :note: in case several authors as the same name than only the first matching author will return
        """

        self._start_year = None
        self._last_year = None
        self._authors_fetcher = authors_fetcher

        if author_id is not None:
            self._json_data = authors_fetcher.get_author_data(author_id=author_id)  # type: dict
        elif fullname is not None:
            self._json_data = authors_fetcher.get_author_data(author_name=fullname)  # type: dict

        self._id = self.author_id
        self._paper_collection_analyzer = None

    def _filter_dict_by_years(self, d, start_year, end_year):
        if start_year is not None:
            d = {k: v for k, v in d.iteritems() if k >= start_year}
        if end_year is not None:
            d = {k: v for k, v in d.iteritems() if k <= end_year}
        return d

    def _get_items_list_between_years(self, key_name, start_year, end_year):
        d = self._json_data[key_name]
        d = self._filter_dict_by_years(d, start_year, end_year)
        return join_all_lists(d.values())

    def get_academic_age(self, at_year):
        """
        Get the author's academic age at specific year
        :param at_year: year
        :return: the author's academic age
        :rtype: int
        """
        return at_year - self.first_publication_year

    def get_papers_list(self, start_year, end_year):
        """
        Return the author's paper list between the start_year and end_year
        :param start_year: start year
        :param end_year: end year
        :return: a list of the author's paper ids that were published between the start and end years
        :rtype: list of str
        """
        return self._get_items_list_between_years('Papers by Years Dict', start_year, end_year)

    def get_papers_list_at_year(self, year):
        """
        Return the author's papers list in a specific year
        :param year: year
        :return: the author's paper ids that were published at the input year
        :rtype: list of str
        """
        return self.get_papers_list(year, year)

    def number_of_papers(self, start_year, end_year):
        """
        Returns the author's number of papers between years
        :param start_year: start year
        :param end_year: end year
        :return: the number of papers the author wrote between the start and end years
        :rtype: int
        """
        return len(self.get_papers_list(start_year, end_year))

    def get_coauthors_list(self, start_year, end_year):
        """
        Return the author's coauthors list between the start_year and end_year
        :param start_year: start year
        :param end_year: end year
        :return: a list of the author's coauthors ids that were published between the start and end years
        :rtype: list of str
        """
        return self._get_items_list_between_years('Coauthors by Years Dict', start_year, end_year)

    def get_coauthors_list_at_year(self, year):
        """
        Return the author's coauthors in a specific year
        :param year: year
        :return: the author's paper ids that were published at the input year
        :rtype: list of str
        """
        return self.get_coauthors_list(year, year)

    def number_of_coauthors(self, start_year, end_year):
        """
        Returns the author's number of papers between years
        :param start_year: start year
        :param end_year: end year
        :return: the number of papers the author wrote between the start and end years
        :rtype: int
        """
        return len(self.get_coauthors_list(start_year, end_year))

    def get_venues_list(self, venue_type, start_year, end_year):
        """
        Returns the venues in which the author published between years
        :param venue_type: venue type of (can be VenueType.journal or VenueType.conference)
        :param start_year: the start year
        :param end_year: the end year
        :return: return a list of all the venues the author published in between the input years
        :rtype: list of str
        """
        k = 'Journal ID by Year Dict'
        if venue_type == VenueType.conference:
            k = 'Conference ID by Year Dict'
        return self._get_items_list_between_years(k, start_year, end_year)

    def times_published_in_venue(self, venue_id, venue_type, start_year, end_year):
        """
        Return the time the author published in specific venue between start_year and end_year
        :param venue_id: the venue id
        :param venue_type: the venue type
        :param start_year: start year
        :param end_year: end year
        :return: the number of time the author published in venue
        :rtype: int
        """
        l = self.get_venues_list(venue_type, start_year, end_year)
        c = Counter(l)
        if venue_id not in c:
            return 0
        return c[venue_id]

    def _get_data_value(self, k):
        """
        Get a data value from the features json data
        :param k: feature name
        :return: the value of the feature name if it exists or None otherwise
        """
        if k in self._json_data:
            return self._json_data[k]
        return None

    @property
    def author_id(self):
        """
        Return the author's id
        :return: author id
         :rtype: str
        """
        return self._get_data_value('Author ID')

    @property
    def gender(self):
        """
        Return the author's gender if it was identified by his/her first name
        :return: The authors gender or None
        :rtype: str
        """
        if ('Gender Dict' not in self._json_data) or (self._json_data['Gender Dict'] is None):
            return None
        return self._json_data['Gender Dict']['Gender']

    @property
    def male_probability(self):
        """
        Returns the probabilty of the author's first name to be male
        :return: The author's probability of being male according to it's first name
        :rtyoe: float
        """
        if ('Gender Dict' not in self._json_data) or (self._json_data['Gender Dict'] is None):
            return None
        return self._json_data['Gender Dict']['Percentage Males']

    @property
    def female_probability(self):
        p = self.male_probability
        if p is None:
            return None
        return 1 - p

    @property
    def fullname(self):
        """
        Returns the authors full name (in lower case)
        :return: the authors full name
        :rtype: str
        """
        return self._get_data_value('Author name')

    @property
    def firstname(self):
        """
        Returns the authors first name (in lower case)
        :return: the authors first name
        :rtype: str
        :note: if the name as less than two words the property will return None
        """
        l = self.fullname.split()
        if len(l) < 2:
            return None
        return l[0]

    @property
    def lastname(self):
        """
        Returns the authors last name (in lower case)
        :return: the authors last name
        :rtype: str
        :note: if the name as less than two words the property will return None
        """
        l = self.fullname.split()
        if len(l) < 2:
            return None
        return l[-1]

    @property
    def coauthors_dict(self):
        if 'Coauthors by Years Dict' in self._json_data:
            return dict(self._json_data['Coauthors by Years Dict'])

    @property
    def papers_dict(self):
        """
        Dict of the authors full paper ids list by year
        :return: dict of the author's paper ids by year
        :rtype: dict
        """
        return self._json_data['Papers by Years Dict']

    @property
    def papers_list(self):
        """
        List of the authors full paper ids list
        :return: list of the author's paper ids
        :rtype: list of str
        """
        return self.get_papers_list(None, None)

    @property
    def journals_dict(self):
        """
        Dict of journals in which the author published in
        :return: dict with list of journals by year
        :rtype: dict<int,list<str>>
        """
        return self._get_data_value('Journal ID by Year Dict')

    @property
    def conference_list(self):
        """
        Dict of conferences in which the author published in
        :return: dict with list of conferences by year
        :rtype: dict<int,list<str>>
        """
        return self._get_data_value('Conference ID by Year Dict')

    @property
    def papers_number(self):
        """
        Returns the number of papers the author publish
        :return: the number of papers the author published
        :rtype: int
        """
        return len(self.papers_list)

    @property
    def first_publication_year(self):
        """
        Returns the year in which the author publish his/her first paper
        :return: the year the author's first paper was published
        :rtype: int
        """
        if self._start_year is None and self.papers_dict is not None:
            self._start_year = min(self.papers_dict.keys())

        return self._start_year

    @property
    def last_publication_year(self):
        """
        The year in which the author's last paper was published according to the dataset
        :return: the year in which the authors first paper was publish
        """
        if self._last_year is None and self.papers_dict is not None:
            self._last_year = max(self.papers_dict.keys())

        return self._last_year

    @property
    def papers_collection_analyzer(self):
        """
        Return PaperCollection object for analyzing the authors papers
        :return: paper collection analyzer object
        :rtype: PapersCollection
        """
        if self._paper_collection_analyzer is None:
            self._paper_collection_analyzer = PapersCollection(papers_ids=self.papers_list)

        return self._paper_collection_analyzer

    @staticmethod
    def find_authors_id_by_name(author_name, authors_fetcher=AUTHORS_FETCHER):
        """
        Returns a list of ids for authors with the input author name
        :param authors_fetcher:
        :param author_name: author's full name or regex object
        :param: authors_fetcher: Author Fetcher object
        :return: list of author_ids
        :rtype: list<str>
        :note the author_name can be regex object
        """
        return authors_fetcher.get_author_ids_by_name(author_name)

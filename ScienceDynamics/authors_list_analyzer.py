from ScienceDynamics.author import Author
from collections import Counter
import numpy as np
from functools import lru_cache


class AuthorsListAnalyzer(object):
    def __init__(self, authors_list):
        """
        :param authors_list: authors list
        :type [Author]
        """
        self._authors_list = []
        if authors_list is not None:
            self._authors_list = authors_list  # type: list[Author]

    @lru_cache(maxsize=100)
    def get_author_academic_ages_list(self, year):
        """
        Returns the authors academic age list in a year
        :param year: year
        :return: list of author academic ages
        :rtype: list of int
        """
        return [a.get_academic_age(year) for a in self._authors_list]

    @lru_cache(maxsize=100)
    def get_publications_number_list(self, start_year, end_year):
        """
        Returns the a list with the number of authors publications
        :param start_year: start year
        :param end_year: end year
        :return: list with the number of publication of each author
        :rtype: list of int
        """
        return [a.number_of_papers(start_year, end_year) for a in self._authors_list]

    def get_average_age(self, year):
        """
        Authors average academic age in specific year
        :param year: year
        :return: Average authors academic age
        :rtype: float
        """
        return np.average(self.get_author_academic_ages_list(year))

    def get_median_age(self, year):
        """
        Authors median academic age in specific year
        :param year: year
        :return: Medan authors academic age
        :rtype: float
        """
        return np.median(self.get_author_academic_ages_list(year))

    def get_average_publication_number(self, start_year, end_year):
        """
        Return authors average publications number
        :param start_year: start year
        :param end_year: end year
        :return: the authors number of publication between years
        :rtype: float
        """
        return np.average(self.get_publications_number_list(start_year, end_year))

    def get_median_publication_number(self, start_year, end_year):
        """
        Return authors median publications number
        :param start_year: start year
        :param end_year: end year
        :return: the authors number of publication between years
        :rtype: float
        """
        return np.median(self.get_publications_number_list(start_year, end_year))

    def get_gender_stats(self):
        """
        Dict return authors' gender with the number of authors in each gender
        :return: Counter object with the number of authors in each gender
        :rtype: Counter
        """
        return Counter([a.gender for a in self._authors_list])

    def get_female_probabilities(self, remove_nulls=True):
        """
        Returns a list if the probability of each author's first name to be of a female
        :param remove_nulls: if True remove None values from list
        :return: list of of probability of the author to be female
        :rtype: list<float>
        """
        if remove_nulls:
            return [a.female_probability for a in self._authors_list if a.female_probability is not None]
        return [a.female_probability for a in self._authors_list]

    def get_avg_female_probabilities(self):
        """
        Returns the authors average female probability based on the authors' first names
        :return: return the authors average female probability
         :rtype: float
        """
        return np.average(self.get_female_probabilities(remove_nulls=True))

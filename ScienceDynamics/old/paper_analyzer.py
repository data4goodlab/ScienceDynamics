from code.author import *
from repoze.lru import lru_cache
import numpy as np
from code.authors_fetcher import *
from code.consts import *


class PaperAnalyzer(object):
    def __init__(self, paper_data_dict, authors_fetcher):
        self._data_dict = paper_data_dict
        self._authors_fetcher = authors_fetcher
        self._authors_list = None
        self._venue_id = None
        self._venue_type = None
        self._init_venue_data()

    def _init_venue_data(self):
        if self._venue_id is None:
            if self._data_dict['Journal ID mapped to venue name'] is not None:
                self._venue_id = self._data_dict['Journal ID mapped to venue name']
                self._venue_type = VenueType.journal
            elif self._data_dict['Conference ID mapped to venue name'] is not None:
                self._venue_id = self._data_dict['Conference ID mapped to venue name']
                self._venue_type = VenueType.conference

    def get_author_academic_birthday(self, i):
        y = self.authors_list[i].first_publication_year
        if y is None:
            return self.publish_year  # author first paper
        return y

    def get_authors_academic_birthdays(self):
        l = []
        for a in self.authors_list:
            if a.first_publication_year is None:
                l.append(self.publish_year)
            else:
                l.append(a.first_publication_year)
        return l

    def get_authors_avg_academic_birthday(self):
        return np.average(self.get_authors_academic_birthdays())

    def get_authors_med_academic_birthday(self):
        return np.median(self.get_authors_academic_birthdays())

    def get_paper_features(self, venues_list):
        d = {'Paper ID': self.paper_id, 'Venue ID': self._venue_id, 'Publish Year': self.publish_year,
             'Ref Count': self.refrences_number, 'Keywords': self.keywords_list,
             'Title Bag of Words': self.title_bag_of_words, 'Authors Number': self.authors_number,
             'first_author_academic_birthday': self.first_author_academic_birthday,
             'last_author_academic_birthday': self.last_author_academic_birthday,
             'get_authors_avg_academic_birthday': self.get_authors_avg_academic_birthday(),
             'get_authors_median_academic_birthday': self.get_authors_med_academic_birthday(),
             'first_author_number_of_papers': self.first_author_number_of_papers,
             'last_author_number_of_papers': self.last_author_number_of_papers,
             'author_max_number_of_papers': self.author_max_number_of_papers}

        for v in venues_list:
            d['any_author_published_in_venue_%s' % v] = self.any_author_published_in_venue(v)
            d['first_author_published_in_venue_%s' % v] = self.first_author_published_in_venue(v)
            d['last_author_published_in_venue_%s' % v] = self.last_author_published_in_venue(v)
            d['total_times_authors_published_in_venue_%s' %v ] = self.total_times_authors_published_in_venue(v)

        return d

    @property
    def paper_id(self):
        return self._data_dict['Paper ID']

    @property
    def refrences_number(self):
        return self._data_dict['Ref Count']

    @property
    def publish_year(self):
        return self._data_dict['Paper publish year']

    @property
    def keywords_list(self):
        return self._data_dict['Keywords List']

    @property
    def title_bag_of_words(self):
        return self._data_dict['Title Bag of Words']

    @lru_cache(maxsize=1000)
    def times_author_published_in_venue(self, i, venue_id, venue_type):
        return self.authors_list[i].times_published_in_venue(venue_id=venue_id, venue_type=venue_type)

    @property
    def authors_number(self):
        return self._data_dict['Authors Number']

    @property
    def authors_ids_list(self):
        return self._data_dict['Authors List Sorted']

    @property
    def authors_list(self):
        if self._authors_list is None:
            self._authors_list = [self.get_author(a) for a in self.authors_ids_list]
        return self._authors_list

    @property
    def first_author(self):
        return self.get_author(self.authors_ids_list[0])

    @property
    def last_author(self):
        return self.get_author(self.authors_ids_list[-1])

    @lru_cache(maxsize=1000)
    def get_author(self, author_id):
        return Author(author_id, self._authors_fetcher)

    @property
    def first_author_academic_birthday(self):
        return self.get_author_academic_birthday(0)

    @property
    def last_author_academic_birthday(self):
        return self.get_author_academic_birthday(-1)

    @lru_cache(maxsize=1)
    def get_authors_number_of_publications_in_venue(self, venue_id, venue_type):
        return [a.times_published_in_venue(venue_id=venue_id, venue_type=venue_type) for a in
                self.authors_list]

    @property
    def first_author_number_of_papers(self):
        return self.first_author.papers_number

    @property
    def last_author_number_of_papers(self):
        return self.last_author.papers_number

    @property
    def author_max_number_of_papers(self):
        return max([a.papers_number for a in self.authors_list])


    def first_author_published_in_venue(self, venue_id, venue_type=VenueType.journal):
        return self.get_authors_number_of_publications_in_venue(venue_id, venue_type)[0]

    def last_author_published_in_venue(self, venue_id, venue_type=VenueType.journal):
        return self.get_authors_number_of_publications_in_venue(venue_id, venue_type)[-1]

    def any_author_published_in_venue(self, venue_id, venue_type=VenueType.journal):
        return sum(self.get_authors_number_of_publications_in_venue(venue_id, venue_type)) > 0

    def total_times_authors_published_in_venue(self,venue_id, venue_type=VenueType.journal):
        return sum(self.get_authors_number_of_publications_in_venue(venue_id, venue_type))


if __name__ == '__main__':
    pass

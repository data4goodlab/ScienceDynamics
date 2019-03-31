from unittest import TestCase
import sys
sys.path.extend([".."])
from paper import *
from configs import PAPERS_FETCHER

class TestPaper(TestCase):
    def testPaperFeatures(self):
        p = Paper('75508021')
        self.assertEqual(p.paper_id, '75508021')
        self.assertEqual(p.references_count, 8)
        self.assertEqual(p.venue_name, 'Nature')
        self.assertEqual(p.total_number_of_times_authors_published_in_venue, 2)
        self.assertEqual(p.title, u'Cell biology: The checkpoint brake relieved')
        self.assertEqual(p.publish_year, 2007)
        self.assertEqual(p.total_citation_number_years_after_publication(4, True), 4)

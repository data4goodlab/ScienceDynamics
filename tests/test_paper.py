from unittest import TestCase
import sys

from ScienceDynamics.paper import Paper

sys.path.extend([".."])


class TestPaper(TestCase):
    def testPaperFeatures(self):
        p = Paper('75508021')
        self.assertEqual(p.paper_id, '75508021')
        self.assertEqual(p.references_count, 8)
        self.assertEqual(p.venue_name, 'Nature')
        self.assertEqual(p.total_number_of_times_authors_published_in_venue, 2)
        self.assertEqual(p.title, u'Cell biology: The checkpoint brake relieved')
        self.assertEqual(p.publish_year, 2007)

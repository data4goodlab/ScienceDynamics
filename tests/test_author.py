from unittest import TestCase
import sys

# hack to include configs.py
sys.path.extend([".."])

from ScienceDynamics.author import Author
from ScienceDynamics.configs import AUTHORS_FETCHER
import re
from collections import Counter


class TestAuthor(TestCase):

    def testAuthorFeatures(self):
        r = re.compile('T.*Berners.*Lee$', re.IGNORECASE)
        l = AUTHORS_FETCHER.get_author_ids_by_name(r)
        self.assertEqual(len(l), 2)
        author_list = [Author(author_id=i) for i in l]
        author_list = sorted(author_list, key=lambda a: a.papers_number)
        a = author_list[-1]
        self.assertEqual(a.fullname, u'tim bernerslee')
        self.assertEqual(a.papers_number, 20)
        self.assertEqual(a.gender, 'Male')
        coauthors = a.get_coauthors_list(None, None)
        self.assertEqual(len(coauthors), 90)
        c = Counter(coauthors)
        a2 = Author(author_id=c.most_common(1)[0])
        self.assertEqual(a2.fullname, 'lalana kagal')
        self.assertEqual(a2.papers_number, 43)

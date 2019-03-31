import sys

# hack to include configs.py
sys.path.extend([".."])

from configs import *

import sys
import graphlab as gl
import graphlab.aggregate as agg
import os, json
from collections import Counter
from author import Author

class AuthorsFeaturesAnalyzer(object):
    def __init__(self, min_ref_num=5):
        """
        Calculate the authors features over time
        :param min_ref_num: the number of references a paper need to cite in order to be considered as a valid paper
        """
        self._min_ref_num = min_ref_num

    def _get_tmp_coauthors_links(self, min_ref_num, end_year=None):
        """
        Returns the path to coauthors links temporary save sframe
        :param min_ref_num: number of references
        :param end_year:  end year
        :return: the path to the temporary coauthors links sframe
        :rtype: str
        """

        return "%s/co_authors_%s_%s.sframe" % (TMP_DIR, min_ref_num, end_year)

    def get_coauthors_sframe(self, end_year=None):
        """
        Returns the coauthors sframe
        :param end_year: end year
        :return: return an SFrame with all the authors coauthorship data
        :rtype: gl.SFrame
        :note: this is ***very*** calculation intensive function.
        """
        # Filter irelevant papers
        p = self._get_tmp_coauthors_links(self._min_ref_num, end_year)
        if os.path.isdir(p):
            sf = gl.load_sframe(p)
        else:
            p_sf = get_papers_sframe(min_ref_num=self._min_ref_num, end_year=end_year)[['Paper ID']]
            a_sf = gl.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)  # 337000127
            a_sf = a_sf.join(p_sf, on="Paper ID")
            sf = a_sf.join(a_sf, on="Paper ID")['Author ID', 'Author ID.1', "Paper ID"]

        g = sf.groupby(['Author ID', 'Author ID.1'], agg.COUNT())
        g2 = g[g['Author ID'] != g['Author ID.1']]
        g2['Authors_Count'] = g2.apply(lambda r: (r['Author ID.1'], r['Count']))
        g3 = g2.groupby('Author ID', {'Coauthors List': agg.CONCAT('Authors_Count')})
        if not os.path.isdir(p):
            g3.save(p)
        return g3

    def get_coauthors_by_years_sframe(self, end_year=None):
        """
        Return the authors co-authorship data for each year
        :param end_year: end year
        :return: SFrame with each author coauthorship data in each year
        :rtype: gl.SFrame
        :note: this is ***very*** calculation intensive function.
        """
        # Filter irelevant papers
        p_sf = get_papers_sframe(min_ref_num=self._min_ref_num, end_year=end_year)[['Paper ID', 'Paper publish year']]
        a_sf = gl.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)  # 337000127
        a_sf = a_sf.join(p_sf, on="Paper ID")
        a_sf = a_sf[['Paper ID', 'Author ID', 'Paper publish year']]
        sf = a_sf.join(a_sf, on="Paper ID")['Author ID', 'Author ID.1', "Paper ID", 'Paper publish year']

        g = sf.groupby(['Author ID', 'Author ID.1', 'Paper publish year'], {'count': agg.COUNT()})
        g2 = g[g['Author ID'] != g['Author ID.1']]
        g2['Authors_Count'] = g2.apply(lambda r: (r['Author ID.1'], r['Count']))
        g3 = g2.groupby(['Author ID', 'Paper publish year'], {'Coauthors List': agg.CONCAT('Authors_Count')})

        return g3

    def get_authors_features_per_year(self):
        """
        Calculates the authors features in each year
        :return: SFrame with the authors features in each year
        :rtype: gl.SFrame

        """
        logger.info("Getting authors features per year")
        p_sf = get_papers_sframe(min_ref_num=self._min_ref_num)
        a_sf = gl.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)  # 337000127
        sf = a_sf.join(p_sf, on="Paper ID")
        g = sf.groupby(["Author ID", 'Paper publish year'], {'Papers Count': agg.COUNT_DISTINCT('Paper ID'),
                                                             'papers_list': agg.CONCAT('Paper ID'),
                                                             'journals_list': agg.CONCAT(
                                                                 'Journal ID mapped to venue name'),
                                                             'conferences_list': agg.CONCAT(
                                                                 'Conference ID mapped to venue name'),
                                                             'affiliations_list': agg.CONCAT('Affiliation ID'),
                                                             'author_seq_list': agg.CONCAT('Author sequence number')})

        g['journals_dict'] = g['journals_list'].apply(lambda l: dict(Counter(l)))
        g['conferences_dict'] = g['conferences_list'].apply(lambda l: dict(Counter(l)))
        g.rename({'Paper publish year': 'Year'})
        return g

    def _parse_authors_names(self, path="Authors.txt"):
        """
        Pasrse the authors name into first & last names
        :param path: path to author names SFrame
        :return: Auhtors SFrame that contains each author first and last names
        :rtype: gl.SFrame
        """
        sf = gl.SFrame.read_csv(path, header=False, delimiter="\t")
        sf.rename({'X1': 'Author ID', 'X2': 'Full Name'})
        sf['Last Name'] = sf['Full Name'].apply(lambda n: n.split()[-1])
        sf['First Name'] = sf['Full Name'].apply(lambda n: n.split()[0])
        return sf

    def get_authors_features(self, end_year=None, first_name_gender_path=None):
        """
        Get the authors features
        :param end_year: end year
        :param first_name_gender_path: SFrame which conatins the gender by first name
        :return: SFrame with the authors general features
        :rtype: gl.SFrame
        """
        logger.info("Getting authors features from %s" % end_year)
        p_sf = get_papers_sframe(min_ref_num=self._min_ref_num, end_year=end_year)
        a_sf = gl.load_sframe(PAPER_AUTHOR_AFFILIATIONS_SFRAME)  # 337000127
        sf = a_sf.join(p_sf, on="Paper ID")
        g = sf.groupby("Author ID", {'Papers Count': agg.COUNT_DISTINCT('Paper ID'),
                                     'start_year': agg.MIN('Paper publish year'),
                                     'last_year': agg.MAX('Paper publish year'),
                                     'papers_list': agg.CONCAT('Paper ID'),
                                     'journals_list': agg.CONCAT('Journal ID mapped to venue name'),
                                     'conferences_list': agg.CONCAT('Conference ID mapped to venue name'),
                                     'affiliations_list': agg.CONCAT('Affiliation ID'),
                                     'author_seq_list': agg.CONCAT('Author sequence number')})

        g['journals_dict'] = g['journals_list'].apply(lambda l: dict(Counter(l)))
        g['conferences_dict'] = g['conferences_list'].apply(lambda l: dict(Counter(l)))

        n_sf = gl.load_sframe(AUTHOR_NAMES_SFRAME)
        g = g.join(n_sf, on="Author ID", how="left")

        #Adding author's gender
        if first_name_gender_path is not None:
            g_sf = gl.SFrame(first_name_gender_path)['First Name', 'Gender', "Percentage Males"]
            g = g.join(g_sf, on='First Name', how='left')
            g.rename({'Name Class': 'Gender'})
        return g

    def add_citations_from_files(self, path):
        sf['Total Citation Dict'] = sf['Author ID'].apply(lambda a: _load_author_citation(a, path))


#Calculating author's citations over the years by using temp files
def create_authors_citations():
    a_sf = gl.load_sframe('/mnt/data/authors_features.sframe')
    a_sf = a_sf.sort('start_year')
    count = 0
    m = ""
    for i in a_sf['Author ID']:
        count += 1
        print count
        m = int(count/1000000.0)
        p = "/mnt/data/authors_results%s" % m
        if not os.path.isdir(p):
            os.mkdir(p)
        if os.path.isfile("%s/%s.json" % (p, i)):
            continue
        a = Author(i)
        d = a.calculate_total_citations_dict(False)

        json.dump(d, file("%s/%s.json" % (p, i), 'w'))

    #load
    authors_list = []
    for a in a_sf['Author ID']:
        authors_list.append(get_author_citation_json(a))
    a_sf['Total Citations'] = authors_list

def get_author_citation_json(r):
    if r['Total Citations'] is not None:
        return r['Total Citations']

    try:
        for m in range(20):
            p = "/mnt/data/authors_results%s" % m
            if os.path.isfile("%s/%s.json" % (p, i)):
                return json.load(file("%s/%s.json" % (p, i), "r"))
    except:
        return None
    return None







def _load_author_citation(aid, path):
    p = "%s/%s.json" % (path, aid)
    if not os.path.isfile(p):
        return None
    return json.load(file(p, "r"))

def load_citations_json(path):
    sf = gl.SFrame()
    l = []
    count = 0
    for p in os.listdir(path):
        count += 1
        j = json.load(file("%s/%s" % (path, p)))
        j["Author ID"] = p.split(".json")[0]
        l.append(j)
        if count % 100000 == 0:
            print p
            sf2 = gl.SFrame()
            sf2 = gl.SFrame(l)
            sf = sf.append(sf2)
            l = []






if __name__ == "__main__":
    a = AuthorsFeaturesAnalyzer()
    start_year = int(sys.argv[1])
    end_year = int(sys.argv[2])

    sf = a.get_authors_features(start_year, end_year)
    sf.save("/data/sframe/authors_papers_%s_%s.sframe" % (start_year, end_year))

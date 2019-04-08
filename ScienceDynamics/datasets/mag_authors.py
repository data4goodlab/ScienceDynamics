import sys
import zipfile

from ScienceDynamics.config.configs import TMP_DIR, SFRAMES_BASE_DIR
from ScienceDynamics.config.log_config import logger
import turicreate as tc
import turicreate.aggregate as agg
from pathlib import Path

from ScienceDynamics.datasets.configs import NAME_GENDER_URL, FIRST_NAMES_SFRAME
from ScienceDynamics.datasets.utils import download_file


def _entities_years_list_to_dict(l):
    """
    Create a dict of entites by year
    :param l: list which each element is a size two tuple (year, entity_id
    :return: a dict in which each key is a year and each value is a list of entities
    :rtype: dict<int,list>
    """
    d = {}
    for y, eid in l:
        y = str(y)  # for easier mongo insert key need to be str
        if y not in d:
            d[y] = []
        d[y].append(eid)
    return d


class AuthorsFeaturesExtractor(object):
    def __init__(self, mag, paper_min_ref=5):
        """
        Consturct and Author Features Extractor object
        :param paper_min_ref: minimum number of references
        """
        self._mag = mag
        self._paper_min_ref = paper_min_ref
        self._p_sf = self._get_extended_papers_sframe(paper_min_ref)
        self._paper_authors_years = None
        self._paper_author_affiliation_join_sframe = None
        if not Path(FIRST_NAMES_SFRAME).exists():
            dataset_zip = FIRST_NAMES_SFRAME.replace(".sframe",".zip")
            download_file(NAME_GENDER_URL, Path(dataset_zip))
            with zipfile.ZipFile(Path(dataset_zip), 'r') as f:
                f.extractall(SFRAMES_BASE_DIR)

    def _get_extended_papers_sframe(self, paper_min_ref):
        """
        Return SFrame with Extended Papers titles only for papers with the minimial input references number
        :param paper_min_ref: minimum number of references
        :return: SFrame with Papers data
        :rtype: tc.SFrame
        """
        extended = self._mag.extended_papers
        if paper_min_ref is not None:
            sf_path = f"{TMP_DIR}/extended_paper_min_ref_{paper_min_ref}.sfrmae"
            if Path(sf_path).is_dir():
                return tc.load_sframe(sf_path)

            extended = extended[extended['Ref Number'] >= paper_min_ref]
            extended.save(sf_path)
            return extended

    @property
    def paper_authors_years(self):
        """
        Return an SFrame in which each row consists of Paper ID, Author ID, Paper Publish Year
        :return: SFrame with Author and Paper by publication year data
        :rtype: tc.SFrame()
        """
        if self._paper_authors_years is None:
            p_sf = self._p_sf["Paper ID", "Paper publish year"]
            self._paper_authors_years = self._mag.paper_author_affiliations[
                "Author ID", "Paper ID"]  # 337000127 for all papers
            self._paper_authors_years = self._paper_authors_years.join(p_sf, on="Paper ID")
        return self._paper_authors_years

    def get_authors_papers_dict_sframe(self):
        """
        Create SFrame in which each row contains an author id and a dict with the author's publication by year dict
        :return: SFrame with Authors ID and Papers by Years Dict columns
        :rtype: tc.SFrame
        """
        logger.info("Calcualting authors' papers by year")
        a_sf = self.paper_authors_years
        a_sf['Paper Year'] = a_sf.apply(lambda r: (r["Paper publish year"], r["Paper ID"]))
        g = a_sf.groupby("Author ID", {"Papers List": agg.CONCAT("Paper Year")})
        g['Papers by Years Dict'] = g["Papers List"].apply(lambda l: _entities_years_list_to_dict(l))
        g = g.remove_column("Papers List")
        return g

    def get_co_authors_dict_sframe(self):
        """
        Create SFrame with each author's coauthors by year
        :return: SFrame with Author ID and Coauthors by Years Dict
        :note: the function can take considerable amount of time to execute
        """
        logger.info("Calcualting authors' coauthors by year")
        sf = self.paper_authors_years
        sf = sf.join(sf, on='Paper ID')
        sf2 = sf[sf['Author ID'] != sf['Author ID.1']]
        sf2 = sf2.remove_column('Paper publish year.1')
        sf2.__materialize__()
        g = sf2.groupby(['Author ID', 'Paper publish year'], {'Coauthors List': agg.CONCAT('Author ID.1')})
        g['Coauthors Year'] = g.apply(lambda r: (r['Paper publish year'], r['Coauthors List']))
        g2 = g.groupby("Author ID", {'Coauthors list': agg.CONCAT('Coauthors Year')})
        g2['Coauthors by Years Dict'] = g2['Coauthors list'].apply(lambda l: {y: coa_list for y, coa_list in l})
        g2 = g2.remove_column('Coauthors list')
        return g2

    def _get_author_feature_by_year_sframe(self, feature_name, feature_col_name):
        """
        Create a SFrame with Author ID and a dict with the author's input feature (feature_name) over the years values
        :param feature_name: input feature name
        :param feature_col_name: the Sframe column name which contains dict with the author feature_name values over the years
        :return: SFrame with Author ID and feature_col_name columns
        :rtype: tc.SFrame
        """
        logger.info("Calcualting authors feature %s by year" % feature_name)
        a_sf = self.paper_author_affiliation_sframe['Author ID', 'Paper publish year', feature_name]
        a_sf['Feature Year'] = a_sf.apply(lambda r: (int(r["Paper publish year"]), r[feature_name]))
        g = a_sf.groupby("Author ID", {"Feature List": agg.CONCAT("Feature Year")})
        g[feature_col_name] = g["Feature List"].apply(lambda l: _entities_years_list_to_dict(l))
        g = g.remove_column("Feature List")

        return g

    @property
    def paper_author_affiliation_sframe(self):
        """
        Returns SFrame in whcih each row contains the Author ID, Paper ID, Paper publish year, Conference ID mapped to venue name, Journal ID mapped to venue name,
             Original venue name
        :return: SFrame with Authors and Papers Data
        :rtype: tc.SFrame
        """
        if self._paper_author_affiliation_join_sframe is None:
            p_sf = self._p_sf[
                ['Paper ID', 'Paper publish year', "Conference ID mapped to venue name", "Journal ID mapped to venue name",
                 "Original venue name"]]
            a_sf = self._mag.paper_author_affiliations
            self._paper_author_affiliation_join_sframe = a_sf.join(p_sf, on="Paper ID")
        return self._paper_author_affiliation_join_sframe

    def get_authors_all_features_sframe(self):
        """
        Create Authors SFrame in which each row is unique Author ID and the author's various features
        :return: SFrame with Authors features
        :rtype: tc. SFrame
        """
        p_sf = self._p_sf[['Paper ID']]  # 22082741
        a_sf = self.paper_author_affiliations["Author ID", "Paper ID"]
        a_sf = a_sf.join(p_sf, on="Paper ID")
        a_sf = a_sf[["Author ID"]].unique()
        g = self.get_authors_papers_dict_sframe()
        a_sf = a_sf.join(g, on="Author ID", how="left")  # 22443094 rows
        g = self.get_co_authors_dict_sframe()
        a_sf = a_sf.join(g, on="Author ID", how='left')
        a_sf = a_sf.join(self._mag.authors_names, on="Author ID", how="left")
        g_sf = tc.load_sframe(FIRST_NAMES_SFRAME)
        a_sf = a_sf.join(g_sf, on={"First name": "First Name"}, how="left")

        feature_names = [("Normalized affiliation name", "Affilation by Year Dict"),
                         ('Author sequence number', 'Sequence Number by Year Dict'),
                         ("Conference ID mapped to venue name", "Conference ID by Year Dict"),
                         ("Journal ID mapped to venue name", "Journal ID by Year Dict"),
                         ("Original venue name", "Venue by Year Dict")]
        for fname, col_name in feature_names:
            f_sf = self._get_author_feature_by_year_sframe(fname, col_name)
            a_sf = a_sf.join(f_sf, on="Author ID", how='left')

        return a_sf
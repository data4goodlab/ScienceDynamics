import sys
import zipfile

from ScienceDynamics.config.configs import TMP_DIR, SFRAMES_BASE_DIR
from ScienceDynamics.config.log_config import logger
import turicreate as tc
import turicreate.aggregate as agg
from pathlib import Path
from tqdm import tqdm
from ScienceDynamics.datasets.configs import FIRST_NAMES_SFRAME
from ScienceDynamics.datasets.utils import download_file, save_sframe


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
    def __init__(self, mag, paper_min_ref=5, fields=None):
        """
        Consturct and Author Features Extractor object
        :param paper_min_ref: minimum number of references
        """
        self._mag = mag
        self._paper_min_ref = paper_min_ref
        self._p_sf = self._get_extended_papers_sframe(paper_min_ref)
        self._paper_authors_years = None
        self._paper_author_affiliation_join_sframe = None
        self._sframe_dir = SFRAMES_BASE_DIR
        if not Path(FIRST_NAMES_SFRAME).exists():
            dataset_zip = str(FIRST_NAMES_SFRAME).replace(".sframe",".zip")
            with zipfile.ZipFile(Path(dataset_zip), 'r') as f:
                f.extractall(SFRAMES_BASE_DIR)

    def _get_extended_papers_sframe(self, paper_min_ref, fields=None):
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
            extended = extended[extended["Authors Number"]<500]
            if fields is not None:
                fos = self._mag.fields_of_study.filter_by(fields, "NormalizedName")["FieldOfStudyId"]
                papers = self._mag.paper_fields_of_study.filter_by(fos, "FieldOfStudyId")["PaperId"]
                extended = extended.filter_by(papers, "PaperId")
            extended.save(sf_path)
            return extended

    @property
    @save_sframe(sframe="paper_authors_years.sframe")
    def paper_authors_years(self):
        """
        Return an SFrame in which each row consists of PaperId, AuthorId, Year
        :return: SFrame with Author and Paper by publication year data
        :rtype: tc.SFrame()
        """
        if self._paper_authors_years is None:
            p_sf = self._p_sf["PaperId", "Year"]
            self._paper_authors_years = self._mag.paper_author_affiliations[
                "AuthorId", "PaperId"]  # 337000127 for all papers
            self._paper_authors_years = self._paper_authors_years.join(p_sf, on="PaperId")
        return self._paper_authors_years
    
    @save_sframe(sframe="authors_papers_dict_sframe.sframe")
    def get_authors_papers_dict_sframe(self):
        """
        Create SFrame in which each row contains an AuthorId and a dict with the author's publication by year dict
        :return: SFrame with Authors ID and Papers by Years Dict columns
        :rtype: tc.SFrame
        """
        logger.info("Calcualting authors' papers by year")
        a_sf = self.paper_authors_years
        a_sf['Paper Year'] = a_sf.apply(lambda r: (r["Year"], r["PaperId"]))
        g = a_sf.groupby("AuthorId", {"Papers List": agg.CONCAT("Paper Year")})
        g['Papers by Years Dict'] = g["Papers List"].apply(lambda l: _entities_years_list_to_dict(l))
        g = g.remove_column("Papers List")
        return g
    
    @save_sframe(sframe="co_authors_dict_sframe.sframe")
    def get_co_authors_dict_sframe(self):
        """
        Create SFrame with each author's coauthors by year
        :return: SFrame with AuthorId and Coauthors by Years Dict
        :note: the function can take considerable amount of time to execute
        """
        logger.info("Calcualting authors' coauthors by year")
        sf = self.paper_authors_years
        sf = sf.join(sf, on='PaperId')
        sf = sf[sf['AuthorId'] != sf['AuthorId.1']]
        sf = sf.remove_column('Year.1')
        sf = sf.groupby(['AuthorId', 'Year'], {'Coauthors List': agg.CONCAT('AuthorId.1')})
        sf['Coauthors Year'] = sf.apply(lambda r: (r['Year'], r['Coauthors List']))
        sf = sf.groupby("AuthorId", {'Coauthors list': agg.CONCAT('Coauthors Year')})
        sf['Coauthors by Years Dict'] = sf['Coauthors list'].apply(lambda l: {y: coa_list for y, coa_list in l})
        sf = sf.remove_column('Coauthors list')
        return sf

    def _get_author_feature_by_year_sframe(self, feature_name, feature_col_name):
        """
        Create a SFrame with AuthorId and a dict with the author's input feature (feature_name) over the years values
        :param feature_name: input feature name
        :param feature_col_name: the Sframe column name which contains dict with the author feature_name values over the years
        :return: SFrame with AuthorId and feature_col_name columns
        :rtype: tc.SFrame
        """
        logger.info("Calcualting authors feature %s by year" % feature_name)
        a_sf = self.paper_author_affiliation_sframe['AuthorId', 'Year', feature_name]
        a_sf['Feature Year'] = a_sf.apply(lambda r: (int(r["Year"]), r[feature_name]))
        g = a_sf.groupby("AuthorId", {"Feature List": agg.CONCAT("Feature Year")})
        g[feature_col_name] = g["Feature List"].apply(lambda l: _entities_years_list_to_dict(l))
        g = g.remove_column("Feature List")

        return g

    @property
    @save_sframe(sframe="paper_author_affiliation_join.sframe")
    def paper_author_affiliation_sframe(self):
        """
        Returns SFrame in whcih each row contains the AuthorId, PaperId, Year, ConferenceSeriesId, JournalId,
             OriginalVenue
        :return: SFrame with Authors and Papers Data
        :rtype: tc.SFrame
        """
        if self._paper_author_affiliation_join_sframe is None:
            p_sf = self._p_sf[
                ['PaperId', 'Year', "ConferenceSeriesId", "JournalId",
                 "OriginalVenue"]]
            a_sf = self._mag.paper_author_affiliations
            self._paper_author_affiliation_join_sframe = a_sf.join(p_sf, on="PaperId")
        return self._paper_author_affiliation_join_sframe

    @property
    @save_sframe(sframe="authors_features.sframe")
    def authors_features(self):
        """
        Create Authors SFrame in which each row is unique AuthorId and the author's various features
        :return: SFrame with Authors features
        :rtype: tc. SFrame
        """
        p_sf = self._p_sf[['PaperId']]  # 22082741
        a_sf = self._mag.paper_author_affiliations["AuthorId", "PaperId"]
        a_sf = a_sf.join(p_sf, on="PaperId")
        a_sf = a_sf[["AuthorId"]].unique()
        g = self.get_authors_papers_dict_sframe()
        a_sf = a_sf.join(g, on="AuthorId", how="left")  # 22443094 rows
        g = self.get_co_authors_dict_sframe()
        a_sf = a_sf.join(g, on="AuthorId", how='left')
        author_names = self._mag.author_names
        author_names["First Name"] =  author_names["NormalizedName"].apply(lambda x: x.split(" ")[0])
        a_sf = a_sf.join(author_names, on="AuthorId", how="left")
        g_sf = tc.load_sframe(str(FIRST_NAMES_SFRAME))
        a_sf = a_sf.join(g_sf, on={"First Name": "First Name"}, how="left")

        feature_names = [("AffiliationId", "Affilation by Year Dict"),
                         ('AuthorSequenceNumber', 'Sequence Number by Year Dict'),
                         ("ConferenceSeriesId", "Conference ID by Year Dict"),
                         ("JournalId", "Journal ID by Year Dict"),
                         ("OriginalVenue", "Venue by Year Dict")]
        for fname, col_name in tqdm(feature_names):
            f_sf = self._get_author_feature_by_year_sframe(fname, col_name)
            a_sf = a_sf.join(f_sf, on="AuthorId", how='left')

        return a_sf

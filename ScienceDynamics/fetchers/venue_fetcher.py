from functools import lru_cache
from ScienceDynamics.config.configs import VenueType, AMINER_MAG_JOIN_SFRAME, SJR_SFRAME, EXTENDED_PAPERS_SFRAME, STORAGE_PATH
from ScienceDynamics.config.log_config import logger
import turicreate as tc
import turicreate.aggregate as agg
import pathlib
from ScienceDynamics.datasets.microsoft_academic_graph import MicrosoftAcademicGraph
from ScienceDynamics.datasets.sjr import SJR


class VenueFetcher(object):
    def __init__(self, db_client, db_name="journals", papers_collection="papers_features",
                 papers_join_collection="aminer_mag_papers", sjr_collection="sjr_journals"):
        """
        Construct venue fetcher object whcih retreive data about a venue
        :param db_client: MongoDB client object
        :param db_name: database name
        :param papers_collection:  papers collections
        :param papers_join_collection:  the collection which contains papers both from the AMiner and MAG datasets
        :param sjr_collection: SJR collection

        """
        self._db = db_client[db_name]
        self._papers_collection = self._db[papers_collection]
        self._papers_join_collection = self._db[papers_join_collection]
        self._sjr_collection = self._db[sjr_collection]
        
                


    def _get_papers_ids(self, venue_id, venue_name, venue_type, use_join_col=False):
        col = self._papers_collection
        paper_id_col = 'Paper ID'
        if use_join_col:
            col = self._papers_join_collection
            paper_id_col = 'MAG Paper ID'
        papers_ids = []
        if venue_id is not None:
            if venue_type == VenueType.journal:
                papers_ids += [j[paper_id_col] for j in col.find({"Journal ID mapped to venue name": venue_id})]
            if venue_type == VenueType.conference:
                papers_ids += [j[paper_id_col] for j in col.find({"Conference ID mapped to venue name": venue_id})]

        if venue_id is None and venue_name is not None:  # get papers by name only if venue id is missing
            papers_ids += [j[paper_id_col] for j in col.find({"Original venue name": venue_name})]

        return list(set(papers_ids))

    @lru_cache(maxsize=100)
    def get_papers_ids_dict(self, venue_id, venue_name, venue_type=VenueType.journal, issn_list=()):
        """
        Returns the venue's paper ids both that appear in the MAG paper dataset and in the AMingerMag join dataset
        :param venue_type:
        :param venue_id: the MAG venue id
        :param venue_name: the venue's name
        :param issn_list: ISSNs list
        :return: dict with the venue's papers ids. The dict has two keys 'papers_ids' & 'join_papers_ids'
        :rtyoe: dict
        :note: ISSN format \d{4}-\d{4} (with '-')
        """
        logger.info(f"Getting papers id of venue_id={venue_id},venue_name={venue_name}. and issn_list={issn_list}")
        papers_ids_dict = {'papers_ids': self._get_papers_ids(venue_id, venue_name, venue_type)}

        l = self._get_papers_ids(venue_id, venue_name, venue_type, use_join_col=True)
        for issn in issn_list:
            l += [j['MAG Paper ID'] for j in self._papers_join_collection.find({"issn": issn})]
        papers_ids_dict['join_papers_ids'] = list(set(l))

        return papers_ids_dict

    def get_sjr_dict(self, venue_name, issn_list=()):
        """
        Get's the venue SJR data from venue name's or ISSN values
        :param venue_name: venue names
        :param issn_list: issn values list (optional)
        :return: list of the matching ISSN journals from the SJR dataset
        :rtype: list<dict>
        :noteo: isssn values in SJR dataset are 8 digits
        """
        logger.info(f"Get SJR data of venue_name={venue_name}, issn_list={issn_list}")
        sjr_data = {}
        l = [j for j in self._sjr_collection.find({"Title": venue_name})]
        for issn in issn_list:
            issn = issn.replace('-', '')
            l += [j for j in self._sjr_collection.find({"ISSN": issn})]

        for j in l:
            if j["ISSN"] not in sjr_data:
                sjr_data[j["ISSN"]] = []
            sjr_data[j["ISSN"]].append(j)
        return sjr_data

    @staticmethod
    def get_valid_venues_papers_ids_sframe(min_ref_number, min_journal_papers_num):

        # Criteria I: we use only journals that have paper with valid DOI that appears in both AMiner and MAG datasets
        sf = tc.load_sframe(str(AMINER_MAG_JOIN_SFRAME))
        sf['Original venue name'] = sf['Original venue name'].apply(lambda n: n.lower())
        g = sf.groupby('Journal ID mapped to venue name', {'venue name': agg.CONCAT('Original venue name'),
                                                           'issn': agg.CONCAT('issn')})

        g['issn'] = g['issn'].apply(lambda l: list(set(l)))
        g['venue name'] = g['venue name'].apply(lambda l: list(set(l)))

        # Criteria II:  the journal as only signle name
        g = g[g['venue name'].apply(lambda l: len(l) == 1)]
        g.materialize()
        g['venue name'] = g['venue name'].apply(lambda l: l[0].strip())

        # Criteria III:  the journal's name appears in SJR
        sjr_dict = VenueFetcher.get_sjr_journals_dict()
        g = g[g['venue name'].apply(lambda v: v in sjr_dict)]

        venues_ids = set(g['Journal ID mapped to venue name'])

        # Criteria IV: Each venue need to have at least min_journal_papers_num papers with at
        # least min_ref_number refs in each paper
        dataset_dir = pathlib.Path(STORAGE_PATH)
        mag_path = dataset_dir / "MAG"/ "MicrosoftAcademicGraph.zip"
        mag = MicrosoftAcademicGraph(mag_path)
        
        sf = mag.extended_papers[
            'Journal ID mapped to venue name', 'Original venue name', 'Paper ID', 'Ref Number']
        sf = sf[sf['Ref Number'] >= min_ref_number]
        sf.materialize()
        sf = sf[sf['Journal ID mapped to venue name'].apply(lambda i: i in venues_ids)]
        sf['Journal name'] = sf['Original venue name'].apply(lambda n: n.lower().strip())
        sf.materialize()
        # Notice that with the full Papers SFrmae journal can have several names
        g = sf.groupby(['Journal ID mapped to venue name'],
                       {'Count': agg.COUNT(), 'Paper IDs List': agg.CONCAT("Paper ID"),
                        'Journals names': agg.CONCAT('Journal name')})
        g['Journals names'] = g['Journals names'].apply(lambda l: list(set(l)))
        g = g[g['Count'] >= min_journal_papers_num]
        g = g[g['Journals names'].apply(lambda l: len(l) == 1)]
        g['Journals names'] = g['Journals names'].apply(lambda l: l[0])
        g = g.rename({'Journals names': 'Journal name'})
        g.materialize()

        return g

    @staticmethod
    def get_valid_venues_papers_ids_sframe_from_mag(min_ref_number, min_journal_papers_num):
        
        dataset_dir = pathlib.Path(STORAGE_PATH)
        mag_path = _dataset_dir / "MAG"/ "MicrosoftAcademicGraph.zip"
        mag = MicrosoftAcademicGraph(mag_path)
        
        sf = mag.extended_papers[
            'Journal ID mapped to venue name', 'Original venue name', 'Paper ID', 'Ref Number']
        sf = sf[sf['Ref Number'] >= min_ref_number]
        sf.materialize()
        sf['Journal name'] = sf['Original venue name'].apply(lambda n: n.lower().strip())
        sf.materialize()
        g = sf.groupby(['Journal ID mapped to venue name'],
                       {'Count': agg.COUNT(), 'Paper IDs List': agg.CONCAT("Paper ID"),
                        'Journals names': agg.CONCAT('Journal name')})
        g['Journals names'] = g['Journals names'].apply(lambda l: list(set(l)))
        g = g[g['Count'] >= min_journal_papers_num]
        g = g[g['Journals names'].apply(lambda l: len(l) == 1)]
        g['Journals names'] = g['Journals names'].apply(lambda l: l[0])
        g = g.rename({'Journals names': 'Journal name'})
        g.materialize()
        return g

    @staticmethod
    def get_sjr_journals_dict():
        """ Returns a dict in which the keys are the journals names and the values are the journal issns
        """
        dataset_dir = pathlib.Path(STORAGE_PATH)

        sjr_path = dataset_dir / "SJR"
        sjr = SJR(sjr_path)
        d = {}
        sf = sjr.data
        sf = sf[sf['Type'] == 'journal']
        sf.materialize()
        for r in sf:
            t = r['Title'].lower().strip()
            if t not in d:
                d[t] = []
            d[t].append(r['ISSN'])
        d = {k: set(v) for k, v in d.items()}
        return d

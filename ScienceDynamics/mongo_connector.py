from pymongo import MongoClient
import turicreate as tc
from ScienceDynamics.datasets.mag_authors import AuthorsFeaturesExtractor

from ScienceDynamics.config.configs import AUTHROS_FEATURES_SFRAME, EXTENDED_PAPERS_SFRAME, SJR_SFRAME, \
    AMINER_MAG_JOIN_SFRAME, MONGO_IP
from ScienceDynamics.config.log_config import logger


class MongoDBConnector(object):
    def __init__(self, host="localhost", port=27017):
        """
        Create connection to the relevant mongo server

        """
        self._client = MongoClient(host, port)

    def insert_sframe(self, sf, db_name, collection_name, insert_rows_iter=100000, index_cols_list=()):
        """
        Insert the input SFrame into the input DB and collection
        :param sf: SFrame object
        :param db_name:  DB name
        :param collection_name:  collection names
        :param insert_rows_iter: how many rows to insert in each iteration
        :param index_cols_list:  list of columns to add index to each element in the list is atuple with the column names
            and if the column is unique


        """
        rows_num = len(sf)
        collection = self._client[db_name][collection_name]
        for i in range(0, rows_num, insert_rows_iter):
            logger.info("Inserting rows %s - %s to %s.%s" % (i, i + insert_rows_iter, db_name, collection_name))
            tmp_sf = sf[i: i + insert_rows_iter]
            json_list = [r for r in tmp_sf]
            collection.insert_many(json_list)
        for i in index_cols_list:
            self.create_index(db_name, collection_name, i[0], unique=i[1])

    def create_index(self, db_name, collection_name, index_col, unique):
        if index_col is None:
            return
        collection = self._client[db_name][collection_name]
        collection.create_index(index_col, unique=unique)

    def get_collection(self, db_name, collection_name):
        """
        Get a Mongo collection object
        :param db_name: DB name
        :param collection_name: collection name
        :return: Mongo collection
        """
        return self._client[db_name][collection_name]

    @property
    def client(self):
        """
        Return the mongo client
        :return: return Mongo Client
        :rtype: MongoClient
        """
        return self._client


def _convert_sframe_dict_key_to_str(sf, col_names):
    for c in col_names:
        sf[c] = sf[c].apply(lambda d: {str(int(float(k))): [i for i in v if i is not ''] for k, v in d.items()})
    # remove empty lists
    for c in col_names:
        sf[c] = sf[c].apply(lambda d: {k: v for k, v in d.items() if v != []})
    sf.materialize()
    return sf


def load_sframes(mag, sjr, joined):
    # from ScienceDynamics.config.configs import DATASETS_BASE_DIR
    # mag = MicrosoftAcademicGraph(DATASETS_BASE_DIR / "MicrosoftAcademicGraph.zip")
    """
    Load the journals/authors sframes to Mongo
    """
    logger.info("Loading authors features")
    md = MongoDBConnector()
    a = AuthorsFeaturesExtractor(mag)

    sf = a.get_authors_all_features_sframe()
    logger.info("Converting")

    sf = _convert_sframe_dict_key_to_str(sf, [c for c in sf.column_names() if "Year" in c])
    sf['Sequence Number by Year Dict'] = sf['Sequence Number by Year Dict'].apply(
        lambda d: {k: [str(int(float(i))) for i in v] for k, v in d.items()})
    sf.materialize()
    index_list = [('Author ID', True), ('Author name', False)]
    md.insert_sframe(sf, 'journals', 'authors_features', index_cols_list=index_list)

    logger.info("Loading papers features")
    sf = mag.extended_papers
    index_list = [('Original venue name', False), ('Paper ID', True), ('Conference ID mapped to venue name', False),
                  ('Journal ID mapped to venue name', False)]
    md.insert_sframe(sf, 'journals', 'papers_features', index_cols_list=index_list)

    logger.info("Loading SJR features")
    sf = sjr.data
    sf = sf.rename({c: c.replace(".", "") for c in sf.column_names()})
    sf['Title'] = sf['Title'].apply(lambda t: t.encode('utf-8'))
    index_list = [('Title', False), ('ISSN', False)]
    md.insert_sframe(sf, 'journals', 'sjr_journals', index_cols_list=index_list)

    sf = joined.aminer_mag_links_by_doi
    sf = sf.rename({c: c.replace(".", "") for c in sf.column_names()})
    index_list = [('Original venue name', False), ('MAG Paper ID', True), ('Conference ID mapped to venue name', False),
                  ('Journal ID mapped to venue name', False), ('issn', False)]

    md.insert_sframe(sf, 'journals', 'aminer_mag_papers', index_cols_list=index_list)

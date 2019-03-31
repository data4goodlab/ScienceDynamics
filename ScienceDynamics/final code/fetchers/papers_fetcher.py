from repoze.lru import lru_cache
from configs import logger

class PapersFetcher(object):
    def __init__(self, db_client, db_name="journals", papers_collection="papers_features", papers_join_collection="aminer_mag_papers"):
        self._db = db_client[db_name]
        self._papers_features_collection = self._db[papers_collection]
        self._papers_join_collections = self._db[papers_join_collection]

    @lru_cache(maxsize=1000000)
    def get_paper_data(self, paper_id):
        j = {}
        logger.debug("Fetching paper %s" % paper_id)
        try:
            j =  self._papers_join_collections.find({"MAG Paper ID": paper_id}).next()

        except StopIteration, e:
            try:
                j =  self._papers_features_collection.find({"Paper ID": paper_id}).next()
            except StopIteration, e:
                return None

        return j

    def get_journal_papers_data(self, journal_id):
        j = {}
        logger.debug("Fetching journal %s papers" % journal_id)
        try:
            c = self._papers_features_collection.find({'Journal ID mapped to venue name': journal_id})
            l = list(c)
        except StopIteration, e:
            return []

        return l

    def get_papers_ids_by_issn(self, issn):
        logger.debug("Fetching papers with ISSN %s" % issn)
        try:
            return [j["MAG Paper ID"] for j in self._papers_join_collections.find({"issn": issn})]

        except StopIteration, e:
            return []



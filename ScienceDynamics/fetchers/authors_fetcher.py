from functools import lru_cache
from ScienceDynamics.config.configs import AuthorNotFound
from ScienceDynamics.config.log_config import logger


class AuthorsFetcher(object):
    def __init__(self, db_client, db_name="journals", authors_features_collection="authors_features"):
        """
        Construct an author's feature object
        :param db_client: a MONGO DB client
        :param db_name: database name
        :param authors_features_collection: the name of the MONGO collection which contains the authors features

        """
        self._db = db_client[db_name]
        self._authors_features_collection = self._db[authors_features_collection]

    @lru_cache(maxsize=50000)
    def get_author_data(self, author_id=None, author_name=None):
        """
        Returns authors data as dict there are two types of data 'features' that include the author general features,
        and 'features_by_year' that include the author's features in specific year, such as papers.
        :param author_id: the author's id
        :param author_name: the author's name (can be regex)
        :return: dict with the author's data
        :rtype: dict
        """
        if author_id is not None:
            return self._get_author_by_id(author_id)
        if author_name is not None:
            return self._get_author_by_name(author_name)
        return None

    def get_author_ids_by_name(self, author_name):
        """
        Returns a list of ids for authors with the input author name
        :param author_name: author's full name or regex object
        :return: list of author_ids
        :rtype: list<str>
        :note the author_name can be regex object
        """
        try:
            return [d["Author ID"] for d in self._authors_features_collection.find({"Author name": author_name})]

        except StopIteration:
            logger.warning('Failed to find author %s ' % author_name)

    def _get_author_by_id(self, author_id):
        """
        Return author data
        :param author_id: author's id
        :return: return the author's data for author who match the input id
        :rtype: dict
        """
        j = {}
        logger.debug("Fetching author %s" % author_id)

        try:
            j = self._authors_features_collection.find({"Author ID": author_id}).next()

        except StopIteration:
            logger.warning(f'Failed to fetch author {author_id} features')
            raise AuthorNotFound()
        # converting the year keys back to int from string
        for k, d in j.items():
            if "by Year" in k and d is not None:
                j[k] = {int(y): v for y, v in d.items()}
        return j

    def _get_author_by_name(self, author_name):
        """
        Return author data
        :param author_name: author's full name
        :return: return the author's data for the first author who match the input full name
        :rtype: dict
        """
        j = {}
        logger.debug("Fetching author %s" % author_name)

        try:
            logger.debug(f"Fetching first author matching name {author_name}")
            j = self._authors_features_collection.find({"Author name": author_name}).next()

        except StopIteration:
            logger.warning(f'Failed to fetch author {author_name} features')
        # converting the year keys back to int from string
        for k, d in j.items():
            if "by Year" in k:
                j[k] = {int(y): v for y, v in d.items()}
        return j

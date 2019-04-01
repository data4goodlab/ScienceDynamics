import turicreate as tc
from functools import lru_cache

from ScienceDynamics.config.configs import FIELD_OF_STUDY_PAPERS_ID_SFRAME


class FieldsOfStudyFetcher(object):
    def __init__(self):
        self._sf = tc.load_sframe(FIELD_OF_STUDY_PAPERS_ID_SFRAME)
        self._id_name_dict = None

    def _get_id_to_name_dict(self):
        """
        Return a dict with all the fields ids as keys and their corresponding names as values
        :return: dict with all the fields ids as keys and fields' names as values
        :rtype: dict<str,str>
        """
        if self._id_name_dict is None:
            self._id_name_dict = {r['Field of study ID']: r['Field of study name'] for r in self._sf}
        return self._id_name_dict

    def _get_field_data_value(self, field_id, key_name):
        """
        Returns a dict with the data of the field id if it exists or None otherwise
        :param field_id: field id
        :param key_name: the requested attribute name
        :return: returns the field id input attribute value if one exists, or None otherwise
        """
        d = self._get_field_data_dict(field_id)
        return d.get(key_name, None)

    @lru_cache(maxsize=100)
    def _get_field_data_dict(self, field_id):
        """
        Returns the input field id data as a dict
        :param field_id: input field id
        :return: dict with the field data if it exists None otherwise
        :rtype: dict
        """
        sf = self._sf[self._sf['Field of study ID'] == field_id]
        if len(sf) == 0:
            return None
        return sf[0]

    def get_field_name(self, field_id):
        """
        Given a field of study id the function will return the field of study name
        :param field_id: field of study id
        :return: the field of study name if it exists or None otherwise
        :rtype: str
        """
        return self.field_id_to_name_dict.get(field_id, None)

    def get_field_paper_ids(self, field_id):
        """
        Returns the field of study papers ids list
        :param field_id: field of study id
        :return: a list of the field of study paperids
        :rtype: list<str>
        """
        return self._get_field_data_value(field_id, "Paper IDs")

    def get_field_level(self, field_id):
        """
        Return the field of study level
        :param field_id: field id
        :return: the field of study level value
        :rtype: int
        """
        return self._get_field_data_value(field_id, "Level")

    def get_field_papers_number(self, field_id):
        """
        Return the input field of study paper number
        :param field_id: field of study id
        :return: the fields of study number of papers
        :rtype: int
        """
        return self._get_field_data_value(field_id, "Number of Paper")

    def get_field_ids_by_level(self, level):
        """
        Returns a list of field of study ids in the input level
        :param level: field of study level
        :return: a list of field of study ids in the input level
        :rtyoe: list<str>
        """
        sf = self._sf[self._sf['Level'] == level]
        return list(sf['Field of study ID'])

    @property
    def field_id_to_name_dict(self):
        """
        Return a dict in which each key is a field id and each name is the field's name
        :return: dict with the fields ids and their names
        :rtype: dict<str, str>
        :note: while the field id is unqiue fields of study with the same name can have several ids
        """
        if self._id_name_dict is None:
            self._id_name_dict = self._get_id_to_name_dict()
        return self._id_name_dict

    def get_field_ids_by_name(self, name_regex):
        """
        The function returns fields id that match the input regex
        :param name_regex: a name regex
        :type name_regex:
        :return: the function returns dict with the fields id and name of the fields which match the input name_regex
        :rtyoe: dict<str,str>
        """
        d = {k: v for k, v in self._get_id_to_name_dict().iteritems() if name_regex.match(v) is not None}
        return d

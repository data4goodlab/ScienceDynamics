from ScienceDynamics.fetchers.authors_fetcher import AuthorsFetcher
from ScienceDynamics.fetchers.fields_of_study_fetcher import FieldsOfStudyFetcher
from ScienceDynamics.fetchers.papers_fetcher import PapersFetcher
from ScienceDynamics.fetchers.venue_fetcher import VenueFetcher
from ScienceDynamics.mongo_connector import MongoDBConnector

HOST = "localhost"
PORT = 27017
MD = MongoDBConnector(HOST, PORT)
AUTHORS_FETCHER = AuthorsFetcher(MD._client)
PAPERS_FETCHER = PapersFetcher(MD._client)
VENUE_FETCHER = VenueFetcher(MD._client)
FIELDS_OF_STUDY_FETCHER = FieldsOfStudyFetcher()
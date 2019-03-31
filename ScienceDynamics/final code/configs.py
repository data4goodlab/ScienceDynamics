import logging
from logging.handlers import RotatingFileHandler

import turicreate as tc
import turicreate.aggregate as agg
from enum import Enum

TMP_DIR = '/data/tmp'

tc.config.set_runtime_config('TURI_CACHE_FILE_LOCATIONS', TMP_DIR)
tc.config.set_runtime_config('TURI_DEFAULT_NUM_PYLAMBDA_WORKERS', 256)
tc.config.set_runtime_config('TURI_DEFAULT_NUM_GRAPH_LAMBDA_WORKERS', 256)


SFRAMES_BASE_DIR = "/data/sframes"
DATASETS_BASE_DIR = "/data/MAG"
DATASETS_AMINER_DIR = "/data/AMiner"
DATASETS_SJR_DIR = "/data/sjr"



PAPERS_ALL_FEATURES = "%s/PapersAllFeatures.sframe" % SFRAMES_BASE_DIR
FIELDS_OF_STUDY_TXT = "%s/FieldsOfStudy.txt" % DATASETS_BASE_DIR
FIELDS_OF_STUDY_SFRAME = "%s/FieldsOfStudy.sframe" % SFRAMES_BASE_DIR

FIELDS_OF_STUDY_HIERARCHY_TXT = "%s/FieldOfStudyHierarchy.txt" % DATASETS_BASE_DIR
FIELDS_OF_STUDY_HIERARCHY_SFRAME = "%s/FieldOfStudyHierarchy.sframe" % SFRAMES_BASE_DIR


PAPERS_TXT = "%s/Papers.txt" % DATASETS_BASE_DIR
PAPERS_SFRAME = "%s/Papers.sframe" % SFRAMES_BASE_DIR
EXTENDED_PAPERS_SFRAME = "%s/ExtendedPapers.sframe" % SFRAMES_BASE_DIR


CLEAN_EXTENDED_PAPERS_SFRAME = "%s/CleanExtendedPapers.sframe" % SFRAMES_BASE_DIR



FEATURES_EXTENDED_PAPERS_SFRAME = "%s/FeaturesCleanExtendedPapers.sframe" % SFRAMES_BASE_DIR

PAPER_AUTHOR_AFFILIATIONS_TXT = "%s/PaperAuthorAffiliations.txt" % DATASETS_BASE_DIR
PAPER_AUTHOR_AFFILIATIONS_SFRAME = "%s/PaperAuthorAffiliations.sframe" % SFRAMES_BASE_DIR


AUTHOR_NAMES_SFRAME = "%s/authors_names.sframe" % SFRAMES_BASE_DIR

CONFRENCES_TXT = "%s/Confrences.txt" % DATASETS_BASE_DIR
CONFRENCES_SFRAME = "%s/Confrences.sframe" % SFRAMES_BASE_DIR



JOURNALS_TXT = "%s/Journals.txt" % DATASETS_BASE_DIR
JOURNALS_SFRAME = "%s/Journals.sframe" % SFRAMES_BASE_DIR


PAPER_KEYWORDS_TXT = "%s/PaperKeywords.txt" % DATASETS_BASE_DIR
PAPER_KEYWORDS_SFRAME = "%s/PaperKeywords.sframe" % SFRAMES_BASE_DIR
PAPER_KEYWORDS_LIST_SFRAME = "%s/PaperKeywordsList.sframe" % SFRAMES_BASE_DIR


PAPER_REFERENCES_TXT = "%s/PaperReferences.txt" % DATASETS_BASE_DIR
PAPER_REFERENCES_SFRAME = "%s/PaperReferences.sframe" % SFRAMES_BASE_DIR
PAPER_REFERENCES_COUNT_SFRAME = "%s/PaperReferencesCount.sframe" % SFRAMES_BASE_DIR


EXTENDED_PAPER_REFERENCES_SFRAME = "%s/ExtendedPaperReferences.sframe" % SFRAMES_BASE_DIR
FIELD_OF_STUDY_HIERARCHY = "%s/FieldOfStudyHierarchy.sframe" % SFRAMES_BASE_DIR
KEYWORDS_SFRAME = "%s/PaperKeywords.sframe" %SFRAMES_BASE_DIR
PAPERS_CITATIONS_BYYEAR_SFRAME = "%s/PapersCitationByYear.sframe" %SFRAMES_BASE_DIR

JOURNALS_DETAILS_SFRAME = "%s/sjr.sframe" % SFRAMES_BASE_DIR

JOURNALS_PAPERS_SFRAMES_DIR = "/data/fire/sframes/journals"
CONFERENCES_PAPERS_SFRAMES_DIR = "/data/fire/sframes/conferences"

CO_AUTHORSHIP_LINK_SFRAME = "%s/co_authors_links.sframe" % SFRAMES_BASE_DIR


L3_FIELD_PAPERS_LIST_SFRAME = "%s/L3DomainPapersLists.sframe" % SFRAMES_BASE_DIR


AUTHORS_ACADEMIC_BIRTH_YEAR = "%s/AuthorsAcademicBirthYear.sframe" % SFRAMES_BASE_DIR
PAPERS_FIELDS_OF_STUDY_SFRAME = "%s/PapersFieldsOfStudy.sframe" % SFRAMES_BASE_DIR
PAPERS_ORDERED_AUTHORS_LIST_SFRAME = "%s/PapersOrderedAuthorsList.sframe" % SFRAMES_BASE_DIR

JOURNAL_AUTHORS_ACADEMIC_BIRTHYEAR_PKL = "%s/journal_authors_academic_birthyear.pkl" % SFRAMES_BASE_DIR
CONFERENCE_AUTHORS_ACADEMIC_BIRTHYEAR_PKL = "%s/conference_authors_academic_birthyear.pkl" % SFRAMES_BASE_DIR

FIELD_OF_STUDY_PAPERS_ID_SFRAME = SFRAMES_BASE_DIR + "/FieldsOfStudyPapersIds.sframe"


AUTHORS_NAMES_TXT = "%s/Authors.txt" % DATASETS_BASE_DIR
AUTHORS_NAMES_SFRAME = "%s/AuthorsNames.sframe" % SFRAMES_BASE_DIR
PAPER_URLS_TXT = "%s/PaperUrls.txt" % DATASETS_BASE_DIR
PAPER_URLS_SFRAME = "%s/PaperUrls.sframe" % SFRAMES_BASE_DIR
FIRST_NAMES_SFRAME = '%s/first_names_gender.sframe' % SFRAMES_BASE_DIR
AUTHROS_FEATURES_SFRAME = '%s/authors_features.sframe' % SFRAMES_BASE_DIR
AMINER_PAPERS_SFRAME =  "%s/PapersAMiner.sframe" % SFRAMES_BASE_DIR
AMINER_TXT_FILES = "%s/AMiner/*.txt" % DATASETS_AMINER_DIR

AMINER_MAG_JOIN_SFRAME = "%s/PapersAMinerMagJoin.sframe" %  SFRAMES_BASE_DIR

SJR_SFRAME = "%s/sjr.sframe" % SFRAMES_BASE_DIR



logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()
fileHandler = RotatingFileHandler(TMP_DIR + '/complex_network.log', mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.DEBUG)

class VenueType(Enum):
    journal = 1
    conference = 2
class AuthorNotFound(Exception):
    pass

#Mongo
from mongo_connector import MongoDBConnector
from fetchers.authors_fetcher import AuthorsFetcher
from fetchers.papers_fetcher import  PapersFetcher
from fetchers.venue_fetcher import VenueFetcher
from fetchers.fileds_of_study_fetcher import  FieldsOfStudyFetcher
HOST = "localhost"
PORT = 27017
MD = MongoDBConnector(HOST, PORT)
AUTHORS_FETCHER = AuthorsFetcher(MD._client)
PAPERS_FETCHER = PapersFetcher(MD._client)
VENUE_FETCHER = VenueFetcher(MD._client)
FIELDS_OF_STUDY_FETCHER = FieldsOfStudyFetcher()



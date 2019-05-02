import multiprocessing
from enum import Enum
import turicreate as tc
import pathlib
from dotenv import load_dotenv
import os

STORAGE_DIR_NAME = ".scidyn"
STORAGE_PATH = pathlib.Path.home().joinpath(STORAGE_DIR_NAME)
STORAGE_PATH.mkdir(exist_ok=True)

TMP_DIR = STORAGE_PATH.joinpath('tmp')
TMP_DIR.mkdir(exist_ok=True)

SFRAMES_BASE_DIR = STORAGE_PATH.joinpath("sframes")
SFRAMES_BASE_DIR.mkdir(exist_ok=True)
DATASETS_BASE_DIR = STORAGE_PATH.joinpath("MAG")
DATASETS_AMINER_DIR = STORAGE_PATH.joinpath("AMiner")
DATASETS_AMINER_DIR.mkdir(exist_ok=True)
DATASETS_SJR_DIR = STORAGE_PATH.joinpath("sjr")
DATASETS_SJR_DIR.mkdir(exist_ok=True)

cores = multiprocessing.cpu_count() // 2

tc.config.set_runtime_config('TURI_CACHE_FILE_LOCATIONS', str(TMP_DIR))
tc.config.set_runtime_config('TURI_DEFAULT_NUM_PYLAMBDA_WORKERS', cores)
tc.config.set_runtime_config('TURI_DEFAULT_NUM_GRAPH_LAMBDA_WORKERS', cores)

PAPERS_ALL_FEATURES = SFRAMES_BASE_DIR.joinpath("PapersAllFeatures.sframe")
FIELDS_OF_STUDY_TXT = DATASETS_BASE_DIR.joinpath("FieldsOfStudy.txt")
FIELDS_OF_STUDY_SFRAME = SFRAMES_BASE_DIR.joinpath("FieldsOfStudy.sframe")

FIELDS_OF_STUDY_HIERARCHY_TXT = DATASETS_BASE_DIR.joinpath("FieldOfStudyHierarchy.txt")
FIELDS_OF_STUDY_HIERARCHY_SFRAME = SFRAMES_BASE_DIR.joinpath("FieldOfStudyHierarchy.sframe")

PAPERS_TXT = DATASETS_BASE_DIR.joinpath("Papers.txt")
PAPERS_SFRAME = SFRAMES_BASE_DIR.joinpath("Papers.sframe")
EXTENDED_PAPERS_SFRAME = SFRAMES_BASE_DIR.joinpath("ExtendedPapers.sframe")

CLEAN_EXTENDED_PAPERS_SFRAME = SFRAMES_BASE_DIR.joinpath("CleanExtendedPapers.sframe")
FEATURES_EXTENDED_PAPERS_SFRAME = SFRAMES_BASE_DIR.joinpath("FeaturesCleanExtendedPapers.sframe")

PAPER_AUTHOR_AFFILIATIONS_TXT = DATASETS_BASE_DIR.joinpath("PaperAuthorAffiliations.txt")
PAPER_AUTHOR_AFFILIATIONS_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperAuthorAffiliations.sframe")

AUTHOR_NAMES_SFRAME = SFRAMES_BASE_DIR.joinpath("authors_names.sframe")

CONFERENCES_TAT = DATASETS_BASE_DIR.joinpath("Conferences.txt")
CONFERENCES_SAME = SFRAMES_BASE_DIR.joinpath("Conferences.sframe")

JOURNALS_TXT = DATASETS_BASE_DIR.joinpath("Journals.txt")
JOURNALS_SFRAME = SFRAMES_BASE_DIR.joinpath("Journals.sframe")

PAPER_KEYWORDS_TXT = DATASETS_BASE_DIR.joinpath("PaperKeywords.txt")
PAPER_KEYWORDS_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperKeywords.sframe")
PAPER_KEYWORDS_LIST_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperKeywordsList.sframe")

PAPER_REFERENCES_TXT = DATASETS_BASE_DIR.joinpath("PaperReferences.txt")
PAPER_REFERENCES_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperReferences.sframe")
PAPER_REFERENCES_COUNT_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperReferencesCount.sframe")

EXTENDED_PAPER_REFERENCES_SFRAME = SFRAMES_BASE_DIR.joinpath("ExtendedPaperReferences.sframe")
FIELD_OF_STUDY_HIERARCHY = SFRAMES_BASE_DIR.joinpath("FieldOfStudyHierarchy.sframe")
KEYWORDS_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperKeywords.sframe")
PAPERS_CITATIONS_BYYEAR_SFRAME = SFRAMES_BASE_DIR.joinpath("PapersCitationByYear.sframe")

JOURNALS_DETAILS_SFRAME = SFRAMES_BASE_DIR.joinpath("sjr.sframe")

JOURNALS_PAPERS_SFRAMES_DIR = SFRAMES_BASE_DIR.joinpath("journals")
CONFERENCES_PAPERS_SFRAMES_DIR = SFRAMES_BASE_DIR.joinpath("conferences")

CO_AUTHORSHIP_LINK_SFRAME = SFRAMES_BASE_DIR.joinpath("co_authors_links.sframe")

L3_FIELD_PAPERS_LIST_SFRAME = SFRAMES_BASE_DIR.joinpath("L3DomainPapersLists.sframe")

AUTHORS_ACADEMIC_BIRTH_YEAR = SFRAMES_BASE_DIR.joinpath("AuthorsAcademicBirthYear.sframe")
PAPERS_FIELDS_OF_STUDY_SFRAME = SFRAMES_BASE_DIR.joinpath("PapersFieldsOfStudy.sframe")
PAPERS_ORDERED_AUTHORS_LIST_SFRAME = SFRAMES_BASE_DIR.joinpath("PapersOrderedAuthorsList.sframe")

JOURNAL_AUTHORS_ACADEMIC_BIRTHYEAR_PKL = SFRAMES_BASE_DIR.joinpath("journal_authors_academic_birthyear.pkl")
CONFERENCE_AUTHORS_ACADEMIC_BIRTHYEAR_PKL = SFRAMES_BASE_DIR.joinpath("conference_authors_academic_birthyear.pkl")

FIELD_OF_STUDY_PAPERS_ID_SFRAME = SFRAMES_BASE_DIR.joinpath("FieldsOfStudyPapersIds.sframe")

AUTHORS_NAMES_TXT = DATASETS_BASE_DIR.joinpath("AuthorsNames.txt")
AUTHORS_NAMES_SFRAME = SFRAMES_BASE_DIR.joinpath("AuthorsNames.sframe")
PAPER_URLS_TXT = DATASETS_BASE_DIR.joinpath("PaperUrls.txt")
PAPER_URLS_SFRAME = SFRAMES_BASE_DIR.joinpath("PaperUrls.sframe")
AUTHROS_FEATURES_SFRAME = SFRAMES_BASE_DIR.joinpath('authors_features.sframe')
AMINER_PAPERS_SFRAME = SFRAMES_BASE_DIR.joinpath("PapersAMiner.sframe")
AMINER_TXT_FILES = DATASETS_AMINER_DIR.joinpath("AMiner/*.txt")

AMINER_MAG_JOIN_SFRAME = SFRAMES_BASE_DIR.joinpath("PapersAMinerMagJoin.sframe")

SJR_SFRAME = SFRAMES_BASE_DIR.joinpath("sjr.sframe")


class VenueType(Enum):
    journal = 1
    conference = 2

# Mongo
load_dotenv()
MONGO_IP = os.getenv("MONGO_IP")


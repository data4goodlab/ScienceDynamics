from ScienceDynamics.config.configs import SFRAMES_BASE_DIR

MAG_URL = ["https://zenodo.org/record/2628216/files/Affiliations.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/Authors.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/ConferenceInstances.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/ConferenceSeries.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/FieldsOfStudy.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/Journals.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/PaperAuthorAffiliations.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/PaperReferences.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/PaperResources.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/Papers.txt.gz?download=1",
           "https://zenodo.org/record/2628216/files/PaperUrls.txt.gz?download=1"]

MAG_URL_DICT = {"Affiliations":"https://zenodo.org/record/2628216/files/Affiliations.txt.gz?download=1",
               "Authors":"https://zenodo.org/record/2628216/files/Authors.txt.gz?download=1",
               "ConferenceInstances":"https://zenodo.org/record/2628216/files/ConferenceInstances.txt.gz?download=1",
               "ConferenceSeries":"https://zenodo.org/record/2628216/files/ConferenceSeries.txt.gz?download=1",
               "FieldsOfStudy":"https://zenodo.org/record/2628216/files/FieldsOfStudy.txt.gz?download=1",
               "Journals":"https://zenodo.org/record/2628216/files/Journals.txt.gz?download=1",
               "PaperAuthorAffiliations": "https://zenodo.org/record/2628216/files/PaperAuthorAffiliations.txt.gz?download=1",
               "PaperReferences":"https://zenodo.org/record/2628216/files/PaperReferences.txt.gz?download=1",
               "PaperResources":"https://zenodo.org/record/2628216/files/PaperResources.txt.gz?download=1",
               "Papers":"https://zenodo.org/record/2628216/files/Papers.txt.gz?download=1",
               "PaperUrls":"https://zenodo.org/record/2628216/files/PaperUrls.txt.gz?download=1"}

# MAG_URL = "https://www.dropbox.com/s/md69223d36htiep/MicrosoftAcademicGraph.zip?dl=1"
NAME_GENDER_URL = "https://www.dropbox.com/s/hkrljwkj02hzgsh/first_names_gender.sframe.zip?dl=1"
AMINER_URLS = ("https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_0.zip",
               "https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_1.zip",
               "https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_2.zip")
SJR_URLS = ((year, f"https://www.scimagojr.com/journalrank.php?year={year}&out=xls") for year in range(1999, 2019))
SJR_OPEN_URLS = ((year, f"https://www.scimagojr.com/journalrank.php?openaccess=true&year={year}&out=xls") for year in range(1999, 2019))
FIRST_NAMES_SFRAME = SFRAMES_BASE_DIR.joinpath('first_names_gender.sframe')

from ScienceDynamics.config.configs import SFRAMES_BASE_DIR

MAG_URL = "https://www.dropbox.com/s/md69223d36htiep/MicrosoftAcademicGraph.zip?dl=1"
NAME_GENDER_URL = "https://www.dropbox.com/s/hkrljwkj02hzgsh/first_names_gender.sframe.zip?dl=1"
# AMINER_URLS = ("https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_0.zip",
#                "https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_1.zip",
#                "https://academicgraphv1wu.blob.core.windows.net/aminer/aminer_papers_2.zip")
AMINER_URLS = ("https://academicgraphv2.blob.core.windows.net/oag/aminer/paper/aminer_papers_0.zip",
               "https://academicgraphv2.blob.core.windows.net/oag/aminer/paper/aminer_papers_1.zip",
               "https://academicgraphv2.blob.core.windows.net/oag/aminer/paper/aminer_papers_2.zip",
               "https://academicgraphv2.blob.core.windows.net/oag/aminer/paper/aminer_papers_3.zip")
SJR_URLS = ((year, f"https://www.scimagojr.com/journalrank.php?year={year}&out=xls") for year in range(1999, 2018))
FIRST_NAMES_SFRAME = SFRAMES_BASE_DIR.joinpath('first_names_gender.sframe')

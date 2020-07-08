# Coronavirus Research Analysis

This folder contains the Jupyter notebooks used to calculate the results of Scientometric Trends for Coronaviruses and Other Emerging Viral Infections. To generate a new pubmed.json file (Pubmed only used in Journals Trends.ipynb ) pleases follow the following steps:
1. [Download PubMed annual basline XMLs](https://www.nlm.nih.gov/databases/download/pubmed_medline.html). For example use wget to download the files: `wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*`
2. `pip install git+git://github.com/titipata/pubmed_parser.git`
3. Run `python pubmed_2_json.py  -i [path to the the directory containing pubmed data]`
4. Put the generated json under Data/pubmed.
5. Run the Pubmed section in Data Preprocessing.ipynb.



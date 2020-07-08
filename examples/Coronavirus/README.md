# Coronavirus Research Analysis

This folder contains the Jupyter notebooks used to calculate the results of Scientometric Trends for Coronaviruses and Other Emerging Viral Infections. To generate the pubmed.json file (Pubmed only used in Journals Trends.ipynb ) pleases follow the following steps:
1. Download pubmed xmls for Medline.
2. pip install git+git://github.com/titipata/pubmed_parser.git
3. Run pubmed_2_json.py
4. Put the generated json under Data/pubmed.
5. Run the Pubmed section in Data Preprocessing.ipynb.

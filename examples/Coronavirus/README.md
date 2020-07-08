# Scientometric Trends for Coronaviruses and Other Emerging Viral Infections

This folder contains the Jupyter notebooks used to calculate the results of Scientometric Trends for Coronaviruses and Other Emerging Viral Infections.


## Clean Installtion

To generate a new pubmed.json file (Pubmed only used in Journals Trends.ipynb ) pleases follow the following steps:
1. [Download PubMed annual basline XMLs](https://www.nlm.nih.gov/databases/download/pubmed_medline.html). For example use wget to download the files:<br/> `wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*`
2. `pip install git+git://github.com/titipata/pubmed_parser.git`
3. Run `python pubmed_2_json.py  -i [path to the the directory containing pubmed data]`
4. Put the generated json under Data/pubmed.
5. Run the Pubmed section in Data Preprocessing.ipynb.

Before running the coronavirus notebooks first run Data Preprocessing.ipynb to download and build the data.

## Loading Pre-computed Data
All the required files are present at TO UPDATE AFTER UPLOAD FINISHES
Download the docker image (sciencedynamics.tar).
Then run `docker load --input sciencedynamics.tar`
To use the already computed data download the data files.
Extract the zip, you should have at least 350GB free on you the hard drive.
To use the docker run:

`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The jupter notebook will open in localhost:9000.

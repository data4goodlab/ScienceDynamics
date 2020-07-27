# Scientometric Trends for Coronaviruses and Other Emerging Viral Infections

This folder contains the Jupyter notebooks used to calculate the results of Scientometric Trends for Coronaviruses and Other Emerging Viral Infections.


## Data
Pre-computed data is available at [GigaDB](http://gigadb.org/dataset/view/id/100772/token/yZNzJ1wcTIdE50KM)

## Clean Installation

To generate a new pubmed.json file (Pubmed only used in Journals Trends.ipynb ) pleases follow the following steps:
1. [Download PubMed annual basline XMLs](https://www.nlm.nih.gov/databases/download/pubmed_medline.html). For example use wget to download the files:<br/> `wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*`
2. `pip install git+git://github.com/titipata/pubmed_parser.git`
3. Create output and Data folders in the Coronavirus directory.
4. Run `python pubmed_2_json.py  -i [path to the directory containing PubMed data] -d Data/`
5. The generated JSON should be found under Data/pubmed.
6. Run the Pubmed section in Data Preprocessing.ipynb.

Before running the coronavirus notebooks first run Data Preprocessing.ipynb to download and build the data.

## Loading Pre-computed Data
Note: To use the pre-computed data you should have at least 350GB free on you the hard drive.
1. Download the docker image [sciencedynamics.tar](https://bit.ly/30KGX26).
2. Run `docker load --input sciencedynamics.tar`
3. Download and extract [scidyn2.tar.gz](https://bit.ly/304J3Lf) 
4. Download and extract [Data.tar.gz](https://bit.ly/3004b5e)  
5. Run:

`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The jupyter notebook will open in localhost:9000.

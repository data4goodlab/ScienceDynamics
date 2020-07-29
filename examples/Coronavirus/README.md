# Scientometric Trends for Coronaviruses and Other Emerging Viral Infections

This folder contains the Jupyter notebooks used to calculate the results of Scientometric Trends for Coronaviruses and Other Emerging Viral Infections.


## Data
Pre-computed data is available at [GigaDB](http://dx.doi.org/10.5524/100772).

## Clean Installation
1. Install the ScienceDynamics package (for instactions see [Installation](https://github.com/data4goodlab/ScienceDynamics#installation)).
2. To generate a new pubmed.json file (Pubmed only used in the [Journals Trends.ipynb](https://github.com/data4goodlab/ScienceDynamics/blob/master/examples/Coronavirus/Journals%20Trends.ipynb) notebook) pleases follow the following steps:
    1. [Download PubMed annual basline XMLs](https://www.nlm.nih.gov/databases/download/pubmed_medline.html). For instance, use wget to download the files:<br/> `wget -r ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/*`.
    2. `pip install git+git://github.com/titipata/pubmed_parser.git`.
    3. Create output and Data folders in the Coronavirus directory.
    4. Run `python pubmed_2_json.py  -i [path to the directory containing PubMed data] -d Data/`.
    5. The generated JSON should be found under Data/pubmed.
3. Before running the notebooks first run [Data Preprocessing.ipynb](https://github.com/data4goodlab/ScienceDynamics/blob/master/examples/Coronavirus/Data%20Preprocessing.ipynb) notebook to download and build the data.
Note: Please be sure to have several hundreds of GB free on your hard drive.

## Loading Pre-computed Data
Note: To use the pre-computed data you should have at least 350GB free on the hard drive.
1. Download the docker image [sciencedynamics.tar](https://bit.ly/30KGX26).
2. Run `docker load --input sciencedynamics.tar`.
3. Download and extract [scidyn2.tar.gz](https://bit.ly/304J3Lf).
4. Download and extract [Data.tar.gz](https://bit.ly/3004b5e).
5. Run: `docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`.
6. The Jupyter notebook will be accessible on localhost:9000.

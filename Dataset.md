# Datasets

The MAG, Aminer, and SJR datasets are downloaded automatically when you first try to access them from the code.
Also, partial pre-computed datasets can be download and imported in the code (see scidyn2.tar.gz  for instructions).
The exact URLs can be found in [config.py](https://github.com/data4goodlab/ScienceDynamics/blob/master/ScienceDynamics/datasets/configs.py).


## Scientometric Trends for Coronaviruses and Other Emerging Viral Infections

### scidyn2.tar.gz 
Constructed datasets that were computed and converted into SFrame format.
Folder structure:
1. MAG - Contains data related to Microsoft Academic Graph
2. MAG/sframes - Contains data in an SFrame format (can be loaded using turicreate).
3. MAG/sframes/Affiliations.sframe - Contains tabular data about academic affiliations.
4. MAG/sframes/ExtendedPapers.sframe - Contains tabular data about academic publications.
5. MAG/sframes/FieldsOfStudy.sframe - Contains tabular data about the fields of studies available in the MAG dataset.
6. MAG/sframes/PaperAuthorAffiliations.sframe - Contains tabular data about that connects between paper author and his/her affiliation.
7. MAG/sframes/PaperFieldsOfStudy.sframe - Contains tabular data about which paper relates to which fields of studies.
8. MAG/sframes/PaperResources.sframe - Contains tabular data about which resources that available inside papers such as code, data, etc.
9. sjr - Contains data related to scimagojr dataset.
10. sjr/scimagojr 1999 - sjr/scimagojr 2018 - Raw data from the scimagojr dataset.
11. sjr/sframes/sjr.sframe - Contains the joined data of all the raw scimagojr dataset files.

To use the data you can use the supplied docker file or install the ScienceDynamics and extract the data and then load it by the following way:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
path_to_dataset = "scidyn2"
mag = MicrosoftAcademicGraph(dataset_dir=path_to_dataset)
```

### Data.tar.gz 
The data computed for "Scientometric Trends for Coronaviruses and Other Emerging Viral Infections" paper.
Folder structure:
1. disease_names.csv - Display name and id of each disease.
2. diseases_id.csv -  Name and aliases for each disease with id.
3. diseases_list.csv - Name and aliases for each disease.
5. mag - Contains data generated based on the MAG dataset.
6. mag/diseases_mag.sframe - Contains all the publications related to the diseases from diseases_list.csv.
7. mag/diseases_med_mag.sframe - Contains all the publications related to the diseases from diseases_list.csv  and their field of study is medicine.
8. mag/diseases_viro_mag.sframe - Contains all the publications related to the diseases from diseases_list.csv and their field of study is virology.
9. mag/med_mag.sframe - Contains all the publications that their field of study is medicine.
10. mag/viro_mag.sframe - Contains all the publications their field of study is virology.
11. pubmed - Contains data generated based on the PubMed dataset.
12. pubmed/diseases_pubmed.sframe - Contains all the publications related to the diseases from diseases_list.csv.
13. pubmed/pubmed.sframe - Contain the Pubmed dataset in a SFrame format.

To access the data extract the Data.tar.gz  and then:
```
from turicreate import load_sframe
path_to_dataset = "Data/mag/diseases_mag.sframe"
sf = load_sframe(path_to_dataset)
```

## Microsoft Academic Graph
Microsoft Academic Graph is a dataset containing scientific publication records, citation relationships between those publications, as well as authors, institutions, journals, conferences, and fields of study. 
The MAG dataset we use [here](https://zenodo.org/record/2628216#.Xw1BEZMzarw) is from 22 March 2019 and contains data on over 210 million papers. 
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph()
```
Has multiple tables to see a list of methods run `dir(mag)`.

## SJR
Scientific Journal Rankings is a dataset containing the information and ranking of over 34,100 journals from 1999 to 2018, including their SJR indicator, the best quartile of the journal, and more.
```
from ScienceDynamics.datasets import SJR
sjr = SJR()
sjr.data
```
## Aminer

Aminer is an academic publication dataset that was generated from a combination of Microsoft Academic Graph (MAG) and AMiner.
The dataset contains details of more than 154.7 million publications.
```
from ScienceDynamics.datasets import Aminer
aminer = Aminer()
aminer.data
```

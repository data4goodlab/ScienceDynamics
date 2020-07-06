# ScienceDynamics (Beta)

The packge supports parsing and extraing data form bibliomeric datasets namely:
1. Microsoft Academics
2. Aminer
3. Scimagojr

This packge is an  imporved version of the code used in [Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490)
The buidling of the datasetes may take in total several hours and requires at least 450GB of free sapace on the hardrive.
We suggest using a  memory intensive server for the computions (we used a server with 1TB RAM).

## Coronavirus
Before runing the coronavirus notebooks first run Data Preprocessing.ipynb to download and buikd the data.

## Instalation
To run on Windows WSL is required.

Installtion from zero:
```
git clone https://github.com/Kagandi/ScienceDynamics
pip install -r requirements.txt
pip install pycld2 
conda install --yes pycurl #Install before wptools
pip install wptools
```
If pycld2 installtion fails install: gcc and g++.
For debain distribution run:
```
apt-get install -y  gcc
apt-get install -y g++
```

Docker:
All the required files are present on Google Drive (https://drive.google.com/drive/folders/1XYbRY9g_9qjfA45j0pAFnX1oCWhQPWfY?usp=sharing)
Download the docker image (sciencedynamics.tar).
Then run `docker load --input sciencedynamics.tar`
To use the already computed data download the data fiels.
Extract the zip, you should have at least 350GB free on you the hard drive.
To use the docker run:

`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/.scidyn2:/root/scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The jupter notebook will open in localhost:9000.


## Folder Structure:
* examples - code examples.
* examples/Coronavirus - The code used in Scientometric Trends for Coronaviruses and Other Emerging Viral Infections
* ScienceDynamics - Library source code.

## To DO
* Code Cleanup
* Refactoring
* Documentation

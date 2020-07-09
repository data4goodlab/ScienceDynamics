# ScienceDynamics (Beta)

The package supports parsing and extracting data from bibliometric datasets namely:
1. Microsoft Academics
2. Aminer
3. Scimagojr

This package is an improved version of the code used in [Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490).
The building of the datasets may take in total several hours and requires at least 450GB of free space on the hard drive. We suggest using a memory-intensive server for the computations (we used a server with 1TB RAM).

## Instalation
To run on Windows WSL is required.

Installtion from zero:
```
git clone https://github.com/data4goodlab/ScienceDynamics
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
All the required files are present at TO UPDATE AFTER UPLOAD FINISHES
Download the docker image (sciencedynamics.tar).
Then run `docker load --input sciencedynamics.tar`
To use the already computed data download the data files.
Extract the zip, you should have at least 350GB free on you the hard drive.
To use the docker run:

`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The jupter notebook will open in localhost:9000.

## Example:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph()
mag.extended_papers
```

## Folder Structure:
* examples - code examples.
* examples/Coronavirus - The code used in "Scientometric Trends for Coronaviruses and Other Emerging Viral Infections"
* ScienceDynamics - Library source code.


## To DO
* Code Cleanup
* Refactoring
* Documentation

# ScienceDynamics

The package supports parsing and extracting data from bibliometric datasets namely:
1. Microsoft Academics
2. Aminer
3. Scimagojr

This package is an improved version of the code used in [Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490).
The building of the datasets may take in total several hours and requires at least 450GB of free space on the hard drive. We suggest using a memory-intensive server for the computations (we used a server with 1TB RAM).

## Folder Structure:
* [examples](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples) - code examples.
* [examples/Coronavirus](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Coronavirus) - The code used in "Scientometric Trends for Coronaviruses and Other Emerging Viral Infections"
* [examples/Over-optimization](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Over-optimization) - The code used in "[Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490)"
* [ScienceDynamics](https://github.com/data4goodlab/ScienceDynamics/tree/master/ScienceDynamics) - Library source code.


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
If pycld2 installation fails to install: GCC and g++.
For Debian distribution run:
```
apt-get install -y  gcc
apt-get install -y g++
```

Docker:
Build or download the docker image ([sciencedynamics.tar](ftp://parrot.genomics.cn/gigadb/pub/10.5524/100001_101000/100772/sciencedynamics.tar).
Then run `docker load --input sciencedynamics.tar`
Since docker is not designed to save data persistently after the container is no longer exists, we recommend mapping the data directories to directories on the hosting machine.
For Example:
`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The jupyter notebook will open in localhost:9000.

Example of how to load the data used in "Scientometric Trends for Coronaviruses and Other Emerging Viral Infections" available [here](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Coronavirus).

## Example:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph()
mag.extended_papers
```
The data will be download when accessing a specific table.
By default the data will be saved in ~\.scidyn2.
You can select the directory to where to download/load from the data using by dataset_dir= parameter.

Also, it is possible to download all the data using one command:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph(download=True)
mag.extended_papers
```


## To Do
* Code Cleanup
* Refactoring
* Documentation

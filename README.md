# ScienceDynamics

The package supports parsing and extracting data from bibliometric datasets namely:
1. [Microsoft Academic](https://academic.microsoft.com/)
2. [AMiner](https://www.aminer.cn/)
3. [ScimagoJR](https://www.scimagojr.com/index.php)

This package is an improved version of the code used in [Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490).
Due to the size of the datasets, the building of the full datasets may take several hours and requires at least 450GB of free space on the hard drive. We suggest using a memory-intensive server for the computations (we used a server with 12 cores and 1TB RAM).

## Folder Structure:
* [examples](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples) - Code examples.
* [examples/Coronavirus](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Coronavirus) - The code used in ["Scientometric Trends for Coronaviruses and Other Emerging Viral Infections"](
https://academic.oup.com/gigascience/article-lookup/doi/10.1093/gigascience/giaa085)
* [examples/Over-optimization](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Over-optimization) - The code used in "[Over-optimization of academic publishing metrics: observing Goodhart’s Law in action](https://academic.oup.com/gigascience/article/8/6/giz053/5506490)"
* [ScienceDynamics](https://github.com/data4goodlab/ScienceDynamics/tree/master/ScienceDynamics) - Library source code.



## System Requirements

* Python 3.6, 3.7
* As much RAM as possible, smaller tables such as Affiliations should work perfectly with 16GB RAM and less.
However, larger tables such as ExtendedPapers requires a lot of RAM. Since Turi Create is not memory bound it should be able to load the data but it will drastically reduce performance and some functions will crash the kernel (out of memory).

### Supported Platforms
* macOS 10.12+
* Linux (with glibc 2.10+)
* Windows 10 (via [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10))

## Installation

Installation from zero:
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
Note: If you have libblas or liblapack errors please read Turi Create [LINUX_INSTALL.md](https://github.com/apple/turicreate/blob/master/INSTALL_ISSUES.md
). 


### Docker:
Build or download the docker image  [sciencedynamics.tar](https://bit.ly/30KGX26).
Then run `docker load --input sciencedynamics.tar`
Since docker is not designed to save data persistently, we recommend mapping the data directories to directories on the hosting machine.
For Example:

`docker run -p 127.0.0.1:9000:8888   -v $(pwd)/scidyn2:/root/.scidyn2 -v $(pwd)/ScienceDynamics/examples/Coronavirus/Data/:/ScienceDynamics/examples/Coronavirus/Data/  --name corona sciencedynamics:1.2`

The Jupyter notebook will be accessible on localhost:9000.

Example of how to load the data used in "Scientometric Trends for Coronaviruses and Other Emerging Viral Infections" available [here](https://github.com/data4goodlab/ScienceDynamics/tree/master/examples/Coronavirus#loading-pre-computed-data).

## Example:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph()
mag.extended_papers
```
The data will be downloaded when accessing a specific table.
By default, the data will be saved in ~\.scidyn2.
You can select the directory to where to download/load from the data using by dataset_dir= parameter.

Also, it is possible to download all the data using one command:
```
from ScienceDynamics.datasets import MicrosoftAcademicGraph
mag = MicrosoftAcademicGraph(download=True)
mag.extended_papers
```


## To Do
* Refactoring
* Documentation

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
```
git clone git://github.com/Kagandi/anomalous-vertices-detection.git
pip install -r requirements.txt
```
## Folder Structure:
* examples - code examples.
* examples/Coronavirus - The code used in Scientometric Trends for Coronaviruses and Other Emerging Viral Infections
* ScienceDynamics - Library source code.

## To DO
* Code Cleanup
* Refactoring
* Documentation

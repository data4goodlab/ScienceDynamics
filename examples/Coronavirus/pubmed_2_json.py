import pubmed_parser as pp
from pathlib import Path
import json
from tqdm import tqdm 
import sys
import argparse
from itertools import islice

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', required=True,
                        help='Path to the pubmed data folder')
    parser.add_argument('-l', type=int, default=0,
                        help='Limit the number of files to read')
    
    args = vars(parser.parse_args())
    res = []
    pubmed_files = Path(args["i"]).rglob("*.xml.gz")

    if args["l"]:
        pubmed_files = islice(pubmed_files,0,args["l"])
    for xml_path in tqdm(pubmed_files):
        res+= pp.parse_medline_xml(str(xml_path))

    with open("pubmed.json", "w") as f:
        f.write(json.dumps(res))

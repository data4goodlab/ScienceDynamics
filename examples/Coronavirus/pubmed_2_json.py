import pubmed_parser as pp
from pathlib import Path
import json
from tqdm import tqdm 

res = []
for xml_path in tqdm(Path("ftp.ncbi.nlm.nih.gov/pubmed/baseline").glob("*.xml.gz")):
    res+= pp.parse_medline_xml(str(xml_path))

with open("pubmed.json", "w") as f:
    f.write(json.dumps(res))

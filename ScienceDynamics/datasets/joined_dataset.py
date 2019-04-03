import pathlib
import re

from ScienceDynamics.datasets.aminer import Aminer
from ScienceDynamics.datasets.microsoft_academic_graph import MicrosoftAcademicGraph
from ScienceDynamics.datasets.sjr import SJR
from ScienceDynamics.datasets.utils import save_sframe
import turicreate.aggregate as agg


class JoinedDataset(object):
    def __init__(self, dataset_dir, sjr_path=None, aminer_path=None, mag_path=None):
        self._dataset_dir = pathlib.Path(dataset_dir)
        self._dataset_dir.mkdir(exist_ok=True)
        self._sframe_dir = self._dataset_dir / "sframes"
        self._sframe_dir.mkdir(exist_ok=True)
        if sjr_path is None:
            sjr_path = self._dataset_dir / "SJR"
        if aminer_path is None:
            aminer_path = self._dataset_dir / "Aminer"
        if mag_path is None:
            mag_path = self._dataset_dir / "SJR"
        self.aminer = Aminer(aminer_path)
        self.mag = MicrosoftAcademicGraph(mag_path)
        self.sjr = SJR(sjr_path)

    @property
    @save_sframe(sframe="PapersAMinerMagJoin.sframe")
    def aminer_mag_links_by_doi(self):
        """
        Create Links Sframe that match papers from the MAG dataset
        with papers from the AMiner dataset based on the papers DOI
        :return:
        """
        extended_papers = self.mag.extended_papers
        g1 = extended_papers.groupby('Paper Document Object Identifier (DOI)', {'Count': agg.COUNT()})
        s1 = set(g1[g1['Count'] > 1]['Paper Document Object Identifier (DOI)'])
        extended_papers = extended_papers[
            extended_papers['Paper Document Object Identifier (DOI)'].apply(lambda doi: doi not in s1)]
        extended_papers.materialize()

        aminer = self.aminer.data
        g2 = aminer.groupby('doi', {'Count': agg.COUNT()})
        s2 = set(g2[g2['Count'] > 1]['doi'])
        aminer = aminer[aminer['doi'].apply(lambda doi: doi not in s2)]
        aminer.materialize()

        aminer_mag = extended_papers.join(aminer, {'Paper Document Object Identifier (DOI)': 'doi'})
        aminer_mag['title_len'] = aminer_mag['title'].apply(lambda t: len(t))
        aminer_mag['title_len2'] = aminer_mag['Original paper title'].apply(lambda t: len(t))
        aminer_mag = aminer_mag[aminer_mag['title_len'] > 0]
        aminer_mag = aminer_mag[aminer_mag['title_len2'] > 0]

        aminer_mag = aminer_mag.rename({"Paper ID": "MAG Paper ID", "id": "Aminer Paper ID"})
        return aminer_mag.remove_columns(['title_len', 'title_len2'])

    def create_aminer_mag_sjr_sframe(self, year):
        """
        Creates a unified SFrame of AMiner, MAG, and the SJR datasets
        :param year: year to use for SJR data
        :return: SFrame with AMiner, MAG, and SJR data
        :rtype: SFrame
        """
        sf = self.aminer_mag_links_by_doi
        sf = sf[sf['issn'] != None]
        sf = sf[sf['issn'] != 'null']
        sf.materialize()
        r = re.compile(r"(\d+)-(\d+)")
        sf['issn_str'] = sf['issn'].apply(lambda i: "".join(r.findall(i)[0]) if len(r.findall(i)) > 0 else None)
        sf = sf[sf['issn_str'] != None]
        sjr_sf = self.sjr.data
        sjr_sf = sjr_sf[sjr_sf['Year'] == year]
        return sf.join(sjr_sf, on={'issn_str': "ISSN"})

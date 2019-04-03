import pathlib
from turicreate import SFrame, load_sframe
from ScienceDynamics.datasets.configs import AMINER_URLS
from ScienceDynamics.datasets.utils import download_file, save_load
import turicreate.aggregate as agg


import zipfile


class Aminer(object):
    def __init__(self, dataset_dir=None):
        self._dataset_dir = pathlib.Path(dataset_dir)
        self._dataset_dir.mkdir(exist_ok=True)
        self._sframe_dir = self._dataset_dir / "sframes"
        self._sframe_dir.mkdir(exist_ok=True)
        for i, url in enumerate(AMINER_URLS):
            aminer_file = self._dataset_dir / f'aminer_papers_{i}.zip'
            if not pathlib.Path(aminer_file).exists():
                download_file(url, aminer_file)
                with zipfile.ZipFile(aminer_file, 'r') as f:
                    f.extractall(self._dataset_dir)

    @property
    @save_load(sframe="PapersAMiner.sframe")
    def data(self):
        """
        Create AMiner Papers sFrame from the AMiner text files. After creating the SFrame, it is save to AMINER_PAPERS_SFRAME
        """

        return SFrame.read_json(self._dataset_dir.joinpath("AMiner/*.txt"), orient='lines')

import pathlib
import re

from turicreate import SFrame
from ScienceDynamics.datasets.configs import SJR_URLS
from ScienceDynamics.datasets.utils import download_file, save_sframe


class SJR(object):
    def __init__(self, dataset_dir=None):
        self._dataset_dir = pathlib.Path(dataset_dir)
        self._dataset_dir.mkdir(exist_ok=True)
        self._sframe_dir = self._dataset_dir / "sframes"
        self._sframe_dir.mkdir(exist_ok=True)
        for y, url in SJR_URLS:
            sjr_file = self._dataset_dir / f'scimagojr {y}.csv'
            if not pathlib.Path(sjr_file).exists():
                download_file(url, sjr_file)

    @property
    @save_sframe(sframe="sjr.sframe")
    def data(self):
        """
        Creating the SJR SFrame from CSV files
        :note: please notice that each file name contains the SJR report year
        """
        sjr_sf = SFrame()
        for p in self._dataset_dir.iterdir():
            if p.suffix == ".csv":
                y = int(re.match(r'.*([1-3][0-9]{3})', p.name).group(1))
                sf = SFrame.read_csv(str(p))
                sf['Year'] = y
                sf = sf.rename({"Total Docs. (%s)" % y: "Total Docs."})
                extra_cols = ["Categories"]
                for c in extra_cols:
                    if c not in sf.column_names():
                        sf[c] = ''
                sjr_sf = sjr_sf.append(sf)

        r_issn = re.compile('(\\d{8})')
        sjr_sf['Issn'] = sjr_sf['Issn'].apply(lambda i: r_issn.findall(i))
        return sjr_sf.stack('Issn', new_column_name='ISSN')

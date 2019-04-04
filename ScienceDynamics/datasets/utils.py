import functools
import os
import pathlib

import requests
from tqdm import tqdm
from turicreate import load_sframe


def download_file(url, output_path, exist_overwrite=False, min_size=-1, verbose=True):
    # Todo handle requests.exceptions.ConnectionError
    if exist_overwrite or not os.path.exists(output_path):
        r = requests.get(url, stream=True)
        total_size = int(r.headers.get('content-length', 0))
        size_read = 0
        if total_size > min_size:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, disable=not verbose) as pbar:
                with open(output_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            size_read = min(total_size, size_read + 1024)
                            pbar.update(len(chunk))


def lazy_property(fn):
    """
    Decorator that makes a property lazy-evaluated.
    """
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazy_property


def save_sframe(sframe):
    def decorator_repeat(func):
        @functools.wraps(func)
        def wrapper_repeat(self, *args, **kwargs):
            sframe_path = pathlib.Path(self._sframe_dir).joinpath(sframe)
            if not sframe_path.exists():
                value = func(self, *args, **kwargs)
                value.save(str(sframe_path))
            else:
                value = load_sframe(str(sframe_path))
            return value

        return wrapper_repeat

    return decorator_repeat

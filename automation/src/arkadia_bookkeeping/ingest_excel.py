from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from acccli.io import expand_inputs, load_excels


def ingest_excel(patterns: Iterable[str]) -> pd.DataFrame:
    paths = expand_inputs(patterns)
    return load_excels(paths)


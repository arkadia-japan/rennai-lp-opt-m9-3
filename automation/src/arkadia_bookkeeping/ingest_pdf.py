from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd

from acccli.io import expand_inputs, load_pdfs


def ingest_pdf(patterns: Iterable[str], has_header: bool = True) -> pd.DataFrame:
    paths = expand_inputs(patterns)
    return load_pdfs(paths, has_header=has_header)


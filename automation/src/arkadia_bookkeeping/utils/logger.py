from __future__ import annotations

import logging
from pathlib import Path
from datetime import datetime


def setup_run_logger(outdir: Path, debug: bool = False) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    log_path = outdir / f"run_{ts}.log"
    logging.basicConfig(
        filename=str(log_path),
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    return log_path


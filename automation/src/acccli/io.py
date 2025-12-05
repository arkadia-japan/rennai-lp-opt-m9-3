from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd


def expand_inputs(inputs: Iterable[str]) -> List[Path]:
    paths: list[Path] = []
    for pattern in inputs:
        p = Path(pattern)
        if any(ch in pattern for ch in "*?["):
            paths.extend(sorted(Path().glob(pattern)))
        elif p.is_dir():
            # Collect common formats
            for pat in ("*.csv", "*.xlsx", "*.xls", "*.pdf"):
                paths.extend(sorted(p.rglob(pat)))
        else:
            paths.append(p)
    unique = []
    seen = set()
    for p in paths:
        if p.exists() and p not in seen:
            unique.append(p)
            seen.add(p)
    return unique


def load_csvs(paths: Iterable[Path], encoding: str = "utf-8") -> pd.DataFrame:
    frames = []
    for p in paths:
        if p.suffix.lower() == ".csv":
            df = pd.read_csv(p, encoding=encoding)
            df = df.reset_index(drop=False).rename(columns={"index": "__idx0"})
            df["__source_file"] = str(p)
            df["__source_sheet"] = "CSV"
            # Assume header row occupies one line; data starts at 2
            df["__source_row"] = df["__idx0"].astype(int) + 2
            df = df.drop(columns=["__idx0"], errors="ignore")
            frames.append(df)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_excels(paths: Iterable[Path]) -> pd.DataFrame:
    frames = []
    for p in paths:
        if p.suffix.lower() in {".xlsx", ".xls"}:
            try:
                # Read all sheets; returns dict of DataFrames when sheet_name=None
                dfs = pd.read_excel(p, sheet_name=None)
                if isinstance(dfs, dict):
                    for sname, df in dfs.items():
                        if df is not None and not df.empty:
                            df = df.reset_index(drop=False).rename(columns={"index": "__idx0"})
                            df["__source_file"] = str(p)
                            df["__source_sheet"] = str(sname)
                            df["__source_row"] = df["__idx0"].astype(int) + 2
                            df = df.drop(columns=["__idx0"], errors="ignore")
                            frames.append(df)
                elif dfs is not None and not dfs.empty:
                    df = dfs.reset_index(drop=False).rename(columns={"index": "__idx0"})
                    df["__source_file"] = str(p)
                    df["__source_sheet"] = "Sheet1"
                    df["__source_row"] = df["__idx0"].astype(int) + 2
                    df = df.drop(columns=["__idx0"], errors="ignore")
                    frames.append(df)
            except Exception as e:
                raise RuntimeError(f"Failed to read Excel: {p}: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_pdfs(paths: Iterable[Path], has_header: bool = True) -> pd.DataFrame:
    try:
        import pdfplumber  # type: ignore
    except Exception:
        # pdf support not installed
        return pd.DataFrame()

    frames = []
    for p in paths:
        if p.suffix.lower() != ".pdf":
            continue
        try:
            with pdfplumber.open(p) as pdf:
                for pidx, page in enumerate(pdf.pages):
                    tables = page.extract_tables()
                    for tidx, tbl in enumerate(tables or []):
                        if not tbl or not any(row for row in tbl):
                            continue
                        if has_header and len(tbl) >= 2:
                            header = tbl[0]
                            rows = tbl[1:]
                            df = pd.DataFrame(rows, columns=header)
                        else:
                            df = pd.DataFrame(tbl)
                        df = df.reset_index(drop=False).rename(columns={"index": "__idx0"})
                        df["__source_file"] = str(p)
                        df["__source_sheet"] = f"PDF p{pidx+1}-t{tidx+1}"
                        df["__source_row"] = df["__idx0"].astype(int) + (2 if has_header else 1)
                        df = df.drop(columns=["__idx0"], errors="ignore")
                        frames.append(df)
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {p}: {e}")
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def load_inputs(paths: Iterable[Path], encoding: str = "utf-8", pdf_has_header: bool = True) -> pd.DataFrame:
    csv_df = load_csvs(paths, encoding=encoding)
    xls_df = load_excels(paths)
    pdf_df = load_pdfs(paths, has_header=pdf_has_header)
    frames = [df for df in (csv_df, xls_df, pdf_df) if not df.empty]
    if not frames:
        return pd.DataFrame()
    # Align columns by union; missing columns will be introduced as NaN
    all_cols = sorted(set().union(*[df.columns for df in frames]))
    norm = [df.reindex(columns=all_cols) for df in frames]
    return pd.concat(norm, ignore_index=True)

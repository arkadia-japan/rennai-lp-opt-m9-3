from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, List, Optional

import pandas as pd
import unicodedata

from acccli.core import _to_decimal


JP_DATE_FORMATS = ["%Y/%m/%d", "%Y-%m-%d", "%Y.%m.%d"]


def parse_date_series(s: pd.Series, explicit_format: Optional[str] = None) -> pd.Series:
    if explicit_format:
        return pd.to_datetime(s, format=explicit_format, errors="coerce")
    # try common JP formats
    dt = pd.to_datetime(s, errors="coerce", format=None)
    if dt.notna().any():
        return dt
    for fmt in JP_DATE_FORMATS:
        dt = pd.to_datetime(s, errors="coerce", format=fmt)
        if dt.notna().any():
            return dt
    return pd.to_datetime(s, errors="coerce")


def quantize_yen(x: object) -> Decimal:
    d = _to_decimal(x)
    # Round to 0 decimals (yen integer)
    return d.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    def _norm_memo(v: object) -> str:
        try:
            return unicodedata.normalize("NFKC", str(v)).strip().lower()
        except Exception:
            return ""
    key = (
        pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)
        + "|"
        + df["amount"].map(lambda x: str(quantize_yen(x)))
        + "|"
        + df.get("memo", df.get("description", pd.Series(["" for _ in range(len(df))]))).map(_norm_memo)
    )
    mask = ~key.duplicated()
    return df.loc[mask].copy()


def to_unified_schema(df: pd.DataFrame) -> pd.DataFrame:
    from acccli.core import unify_schema

    # convert to unified schema then coerce amount to yen integer strings
    uni = unify_schema(df)
    if not uni.empty:
        uni["amount"] = uni["amount"].map(lambda x: str(quantize_yen(x)))
    return uni


from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional, Tuple

import pandas as pd


def _norm(s: object) -> str:
    return unicodedata.normalize("NFKC", str(s)).strip().lower()


def filter_activity(df: pd.DataFrame, selected: Optional[List[str]] = None, not_set: Optional[List[str]] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty or "activity" not in df.columns:
        return df, pd.DataFrame(columns=df.columns.tolist() + ["reason"])  # nothing to exclude
    col = df["activity"].map(_norm)
    excl_rows = []
    mask = pd.Series([True] * len(df))
    if selected:
        sel = {_norm(v) for v in selected}
        mask = col.isin(sel)
    if not_set:
        ns = {_norm(v) for v in not_set}
        mask = mask & (~col.isin(ns))
    excluded = df.loc[~mask].copy()
    if not excluded.empty:
        excluded["reason"] = "activity_excluded"
    return df.loc[mask].copy(), excluded


def exclude_private(df: pd.DataFrame, token: Optional[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not token or df.empty:
        return df, pd.DataFrame(columns=df.columns.tolist() + ["reason"])  # no change
    pattern = re.compile(_norm(token))
    def match_row(row) -> bool:
        desc = _norm(row.get("memo", row.get("description", "")))
        note = _norm(row.get("remarks", row.get("note", "")))
        return bool(pattern.search(desc) or pattern.search(note))
    is_private = df.apply(match_row, axis=1)
    excluded = df.loc[is_private].copy()
    if not excluded.empty:
        excluded["reason"] = "non_business"
    return df.loc[~is_private].copy(), excluded


def exclude_loan_inflows(df: pd.DataFrame, keywords: Optional[List[str]]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if not keywords or df.empty:
        return df, pd.DataFrame(columns=df.columns.tolist() + ["reason"])  # no change
    pats = [re.compile(_norm(k)) for k in keywords]
    def is_inflow(row) -> bool:
        io = _norm(row.get("inout", ""))
        return io in {"in", "income", "deposit", "入", "入金", "収入"} or (str(row.get("amount", "")).startswith("-") is False)
    def hit(row) -> bool:
        if not is_inflow(row):
            return False
        text = _norm(row.get("memo", row.get("description", "")))
        return any(p.search(text) for p in pats)
    mask = df.apply(hit, axis=1)
    excluded = df.loc[mask].copy()
    if not excluded.empty:
        excluded["reason"] = "借入入金"
    return df.loc[~mask].copy(), excluded


def tag_repayment_expense(df: pd.DataFrame, keywords: Optional[List[str]]) -> pd.DataFrame:
    if not keywords or df.empty:
        return df
    pats = [re.compile(_norm(k)) for k in keywords]
    def is_outflow(row) -> bool:
        io = _norm(row.get("inout", ""))
        return io in {"out", "expense", "withdrawal", "出", "出金", "支出"} or (str(row.get("amount", "")).startswith("-"))
    def hit(row) -> bool:
        if not is_outflow(row):
            return False
        text = _norm(row.get("memo", row.get("description", "")))
        return any(p.search(text) for p in pats)
    mask = df.apply(hit, axis=1)
    if "category" not in df.columns:
        df = df.assign(category=None)
    df.loc[mask, "category"] = "expense"
    return df


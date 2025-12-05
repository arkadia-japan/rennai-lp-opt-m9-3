from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, Iterable, List, Union

import yaml
from pydantic import BaseModel
import re
import unicodedata


ColumnRef = Union[str, List[str]]
RegexRef = Union[str, List[str]]


class ColumnMapping(BaseModel):
    date: ColumnRef = "date"
    account: ColumnRef = "account"
    amount: ColumnRef = "amount"
    # Optional alternative numeric sources
    debit: Optional[ColumnRef] = None
    credit: Optional[ColumnRef] = None
    in_amount: Optional[ColumnRef] = None
    out_amount: Optional[ColumnRef] = None
    dept: Optional[ColumnRef] = "dept"
    subaccount: Optional[ColumnRef] = None
    memo: Optional[ColumnRef] = None
    inout: Optional[ColumnRef] = None
    activity: Optional[ColumnRef] = None
    remarks: Optional[ColumnRef] = None
    # Explicit revenue flag column (e.g., values like "売上入金", "その他入金")
    revenue_flag: Optional[ColumnRef] = None

    # Regex-based hints (case-insensitive, NFKC normalized)
    date_regex: Optional[RegexRef] = None
    account_regex: Optional[RegexRef] = None
    amount_regex: Optional[RegexRef] = None
    debit_regex: Optional[RegexRef] = None
    credit_regex: Optional[RegexRef] = None
    in_amount_regex: Optional[RegexRef] = None
    out_amount_regex: Optional[RegexRef] = None
    dept_regex: Optional[RegexRef] = None
    subaccount_regex: Optional[RegexRef] = None
    memo_regex: Optional[RegexRef] = None
    inout_regex: Optional[RegexRef] = None
    activity_regex: Optional[RegexRef] = None
    remarks_regex: Optional[RegexRef] = None
    revenue_flag_regex: Optional[RegexRef] = None

    def _norm(self, s: str) -> str:
        return unicodedata.normalize("NFKC", s).strip().lower()

    def _first_match(self, candidates: Optional[ColumnRef], existing: Iterable[str]) -> Optional[str]:
        if candidates is None:
            return None
        if isinstance(candidates, str):
            return candidates if candidates in existing else None
        for c in candidates:
            if c in existing:
                return c
        return None

    def _first_regex_match(self, patterns: Optional[RegexRef], existing: Iterable[str]) -> Optional[str]:
        if patterns is None:
            return None
        pats = [patterns] if isinstance(patterns, str) else list(patterns)
        # Precompute normalized headers
        norm_map = {self._norm(col): col for col in existing}
        for pat in pats:
            try:
                rx = re.compile(pat, flags=re.IGNORECASE)
            except re.error:
                continue
            for ncol, orig in norm_map.items():
                if rx.search(ncol):
                    return orig
        return None

    def build_renames(self, existing_columns: Iterable[str]) -> Dict[str, str]:
        existing = list(existing_columns)
        mapping: Dict[str, str] = {}
        order = (
            ("date", "date"),
            ("account", "account"),
            ("amount", "amount"),
            ("debit", "debit"),
            ("credit", "credit"),
            ("in_amount", "in_amount"),
            ("out_amount", "out_amount"),
            ("dept", "dept"),
            ("subaccount", "subaccount"),
            ("memo", "memo"),
            ("inout", "inout"),
            ("activity", "activity"),
            ("remarks", "remarks"),
            ("revenue_flag", "revenue_flag"),
        )
        # 1) Try explicit candidates
        for attr, target in order:
            src = self._first_match(getattr(self, attr), existing)
            if src:
                mapping[src] = target
        # 2) Try regex-based hints for fields still unmapped
        regex_attrs = {
            "date": self.date_regex,
            "account": self.account_regex,
            "amount": self.amount_regex,
            "debit": self.debit_regex,
            "credit": self.credit_regex,
            "in_amount": self.in_amount_regex,
            "out_amount": self.out_amount_regex,
            "dept": self.dept_regex,
            "subaccount": self.subaccount_regex,
            "memo": self.memo_regex,
            "inout": self.inout_regex,
            "activity": self.activity_regex,
            "remarks": self.remarks_regex,
            "revenue_flag": self.revenue_flag_regex,
        }
        already = set(mapping.values())
        for target, patterns in regex_attrs.items():
            if target in already:
                continue
            src = self._first_regex_match(patterns, existing)
            if src and src not in mapping:
                mapping[src] = target
        return mapping

    def resolved_required(self, existing_columns: Iterable[str]) -> set[str]:
        existing = list(existing_columns)
        req = set()
        for attr in ("date", "account", "amount"):
            src = self._first_match(getattr(self, attr), existing)
            if src:
                req.add(src)
        return req


class Template(BaseModel):
    name: str
    filename_regex: Optional[List[str]] = None
    header_regex: Optional[List[str]] = None
    columns: ColumnMapping = ColumnMapping()


def select_template(templates: Optional[List[Template]], existing_columns: Iterable[str], source_name: str) -> Optional[Template]:
    if not templates:
        return None
    cols = list(existing_columns)
    for t in templates:
        ok = False
        if t.filename_regex:
            for pat in t.filename_regex:
                try:
                    if re.search(pat, source_name, flags=re.IGNORECASE):
                        ok = True
                        break
                except re.error:
                    continue
        if not ok and t.header_regex:
            for pat in t.header_regex:
                try:
                    rx = re.compile(pat, flags=re.IGNORECASE)
                except re.error:
                    continue
                if any(rx.search(unicodedata.normalize("NFKC", c).lower()) for c in cols):
                    ok = True
                    break
        if ok:
            return t
    return None


class Settings(BaseModel):
    columns: ColumnMapping = ColumnMapping()
    date_format: Optional[str] = None
    account_map: Optional[Dict[str, str]] = None
    # Optional: map account -> category: one of {revenue, expense, other}
    category_map: Optional[Dict[str, str]] = None
    # PDF parsing behavior (best-effort)
    pdf_has_header: bool = True
    # Amount parsing options
    strip_currency_symbols: list[str] = ["¥", "円", "JPY"]
    parse_parentheses_negative: bool = True
    templates: Optional[List[Template]] = None
    revenue_flag_values: List[str] = ['売上入金']
    expense_include: Optional[Dict[str, List[str]]] = None
    expense_exclude: Optional[Dict[str, List[str]]] = None
    revenue_exclude: Optional[Dict[str, List[str]]] = None
    activity_exclude_values: List[str] = ["要設定"]


def load_settings(data: Optional[dict] = None) -> Settings:
    return Settings(**(data or {}))


def load_config(config_path: Optional[Path] = None) -> Settings:
    """Load configuration from YAML file."""
    if config_path and config_path.exists():
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return Settings(**(data or {}))
    return Settings()






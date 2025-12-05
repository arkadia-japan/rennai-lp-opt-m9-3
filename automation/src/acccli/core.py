from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, Optional, Tuple, List

import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
import unicodedata
import re


def normalize_columns(df: pd.DataFrame, mapping: Dict[str, str]) -> pd.DataFrame:
    existing = {k: v for k, v in mapping.items() if k in df.columns}
    renamed = df.rename(columns=existing)
    return renamed


def parse_dates(df: pd.DataFrame, date_format: Optional[str]) -> pd.DataFrame:
    if "date" not in df.columns:
        return df
    if date_format:
        df["date"] = pd.to_datetime(df["date"], format=date_format, errors="coerce")
    else:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df


def apply_account_map(df: pd.DataFrame, mapping: Optional[Dict[str, str]]) -> pd.DataFrame:
    if mapping and "account" in df.columns:
        df["account"] = df["account"].map(mapping).fillna(df["account"])  
    return df


def filter_period(
    df: pd.DataFrame, start: Optional[str] = None, end: Optional[str] = None
) -> pd.DataFrame:
    if "date" not in df.columns:
        return df
    out = df
    if start:
        start_dt = pd.Timestamp(start)
        out = out[out["date"] >= start_dt]
    if end:
        end_dt = pd.Timestamp(end)
        out = out[out["date"] <= end_dt]
    return out


def aggregate(
    df: pd.DataFrame,
    by: Iterable[str],
    date_format: Optional[str] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    account_map: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df = parse_dates(df, date_format)
    df = apply_account_map(df, account_map)
    if "amount" in df.columns:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = filter_period(df, start, end)
    # Deduplicate by date+amount(monetary 2dp)+memo
    if "date" in df.columns and "amount" in df.columns:
        def _norm_memo(s: object) -> str:
            try:
                return unicodedata.normalize("NFKC", str(s)).strip().lower()
            except Exception:
                return ""
        key = (
            df["date"].dt.date.astype(str)
            + "|"
            + df["amount"].round(2).map(lambda x: f"{x:.2f}")
            + "|"
            + df.get("memo", pd.Series([""] * len(df))).map(_norm_memo)
        )
        df = df.loc[~key.duplicated()].copy()
    dims = [c for c in by if c in df.columns]
    if not dims:
        dims = []
    grouped = df.groupby(dims, dropna=False, as_index=False)["amount"].sum()
    return grouped.sort_values(by=dims + (["amount"] if dims else []), ignore_index=True)


def validate(
    df: pd.DataFrame,
    required_cols: Iterable[str],
    date_format: Optional[str] = None,
    account_map: Optional[Dict[str, str]] = None,
) -> Dict[str, int]:
    result = {
        "missing_columns": 0,
        "invalid_dates": 0,
        "non_numeric_amounts": 0,
        "unmapped_accounts": 0,
    }

    missing = [c for c in required_cols if c not in df.columns]
    result["missing_columns"] = len(missing)
    if missing:
        return result

    parsed = parse_dates(df.copy(), date_format)
    result["invalid_dates"] = int(parsed["date"].isna().sum())

    if "amount" in df.columns:
        numeric = pd.to_numeric(df["amount"], errors="coerce")
        result["non_numeric_amounts"] = int(numeric.isna().sum())

    if account_map and "account" in df.columns:
        unmapped = df["account"].map(account_map).isna()
        result["unmapped_accounts"] = int(unmapped.sum())

    return result


def summarize_year(
    df: pd.DataFrame,
    year: int,
    date_format: Optional[str] = None,
    account_map: Optional[Dict[str, str]] = None,
    category_map: Optional[Dict[str, str]] = None,
) -> Dict[str, Decimal]:
    if df.empty:
        return {"revenue": Decimal("0"), "expense": Decimal("0"), "profit": Decimal("0")}
    df = df.copy()
    df = parse_dates(df, date_format)
    df = apply_account_map(df, account_map)
    if "amount" in df.columns:
        # Keep as string -> Decimal to avoid float summation issues
        df["amount"] = df["amount"].astype(str)
    # Filter for the calendar year exactly
    start = pd.Timestamp(year=year, month=1, day=1)
    end = pd.Timestamp(year=year, month=12, day=31, hour=23, minute=59, second=59)
    if "date" in df.columns:
        df = df[(df["date"] >= start) & (df["date"] <= end)]

    def to_decimal(x: str) -> Decimal:
        try:
            # Normalize locale-like commas if any
            y = x.replace(",", "")
            return Decimal(y)
        except Exception:
            return Decimal("0")

    # Deduplicate by date+amount+memo (after parsing)
    if "date" in df.columns and "amount" in df.columns:
        def _norm_memo(s: object) -> str:
            try:
                return unicodedata.normalize("NFKC", str(s)).strip().lower()
            except Exception:
                return ""
        amt2 = df["amount"].map(lambda x: _to_decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        key = df["date"].dt.date.astype(str) + "|" + amt2.astype(str) + "|" + df.get("memo", pd.Series([""] * len(df))).map(_norm_memo)
        df = df.loc[~key.duplicated()].copy()

    # Category determination
    if category_map and "account" in df.columns:
        cats = df["account"].map(category_map)
    else:
        # Fallback: infer by sign
        amt_dec = df["amount"].map(to_decimal)
        cats = amt_dec.map(lambda d: "revenue" if d >= 0 else "expense")
    # Apply expense inclusion hints if provided via DataFrame attrs
    include = getattr(df, "attrs", {}).get("expense_include") if hasattr(df, "attrs") else None
    if isinstance(include, dict):
        acct_pats = include.get("account_regex") or []
        memo_pats = include.get("memo_regex") or []
        act_pats = include.get("activity_regex") or []
        def _match(text: Optional[str], pats: list[str]) -> bool:
            if not text or not pats:
                return False
            t = unicodedata.normalize("NFKC", str(text)).lower()
            for pat in pats:
                try:
                    if re.search(pat, t, flags=re.IGNORECASE):
                        return True
                except re.error:
                    continue
            return False
        if "account" in df.columns:
            mask = df["account"].astype(str).map(lambda x: _match(x, acct_pats))
        else:
            mask = pd.Series([False] * len(df))
        if "memo" in df.columns:
            mask = mask | df["memo"].astype(str).map(lambda x: _match(x, memo_pats))
        if "activity" in df.columns:
            mask = mask | df["activity"].astype(str).map(lambda x: _match(x, act_pats))
        cats = cats.mask(mask, "expense")
    # Apply revenue exclusion (e.g., loans) -> mark as 'other'
    rev_ex = getattr(df, "attrs", {}).get("revenue_exclude") if hasattr(df, "attrs") else None
    if isinstance(rev_ex, dict):
        acct_p = rev_ex.get("account_regex") or []
        memo_p = rev_ex.get("memo_regex") or []
        act_p = rev_ex.get("activity_regex") or []
        inout_p = rev_ex.get("inout_regex") or []
        def _m(text: Optional[str], pats: list[str]) -> bool:
            if not text or not pats:
                return False
            t = unicodedata.normalize("NFKC", str(text)).lower()
            for pat in pats:
                try:
                    if re.search(pat, t, flags=re.IGNORECASE):
                        return True
                except re.error:
                    continue
            return False
        mask = pd.Series([False] * len(df))
        if "account" in df.columns:
            mask = mask | df["account"].astype(str).map(lambda x: _m(x, acct_p))
        if "memo" in df.columns:
            mask = mask | df["memo"].astype(str).map(lambda x: _m(x, memo_p))
        if "activity" in df.columns:
            mask = mask | df["activity"].astype(str).map(lambda x: _m(x, act_p))
        if "inout" in df.columns:
            mask = mask | df["inout"].astype(str).map(lambda x: _m(x, inout_p))
        cats = cats.mask(mask, "other")

    # Apply revenue flag: only values listed count as revenue; other positive inflows become 'other'
    rf_vals = getattr(df, "attrs", {}).get("revenue_flag_values") if hasattr(df, "attrs") else None
    if isinstance(rf_vals, list) and "revenue_flag" in df.columns:
        def _in_flag(x: Optional[str]) -> bool:
            if x is None:
                return False
            t = unicodedata.normalize("NFKC", str(x)).lower().strip()
            for v in rf_vals:
                try:
                    if t == unicodedata.normalize("NFKC", str(v)).lower().strip():
                        return True
                except Exception:
                    continue
            return False
        is_flagged = df["revenue_flag"].map(_in_flag)
        is_positive = df["amount"].map(to_decimal).ge(0)
        mask_other = (~is_flagged) & is_positive
        cats = cats.mask(mask_other, "other")
    df = df.assign(_cat=cats, _amt=df["amount"].map(to_decimal))

    revenue = sum((df.loc[df["_cat"] == "revenue", "_amt"]).tolist(), start=Decimal("0"))
    expense = sum((df.loc[df["_cat"] == "expense", "_amt"]).tolist(), start=Decimal("0"))
    # If expense amounts are positive (by mapping), treat as absolute; else negative -> take abs
    if expense > 0:
        expense_total = expense
    else:
        expense_total = -expense
    profit = (revenue - expense_total).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return {
        "revenue": revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "expense": expense_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
        "profit": profit,
    }


def _to_decimal(value: object) -> Decimal:
    try:
        s = str(value)
        # Normalize full-width numbers to ASCII
        s = unicodedata.normalize("NFKC", s)
        s = s.replace(",", "")
        # Handle parentheses negative e.g. (1234.56)
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        return Decimal(s)
    except Exception:
        return Decimal("0")


def synthesize_amount_columns(df: pd.DataFrame) -> pd.DataFrame:
    """If amount is missing but paired columns exist, synthesize amount.

    Rules:
      - if both 'in_amount' and 'out_amount' exist: amount = in - out
      - elif both 'credit' and 'debit' exist: amount = credit - debit
      - else keep existing 'amount' if present
    All inputs are parsed via _to_decimal, output is string with 2 decimals.
    """
    if "amount" in df.columns and df["amount"].notna().any():
        return df
    in_cols = {c for c in df.columns if c == "in_amount"}
    out_cols = {c for c in df.columns if c == "out_amount"}
    if in_cols and out_cols:
        indec = df["in_amount"].map(_to_decimal)
        outdec = df["out_amount"].map(_to_decimal)
        amt = (indec - outdec).map(lambda d: d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        return df.assign(amount=amt.astype(str))
    if "credit" in df.columns and "debit" in df.columns:
        cred = df["credit"].map(_to_decimal)
        deb = df["debit"].map(_to_decimal)
        amt = (cred - deb).map(lambda d: d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        return df.assign(amount=amt.astype(str))
    return df


def prepare_transactions(
    df: pd.DataFrame,
    year: int,
    date_format: Optional[str] = None,
    account_map: Optional[Dict[str, str]] = None,
    category_map: Optional[Dict[str, str]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split into included (for aggregation) and excluded (with reasons).

    Included columns: date(ISO), month(YYYY-MM), account, dept(optional), amount(Decimal str), category.
    Excluded columns: reason, along with available original fields (date/account/amount/dept).
    """
    if df.empty:
        return pd.DataFrame(columns=["date", "month", "account", "dept", "amount", "category"]), pd.DataFrame(
            columns=["reason", "date", "account", "amount", "dept"]
        )
    work = df.copy()
    work = parse_dates(work, date_format)
    work = apply_account_map(work, account_map)
    work = synthesize_amount_columns(work)

    included_rows: List[Dict[str, object]] = []
    excluded_rows: List[Dict[str, object]] = []

    seen_keys: set[str] = set()
    for idx, row in work.iterrows():
        r_date = row.get("date")
        r_acc = row.get("account")
        r_amt = row.get("amount")
        r_dept = row.get("dept") if "dept" in work.columns else None
        r_sub = row.get("subaccount") if "subaccount" in work.columns else None
        r_memo = row.get("memo") if "memo" in work.columns else None
        r_inout = row.get("inout") if "inout" in work.columns else None
        r_activity = row.get("activity") if "activity" in work.columns else None
        r_remarks = row.get("remarks") if "remarks" in work.columns else None
        r_revflag = row.get("revenue_flag") if "revenue_flag" in work.columns else None
        r_src_file = row.get("__source_file") if "__source_file" in work.columns else None
        r_src_sheet = row.get("__source_sheet") if "__source_sheet" in work.columns else None
        r_src_row = row.get("__source_row") if "__source_row" in work.columns else None

        if pd.isna(r_acc) or str(r_acc).strip() == "":
            excluded_rows.append({"reason": "missing_account", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue
        # date check
        if pd.isna(r_date):
            excluded_rows.append({"reason": "invalid_date", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue
        try:
            d = pd.Timestamp(r_date)
        except Exception:
            excluded_rows.append({"reason": "invalid_date", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue
        if d.year != year:
            excluded_rows.append({"reason": "out_of_period", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue

        # amount check
        if pd.isna(r_amt):
            excluded_rows.append({"reason": "non_numeric_amount", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue
        try:
            # Clean currency symbols if present in strings
            dec = _to_decimal(r_amt)
        except Exception:
            excluded_rows.append({"reason": "non_numeric_amount", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue

        # Duplicate check: date + amount(2dp) + memo(NFKC lower)
        mnorm = unicodedata.normalize("NFKC", str(r_memo)).strip().lower() if r_memo is not None else ""
        dup_key = f"{d.date().isoformat()}|{dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)}|{mnorm}"
        if dup_key in seen_keys:
            excluded_rows.append({"reason": "duplicate", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
            continue
        seen_keys.add(dup_key)

        # Non-business exclusion via df.attrs['expense_exclude'] regex on account/memo/activity/inout
        ex_rules = getattr(df, "attrs", {}).get("expense_exclude") if hasattr(df, "attrs") else None
        if isinstance(ex_rules, dict):
            acct_pats = ex_rules.get("account_regex") or []
            memo_pats = ex_rules.get("memo_regex") or []
            act_pats = ex_rules.get("activity_regex") or []
            inout_pats = ex_rules.get("inout_regex") or []

            def _match_any(text: Optional[str], pats: list[str]) -> bool:
                if not text or not pats:
                    return False
                t = unicodedata.normalize("NFKC", str(text)).lower()
                for pat in pats:
                    try:
                        if re.search(pat, t, flags=re.IGNORECASE):
                            return True
                    except re.error:
                        continue
                return False

            if _match_any(r_acc, acct_pats) or _match_any(r_memo, memo_pats) or _match_any(r_activity, act_pats) or _match_any(r_inout, inout_pats):
                excluded_rows.append({"reason": "non_business", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
                continue

        # category
        cat = None
        if category_map is not None:
            cat = category_map.get(str(r_acc))
        # in/out classification overrides when provided
        if r_inout is not None and str(r_inout).strip() != "":
            val = str(r_inout).strip().lower()
            inflow = {"in", "income", "deposit", "入", "入金", "収入"}
            outflow = {"out", "expense", "withdrawal", "出", "出金", "支出"}
            if val in outflow:
                cat = "expense"
                dec = abs(dec)
            elif val in inflow:
                # If revenue flag is configured and present, only count as revenue when flagged
                rf_vals = getattr(df, "attrs", {}).get("revenue_flag_values") if hasattr(df, "attrs") else None
                if r_revflag is not None and isinstance(rf_vals, list):
                    norm_val = unicodedata.normalize("NFKC", str(r_revflag)).strip().lower()
                    norm_set = {unicodedata.normalize("NFKC", str(v)).strip().lower() for v in rf_vals}
                    if norm_val in norm_set:
                        cat = "revenue"
                    else:
                        cat = "other"
                else:
                    cat = "revenue"
                dec = abs(dec)
        # Expense inclusion regex rules (account/memo/activity)
        if not cat:
            try:
                from acccli.config import Settings  # type: ignore
            except Exception:
                Settings = None
            # Access via closure is not available here; pass rules via params would be cleaner,
            # but we can infer from category_map type. Instead, rely on sign fallback first; include rules will be applied below.
            pass

        if not cat and any(v is not None for v in [r_acc, r_memo, r_activity]):
            # Best-effort: check environment for inclusion patterns via a hidden attribute on df (optional)
            # If not present, this block is skipped. The CLI can set df.attrs['expense_include'].
            include = getattr(df, "attrs", {}).get("expense_include") if hasattr(df, "attrs") else None
            patterns = {"account_regex": [], "memo_regex": [], "activity_regex": []}
            if isinstance(include, dict):
                for k in patterns.keys():
                    if isinstance(include.get(k), list):
                        patterns[k] = include.get(k)  # type: ignore
            # Normalize helper
            def _match_any(text: Optional[str], pats: list[str]) -> bool:
                if not text or not pats:
                    return False
                t = unicodedata.normalize("NFKC", str(text)).lower()
                for pat in pats:
                    try:
                        if re.search(pat, t, flags=re.IGNORECASE):
                            return True
                    except re.error:
                        continue
                return False

            if _match_any(r_acc, patterns["account_regex"]) or _match_any(r_memo, patterns["memo_regex"]) or _match_any(r_activity, patterns["activity_regex"]):
                cat = "expense"

        # Revenue exclusion (e.g., loans): log and exclude from included breakdown
        if not cat:
            rev_ex = getattr(df, "attrs", {}).get("revenue_exclude") if hasattr(df, "attrs") else None
            if isinstance(rev_ex, dict):
                acct_pats = rev_ex.get("account_regex") or []
                memo_pats = rev_ex.get("memo_regex") or []
                act_pats = rev_ex.get("activity_regex") or []
                inout_pats = rev_ex.get("inout_regex") or []
                def _m(text: Optional[str], pats: list[str]) -> bool:
                    if not text or not pats:
                        return False
                    t = unicodedata.normalize("NFKC", str(text)).lower()
                    for pat in pats:
                        try:
                            if re.search(pat, t, flags=re.IGNORECASE):
                                return True
                        except re.error:
                            continue
                    return False
                if _m(r_acc, acct_pats) or _m(r_memo, memo_pats) or _m(r_activity, act_pats) or _m(r_inout, inout_pats):
                    excluded_rows.append({"reason": "revenue_excluded", "date": r_date, "account": r_acc, "amount": r_amt, "dept": r_dept})
                    continue

        # Revenue flag fallback: if positive inflow with revenue_flag present but not matching, classify as other
        if not cat and dec >= 0 and r_revflag is not None:
            rf_vals = getattr(df, "attrs", {}).get("revenue_flag_values") if hasattr(df, "attrs") else None
            if isinstance(rf_vals, list):
                norm_val = unicodedata.normalize("NFKC", str(r_revflag)).strip().lower()
                norm_set = {unicodedata.normalize("NFKC", str(v)).strip().lower() for v in rf_vals}
                if norm_val in norm_set:
                    cat = "revenue"
                else:
                    cat = "other"

        if not cat:
            cat = "revenue" if dec >= 0 else "expense"

        included_rows.append(
            {
                "date": d.date().isoformat(),
                "month": f"{d.year:04d}-{d.month:02d}",
                "account": r_acc,
                "dept": r_dept,
                "subaccount": r_sub,
                "memo": r_memo,
                "inout": r_inout,
                "activity": r_activity,
                "remarks": r_remarks,
                "amount": str(dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "category": cat,
                "source_file": r_src_file,
                "source_sheet": r_src_sheet,
                "source_row": r_src_row,
            }
        )

    inc_cols = [
        "date",
        "month",
        "account",
        "dept",
        "subaccount",
        "memo",
        "inout",
        "activity",
        "remarks",
        "amount",
        "category",
        "source_file",
        "source_sheet",
        "source_row",
    ]
    inc_df = pd.DataFrame(included_rows, columns=inc_cols) if included_rows else pd.DataFrame(columns=inc_cols)
    exc_df = pd.DataFrame(excluded_rows, columns=["reason", "date", "account", "amount", "dept"]) if excluded_rows else pd.DataFrame(columns=["reason", "date", "account", "amount", "dept"])
    return inc_df, exc_df


def monthly_and_yearly_summary(included_breakdown: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Compute monthly revenue/expense/profit and yearly totals from included rows.

    included_breakdown must contain columns: month, category, amount (decimal string)
    """
    months = sorted(included_breakdown["month"].dropna().unique().tolist()) if not included_breakdown.empty else []
    monthly_rows: List[Dict[str, object]] = []
    year_tot_rev = Decimal("0")
    year_tot_exp = Decimal("0")

    for m in months:
        dfm = included_breakdown[included_breakdown["month"] == m]
        rev = Decimal("0")
        exp = Decimal("0")
        for _, r in dfm.iterrows():
            amt = _to_decimal(r.get("amount"))
            if r.get("category") == "expense":
                exp += (amt if amt > 0 else -amt)
            elif r.get("category") == "revenue":
                rev += amt
            else:
                # 'other' or unknown category: ignore in revenue/expense totals
                pass
        prof = (rev - exp).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        monthly_rows.append(
            {
                "month": m,
                "revenue": str(rev.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "expense": str(exp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "profit": str(prof),
            }
        )
        year_tot_rev += rev
        year_tot_exp += exp

    year_prof = (year_tot_rev - year_tot_exp).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    monthly_df = pd.DataFrame(monthly_rows, columns=["month", "revenue", "expense", "profit"]) if monthly_rows else pd.DataFrame(columns=["month", "revenue", "expense", "profit"]).astype({})
    yearly_df = pd.DataFrame(
        [
            {
                "revenue": str(year_tot_rev.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "expense": str(year_tot_exp.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                "profit": str(year_prof),
            }
        ]
    )
    return monthly_df, yearly_df


def filter_activity(
    df: pd.DataFrame,
    exclude_values: Optional[List[str]] = None,
    include_values: Optional[List[str]] = None,
) -> pd.DataFrame:
    if df.empty or "activity" not in df.columns:
        return df
    col_norm = df["activity"].astype(str).map(lambda x: unicodedata.normalize("NFKC", x).strip().lower())
    if include_values is not None:
        inc = {unicodedata.normalize("NFKC", str(v)).strip().lower() for v in include_values}
        return df.loc[col_norm.isin(inc)].copy()
    if exclude_values is not None:
        exc = {unicodedata.normalize("NFKC", str(v)).strip().lower() for v in exclude_values}
        return df.loc[~col_norm.isin(exc)].copy()
    return df


def filter_non_business(df: pd.DataFrame, rules: Optional[Dict[str, List[str]]]) -> pd.DataFrame:
    if df.empty or not isinstance(rules, dict):
        return df
    acct_pats = rules.get("account_regex") or []
    memo_pats = rules.get("memo_regex") or []
    act_pats = rules.get("activity_regex") or []
    inout_pats = rules.get("inout_regex") or []

    def _match_series(series: pd.Series, pats: list[str]) -> pd.Series:
        if not pats or series.empty:
            return pd.Series([False] * len(series), index=series.index)
        s = series.astype(str).map(lambda x: unicodedata.normalize("NFKC", x).lower())
        mask = pd.Series([False] * len(series), index=series.index)
        for pat in pats:
            try:
                mask = mask | s.str.contains(pat, case=False, regex=True)
            except re.error:
                continue
        return mask

    mask = pd.Series([False] * len(df))
    if "account" in df.columns:
        mask = mask | _match_series(df["account"], acct_pats)
    if "memo" in df.columns:
        mask = mask | _match_series(df["memo"], memo_pats)
    if "activity" in df.columns:
        mask = mask | _match_series(df["activity"], act_pats)
    if "inout" in df.columns:
        mask = mask | _match_series(df["inout"], inout_pats)
    return df.loc[~mask].copy()


def unify_schema(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with unified schema:
    [date, description, inout, amount, activity, note, source_file, source_sheet, source_row]
    Missing columns are filled with empty values. Amount is quantized to 2 decimals as string.
    Date is ISO date (YYYY-MM-DD) when possible.
    """
    if df is None or df.empty:
        return pd.DataFrame(
            columns=[
                "date",
                "description",
                "inout",
                "amount",
                "activity",
                "note",
                "source_file",
                "source_sheet",
                "source_row",
            ]
        )
    out = pd.DataFrame()
    # Date -> ISO date
    if "date" in df.columns:
        try:
            dts = pd.to_datetime(df["date"], errors="coerce")
            out["date"] = dts.dt.date.astype(str)
        except Exception:
            out["date"] = df["date"].astype(str)
    else:
        out["date"] = ""
    # Description from memo/description
    if "memo" in df.columns:
        out["description"] = df["memo"].astype(str)
    elif "description" in df.columns:
        out["description"] = df["description"].astype(str)
    else:
        out["description"] = ""
    # In/Out
    out["inout"] = df.get("inout", pd.Series(["" for _ in range(len(df))])).astype(str)
    # Amount as 2dp string
    if "amount" in df.columns:
        am = df["amount"].map(lambda x: _to_decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
        out["amount"] = am.astype(str)
    else:
        out["amount"] = ""
    # Activity
    out["activity"] = df.get("activity", pd.Series(["" for _ in range(len(df))])).astype(str)
    # Note from remarks
    if "remarks" in df.columns:
        out["note"] = df["remarks"].astype(str)
    elif "note" in df.columns:
        out["note"] = df["note"].astype(str)
    else:
        out["note"] = ""
    # Source info
    # Prefer already normalized names if present
    if "source_file" in df.columns or "source_sheet" in df.columns or "source_row" in df.columns:
        out["source_file"] = df.get("source_file", pd.Series(["" for _ in range(len(df))])).astype(str)
        out["source_sheet"] = df.get("source_sheet", pd.Series(["" for _ in range(len(df))])).astype(str)
        out["source_row"] = df.get("source_row", pd.Series(["" for _ in range(len(df))])).astype(str)
    else:
        out["source_file"] = df.get("__source_file", pd.Series(["" for _ in range(len(df))])).astype(str)
        out["source_sheet"] = df.get("__source_sheet", pd.Series(["" for _ in range(len(df))])).astype(str)
        out["source_row"] = df.get("__source_row", pd.Series(["" for _ in range(len(df))])).astype(str)
    # Ensure column order
    cols = [
        "date",
        "description",
        "inout",
        "amount",
        "activity",
        "note",
        "source_file",
        "source_sheet",
        "source_row",
    ]
    return out.reindex(columns=cols)

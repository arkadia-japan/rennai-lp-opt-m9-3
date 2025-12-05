from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

import logging
from datetime import datetime
from typing import Dict, Any
import yaml
import pandas as pd

from arkadia_bookkeeping.ingest_excel import ingest_excel
from arkadia_bookkeeping.ingest_pdf import ingest_pdf
from arkadia_bookkeeping.normalize import parse_date_series, to_unified_schema, deduplicate
from arkadia_bookkeeping.rules import (
    filter_activity as rule_filter_activity,
    exclude_private as rule_exclude_private,
    exclude_loan_inflows as rule_exclude_loan_inflows,
    tag_repayment_expense as rule_tag_repayment_expense,
)
from arkadia_bookkeeping.aggregate import monthly_and_yearly
from arkadia_bookkeeping.outputs import write_excel
from acccli.core import synthesize_amount_columns


app = typer.Typer(help="Arkadia Bookkeeping CLI (wrapper over acccli)")


@app.command()
def report(
    year: int = typer.Option(2025, "--year", help="Target year"),
    excel_glob: List[str] = typer.Option([], "--excel-glob", help="Excel glob(s)", show_default=False),
    pdf_glob: List[str] = typer.Option([], "--pdf-glob", help="PDF glob(s)", show_default=False),
    schema: Optional[Path] = typer.Option(None, "--schema", help="Path to schema.yaml"),
    outdir: Optional[Path] = typer.Option(None, "--outdir", help="Base output directory"),
    debug: bool = typer.Option(False, "--debug", help="Verbose debug logging"),
):
    # setup logging
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    out_base = Path("out") if outdir is None else Path(outdir)
    out_base.mkdir(parents=True, exist_ok=True)
    log_path = out_base / f"run_{ts}.log"
    logging.basicConfig(filename=log_path, level=logging.DEBUG if debug else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("arkadia report start")

    # Load schema
    cfg: Dict[str, Any] = {}
    if schema and Path(schema).exists():
        cfg = yaml.safe_load(Path(schema).read_text(encoding="utf-8")) or {}

    # Ingest
    df_list: List[pd.DataFrame] = []
    if excel_glob:
        df_list.append(ingest_excel(excel_glob))
    if pdf_glob:
        df_list.append(ingest_pdf(pdf_glob, has_header=cfg.get("pdf_has_header", True)))
    df_raw = pd.concat([d for d in df_list if d is not None and not d.empty], ignore_index=True) if df_list else pd.DataFrame()
    if df_raw.empty:
        typer.echo("No input rows after ingestion.")
        raise typer.Exit(code=2)

    # Column mapping (simple): try schema.columns and excel.default_sheet_mapping
    def build_renames(cols: List[str]) -> Dict[str, str]:
        ren: Dict[str, str] = {}
        mapping = cfg.get("columns", {})
        alias = {"description": "memo", "note": "remarks"}
        def add_mapping(srcs, target):
            if isinstance(srcs, list):
                for s in srcs:
                    if s in cols and target not in ren.values():
                        ren[s] = target
                        break
            elif isinstance(srcs, str) and srcs in cols and target not in ren.values():
                ren[srcs] = target
        for key, srcs in mapping.items():
            target = alias.get(key, key)
            add_mapping(srcs, target)
        excel_cfg = cfg.get("excel", {}).get("default_sheet_mapping", {})
        for key, srcs in excel_cfg.items():
            target = alias.get(key, key)
            add_mapping(srcs, target)
        return ren

    renames = build_renames(df_raw.columns.tolist())
    df = df_raw.rename(columns=renames)

    # Date parse & amount synthesis
    if "date" in df.columns:
        dt = parse_date_series(df["date"], explicit_format=cfg.get("date_format"))
        df["date"] = dt.dt.strftime("%Y-%m-%d")
    df = synthesize_amount_columns(df)

    # Apply PDF sign rules based on templates (filename regex)
    def apply_pdf_sign_rules(_df: pd.DataFrame, cfg: Dict[str, Any]) -> pd.DataFrame:
        templates = (cfg.get("pdf") or {}).get("templates") or []
        if not templates or _df.empty:
            return _df
        import re
        def n(s: object) -> str:
            import unicodedata
            return unicodedata.normalize("NFKC", str(s)).strip().lower()
        out = _df.copy()
        for t in templates:
            detect = (t.get("detect") or {}).get("any_regex") or []
            cols = t.get("columns") or {}
            sign_rule = cols.get("sign_rule")
            if not detect or not sign_rule:
                continue
            # build mask by filename match
            mask = pd.Series([False] * len(out))
            for pat in detect:
                try:
                    rx = re.compile(pat.strip(), flags=re.IGNORECASE)
                except re.error:
                    continue
                m = out.get("__source_file", pd.Series([""] * len(out))).astype(str).map(lambda x: bool(rx.search(x)))
                mask = mask | m
            if not mask.any():
                continue
            # adjust sign/inout heuristically using description text
            desc = out.get("memo", out.get("description", pd.Series(["" for _ in range(len(out))]))).astype(str)
            if sign_rule == "credit_positive_debit_negative":
                # 入金系ワードで正、出金系ワードで負
                inflow_words = ["入金", "預け入れ", "預入", "deposit", "credit"]
                outflow_words = ["出金", "引出", "withdrawal", "debit"]
                def infer_inout(txt: str) -> Optional[str]:
                    low = n(txt)
                    if any(w in low for w in map(n, inflow_words)):
                        return "入金"
                    if any(w in low for w in map(n, outflow_words)):
                        return "出金"
                    return None
                inferred = desc.map(infer_inout)
                # set inout and amount sign
                pos_mask = mask & (inferred == "入金")
                neg_mask = mask & (inferred == "出金")
                # amount to Decimal
                out.loc[pos_mask, "inout"] = "入金"
                out.loc[neg_mask, "inout"] = "出金"
                from acccli.core import _to_decimal
                out.loc[pos_mask, "amount"] = out.loc[pos_mask, "amount"].map(lambda x: str(_to_decimal(x).copy_abs()))
                out.loc[neg_mask, "amount"] = out.loc[neg_mask, "amount"].map(lambda x: str(-_to_decimal(x).copy_abs()))
            elif sign_rule == "debit_negative_only":
                refund_words = ["返金", "キャンセル", "取消", "払戻"]
                def is_refund(txt: str) -> bool:
                    return any(w in n(txt) for w in map(n, refund_words))
                is_ref = desc.map(is_refund)
                from acccli.core import _to_decimal
                # default negative (出金) if not refund; refund becomes positive (入金)
                dmask = mask & (~is_ref)
                pmask = mask & is_ref
                out.loc[dmask, "inout"] = "出金"
                out.loc[pmask, "inout"] = "入金"
                out.loc[dmask, "amount"] = out.loc[dmask, "amount"].map(lambda x: str(-_to_decimal(x).copy_abs()))
                out.loc[pmask, "amount"] = out.loc[pmask, "amount"].map(lambda x: str(_to_decimal(x).copy_abs()))
        return out

    df = apply_pdf_sign_rules(df, cfg)

    # Unified schema
    uni = to_unified_schema(df)

    # Deduplicate first (log duplicates)
    # Compute key for duplicates
    def make_key(_df: pd.DataFrame) -> pd.Series:
        import unicodedata
        def norm(v: object) -> str:
            try:
                return unicodedata.normalize("NFKC", str(v)).strip().lower()
            except Exception:
                return ""
        return (
            pd.to_datetime(_df["date"], errors="coerce").dt.date.astype(str)
            + "|" + _df["amount"].astype(str) + "|" + _df["description"].map(norm)
        )
    key = make_key(uni)
    dup_mask = key.duplicated()
    dup_exc = uni.loc[dup_mask].copy()
    if not dup_exc.empty:
        dup_exc["reason"] = "重複"
    uni = uni.loc[~dup_mask].copy()

    # Year filter
    if "date" in uni.columns:
        dts = pd.to_datetime(uni["date"], errors="coerce")
        start = pd.Timestamp(year=year, month=1, day=1)
        end = pd.Timestamp(year=year, month=12, day=31, hour=23, minute=59, second=59)
        in_year = (dts >= start) & (dts <= end)
        out_year = ~in_year
        out_exc = uni.loc[out_year].copy()
        if not out_exc.empty:
            out_exc["reason"] = "対象外期間"
        uni = uni.loc[in_year].copy()
    else:
        out_exc = pd.DataFrame(columns=uni.columns.tolist())

    # Activity selection
    selected_vals = cfg.get("excel", {}).get("boolean_values", {}).get("selected", [])
    not_set_vals = cfg.get("activity_exclude_values", []) or [cfg.get("rules", {}).get("activity_not_set_token")] if cfg.get("rules", {}).get("activity_not_set_token") else []
    uni, act_exc = rule_filter_activity(uni, selected=selected_vals, not_set=not_set_vals)
    if not act_exc.empty:
        act_exc["reason"] = "アクティビティ未選択"

    # Private spend exclusion
    priv_token = cfg.get("rules", {}).get("private_spend_token")
    uni, priv_exc = rule_exclude_private(uni, token=priv_token)
    if not priv_exc.empty:
        priv_exc["reason"] = "私用・事業外"

    # Loan inflow exclusion
    loan_kw = cfg.get("rules", {}).get("loan_keywords_in_desc")
    uni, loan_exc = rule_exclude_loan_inflows(uni, keywords=loan_kw)
    if not loan_exc.empty:
        loan_exc["reason"] = "借入入金"

    # Classification
    uni = rule_tag_repayment_expense(uni, keywords=cfg.get("rules", {}).get("repayment_keywords"))
    # Sales activity token
    sat = cfg.get("rules", {}).get("sales_activity_token")
    def norm(s: object) -> str:
        import unicodedata
        return unicodedata.normalize("NFKC", str(s)).strip().lower()
    if sat:
        mask_in = uni["inout"].map(norm).isin({"in","income","deposit","入","入金","収入"}) | (~uni["amount"].astype(str).str.startswith("-"))
        mask_sales = mask_in & (uni["activity"].map(norm) == norm(sat))
        # set revenue if not already expense by repayment
        uni.loc[mask_sales & (uni.get("category").ne("expense") if "category" in uni.columns else True), "category"] = "revenue"
    # Fallback: outflows -> expense, inflows -> other (if not set yet)
    io = uni["inout"].map(norm)
    outflow = io.isin({"out","expense","withdrawal","出","出金","支出"}) | (uni["amount"].astype(str).str.startswith("-"))
    uni.loc[outflow & (uni.get("category").isna() if "category" in uni.columns else True), "category"] = "expense"
    uni.loc[(~outflow) & (uni.get("category").isna() if "category" in uni.columns else True), "category"] = "other"

    # Build breakdown and exclusions
    # Flags: add minimal flags to breakdown
    breakdown = uni.copy()
    breakdown["flags"] = ""
    # mark activity selected
    if "activity" in breakdown.columns:
        sel_set = {norm(x) for x in (selected_vals or [])}
        if sel_set:
            breakdown.loc[breakdown["activity"].map(norm).isin(sel_set), "flags"] = breakdown["flags"].astype(str) + ("|activity_selected")
    # mark sales activity
    if sat:
        breakdown.loc[(breakdown["activity"].map(norm) == norm(sat)) & (breakdown["category"] == "revenue"), "flags"] = breakdown["flags"].astype(str) + ("|sales_activity")
    # mark repayment expense
    rep_kw = [norm(x) for x in (cfg.get("rules", {}).get("repayment_keywords") or [])]
    if rep_kw:
        def has_rep(row):
            text = norm(row.get("description", ""))
            return any(k in text for k in rep_kw)
        breakdown.loc[(breakdown["category"] == "expense") & breakdown.apply(has_rep, axis=1), "flags"] = breakdown["flags"].astype(str) + ("|repayment_expense")
    breakdown["flags"] = breakdown["flags"].str.strip("|")

    exclusions = pd.concat([d for d in [dup_exc, out_exc, act_exc, priv_exc, loan_exc] if d is not None and not d.empty], ignore_index=True) if any([not dup_exc.empty, not out_exc.empty, not act_exc.empty, not priv_exc.empty, not loan_exc.empty]) else pd.DataFrame(columns=breakdown.columns.tolist() + ["reason"]).head(0)
    if not exclusions.empty and "flags" not in exclusions.columns:
        exclusions["flags"] = exclusions["reason"].astype(str)

    # Aggregate
    mon_df, yr_df = monthly_and_yearly(breakdown)

    # Split sheets
    sales_df = breakdown[breakdown["category"] == "revenue"] if "category" in breakdown.columns else pd.DataFrame(columns=breakdown.columns)
    expense_df = breakdown[breakdown["category"] == "expense"] if "category" in breakdown.columns else pd.DataFrame(columns=breakdown.columns)

    # Write outputs
    excel_path = out_base / f"summary_year_{year}.xlsx"
    write_excel(excel_path, yr_df, mon_df, sales_df, expense_df, exclusions, breakdown)
    # CSVs
    (out_base / "breakdown.csv").write_text(breakdown.to_csv(index=False), encoding="utf-8")
    (out_base / "exclusions.csv").write_text(exclusions.to_csv(index=False), encoding="utf-8")
    (out_base / "monthly.csv").write_text(mon_df.to_csv(index=False), encoding="utf-8")
    (out_base / "yearly.csv").write_text(yr_df.to_csv(index=False), encoding="utf-8")
    (out_base / f"normalized_{year}.csv").write_text(breakdown.to_csv(index=False), encoding="utf-8")
    # Markdown
    md_path = out_base / f"summary_year_{year}.md"
    lines = [f"# Summary {year}", "", "## 年間サマリ（売上経費利益）", "", "| 売上 | 経費 | 利益 |", "| ---: | ---: | ---: |"]
    if not yr_df.empty:
        yrev = float(yr_df.loc[0, "revenue"]) if "revenue" in yr_df.columns else 0
        yexp = float(yr_df.loc[0, "expense"]) if "expense" in yr_df.columns else 0
        ypro = float(yr_df.loc[0, "profit"]) if "profit" in yr_df.columns else yrev - yexp
        lines.append(f"| {yrev:.0f} | {yexp:.0f} | {ypro:.0f} |")
    lines += ["", "## 月次サマリ（〜12月）", "", "| 月 | 売上 | 経費 | 利益 |", "| --- | ---: | ---: | ---: |"]
    for m in [f"{year:04d}-{i:02d}" for i in range(1, 13)]:
        row = mon_df[mon_df["month"] == m]
        if not row.empty:
            r = row.iloc[0]
            lines.append(f"| {m} | {float(r['revenue']):.0f} | {float(r['expense']):.0f} | {float(r['profit']):.0f} |")
        else:
            lines.append(f"| {m} | 0 | 0 | 0 |")
    lines += ["", "## 除外件数（理由別）", ""]
    if not exclusions.empty and "reason" in exclusions.columns:
        counts = exclusions["reason"].value_counts().to_dict()
        lines += ["| 理由 | 件数 |", "| --- | ---: |"]
        for k in sorted(counts.keys()):
            lines.append(f"| {k} | {counts[k]} |")
    else:
        lines.append("除外はありません。")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    # JSON
    import json, datetime as _dt
    data = {
        "year": year,
        "generated_at": _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "yearly": {
            "revenue": float(yr_df.loc[0, "revenue"]) if not yr_df.empty else 0,
            "expense": float(yr_df.loc[0, "expense"]) if not yr_df.empty else 0,
            "profit": float(yr_df.loc[0, "profit"]) if not yr_df.empty else 0,
        },
        "monthly": [
            {
                "month": m,
                "revenue": float(mon_df[mon_df["month"] == m]["revenue"].iloc[0]) if (mon_df["month"] == m).any() else 0,
                "expense": float(mon_df[mon_df["month"] == m]["expense"].iloc[0]) if (mon_df["month"] == m).any() else 0,
                "profit": float(mon_df[mon_df["month"] == m]["profit"].iloc[0]) if (mon_df["month"] == m).any() else 0,
            }
            for i, m in enumerate([f"{year:04d}-{i:02d}" for i in range(1, 13)], start=1)
        ],
        "counts": {
            "included_rows": int(len(breakdown)),
            "excluded_rows": int(len(exclusions)),
            "exclusions_by_reason": exclusions["reason"].value_counts().astype(int).to_dict() if not exclusions.empty and "reason" in exclusions.columns else {},
        },
    }
    (out_base / f"summary_year_{year}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    typer.echo(f"Wrote outputs to {out_base}")


@app.command()
def summary(
    year: int = typer.Option(2025, "--year", help="Target year"),
    excel_glob: List[str] = typer.Option([], "--excel-glob", help="Excel glob(s)", show_default=False),
    pdf_glob: List[str] = typer.Option([], "--pdf-glob", help="PDF glob(s)", show_default=False),
    schema: Optional[Path] = typer.Option(None, "--schema", help="Path to schema.yaml"),
    debug: bool = typer.Option(False, "--debug", help="Verbose debug logging"),
):
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    logging.basicConfig(filename=f"out/run_{ts}.log", level=logging.DEBUG if debug else logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    logging.info("arkadia summary start")

    patterns: List[str] = []
    patterns.extend(excel_glob or [])
    patterns.extend(pdf_glob or [])
    if not patterns:
        typer.echo("No input patterns provided.")
        raise typer.Exit(code=2)
    # Reuse report path: we can compute summary after ingest + normalize
    # For simplicity, call report then extract yearly CSV
    report(year=year, excel_glob=excel_glob, pdf_glob=pdf_glob, schema=schema, outdir=Path("out"), debug=debug)
    # Print summary CSV to stdout
    ypath = Path("out") / "yearly.csv"
    if ypath.exists():
        typer.echo(Path(ypath).read_text(encoding="utf-8"))

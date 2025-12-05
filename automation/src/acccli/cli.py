from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from acccli.config import Settings, load_config, select_template
from acccli.core import (
    aggregate as agg_fn,
    normalize_columns,
    validate as val_fn,
    summarize_year,
    prepare_transactions,
    monthly_and_yearly_summary,
    filter_activity,
    filter_non_business,
    unify_schema,
)
from acccli.io import expand_inputs, load_inputs
import pandas as pd


app = typer.Typer(help="Accounting data aggregation CLI")


def _load_and_normalize_all(paths: List[Path], settings: Settings, encoding: str, debug: bool = False) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for p in paths:
        # Load this file only
        df = load_inputs([p], encoding=encoding, pdf_has_header=settings.pdf_has_header)
        if df.empty:
            continue
        # Select template based on filename/headers
        tmpl = select_template(getattr(settings, "templates", None), df.columns, str(p))
        if debug:
            typer.echo(f"[debug] Loaded {p} rows={len(df)} cols={len(df.columns)}")
        if tmpl is not None:
            ren = tmpl.columns.build_renames(df.columns)
            # Augment with global mapping for any missing fields
            extra = settings.columns.build_renames(df.columns)
            for src, tgt in extra.items():
                if tgt not in ren.values():
                    ren[src] = tgt
        else:
            ren = settings.columns.build_renames(df.columns)
        if debug:
            if tmpl is not None:
                typer.echo(f"[debug] Template '{tmpl.name}' mapped cols={len(ren)}")
            else:
                typer.echo(f"[debug] Global mapping mapped cols={len(ren)}")
        ndf = normalize_columns(df, ren)
        from acccli.core import synthesize_amount_columns
        ndf = synthesize_amount_columns(ndf)
        # Pass expense inclusion patterns via DataFrame attrs for downstream classification
        if settings.expense_include:
            try:
                ndf.attrs["expense_include"] = settings.expense_include
            except Exception:
                pass
        if getattr(settings, "expense_exclude", None):
            try:
                ndf.attrs["expense_exclude"] = settings.expense_exclude
            except Exception:
                pass
        if getattr(settings, "activity_exclude_values", None):
            try:
                ndf.attrs["activity_exclude_values"] = settings.activity_exclude_values
            except Exception:
                pass
        if getattr(settings, "revenue_flag_values", None):
            try:
                ndf.attrs["revenue_flag_values"] = settings.revenue_flag_values
            except Exception:
                pass
        if getattr(settings, "revenue_exclude", None):
            try:
                ndf.attrs["revenue_exclude"] = settings.revenue_exclude
            except Exception:
                pass
        frames.append(ndf)
    if not frames:
        return pd.DataFrame()
    # Align columns by union
    all_cols = sorted(set().union(*[f.columns for f in frames]))
    frames = [f.reindex(columns=all_cols) for f in frames]
    out = pd.concat(frames, ignore_index=True)
    if debug:
        typer.echo(f"[debug] Combined rows={len(out)} cols={len(out.columns)}")
    return out


@app.command()
def aggregate(
    input: List[str] = typer.Option(..., "--input", help="Input CSV files, dirs, or globs", show_default=False),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to YAML config"),
    by: List[str] = typer.Option(["account"], "--by", help="Grouping keys"),
    start: Optional[str] = typer.Option(None, "--from", help="Start date inclusive"),
    end: Optional[str] = typer.Option(None, "--to", help="End date inclusive"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output CSV path"),
    encoding: str = typer.Option("utf-8", help="Input CSV encoding"),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug logging"),
):
    settings: Settings = load_config(config)
    paths = expand_inputs(input)
    if not paths:
        raise typer.Exit(code=2)
    df = _load_and_normalize_all(paths, settings, encoding, debug=debug)
    # Exclude non-selected activity values and non-business rows
    df = filter_activity(df, getattr(settings, "activity_exclude_values", None))
    df = filter_non_business(df, getattr(settings, "expense_exclude", None))
    out = agg_fn(
        df,
        by=by,
        date_format=settings.date_format,
        start=start,
        end=end,
        account_map=settings.account_map,
    )
    if debug:
        typer.echo(f"[debug] aggregate grouped by {by} -> rows={len(out)}")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        out.to_csv(output, index=False)
    else:
        typer.echo(out.to_csv(index=False))


@app.command()
def validate(
    input: List[str] = typer.Option(..., "--input", help="Input CSV files, dirs, or globs", show_default=False),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to YAML config"),
    report: Optional[Path] = typer.Option(None, "--report", help="CSV path for summary report"),
    encoding: str = typer.Option("utf-8", help="Input CSV encoding"),
    strict: bool = typer.Option(False, "--strict", help="Exit non-zero on any issue"),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug logging"),
):
    settings: Settings = load_config(config)
    paths = expand_inputs(input)
    if not paths:
        raise typer.Exit(code=2)
    df = _load_and_normalize_all(paths, settings, encoding, debug=debug)
    required = {"date", "account", "amount"}
    if "dept" in df.columns:
        required.add("dept")
    from acccli.core import synthesize_amount_columns
    df = synthesize_amount_columns(df)
    metrics = val_fn(
        df,
        required_cols=required,
        date_format=settings.date_format,
        account_map=settings.account_map,
    )
    if debug:
        typer.echo(f"[debug] validate metrics: {metrics}")
    if report:
        import pandas as pd

        pd.DataFrame([metrics]).to_csv(report, index=False)
    else:
        for k, v in metrics.items():
            typer.echo(f"{k},{v}")
    if strict and any(v > 0 for v in metrics.values()):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()


@app.command()
def summary(
    input: List[str] = typer.Option(..., "--input", help="Input CSV/XLSX/PDF", show_default=False),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to YAML config"),
    year: int = typer.Option(2025, "--year", help="Target year"),
    encoding: str = typer.Option("utf-8", help="Input CSV encoding"),
    excel_glob: List[str] = typer.Option([], "--excel-glob", help="Excel glob(s) to include", show_default=False),
    pdf_glob: List[str] = typer.Option([], "--pdf-glob", help="PDF glob(s) to include", show_default=False),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug logging"),
):
    """Summarize revenue, expense and profit for a given year.

    Uses Decimal arithmetic for accuracy. If `category_map` is provided in config,
    it will classify by account; otherwise falls back to sign-based inference.
    """
    settings: Settings = load_config(config)
    patterns: List[str] = []
    patterns.extend(input or [])
    patterns.extend(excel_glob or [])
    patterns.extend(pdf_glob or [])
    paths = expand_inputs(patterns)
    if not paths:
        raise typer.Exit(code=2)
    df = _load_and_normalize_all(paths, settings, encoding, debug=debug)
    # Exclude non-selected activity values and non-business rows for totals
    df = filter_activity(df, getattr(settings, "activity_exclude_values", None))
    df = filter_non_business(df, getattr(settings, "expense_exclude", None))
    metrics = summarize_year(
        df,
        year=year,
        date_format=settings.date_format,
        account_map=settings.account_map,
        category_map=settings.category_map,
    )
    typer.echo("metric,value")
    for k in ("revenue", "expense", "profit"):
        typer.echo(f"{k},{metrics[k]}")


@app.command()
def report(
    input: List[str] = typer.Option(..., "--input", help="Input CSV/XLSX/PDF", show_default=False),
    config: Optional[Path] = typer.Option(None, "--config", help="Path to YAML config"),
    year: int = typer.Option(2025, "--year", help="Target year"),
    encoding: str = typer.Option("utf-8", help="Input CSV encoding"),
    excel_glob: List[str] = typer.Option([], "--excel-glob", help="Excel glob(s) to include", show_default=False),
    pdf_glob: List[str] = typer.Option([], "--pdf-glob", help="PDF glob(s) to include", show_default=False),
    breakdown: Optional[Path] = typer.Option(None, "--breakdown", help="Output CSV for included breakdown"),
    exclusions: Optional[Path] = typer.Option(None, "--exclusions", help="Output CSV for exclusion reasons"),
    monthly: Optional[Path] = typer.Option(None, "--monthly", help="Output CSV for monthly summary"),
    yearly: Optional[Path] = typer.Option(None, "--yearly", help="Output CSV for yearly total"),
    excel_summary: Optional[Path] = typer.Option(None, "--excel-summary", help="Output Excel for yearly summary sheet"),
    md_summary: Optional[Path] = typer.Option(None, "--md-summary", help="Output Markdown summary path"),
    json_summary: Optional[Path] = typer.Option(None, "--json-summary", help="Output JSON summary path"),
    outdir: Optional[Path] = typer.Option(None, "--outdir", help="Base output directory for default outputs"),
    debug: bool = typer.Option(False, "--debug", help="Enable verbose debug logging"),
):
    """Produce breakdown (根拠内訳), exclusion reason log, and monthly/yearly summaries."""
    settings: Settings = load_config(config)
    patterns: List[str] = []
    patterns.extend(input or [])
    patterns.extend(excel_glob or [])
    patterns.extend(pdf_glob or [])
    paths = expand_inputs(patterns)
    if not paths:
        raise typer.Exit(code=2)
    df = _load_and_normalize_all(paths, settings, encoding, debug=debug)
    inc_df, exc_df = prepare_transactions(
        df,
        year=year,
        date_format=settings.date_format,
        account_map=settings.account_map,
        category_map=settings.category_map,
    )
    mon_df, yr_df = monthly_and_yearly_summary(inc_df)

    # Defaults if not provided
    base = Path("out") if outdir is None else Path(outdir)
    if breakdown is None:
        breakdown = base / "breakdown.csv"
    if exclusions is None:
        exclusions = base / "exclusions.csv"
    if monthly is None:
        monthly = base / "monthly.csv"
    if yearly is None:
        yearly = base / "yearly.csv"
    if excel_summary is None:
        excel_summary = base / f"summary_year_{year}.xlsx"
    if md_summary is None:
        md_summary = base / f"summary_year_{year}.md"
    if json_summary is None:
        json_summary = base / f"summary_year_{year}.json"

    # Also write normalized (unified schema) for target year only
    norm_df = unify_schema(inc_df)
    normalized_path = base / f"normalized_{year}.csv"

    for pth, dfx in ((breakdown, inc_df), (exclusions, exc_df), (monthly, mon_df), (yearly, yr_df), (normalized_path, norm_df)):
        pth.parent.mkdir(parents=True, exist_ok=True)
        dfx.to_csv(pth, index=False)
    typer.echo(f"Wrote: {breakdown}, {exclusions}, {monthly}, {yearly}, {normalized_path}")

    # Write Excel yearly summary with specified sheet name
    try:
        import pandas as pd
        # Yearly sheet
        yearly_sheet = "年間サマリ（売上経費利益）"
        yrev = pd.to_numeric(yr_df.loc[0, "revenue"]) if "revenue" in yr_df.columns else 0
        yexp = pd.to_numeric(yr_df.loc[0, "expense"]) if "expense" in yr_df.columns else 0
        ypro = pd.to_numeric(yr_df.loc[0, "profit"]) if "profit" in yr_df.columns else yrev - yexp
        df_year = pd.DataFrame([{ "売上": yrev, "経費": yexp, "利益": ypro }])

        # Monthly sheet (ensure rows for all months up to December)
        monthly_sheet = "月次サマリ（〜12月）"
        target_months = [f"{year:04d}-{m:02d}" for m in range(1, 13)]
        mon = mon_df.copy()
        if not mon.empty:
            mon["month"] = mon["month"].astype(str)
        mon = mon.set_index("month") if not mon.empty else pd.DataFrame(columns=["revenue","expense","profit"]).set_index(pd.Index([]))
        # Initialize all months with zeros then update existing
        df_mon = pd.DataFrame(index=target_months, columns=["revenue","expense","profit"]).fillna(0)
        if not mon.empty:
            for col in ["revenue","expense","profit"]:
                if col in mon.columns:
                    df_mon.loc[mon.index, col] = pd.to_numeric(mon[col], errors="coerce").fillna(0).values
        df_mon = df_mon.reset_index().rename(columns={"index": "month", "revenue": "売上", "expense": "経費", "profit": "利益"})

        excel_summary.parent.mkdir(parents=True, exist_ok=True)
        with pd.ExcelWriter(excel_summary, engine="openpyxl") as writer:
            df_year.to_excel(writer, index=False, sheet_name=yearly_sheet)
            df_mon.to_excel(writer, index=False, sheet_name=monthly_sheet)
            # Sales breakdown sheet with source metadata
            sales = inc_df.copy()
            if not sales.empty:
                sales = sales[sales.get("category") == "revenue"]
            sales_sheet = "売上内訳（全行、元ファイルシート行番号付き）"
            cols = [
                "date",
                "account",
                "dept",
                "subaccount",
                "memo",
                "amount",
                "source_file",
                "source_sheet",
                "source_row",
            ]
            exist_cols = [c for c in cols if c in sales.columns]
            (sales[exist_cols] if not sales.empty else pd.DataFrame(columns=exist_cols)).to_excel(
                writer, index=False, sheet_name=sales_sheet
            )
            # Expense breakdown sheet
            expense = inc_df.copy()
            if not expense.empty:
                expense = expense[expense.get("category") == "expense"]
            expense_sheet = "経費内訳（全行、元ファイルシート行番号付き）"
            exist_cols_e = [c for c in cols if c in expense.columns]
            (expense[exist_cols_e] if not expense.empty else pd.DataFrame(columns=exist_cols_e)).to_excel(
                writer, index=False, sheet_name=expense_sheet
            )
            # Exclusions sheet (reason included)
            excl_sheet = "除外一覧（理由付き）"
            excl_cols = ["reason", "date", "account", "amount", "dept", "source_file", "source_sheet", "source_row"]
            exc_cols_exist = [c for c in excl_cols if c in exc_df.columns]
            # Ensure at least the core columns exist
            if not exc_cols_exist:
                exc_cols_exist = ["reason", "date", "account", "amount", "dept"]
            (exc_df[exc_cols_exist] if not exc_df.empty else pd.DataFrame(columns=exc_cols_exist)).to_excel(
                writer, index=False, sheet_name=excl_sheet
            )
            # Normalized unified schema (target year only)
            try:
                norm_sheet = "正規化（統一スキーマ）"
                norm_df.to_excel(writer, index=False, sheet_name=norm_sheet)
            except Exception:
                # Fallback ASCII sheet name if unicode fails
                norm_df.to_excel(writer, index=False, sheet_name="Normalized")
        typer.echo(f"Wrote Excel summary: {excel_summary} [{yearly_sheet}], [{monthly_sheet}]")
    except Exception as e:
        # Do not fail the command if Excel creation fails; just notify
        typer.echo(f"Warning: failed to write Excel summary: {e}")

    # Write Markdown summary for Git-friendly report
    try:
        # Build Markdown content
        lines: list[str] = []
        lines.append(f"# Summary {year}")
        lines.append("")
        lines.append("## 年間サマリ（売上経費利益）")
        lines.append("")
        yrev_s = f"{float(yrev):.2f}" if isinstance(yrev, (int, float)) else str(yrev)
        yexp_s = f"{float(yexp):.2f}" if isinstance(yexp, (int, float)) else str(yexp)
        ypro_s = f"{float(ypro):.2f}" if isinstance(ypro, (int, float)) else str(ypro)
        lines.append("| 売上 | 経費 | 利益 |")
        lines.append("| ---: | ---: | ---: |")
        lines.append(f"| {yrev_s} | {yexp_s} | {ypro_s} |")
        lines.append("")
        lines.append("## 月次サマリ（〜12月）")
        lines.append("")
        # Reuse df_mon (target 1..12)
        lines.append("| 月 | 売上 | 経費 | 利益 |")
        lines.append("| --- | ---: | ---: | ---: |")
        for m in [f"{year:04d}-{i:02d}" for i in range(1, 13)]:
            row = df_mon[df_mon["month"] == m]
            if not row.empty:
                r = row.iloc[0]
                rv = float(r["売上"]) if "売上" in r else 0.0
                ex = float(r["経費"]) if "経費" in r else 0.0
                pf = float(r["利益"]) if "利益" in r else (rv - ex)
            else:
                rv = ex = pf = 0.0
            lines.append(f"| {m} | {rv:.2f} | {ex:.2f} | {pf:.2f} |")
        lines.append("")
        lines.append("## 除外件数（理由別）")
        lines.append("")
        if not exc_df.empty and "reason" in exc_df.columns:
            counts = exc_df["reason"].value_counts().to_dict()
            lines.append("| 理由 | 件数 |")
            lines.append("| --- | ---: |")
            for k in sorted(counts.keys()):
                lines.append(f"| {k} | {counts[k]} |")
        else:
            lines.append("除外はありません。")
        md_summary.parent.mkdir(parents=True, exist_ok=True)
        md_summary.write_text("\n".join(lines), encoding="utf-8")
        typer.echo(f"Wrote Markdown summary: {md_summary}")
    except Exception as e:
        typer.echo(f"Warning: failed to write Markdown summary: {e}")

    # Write machine-readable JSON summary
    try:
        import json
        import datetime as _dt
        # Yearly totals
        yobj = {
            "revenue": float(yrev) if not pd.isna(yrev) else 0.0,
            "expense": float(yexp) if not pd.isna(yexp) else 0.0,
            "profit": float(ypro) if not pd.isna(ypro) else 0.0,
        }
        # Monthly list of 12 entries
        monthly_list = []
        for m in [f"{year:04d}-{i:02d}" for i in range(1, 13)]:
            row = df_mon[df_mon["month"] == m]
            if not row.empty:
                r = row.iloc[0]
                rv = float(r["売上"]) if "売上" in r else 0.0
                ex = float(r["経費"]) if "経費" in r else 0.0
                pf = float(r["利益"]) if "利益" in r else (rv - ex)
            else:
                rv = ex = pf = 0.0
            monthly_list.append({"month": m, "revenue": rv, "expense": ex, "profit": pf})

        counts = {"included_rows": int(len(inc_df)), "excluded_rows": int(len(exc_df))}
        if not exc_df.empty and "reason" in exc_df.columns:
            counts["exclusions_by_reason"] = (
                exc_df["reason"].value_counts().astype(int).to_dict()
            )
        data = {
            "year": year,
            "generated_at": _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "yearly": yobj,
            "monthly": monthly_list,
            "counts": counts,
        }
        json_summary.parent.mkdir(parents=True, exist_ok=True)
        json_summary.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        typer.echo(f"Wrote JSON summary: {json_summary}")
    except Exception as e:
        typer.echo(f"Warning: failed to write JSON summary: {e}")

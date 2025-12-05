from __future__ import annotations

from pathlib import Path
import pandas as pd


def write_csvs(base: Path, breakdown: pd.DataFrame, exclusions: pd.DataFrame, monthly: pd.DataFrame, yearly: pd.DataFrame, normalized: pd.DataFrame) -> None:
    base.mkdir(parents=True, exist_ok=True)
    breakdown.to_csv(base / "breakdown.csv", index=False)
    exclusions.to_csv(base / "exclusions.csv", index=False)
    monthly.to_csv(base / "monthly.csv", index=False)
    yearly.to_csv(base / "yearly.csv", index=False)
    normalized.to_csv(base / ("normalized_" + str(pd.to_datetime(breakdown["date"]).dt.year.mode().iloc[0]) + ".csv" if not breakdown.empty else "normalized.csv"), index=False)


def write_excel(path: Path, yearly_df: pd.DataFrame, monthly_df: pd.DataFrame, sales_df: pd.DataFrame, expense_df: pd.DataFrame, excl_df: pd.DataFrame, normalized_df: pd.DataFrame, year: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        yearly_df.rename(columns={"revenue": "売上", "expense": "経費", "profit": "利益"}).to_excel(writer, index=False, sheet_name="年間サマリ（売上経費利益）")
        md = monthly_df.rename(columns={"revenue": "売上", "expense": "経費", "profit": "利益"})
        # Ensure 1..12 rows
        target_months = [f"{year:04d}-{m:02d}" for m in range(1, 13)]
        md = md.set_index("month").reindex(target_months, fill_value=0).reset_index().rename(columns={"index": "month"})
        md.to_excel(writer, index=False, sheet_name="月次サマリ（〜12月）")
        s_cols = [c for c in ["date","account","dept","subaccount","memo","amount","source_file","source_sheet","source_row"] if c in sales_df.columns]
        (sales_df[s_cols] if not sales_df.empty else pd.DataFrame(columns=s_cols)).to_excel(writer, index=False, sheet_name="売上内訳（全行、元ファイルシート行番号付き）")
        e_cols = [c for c in ["date","account","dept","subaccount","memo","amount","source_file","source_sheet","source_row"] if c in expense_df.columns]
        (expense_df[e_cols] if not expense_df.empty else pd.DataFrame(columns=e_cols)).to_excel(writer, index=False, sheet_name="経費内訳（全行、元ファイルシート行番号付き）")
        excl_cols = [c for c in ["reason","date","account","amount","dept","source_file","source_sheet","source_row"] if c in excl_df.columns]
        (excl_df[excl_cols] if not excl_df.empty else pd.DataFrame(columns=excl_cols)).to_excel(writer, index=False, sheet_name="除外一覧（理由付き）")
        normalized_df.to_excel(writer, index=False, sheet_name="正規化（統一スキーマ）")


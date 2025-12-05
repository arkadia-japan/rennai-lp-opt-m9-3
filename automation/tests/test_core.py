from __future__ import annotations

from pathlib import Path

import pandas as pd

from acccli.core import aggregate, normalize_columns, validate
from acccli.config import ColumnMapping


def test_aggregate_basic(tmp_path: Path):
    csv = tmp_path / "data.csv"
    csv.write_text(
        """date,account,dept,amount\n2024-01-01,Sales,A,100\n2024-01-15,Sales,A,250\n2024-02-01,COGS,B,50\n""",
        encoding="utf-8",
    )
    df = pd.read_csv(csv)
    df = normalize_columns(df, ColumnMapping().standard_columns())
    out = aggregate(df, by=["account"], start="2024-01-01", end="2024-12-31")
    totals = dict(zip(out["account"], out["amount"]))
    assert totals["Sales"] == 350
    assert totals["COGS"] == 50


def test_validate_flags_issues(tmp_path: Path):
    csv = tmp_path / "bad.csv"
    csv.write_text(
        """date,account,dept,amount\nnot-a-date,Unknown,A,xx\n""",
        encoding="utf-8",
    )
    df = pd.read_csv(csv)
    df = normalize_columns(df, ColumnMapping().standard_columns())
    metrics = validate(df, required_cols={"date", "account", "dept", "amount"}, account_map={})
    assert metrics["invalid_dates"] == 1
    assert metrics["non_numeric_amounts"] == 1


def test_synthesize_amount_debit_credit():
    import pandas as pd
    from acccli.core import synthesize_amount_columns

    df = pd.DataFrame({
        "date": ["2025-01-01"],
        "account": ["Sales"],
        "debit": ["0"],
        "credit": ["1,234.50"],
    })
    out = synthesize_amount_columns(df)
    assert "amount" in out.columns
    assert out.loc[0, "amount"] == "1234.50"


def test_synthesize_amount_in_out_and_parentheses():
    import pandas as pd
    from acccli.core import synthesize_amount_columns, _to_decimal

    df = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02"],
        "account": ["Misc", "Misc"],
        "in_amount": ["1,000"],
        "out_amount": ["(200)"],
    })
    out = synthesize_amount_columns(df)
    # amount = 1000 - 200 = 800.00
    assert out.loc[0, "amount"] == "800.00" or out.loc[0, "amount"] == "800"

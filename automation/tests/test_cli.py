from __future__ import annotations

from pathlib import Path

import pandas as pd
from typer.testing import CliRunner

from acccli.cli import app


def test_cli_aggregate_outputs_csv(tmp_path: Path):
    data = tmp_path / "data.csv"
    data.write_text(
        "date,account,amount\n2024-01-01,Sales,100\n2024-01-02,Sales,50\n", encoding="utf-8"
    )
    config = tmp_path / "config.yml"
    config.write_text("""columns: {date: date, account: account, amount: amount}\n""")
    out = tmp_path / "out.csv"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "aggregate",
            "--input",
            str(data),
            "--config",
            str(config),
            "--by",
            "account",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    df = pd.read_csv(out)
    assert df.loc[0, "amount"] == 150


def test_cli_summary_2025_category_map(tmp_path: Path):
    data = tmp_path / "data.xlsx"
    # Create 2025 and 2024 rows to check filtering
    df_in = pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-06-30", "2024-12-31"],
            "account": ["Sales", "Rent Expense", "Sales"],
            "amount": ["1000", "300", "999"],
        }
    )
    df_in.to_excel(data, index=False)

    config = tmp_path / "config.yml"
    config.write_text(
        """
columns: {date: date, account: account, amount: amount}
category_map:
  Sales: revenue
  Rent Expense: expense
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(data),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    # Parse output CSV-like text, expect revenue=1000, expense=300, profit=700
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    assert "metric,value" in lines[0]
    out = dict(line.split(",") for line in lines[1:])
    assert out["revenue"] == "1000.00"
    assert out["expense"] == "300.00"
    assert out["profit"] == "700.00"


def test_excel_multiple_sheets_are_combined(tmp_path: Path):
    import pandas as pd
    xlsx = tmp_path / "multi.xlsx"
    with pd.ExcelWriter(xlsx) as writer:
        pd.DataFrame({"date": ["2025-01-01"], "account": ["Sales"], "amount": [100]}).to_excel(
            writer, sheet_name="S1", index=False
        )
        pd.DataFrame({"date": ["2025-01-02"], "account": ["Sales"], "amount": [50]}).to_excel(
            writer, sheet_name="S2", index=False
        )

    config = tmp_path / "config.yml"
    config.write_text("columns: {date: date, account: account, amount: amount}\n")
    out = tmp_path / "agg.csv"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "aggregate",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--by",
            "account",
            "--from",
            "2025-01-01",
            "--to",
            "2025-12-31",
            "--output",
            str(out),
        ],
    )
    assert result.exit_code == 0
    df = pd.read_csv(out)
    assert df.loc[0, "amount"] == 150


def test_deduplicate_by_date_amount_memo_in_summary(tmp_path: Path):
    # Two files with duplicate transaction should be counted once
    import pandas as pd
    f1 = tmp_path / "a.xlsx"
    f2 = tmp_path / "b.xlsx"
    for f in (f1, f2):
        with pd.ExcelWriter(f) as w:
            pd.DataFrame({"日付": ["2025-01-01"], "科目": ["Sales"], "金額": ["100"], "摘要": ["同取引"]}).to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  memo: 摘要
        """.strip()
    )
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(f1),
            "--input",
            str(f2),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    out = dict(line.split(",") for line in lines[1:])
    assert out["revenue"] in ("100.00", "100")


def test_report_logs_duplicate(tmp_path: Path):
    # Same file with duplicate rows -> one included, one logged as duplicate
    import pandas as pd
    xlsx = tmp_path / "dup.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-01-05", "2025-01-05"],
        "科目": ["Sales", "Sales"],
        "金額": ["100", "100"],
        "摘要": ["重複テスト", "重複テスト"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  memo: 摘要
        """.strip()
    )
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    exc = pd.read_csv(tmp_path / "out" / "exclusions.csv")
    assert "duplicate" in set(exc["reason"].tolist())


def test_report_writes_excel_year_summary(tmp_path: Path):
    # Create minimal dataset to produce yearly summary Excel with JP sheet
    import pandas as pd
    xlsx = tmp_path / "data.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-01-01"],
        "科目": ["Sales"],
        "金額": ["1234.5"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
        """.strip()
    )

    outxlsx = tmp_path / "out" / "summary_year_2025.xlsx"
    outmd = tmp_path / "out" / "summary_year_2025.md"
    outjson = tmp_path / "out" / "summary_year_2025.json"
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    assert outxlsx.exists()
    assert outmd.exists()
    txt = outmd.read_text(encoding="utf-8")
    assert "年間サマリ（売上経費利益）" in txt
    assert "月次サマリ（〜12月）" in txt
    assert outjson.exists()
    import json
    data = json.loads(outjson.read_text(encoding="utf-8"))
    assert data.get("year") == 2025
    assert "yearly" in data and "monthly" in data
    assert len(data.get("monthly", [])) == 12
    # Read back the sheet and verify values
    df_out = pd.read_excel(outxlsx, sheet_name="年間サマリ（売上経費利益）")
    assert int(df_out.loc[0, "売上"]) == 1234
    # Monthly sheet includes all months to December
    mon_out = pd.read_excel(outxlsx, sheet_name="月次サマリ（〜12月）")
    assert len(mon_out) == 12
    assert mon_out.columns.tolist() == ["month", "売上", "経費", "利益"]
    # Sales breakdown sheet exists with columns including source metadata
    sales_out = pd.read_excel(outxlsx, sheet_name="売上内訳（全行、元ファイルシート行番号付き）")
    assert set(["date", "account", "amount"]).issubset(set(sales_out.columns))
    # Expense breakdown sheet exists
    expense_out = pd.read_excel(outxlsx, sheet_name="経費内訳（全行、元ファイルシート行番号付き）")
    assert set(["date", "account", "amount"]).issubset(set(expense_out.columns))
    # Exclusions sheet exists with reason column
    excl_out = pd.read_excel(outxlsx, sheet_name="除外一覧（理由付き）")
    assert "reason" in excl_out.columns


def test_cli_report_outputs_all(tmp_path: Path):
    # Include: one revenue, one expense; Exclude: one invalid date, one out of period, one non-numeric
    data = tmp_path / "data.csv"
    data.write_text(
        """
date,account,amount,dept
2025-01-05,Sales,100,A
2025-02-10,Rent Expense,30,B
bad-date,Sales,50,A
2024-12-31,Sales,999,A
2025-03-01,Sales,xx,A
        """.strip()
    )
    config = tmp_path / "config.yml"
    config.write_text(
        """
columns: {date: date, account: account, amount: amount, dept: dept}
category_map:
  Sales: revenue
  Rent Expense: expense
        """.strip()
    )

    out_break = tmp_path / "breakdown.csv"
    out_exc = tmp_path / "exclusions.csv"
    out_month = tmp_path / "monthly.csv"
    out_year = tmp_path / "yearly.csv"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(data),
            "--config",
            str(config),
            "--year",
            "2025",
            "--breakdown",
            str(out_break),
            "--exclusions",
            str(out_exc),
            "--monthly",
            str(out_month),
            "--yearly",
            str(out_year),
        ],
    )
    assert result.exit_code == 0

    # Check files exist and contents
    import pandas as pd

    inc = pd.read_csv(out_break)
    exc = pd.read_csv(out_exc)
    mon = pd.read_csv(out_month)
    yr = pd.read_csv(out_year)

    # Included: two rows (100 revenue, 30 expense)
    assert len(inc) == 2
    # Excluded: three rows with reasons
    reasons = sorted(exc["reason"].tolist())
    assert reasons == ["invalid_date", "non_numeric_amount", "out_of_period"]

    # Monthly: 2025-01 profit 100, 2025-02 profit -30
    prof = dict(zip(mon["month"], mon["profit"].astype(str)))
    assert prof.get("2025-01") == "100.00"
    assert prof.get("2025-02") == "-30.00"
    # Yearly total: 70 profit
    assert yr.loc[0, "profit"] == 70 or str(yr.loc[0, "profit"]) == "70.00"


def test_regex_column_mapping(tmp_path: Path):
    # Headers are Japanese variants; mapping via regex should resolve
    data = tmp_path / "jp.csv"
    data.write_text(
        "ご利用日,科目,ご利用金額\n2025-01-01,Sales,1000\n", encoding="utf-8"
    )
    config = tmp_path / "config.yml"
    config.write_text(
        """
columns:
  date_regex: "(ご利用日|利用日)"
  account: 科目
  amount_regex: "(ご利用金額|利用金額)"
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "aggregate",
            "--input",
            str(data),
            "--config",
            str(config),
            "--by",
            "account",
        ],
    )
    assert result.exit_code == 0
    # Expect stdout CSV with amount=1000 for Sales
    out = result.stdout.strip().splitlines()
    assert out and "Sales,1000" in out[-1]


def test_expense_include_memo_regex(tmp_path: Path):
    # Positive amount but memo indicates fee -> classify as expense via include rule
    data = tmp_path / "fee.xlsx"
    import pandas as pd
    df = pd.DataFrame({
        "日付": ["2025-01-10"],
        "科目": ["Misc"],
        "金額": ["100"],
        "摘要": ["振込手数料"],
    })
    with pd.ExcelWriter(data) as writer:
        df.to_excel(writer, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  memo: 摘要
expense_include:
  memo_regex: ["手数料", "fee"]
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(data),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    # Check yearly profit is -100 (revenue 0, expense 100)
    import pandas as pd
    yearly = pd.read_csv(tmp_path / "out" / "yearly.csv")
    assert float(yearly.loc[0, "expense"]) == 100.0


def test_activity_excluded_in_report(tmp_path: Path):
    # Row with activity '要設定' should be excluded with reason activity_excluded
    import pandas as pd
    xlsx = tmp_path / "act.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-04-01", "2025-04-02"],
        "科目": ["Sales", "Sales"],
        "金額": ["100", "200"],
        "アクティビティ": ["要設定", "選択済み"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  activity: アクティビティ
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    import pandas as pd
    exc = pd.read_csv(tmp_path / "out" / "exclusions.csv")
    assert "activity_excluded" in set(exc["reason"].tolist())


def test_activity_filtered_from_summary(tmp_path: Path):
    # Summary should ignore rows with activity excluded value
    import pandas as pd
    xlsx = tmp_path / "act2.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-05-01", "2025-05-02"],
        "科目": ["Sales", "Sales"],
        "金額": ["100", "200"],
        "アクティビティ": ["要設定", "選択済み"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  activity: アクティビティ
        """.strip()
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    out = dict(line.split(",") for line in lines[1:])
    # Only the selected row (200) should count as revenue
    assert out["revenue"] in ("200.00", "200")


def test_private_use_excluded(tmp_path: Path):
    # Memo"出金プライベート利用" must be excluded as non-business
    import pandas as pd
    xlsx = tmp_path / "private.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-06-01"],
        "科目": ["Misc"],
        "金額": ["300"],
        "摘要": ["出金プライベート利用"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  memo: 摘要
expense_exclude:
  memo_regex: ["出金プライベート利用"]
        """.strip()
    )

    # Summary should treat it as excluded (revenue/expense zero)
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    out = dict(line.split(",") for line in lines[1:])
    assert out["revenue"] in ("0.00", "0") and out["expense"] in ("0.00", "0")

    # Report should log it as non_business
    result2 = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result2.exit_code == 0
    exc = pd.read_csv(tmp_path / "out" / "exclusions.csv")
    assert "non_business" in set(exc["reason"].tolist())


def test_loan_proceeds_not_sales(tmp_path: Path):
    # Loan deposit should not be counted as revenue (category -> other)
    import pandas as pd
    xlsx = tmp_path / "loan.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-07-01"],
        "科目": ["Misc"],
        "金額": ["5000"],
        "摘要": ["借入金 受入"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  memo: 摘要
revenue_exclude:
  memo_regex: ["借入|ローン|融資|Loan"]
        """.strip()
    )

    # Summary should not count as revenue
    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    out = dict(line.split(",") for line in lines[1:])
    assert out["revenue"] in ("0.00", "0") and out["expense"] in ("0.00", "0")

    # Report should log as revenue_excluded in exclusions
    result2 = runner.invoke(
        app,
        [
            "report",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result2.exit_code == 0
    exc = pd.read_csv(tmp_path / "out" / "exclusions.csv")
    assert "revenue_excluded" in set(exc["reason"].tolist())


def test_revenue_flag_only_sales_income(tmp_path: Path):
    # Only rows flagged as 売上入金 should count as revenue
    import pandas as pd
    xlsx = tmp_path / "flag.xlsx"
    df = pd.DataFrame({
        "日付": ["2025-08-01", "2025-08-02"],
        "科目": ["Misc", "Misc"],
        "金額": ["1000", "2000"],
        "種別": ["売上入金", "その他入金"],
    })
    with pd.ExcelWriter(xlsx) as w:
        df.to_excel(w, index=False)

    config = tmp_path / "config.yaml"
    config.write_text(
        """
columns:
  date: 日付
  account: 科目
  amount: 金額
  revenue_flag: 種別
revenue_flag_values: ["売上入金"]
        """.strip()
    )

    from typer.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "summary",
            "--input",
            str(xlsx),
            "--config",
            str(config),
            "--year",
            "2025",
        ],
    )
    assert result.exit_code == 0
    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    out = dict(line.split(",") for line in lines[1:])
    # Only 1000 (売上入金) should be counted as revenue
    assert out["revenue"] in ("1000.00", "1000")

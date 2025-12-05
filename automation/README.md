**Overview**
- `acccli` is a Python CLI for validating and aggregating accounting transaction data from CSV/Excel/PDF files.
- Supports column mapping via YAML config, date filtering, simple account mapping, and CSV output.
- PDF support is best-effort via optional `pdfplumber`.

**Installation**
- Requires Python 3.10+
- Install dependencies and the CLI locally:
  - `pip install -e .`
  - Optional PDF support: `pip install -e .[pdf]`

**Quick Start**
- Prepare CSV/Excel with columns (defaults): `date, account, amount[, dept, subaccount]`.
- Optional config `config.yml` to map your source columns to standard names.

Example `config.yml`:
```
columns:
  date: date
  account: account
  amount: amount
  dept: dept
date_format: null  # e.g. "%Y/%m/%d" if needed
account_map:
  Sales Intl: Sales
  COGS Raw: COGS
```

**Commands**
- `aggregate`
  - Usage: `acccli aggregate --input data/*.csv --config config.yml --by account dept --from 2024-01-01 --to 2024-12-31 --output out/summary.csv`
  - Groups by requested keys and sums `amount`.
- `validate`
  - Usage: `acccli validate --input data/*.csv --config config.yml --report out/validate.csv --strict`
  - Checks: missing columns, invalid dates, non-numeric amounts, unmapped accounts.
- `summary`
  - Usage: `acccli summary --input data/*.(csv|xlsx|pdf) --config config.yml --year 2025`
  - Computes revenue, expense, and profit for a given year using Decimal arithmetic. If `category_map` is provided, it classifies by account; otherwise it infers by sign.
- `report`
  - Outputs three artifacts in one run for a target year:
    - Breakdown (根拠内訳): normalized rows that contribute to totals with `date, month, account, dept, amount, category`
    - Exclusions (除外理由ログ): rows excluded with `reason` (`invalid_date`, `non_numeric_amount`, `out_of_period`, `missing_account`)
    - Monthly/Yearly summary: revenue/expense/profit by month and totals
  - Usage (paths optional; defaults to `out/`):
    - `acccli report --input data/**/*.* --config config.yml --year 2025 --breakdown out/breakdown.csv --exclusions out/exclusions.csv --monthly out/monthly.csv --yearly out/yearly.csv`

**Input Handling**
- `--input` accepts file paths, directories (recursively loads `*.csv|*.xlsx|*.xls|*.pdf`), or globs.
- Encoding defaults to `utf-8` for CSV.
- Excel: reads all sheets in each workbook and combines them.
- PDF: requires `pdfplumber`; table extraction expects a header row by default.

Bank/Card/PayPay PDFs
- Use `columns` mapping to align different headers to standard fields. Typical examples:
  - Bank: `date: [取引日, 入出金日]`, `in_amount: [入金額]`, `out_amount: [出金額]`, `memo: [摘要]`
  - Credit Card: `date: [利用日, ご利用日]`, `amount: [ご利用金額, 利用金額]`, `memo: [利用先, 摘要]`
  - PayPay: `date: [支払日時, 決済日]`, `in_amount: [受け取り金額, チャージ金額]`, `out_amount: [支払金額]`, `memo: [内訳, 摘要]`
- Amount synthesis:
  - If `amount` is missing but `in_amount`/`out_amount` exist, the tool computes `amount = in_amount - out_amount`.
  - If `debit`/`credit` exist, it computes `amount = credit - debit`.
  - Parentheses negatives like `(1,234)` and full-width digits are handled.

**Output**
- Aggregation: CSV to `--output` or prints CSV to stdout.
- Validation: Writes a one-line CSV summary to `--report`, or prints `key,value` lines to stdout.
- Summary: prints `metric,value` lines (revenue, expense, profit).

**Testing**
- Run tests locally:
  - `pip install -e .[test]` (or separately install `pytest`)
  - `pytest`

**Notes**
- PDF parsing accuracy depends on the document’s table structure; complex layouts may need preprocessing.
- Extendable: add currency handling, tax categories, and richer mappings via `config.yml`.

**Config additions**
- `category_map`: map account name to `revenue` or `expense` for precise classification.
- `pdf_has_header`: whether the first row of PDF tables is a header (default true).
 - `expense_include`: regex hints to treat rows as expense even without `inout` or when signs vary.
  - keys: `account_regex`, `memo_regex`, `activity_regex` (lists of regex strings)
 - example:
     - `expense_include: { memo_regex: ["手数料", "通信料|携帯", "サブスク|subscription"], account_regex: ["(旅費|交通費|交際費|消耗品|水道光熱費|地代家賃)"] }`
- `expense_exclude`: regex to exclude non-business/private rows (e.g., 出金プライベート利用)。
   - keys: `account_regex`, `memo_regex`, `activity_regex`, `inout_regex`
   - example: `expense_exclude: { memo_regex: ["出金プライベート利用|プライベート"] }`
 - `revenue_exclude`: regex to exclude non-sales inflows from revenue totals (e.g., 借入/ローン/融資)。
   - keys: `account_regex`, `memo_regex`, `activity_regex`, `inout_regex`
   - example: `revenue_exclude: { memo_regex: ["借入|ローン|融資|Loan"] }`
 - `activity_exclude_values`: list of exact values to exclude (normalized) from aggregation, default `["要設定"]`.
   - Rows whose `activity` equals one of these values are excluded from `aggregate`/`summary` and logged as `activity_excluded` in `report`.

**Field Mapping (JP examples)**
- Map your fields to standard names via `columns` in `config.yml`.
- You can specify multiple candidate source columns as a list; the first existing one is used.

Example:
```
columns:
  date: 日付
  account: 科目
  subaccount: サブ科目
  amount: 金額
  memo: [摘要, メモ]
  inout: 入出金区分   # values like 入金/出金 or IN/OUT are supported
  activity: アクティビティ
  remarks: 備考
```

In/out handling:
- If `inout` is provided, the tool classifies rows and treats amounts as absolute values for totals:
  - Outflow keywords: 出金/支出/out/expense
  - Inflow keywords: 入金/収入/in/income
- Without `inout`, classification falls back to amount sign (>=0: revenue, <0: expense).

**Regex Mapping and Templates**
- You can specify regex-based hints for headers when names vary widely:
  - Example:
    - `columns: { date_regex: "(ご利用日|利用日)", amount_regex: "(ご利用金額|利用金額)", memo_regex: "(摘要|利用先)" }`
- Templates: choose different mappings per source (by filename/header patterns):
```
templates:
  - name: bank_generic
    filename_regex: ["bank|statement"]
    columns:
      date_regex: "(取引日|入出金日)"
      in_amount_regex: "入金(額|金)?"
      out_amount_regex: "出金(額|金)?"
      memo_regex: "(摘要|内容)"
  - name: paypay
    filename_regex: ["paypay"]
    columns:
      date_regex: "(支払日時|決済日)"
      in_amount_regex: "(受け取り金額|チャージ金額)"
      out_amount_regex: "支払金額"
      memo_regex: "(内訳|摘要)"
```
- Resolution order per file: template mapping (if matched) → global `columns` mapping → regex hints.

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def monthly_and_yearly(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return (
            pd.DataFrame(columns=["month", "revenue", "expense", "profit"]),
            pd.DataFrame([[0, 0, 0]], columns=["revenue", "expense", "profit"]),
        )
    # ensure month
    if "date" in df.columns:
        dts = pd.to_datetime(df["date"], errors="coerce")
        df = df.assign(month=dts.dt.strftime("%Y-%m"))
    # to Decimal
    def to_dec(x):
        try:
            return Decimal(str(x))
        except Exception:
            return Decimal("0")
    rev = df.loc[df["category"] == "revenue"].copy()
    exp = df.loc[df["category"] == "expense"].copy()
    rev["amount"] = rev["amount"].map(to_dec)
    exp["amount"] = exp["amount"].map(to_dec).map(lambda d: d if d > 0 else -d)
    m_rev = rev.groupby("month", as_index=False)["amount"].sum().rename(columns={"amount": "revenue"})
    m_exp = exp.groupby("month", as_index=False)["amount"].sum().rename(columns={"amount": "expense"})
    months = sorted(set(m_rev["month"]).union(set(m_exp["month"])) )
    m = pd.DataFrame({"month": months})
    m = m.merge(m_rev, on="month", how="left").merge(m_exp, on="month", how="left").fillna(0)
    m["profit"] = m["revenue"] - m["expense"]
    y = pd.DataFrame(
        [[m["revenue"].sum(), m["expense"].sum(), (m["revenue"].sum() - m["expense"].sum())]],
        columns=["revenue", "expense", "profit"],
    )
    return m, y


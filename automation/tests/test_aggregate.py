from __future__ import annotations

import pandas as pd

from arkadia_bookkeeping.aggregate import monthly_and_yearly


def test_monthly_yearly_basic():
    df = pd.DataFrame({
        "date": ["2025-01-01", "2025-01-02", "2025-02-01"],
        "category": ["revenue", "expense", "revenue"],
        "amount": [1000, -300, 200],
    })
    m, y = monthly_and_yearly(df)
    jan = m[m["month"] == "2025-01"]
    assert int(jan["revenue"].iloc[0]) == 1000
    assert int(jan["expense"].iloc[0]) == 300
    assert int(jan["profit"].iloc[0]) == 700
    assert int(y.loc[0, "profit"]) == int(m["profit"].sum())

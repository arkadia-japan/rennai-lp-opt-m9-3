from __future__ import annotations

import pandas as pd

from arkadia_bookkeeping.rules import filter_activity, exclude_private, exclude_loan_inflows, tag_repayment_expense


def test_activity_not_set_excluded():
    df = pd.DataFrame({"activity": ["要設定", "選択"], "description": ["a", "b"]})
    inc, exc = filter_activity(df, selected=["選択"], not_set=["要設定"])
    assert len(inc) == 1 and len(exc) == 1
    assert exc.iloc[0]["reason"] == "activity_excluded"


def test_private_spend_excluded():
    df = pd.DataFrame({"description": ["出金プライベート利用", "通常"]})
    inc, exc = exclude_private(df, token="出金プライベート利用")
    assert len(inc) == 1 and len(exc) == 1
    assert exc.iloc[0]["reason"] == "non_business"


def test_loan_inflow_excluded_from_sales():
    df = pd.DataFrame({"inout": ["入金"], "description": ["借入 実行"]})
    inc, exc = exclude_loan_inflows(df, keywords=["借入", "融資", "ローン"]) 
    assert len(inc) == 0 and len(exc) == 1
    assert "借入入金" in set(exc["reason"].tolist())


def test_repayment_outflow_tagged_as_expense():
    df = pd.DataFrame({"inout": ["出金", "入金"], "description": ["ローン返済", "ローン返済"]})
    out = tag_repayment_expense(df, keywords=["返済", "ローン返済"]) 
    assert out.loc[0, "category"] == "expense"

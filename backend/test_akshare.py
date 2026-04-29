"""Test AKShare on server"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import akshare as ak

print("AKShare imported")

try:
    df = ak.fund_open_fund_info_em(symbol="019005", indicator="单位净值走势")
    print(f"Fund 019005: {len(df)} rows")
    if not df.empty:
        print(df.tail(2).to_string())
except Exception as e:
    print(f"Fund error: {e}")

try:
    df = ak.stock_zh_a_spot_em()
    print(f"Stocks: {len(df)} rows")
    match = df[df["代码"] == "600519"]
    if not match.empty:
        print(f"茅台: {match.iloc[0]['名称']} - {match.iloc[0]['最新价']}")
except Exception as e:
    print(f"Stock error: {e}")

"""Test fund_name_em search"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import akshare as ak

print("Loading fund names...")
df = ak.fund_name_em()
print(f"Total funds: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Search by code
match = df[df["基金代码"].str.contains("019005")]
print(f"\nSearch 019005: {len(match)} results")
if not match.empty:
    print(match[["基金代码", "基金简称"]].head(5).to_string())

# Search by name
match2 = df[df["基金简称"].str.contains("东方双债", na=False)]
print(f"\nSearch 东方双债: {len(match2)} results")
if not match2.empty:
    print(match2[["基金代码", "基金简称"]].head(5).to_string())

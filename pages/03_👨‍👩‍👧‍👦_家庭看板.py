"""家庭看板 - 所有家庭成员持仓汇总"""
import streamlit as st
from src.portfolio import get_family_summary, plot_portfolio_pie, plot_profit_bar

st.set_page_config(page_title="家庭看板", page_icon="👨‍👩‍👧‍👦", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("请先在首页登录")
    st.stop()

st.title("👨‍👩‍👧‍👦 家庭投资看板")

family_data = get_family_summary()

if not family_data:
    st.info("暂无家庭成员持仓数据")
    st.stop()

# 家庭总资产汇总
total_family_cost = sum(m["portfolio"]["total_cost"] for m in family_data)
total_family_value = sum(m["portfolio"]["total_value"] for m in family_data)
total_family_profit = sum(m["portfolio"]["total_profit"] for m in family_data)
total_family_profit_pct = (total_family_profit / total_family_cost * 100) if total_family_cost > 0 else 0

# 家庭总览 KPI
st.subheader("🏠 家庭资产总览")
kpi_cols = st.columns(4)
with kpi_cols[0]:
    st.metric("家庭总资产", f"¥{total_family_value:,.2f}")
with kpi_cols[1]:
    st.metric("家庭总成本", f"¥{total_family_cost:,.2f}")
with kpi_cols[2]:
    st.metric("家庭总盈亏", f"¥{total_family_profit:+,.2f}", delta=f"{total_family_profit:+,.2f}")
with kpi_cols[3]:
    st.metric("家庭收益率", f"{total_family_profit_pct:+.2f}%")

st.divider()

# 个人卡片
st.subheader("👤 个人明细")
person_cols = st.columns(len(family_data))
for i, member in enumerate(family_data):
    p = member["portfolio"]
    with person_cols[i]:
        with st.container(border=True):
            st.markdown(f"### {member['user_name']}")
            st.metric("总资产", f"¥{p['total_value']:,.2f}")
            st.metric("总盈亏", f"¥{p['total_profit']:+,.2f}", delta=f"{p['total_profit_pct']:+.2f}%")
            if p["items"]:
                fig = plot_portfolio_pie(p)
                st.plotly_chart(fig, use_container_width=True)

# 家庭持仓明细
st.divider()
st.subheader("📋 家庭持仓明细")
all_items = []
for member in family_data:
    for item in member["portfolio"]["items"]:
        type_map = {"stock": "股票", "fund": "基金", "bond": "债券", "gold": "黄金"}
        all_items.append({
            "持有人": member["user_name"],
            "类型": type_map.get(item["asset_type"], item["asset_type"]),
            "名称": item["asset_name"],
            "代码": item["asset_code"],
            "持有数量": item["quantity"],
            "市值": f"¥{item['value']:,.2f}",
            "盈亏": f"¥{item['profit']:+,.2f}",
            "收益率": f"{item['profit_pct']:+.2f}%",
        })

if all_items:
    st.dataframe(all_items, use_container_width=True, hide_index=True)

# 家庭资产分布图（合并所有持仓）
st.divider()
st.subheader("📊 家庭资产分布")
from src.portfolio import calculate_portfolio

all_holdings = []
for member in family_data:
    for h in member["portfolio"]["items"]:
        all_holdings.append(h)

# 汇总计算家庭合并持仓做图表
combined_items = {}
for item in all_holdings:
    key = (item["asset_type"], item["asset_code"])
    if key in combined_items:
        combined_items[key]["value"] += item["value"]
        combined_items[key]["cost"] += item["cost"]
        combined_items[key]["profit"] += item["profit"]
    else:
        combined_items[key] = {
            "asset_type": item["asset_type"],
            "asset_name": item["asset_name"],
            "value": item["value"],
            "cost": item["cost"],
            "profit": item["profit"],
        }

# 家庭合并饼图
import plotly.express as px
type_values = {}
for item in combined_items.values():
    t = item["asset_type"]
    type_values[t] = type_values.get(t, 0) + item["value"]

type_names = {"stock": "股票", "fund": "基金", "bond": "债券", "gold": "黄金"}
fig = px.pie(
    values=list(type_values.values()),
    names=[type_names.get(k, k) for k in type_values.keys()],
    title="家庭资产分布",
    hole=0.4,
    color_discrete_sequence=px.colors.sequential.Greens_r,
)
fig.update_traces(textposition="inside", textinfo="percent+label")
st.plotly_chart(fig, use_container_width=True)

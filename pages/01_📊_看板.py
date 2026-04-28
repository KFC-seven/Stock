"""看板 - 投资总览"""
import streamlit as st
import plotly.express as px
from src.portfolio import (
    get_user_holdings, calculate_portfolio, get_asset_distribution,
    plot_portfolio_pie, plot_profit_bar
)
from src.data_provider import update_all_prices
from src.styles import inject_css
from src.auth import ensure_auth

st.set_page_config(page_title="投资看板", page_icon="📊", layout="wide")
inject_css()

ensure_auth()

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("name", "用户")

# 获取持仓数据
holdings = get_user_holdings(user_id)
portfolio = calculate_portfolio(holdings) if holdings else None

st.title(f"📊 {user_name} 的投资看板")

# 顶部：关键指标
if portfolio:
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        st.metric("总资产", f"¥{portfolio['total_value']:,.2f}")
    with kpi_cols[1]:
        st.metric("总成本", f"¥{portfolio['total_cost']:,.2f}")
    with kpi_cols[2]:
        delta = f"{portfolio['total_profit']:+,.2f}"
        st.metric("总盈亏", f"¥{delta}", delta=delta)
    with kpi_cols[3]:
        st.metric("收益率", f"{portfolio['total_profit_pct']:+.2f}%")

    st.divider()

    # 图表行
    chart_cols = st.columns(2)
    with chart_cols[0]:
        fig_pie = plot_portfolio_pie(portfolio)
        st.plotly_chart(fig_pie, use_container_width=True)
    with chart_cols[1]:
        fig_bar = plot_profit_bar(portfolio)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # 持仓详情表格
    st.subheader("📋 持仓明细")
    detail_data = []
    for item in portfolio["items"]:
        type_map = {"stock": "股票", "fund": "基金", "bond": "债券", "gold": "黄金"}
        detail_data.append({
            "类型": type_map.get(item["asset_type"], item["asset_type"]),
            "名称": item["asset_name"],
            "代码": item["asset_code"],
            "持有数量": item["quantity"],
            "成本价": f"¥{item['cost_price']:.4f}",
            "现价": f"¥{item['current_price']:.4f}",
            "市值": f"¥{item['value']:,.2f}",
            "盈亏": f"¥{item['profit']:+,.2f}",
            "收益率": f"{item['profit_pct']:+.2f}%",
        })

    st.dataframe(detail_data, use_container_width=True, hide_index=True)

else:
    st.info("📭 还没有持仓记录，请在「持仓管理」页面添加")

    # 手动更新按钮
st.divider()
if st.button("🔄 手动更新最新行情", type="secondary", use_container_width=True):
    with st.spinner("正在获取最新行情..."):
        results = update_all_prices(holdings)
        success = sum(1 for r in results if r[3])
        fail = sum(1 for r in results if not r[3])
        st.toast(f"更新完成：成功 {success}，失败 {fail}", icon="✅")
        st.rerun()

"""持仓管理 - 添加/编辑/删除持仓"""
import streamlit as st
from datetime import date
from src.portfolio import (
    get_user_holdings, add_holding, update_holding, delete_holding
)
from src.data_provider import get_current_price, save_price, search_asset
from src.styles import inject_css

st.set_page_config(page_title="持仓管理", page_icon="📈", layout="wide")
inject_css()

if not st.session_state.get("authentication_status"):
    st.warning("请先在首页登录")
    st.stop()

user_id = st.session_state.get("user_id")
user_name = st.session_state.get("name", "用户")

st.title(f"📈 持仓管理")

ASSET_TYPES = {
    "stock": "股票",
    "fund": "基金",
    "bond": "债券",
    "gold": "黄金",
}

# 初始化搜索状态
if "search_results" not in st.session_state:
    st.session_state.search_results = None
if "selected_asset" not in st.session_state:
    st.session_state.selected_asset = None

# 添加新持仓
with st.expander("➕ 添加新持仓", expanded=True):
    # 搜索区：输入即搜 + 结果下拉
    search_query = st.text_input(
        "搜索资产",
        placeholder="输入代码或名称，自动搜索..."
    )

    # 自动搜索（每次 rerun 检查输入变化）
    if search_query and len(search_query.strip()) >= 1:
        q = search_query.strip()
        if st.session_state.get("_last_search") != q:
            st.session_state._last_search = q
            results = search_asset(q)
            st.session_state.search_results = results
            st.session_state.selected_asset = None

    # 显示搜索结果
    if st.session_state.get("search_results"):
        results = st.session_state.search_results
        if results:
            options = [f"[{r['type_label']}] {r['code']} - {r['name']}" for r in results]
            selected = st.radio("匹配结果：", options, index=None, horizontal=True, label_visibility="collapsed")
            if selected:
                idx = options.index(selected)
                st.session_state.selected_asset = results[idx]
                st.session_state.search_results = None
                st.session_state._last_search = ""
                st.rerun()
        else:
            st.caption("未找到匹配，请手动填写下方信息")

    # 已选中的资产，显示确认信息
    if st.session_state.get("selected_asset"):
        a = st.session_state.selected_asset
        st.success(f"已识别: [{a['type_label']}] {a['code']} - {a['name']}")

    # 添加表单（key 随选中资产变化，确保选中后自动填充）
    selected_code = st.session_state.selected_asset["code"] if st.session_state.get("selected_asset") else ""
    form_key = f"add_form_{selected_code}" if selected_code else "add_form_empty"

    with st.form(form_key):
        cols = st.columns(2)
        with cols[0]:
            default_type = st.session_state.selected_asset["type"] if st.session_state.get("selected_asset") else "stock"
            asset_type = st.selectbox(
                "资产类型",
                options=list(ASSET_TYPES.keys()),
                format_func=lambda x: ASSET_TYPES[x],
                index=list(ASSET_TYPES.keys()).index(default_type) if default_type in ASSET_TYPES else 0,
            )
            asset_code = st.text_input(
                "代码",
                value=st.session_state.selected_asset["code"] if st.session_state.get("selected_asset") else "",
                placeholder="如: 600519"
            )
        with cols[1]:
            asset_name = st.text_input(
                "名称",
                value=st.session_state.selected_asset["name"] if st.session_state.get("selected_asset") else "",
                placeholder="如: 贵州茅台"
            )
            quantity = st.number_input("持有数量", min_value=0.0, step=0.01, format="%.4f")

        col3, col4 = st.columns(2)
        with col3:
            cost_price = st.number_input("成本价", min_value=0.0, step=0.001, format="%.4f")
        with col4:
            buy_date = st.date_input("买入日期", value=date.today())

        notes = st.text_area("备注（可选）", placeholder="买入理由、备注信息...")
        submitted = st.form_submit_button("确认添加", type="primary", use_container_width=True)

        if submitted:
            if not asset_code or quantity <= 0 or cost_price <= 0:
                st.error("请填写完整信息（代码、数量、成本价必填）")
            else:
                ok, msg = add_holding(
                    user_id, asset_type, asset_code.strip(),
                    asset_name.strip() or asset_code.strip(),
                    quantity, cost_price, buy_date, notes
                )
                if ok:
                    st.success("持仓已添加，正在获取最新行情...")
                    price = get_current_price(asset_code.strip(), asset_type)
                    if price and price > 0:
                        save_price(asset_code.strip(), asset_type, price)
                        st.toast(f"已获取最新价格: ¥{price:.4f}", icon="💰")
                    else:
                        st.info("暂未获取到实时行情，今晚 22:00 自动更新")
                    # 清空搜索状态
                    st.session_state.search_results = None
                    st.session_state.selected_asset = None
                    st.rerun()
                else:
                    st.error(msg)

# 现有持仓列表
st.divider()
st.subheader("📋 我的持仓")

holdings = get_user_holdings(user_id)

if not holdings:
    st.info("暂无持仓记录，请在上方添加")
    st.stop()

# 显示每个持仓的编辑/删除卡片
for h in holdings:
    type_label = ASSET_TYPES.get(h.asset_type, h.asset_type)
    with st.container(border=True):
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.markdown(f"**{h.asset_name}** ({h.asset_code})")
            st.caption(f"类型: {type_label} | 买入: {h.buy_date or '未设置'}")
        with cols[1]:
            st.markdown(f"数量: **{h.quantity:.4f}**")
            st.markdown(f"成本价: **¥{h.cost_price:.4f}**")
        with cols[2]:
            # 编辑按钮
            edit_key = f"edit_{h.id}"
            del_key = f"del_{h.id}"
            if st.button("✏️ 编辑", key=edit_key, use_container_width=True):
                st.session_state[f"editing_{h.id}"] = True

            if st.button("🗑️ 删除", key=del_key, use_container_width=True):
                ok, msg = delete_holding(h.id)
                if ok:
                    st.toast(msg, icon="✅")
                    st.rerun()
                else:
                    st.error(msg)

        # 编辑表单
        if st.session_state.get(f"editing_{h.id}"):
            with st.form(f"edit_form_{h.id}", border=False):
                ec1, ec2 = st.columns(2)
                with ec1:
                    new_type = st.selectbox(
                        "类型",
                        options=list(ASSET_TYPES.keys()),
                        format_func=lambda x: ASSET_TYPES[x],
                        index=list(ASSET_TYPES.keys()).index(h.asset_type) if h.asset_type in ASSET_TYPES else 0,
                        key=f"type_{h.id}"
                    )
                    new_code = st.text_input("代码", value=h.asset_code, key=f"code_{h.id}")
                    new_qty = st.number_input("数量", value=h.quantity, step=0.01, format="%.4f", key=f"qty_{h.id}")
                with ec2:
                    new_name = st.text_input("名称", value=h.asset_name, key=f"name_{h.id}")
                    new_cost = st.number_input("成本价", value=h.cost_price, step=0.001, format="%.4f", key=f"cost_{h.id}")
                    new_notes = st.text_area("备注", value=h.notes or "", key=f"notes_{h.id}")

                ec3, ec4 = st.columns(2)
                with ec3:
                    if st.form_submit_button("保存", type="primary", use_container_width=True):
                        ok, msg = update_holding(
                            h.id,
                            asset_type=new_type,
                            asset_code=new_code.strip(),
                            asset_name=new_name,
                            quantity=new_qty,
                            cost_price=new_cost,
                            notes=new_notes,
                        )
                        if ok:
                            st.success(msg)
                            st.session_state[f"editing_{h.id}"] = False
                            st.rerun()
                        else:
                            st.error(msg)
                with ec4:
                    if st.form_submit_button("取消", use_container_width=True):
                        st.session_state[f"editing_{h.id}"] = False
                        st.rerun()

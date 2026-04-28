"""持仓管理 - 添加/编辑/删除持仓"""
import streamlit as st
from datetime import date
from src.portfolio import (
    get_user_holdings, add_holding, update_holding, delete_holding
)

st.set_page_config(page_title="持仓管理", page_icon="📈", layout="wide")

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

# 添加新持仓
with st.expander("➕ 添加新持仓", expanded=False):
    with st.form("add_holding_form"):
        col1, col2 = st.columns(2)
        with col1:
            asset_type = st.selectbox(
                "资产类型",
                options=list(ASSET_TYPES.keys()),
                format_func=lambda x: ASSET_TYPES[x],
            )
            asset_code = st.text_input("代码", placeholder="如: 600519（股票代码）")
        with col2:
            asset_name = st.text_input("名称", placeholder="如: 贵州茅台")
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
                    st.success(msg)
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
                    new_qty = st.number_input("数量", value=h.quantity, step=0.01, format="%.4f", key=f"qty_{h.id}")
                    new_cost = st.number_input("成本价", value=h.cost_price, step=0.001, format="%.4f", key=f"cost_{h.id}")
                with ec2:
                    new_name = st.text_input("名称", value=h.asset_name, key=f"name_{h.id}")
                    new_notes = st.text_area("备注", value=h.notes or "", key=f"notes_{h.id}")

                ec3, ec4 = st.columns(2)
                with ec3:
                    if st.form_submit_button("保存", type="primary", use_container_width=True):
                        ok, msg = update_holding(
                            h.id,
                            quantity=new_qty,
                            cost_price=new_cost,
                            asset_name=new_name,
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

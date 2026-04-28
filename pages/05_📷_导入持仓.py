"""导入持仓 - 多图OCR识别 + 合并去重导入"""
import streamlit as st
import pandas as pd
from io import BytesIO
from PIL import Image
from src.portfolio import get_user_holdings, add_holding, update_holding
from src.data_provider import save_price
from src.ocr_import import ocr_image, parse_fund_text, calculate_holding_from_screenshot

st.set_page_config(page_title="导入持仓", page_icon="📷", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("请先在首页登录")
    st.stop()

user_id = st.session_state.get("user_id")
st.title("📷 导入持仓")

st.markdown("""
支持一次上传多张截图，自动合并重复持仓。
支持：**支付宝基金**、**天天基金**、**券商APP**等。
""")

# 上传多张图片
uploaded_files = st.file_uploader(
    "选择截图（可多选）", type=["png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="可一次选择多张截图，Ctrl/Command 多选"
)

if uploaded_files:
    st.info(f"已选择 {len(uploaded_files)} 张截图")

    # 显示缩略图
    with st.expander("📸 查看已上传的截图", expanded=False):
        cols = st.columns(min(len(uploaded_files), 4))
        for i, f in enumerate(uploaded_files):
            with cols[i % 4]:
                img = Image.open(f)
                st.image(img, caption=f"{f.name}", use_container_width=True)

    # 开始识别
    if st.button("🔍 开始识别所有截图", type="primary", use_container_width=True):
        all_parsed = []
        progress_bar = st.progress(0)

        for i, f in enumerate(uploaded_files):
            with st.status(f"正在识别: {f.name}...", expanded=False) as status:
                try:
                    image = Image.open(f)
                    raw_text = ocr_image(image)
                    parsed = parse_fund_text(raw_text)
                    for item in parsed:
                        item["_source"] = f.name
                    all_parsed.extend(parsed)
                    status.update(label=f"✅ {f.name}: 识别到 {len(parsed)} 条", state="complete")
                except Exception as e:
                    status.update(label=f"❌ {f.name}: 识别失败", state="error")
            progress_bar.progress((i + 1) / len(uploaded_files))

        if all_parsed:
            st.session_state["ocr_all_parsed"] = all_parsed
            st.success(f"所有截图识别完成，共识别到 {len(all_parsed)} 条记录")
        else:
            st.warning("所有截图均未识别到持仓信息")
            st.session_state["ocr_all_parsed"] = []

# 识别结果处理
if "ocr_all_parsed" in st.session_state and st.session_state["ocr_all_parsed"]:
    all_parsed = st.session_state["ocr_all_parsed"]
    st.divider()
    st.subheader("📋 识别结果")

    # 显示每个识别项，供用户编辑
    edited_items = []
    for i, item in enumerate(all_parsed):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            with c1:
                name = st.text_input(
                    "名称", value=item.get("name", ""),
                    key=f"ocr_name_{i}"
                )
            with c2:
                profit_amount = st.number_input(
                    "昨日收益", value=item.get("profit_amount") or 0.0,
                    step=0.01, format="%.2f", key=f"ocr_amt_{i}"
                )
            with c3:
                profit_rate = st.number_input(
                    "收益率%", value=item.get("profit_rate") or 0.0,
                    step=0.01, format="%.2f", key=f"ocr_rate_{i}"
                )
            with c4:
                source = item.get("_source", "")
                st.caption(f"来源: {source}")

            # 计算按钮
            if st.button("📊 计算", key=f"ocr_calc_{i}", use_container_width=True):
                result = calculate_holding_from_screenshot(name, profit_amount, profit_rate)
                if "error" in result:
                    st.warning(f"计算失败: {result['error']}")
                else:
                    st.session_state[f"ocr_calc_{i}"] = result
                    st.rerun()

            # 显示计算结果
            if st.session_state.get(f"ocr_calc_{i}"):
                r = st.session_state[f"ocr_calc_{i}"]
                if "error" not in r:
                    st.success(
                        f"✅ {r.get('fund_name', name)}({r.get('fund_code', '?')}) | "
                        f"份额: {r['quantity']} | "
                        f"成本价: ¥{r['cost_price']} | "
                        f"净值: ¥{r['current_price']}"
                    )

    # ---- 合并去重 + 预览 ----
    st.divider()
    st.subheader("📊 导入预览")

    # 收集所有已计算的结果
    all_ready = []
    for i in range(len(all_parsed)):
        r = st.session_state.get(f"ocr_calc_{i}")
        if r and "error" not in r:
            # 用用户编辑框中的最新值覆盖
            name_key = f"ocr_name_{i}"
            if name_key in st.session_state:
                r["fund_name"] = st.session_state[name_key]
            all_ready.append(r)

    if not all_ready:
        st.info("请先点击每条记录旁的「计算」按钮，确认识别结果")
    else:
        # --- 合并重复（同一基金代码合并份额和成本）---
        merged = {}
        for r in all_ready:
            code = r.get("fund_code", "")
            if code in merged:
                # 合并：份额相加，成本价加权平均
                existing = merged[code]
                total_qty = existing["quantity"] + r["quantity"]
                total_cost = existing["quantity"] * existing["cost_price"] + r["quantity"] * r["cost_price"]
                merged[code] = {
                    "fund_name": r["fund_name"],
                    "fund_code": code,
                    "quantity": round(total_qty, 2),
                    "cost_price": round(total_cost / total_qty, 4),
                    "current_price": r["current_price"],
                }
            else:
                merged[code] = {
                    "fund_name": r["fund_name"],
                    "fund_code": code,
                    "quantity": r["quantity"],
                    "cost_price": r["cost_price"],
                    "current_price": r["current_price"],
                }

        merge_count = len(all_ready) - len(merged)
        if merge_count > 0:
            st.success(f"已合并 {merge_count} 条重复持仓")

        # --- 检查与现有持仓的冲突 ---
        existing_holdings = get_user_holdings(user_id)
        existing_map = {}
        for h in existing_holdings:
            existing_map[h.asset_code] = h

        conflict_items = []
        new_items = []
        for code, data in merged.items():
            if code in existing_map:
                conflict_items.append(data)
            else:
                new_items.append(data)

        # --- 显示导入表格 ---
        preview_rows = []
        for data in new_items:
            preview_rows.append({
                "状态": "🆕 新增",
                "名称": data["fund_name"],
                "代码": data["fund_code"],
                "份额": data["quantity"],
                "成本价": data["cost_price"],
            })
        for data in conflict_items:
            existing = existing_map[data["fund_code"]]
            preview_rows.append({
                "状态": "⚠️ 已存在",
                "名称": data["fund_name"],
                "代码": data["fund_code"],
                "份额": f"原{existing.quantity:.2f} → 现{data['quantity']:.2f}",
                "成本价": f"原{existing.cost_price} → 现{data['cost_price']}",
            })

        st.dataframe(pd.DataFrame(preview_rows), hide_index=True, use_container_width=True)

        # 冲突处理选项
        if conflict_items:
            conflict_action = st.radio(
                "已存在的持仓处理方式：",
                options=["跳过（保留原数据）", "覆盖（用量和新数据替换）"],
                horizontal=True,
            )
        else:
            conflict_action = "跳过（保留原数据）"

        # 确认导入
        if st.button("✅ 确认导入", type="primary", use_container_width=True):
            success_count = 0
            skip_count = 0
            update_count = 0

            # 新增
            for data in new_items:
                ok, msg = add_holding(
                    user_id=user_id,
                    asset_type="fund",
                    asset_code=data["fund_code"],
                    asset_name=data["fund_name"],
                    quantity=data["quantity"],
                    cost_price=data["cost_price"],
                )
                if ok:
                    save_price(data["fund_code"], "fund", data["current_price"])
                    success_count += 1

            # 处理冲突
            for data in conflict_items:
                code = data["fund_code"]
                if conflict_action == "覆盖（用量和新数据替换）":
                    # 更新现有持仓
                    existing = existing_map[code]
                    ok, msg = update_holding(
                        existing.id,
                        quantity=data["quantity"],
                        cost_price=data["cost_price"],
                        asset_name=data["fund_name"],
                    )
                    if ok:
                        save_price(data["fund_code"], "fund", data["current_price"])
                        update_count += 1
                else:
                    skip_count += 1

            total = success_count + update_count
            if total > 0:
                st.balloons()
                st.success(
                    f"导入完成！新增 {success_count}，更新 {update_count}，跳过 {skip_count}"
                )
            else:
                st.info("没有可导入的数据")

            # 清空会话状态
            for key in list(st.session_state.keys()):
                if key.startswith("ocr_") or key.startswith("ocr_calc_"):
                    del st.session_state[key]
            st.rerun()

# 手动输入备选方案
with st.expander("✏️ 手动输入（OCR识别不准确时使用）"):
    st.markdown("一行一个，格式：`基金名称, 昨日收益, 持有收益率`")
    manual_text = st.text_area(
        "手动输入",
        placeholder="东方双债添利债券D, 12.34, 5.67\n易方达蓝筹精选, -23.45, -3.21",
        height=100,
        label_visibility="collapsed",
    )
    if st.button("解析手动输入", use_container_width=True):
        if manual_text.strip():
            lines = manual_text.strip().split("\n")
            parsed = []
            for line in lines:
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 3:
                    try:
                        parsed.append({
                            "name": parts[0],
                            "profit_amount": float(parts[1]),
                            "profit_rate": float(parts[2]),
                            "_source": "手动输入",
                        })
                    except ValueError:
                        pass
            if parsed:
                st.session_state["ocr_all_parsed"] = parsed
                st.rerun()

"""导入持仓 - OCR 识别截图导入"""
import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
from src.portfolio import add_holding
from src.data_provider import get_current_price, save_price
from src.ocr_import import ocr_image, parse_fund_text, batch_parse_and_calculate

st.set_page_config(page_title="导入持仓", page_icon="📷", layout="wide")

if not st.session_state.get("authentication_status"):
    st.warning("请先在首页登录")
    st.stop()

user_id = st.session_state.get("user_id")
st.title("📷 导入持仓")

st.markdown("""
上传你的基金/股票持仓截图，系统将自动识别并计算持仓数据。
支持：**支付宝基金**、**天天基金**、**券商APP**等截图。
""")

# 上传图片
uploaded_file = st.file_uploader(
    "选择截图", type=["png", "jpg", "jpeg"],
    help="支持支付宝基金、天天基金等APP的持仓截图"
)

if uploaded_file:
    # 显示图片
    image = Image.open(uploaded_file)

    col1, col2 = st.columns(2)
    with col1:
        st.image(image, caption="上传的截图", use_container_width=True)

    with col2:
        if st.button("🔍 开始识别", type="primary", use_container_width=True):
            with st.spinner("正在识别图片中的文字..."):
                try:
                    raw_text = ocr_image(image)
                    st.session_state["ocr_raw_text"] = raw_text

                    parsed = parse_fund_text(raw_text)
                    st.session_state["ocr_parsed"] = parsed

                    if parsed:
                        st.success(f"识别到 {len(parsed)} 条基金持仓")
                    else:
                        st.warning("未自动识别到持仓信息，请手动查看下方识别结果")
                except Exception as e:
                    st.error(f"OCR识别失败: {e}")
                    st.session_state["ocr_raw_text"] = ""
                    st.session_state["ocr_parsed"] = []

    # 显示OCR原始文本
    if "ocr_raw_text" in st.session_state and st.session_state["ocr_raw_text"]:
        with st.expander("📝 OCR 原始识别文本（可编辑）"):
            raw_text = st.text_area(
                "识别结果",
                value=st.session_state["ocr_raw_text"],
                height=200,
                label_visibility="collapsed",
            )
            st.session_state["ocr_raw_text"] = raw_text

            # 重新解析
            if st.button("🔄 重新解析", use_container_width=True):
                parsed = parse_fund_text(raw_text)
                st.session_state["ocr_parsed"] = parsed
                st.rerun()

    # 显示解析结果
    if "ocr_parsed" in st.session_state and st.session_state["ocr_parsed"]:
        st.divider()
        st.subheader("📋 识别到以下持仓，请核对并补充")

        parsed_items = st.session_state["ocr_parsed"]

        # 展示每个识别项
        import_items = []
        for i, item in enumerate(parsed_items):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    name = st.text_input(
                        "基金名称", value=item.get("name", ""),
                        key=f"name_{i}"
                    )
                with c2:
                    profit_amount = st.number_input(
                        "昨日收益(元)", value=item.get("profit_amount") or 0.0,
                        step=0.01, format="%.2f", key=f"amt_{i}"
                    )
                with c3:
                    profit_rate = st.number_input(
                        "持有收益率(%)", value=item.get("profit_rate") or 0.0,
                        step=0.01, format="%.2f", key=f"rate_{i}"
                    )

                if st.button("📊 计算此持仓", key=f"calc_{i}", use_container_width=True):
                    from src.ocr_import import calculate_holding_from_screenshot
                    result = calculate_holding_from_screenshot(
                        name, profit_amount, profit_rate
                    )
                    st.session_state[f"calc_result_{i}"] = result
                    st.rerun()

                # 显示计算结果
                if st.session_state.get(f"calc_result_{i}"):
                    result = st.session_state[f"calc_result_{i}"]
                    if "error" in result:
                        st.warning(f"计算失败: {result['error']}")
                    else:
                        st.success(
                            f"✅ {result['fund_name']}({result['fund_code']})\n"
                            f"  份额: {result['quantity']} | "
                            f"成本价: ¥{result['cost_price']} | "
                            f"最新净值: ¥{result['current_price']}"
                        )
                        st.session_state[f"import_ready_{i}"] = result

        # 批量导入
        st.divider()
        ready_items = []
        for i in range(len(parsed_items)):
            result = st.session_state.get(f"import_ready_{i}")
            if result and "error" not in result:
                ready_items.append(result)

        if ready_items:
            st.info(f"已准备好 {len(ready_items)} 条记录，确认后导入")

            # 显示预览表格
            preview_data = []
            for r in ready_items:
                preview_data.append({
                    "基金名称": r["fund_name"],
                    "代码": r.get("fund_code", ""),
                    "持有份额": r["quantity"],
                    "成本价": r["cost_price"],
                    "最新净值": r["current_price"],
                })
            st.dataframe(pd.DataFrame(preview_data), hide_index=True, use_container_width=True)

            if st.button("✅ 确认导入", type="primary", use_container_width=True):
                success_count = 0
                for r in ready_items:
                    ok, msg = add_holding(
                        user_id=user_id,
                        asset_type="fund",
                        asset_code=r.get("fund_code", ""),
                        asset_name=r["fund_name"],
                        quantity=r["quantity"],
                        cost_price=r["cost_price"],
                    )
                    if ok:
                        # 保存最新净值
                        save_price(r.get("fund_code", ""), "fund", r["current_price"])
                        success_count += 1

                if success_count > 0:
                    st.balloons()
                    st.success(f"成功导入 {success_count} 条持仓记录！")
                    # 清空状态
                    for key in list(st.session_state.keys()):
                        if key.startswith("ocr_") or "calc_result_" in key or "import_ready_" in key:
                            del st.session_state[key]
                    st.rerun()

    # 手动输入备选方案
    with st.expander("✏️ 手动导入（OCR识别不准确时使用）"):
        st.markdown("手动输入基金信息，一行一个，格式：`基金名称, 昨日收益, 持有收益率`")
        manual_text = st.text_area(
            "手动输入",
            placeholder="例：\n东方双债添利债券D, 12.34, 5.67\n易方达蓝筹精选, -23.45, -3.21",
            height=100,
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
                            })
                        except ValueError:
                            pass
                if parsed:
                    st.session_state["ocr_parsed"] = parsed
                    st.rerun()

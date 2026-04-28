"""OCR 导入模块 - 截图识别 + 持仓计算"""
import re
import logging
from datetime import date, datetime

logger = logging.getLogger(__name__)

# ---------- OCR ----------

def preprocess_image(image):
    """图片预处理：提高 OCR 识别率"""
    import cv2
    import numpy as np

    img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 二值化
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # 降噪
    denoised = cv2.medianBlur(thresh, 1)
    return denoised


def ocr_image(image):
    """OCR 识别图片中的文字"""
    import pytesseract

    processed = preprocess_image(image)
    custom_config = r"--oem 1 --psm 6 -l chi_sim+eng"
    text = pytesseract.image_to_string(processed, config=custom_config)
    return text


# ---------- 文本解析 ----------

def parse_numbers(text):
    """从文本中提取所有数字（含正负号和小数）"""
    return re.findall(r"[-+]?\d+\.?\d*", text)


def parse_fund_text(text):
    """解析基金持仓截图文本，提取基金名称、昨日收益、持有收益率"""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    results = []

    # 常见投资APP的文本模式
    # 模式：一行是基金名称，后面跟着收益率和收益金额
    current_fund = None
    for i, line in enumerate(lines):
        # 检测基金名称（含"基金"、"增长"、"混合"、"债券"等关键词的行）
        fund_keywords = ["基金", "增长", "混合", "债券", "指数", "货币", "纯债",
                         "双债", "添利", "增利", "优选", "精选", "行业", "ETF",
                         "联接", "LOF", "FOF", "量化", "增强", "沪深", "中证"]
        has_fund_kw = any(kw in line for kw in fund_keywords)
        # 也匹配纯中文名称（至少2个汉字，不含数字开头）
        has_chinese_name = bool(re.match(r"^[一-龥][一-龥\w]{1,20}$", line))

        if has_fund_kw or (has_chinese_name and len(line) >= 3):
            # 检查周围行是否包含收益率和收益金额
            context = "\n".join(lines[max(0, i - 1):min(len(lines), i + 4)])
            nums = parse_numbers(context)

            profit_rate = None   # 持有收益率 (%)
            profit_amount = None  # 昨日收益 (元)

            for n in nums:
                nf = float(n)
                # 收益率：通常在 -100 到 100 之间（百分比）
                if abs(nf) < 100 and abs(nf) > 0.01:
                    profit_rate = nf
                # 收益金额：可能是几千到几万
                elif abs(nf) >= 100:
                    profit_amount = nf

            results.append({
                "name": line,
                "profit_rate": profit_rate,
                "profit_amount": profit_amount,
                "raw_context": context,
            })

    # 如果上面的模式没匹配到，尝试整体扫描
    if not results:
        results = parse_fund_text_fallback(text)

    return results


def parse_fund_text_fallback(text):
    """备选解析：扫描所有行，找数字对（收益率 + 收益金额）"""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    results = []

    # 找包含数字的行
    number_lines = []
    for i, line in enumerate(lines):
        nums = parse_numbers(line)
        if len(nums) >= 2:
            number_lines.append((i, line, nums))

    # 找中文名称行附近的数字行
    for i, line in enumerate(lines):
        # 至少2个汉字的行可能是名称
        chinese_chars = re.findall(r"[一-龥]", line)
        if len(chinese_chars) >= 2 and not any(kw in line for kw in ["收益率", "持有", "昨日", "收益"]):
            # 看它后面的行是否有数字
            for j in range(i + 1, min(len(lines), i + 4)):
                nums = parse_numbers(lines[j])
                if len(nums) >= 2:
                    profit_rate = None
                    profit_amount = None
                    for n in nums:
                        nf = float(n)
                        if abs(nf) < 100 and abs(nf) > 0.01:
                            profit_rate = nf
                        elif abs(nf) >= 100:
                            profit_amount = nf
                    results.append({
                        "name": line,
                        "profit_rate": profit_rate,
                        "profit_amount": profit_amount,
                        "raw_context": lines[j],
                    })
                    break

    return results


# ---------- 基金代码查询 ----------

_fund_name_cache = None


def _cached(func):
    """如果有 Streamlit 则用 st.cache_data 缓存，否则直接执行"""
    try:
        import streamlit as st
        return st.cache_data(ttl=3600)(func)
    except ImportError:
        return func


@_cached
def _load_fund_names_from_api():
    """直接从 API 加载基金列表（可被 Streamlit 缓存）"""
    import akshare as ak
    df = ak.fund_name_em()
    lookup = {}
    for _, row in df.iterrows():
        code = str(row["基金代码"])
        short = str(row["基金简称"]).strip()
        full = str(row.get("基金全称", short)).strip()
        lookup[short] = code
        if full != short:
            lookup[full] = code
    return lookup


def _load_fund_names():
    """加载并缓存基金名称列表"""
    global _fund_name_cache
    if _fund_name_cache is not None:
        return _fund_name_cache
    _fund_name_cache = _load_fund_names_from_api()
    return _fund_name_cache


def search_fund_by_name(name):
    """根据基金名称模糊搜索基金代码"""
    name = name.strip()
    lookup = _load_fund_names()

    # 1. 精确匹配
    if name in lookup:
        code = lookup[name]
        return code, name

    # 2. 包含匹配（找名称中包含输入关键词的基金）
    matches = []
    for full_name, code in lookup.items():
        if name[:4] in full_name:
            matches.append((full_name, code))

    if matches:
        # 取最短的名称（最可能是精确简称）
        matches.sort(key=lambda x: len(x[0]))
        return matches[0][1], matches[0][0]

    return None, name


# ---------- 净值计算 ----------

def get_fund_net_values(asset_code):
    """获取基金最新和上一交易日净值"""
    import akshare as ak

    try:
        df = ak.fund_open_fund_info_em(symbol=asset_code, indicator="单位净值走势")
        if df.empty or len(df) < 2:
            return None, None, None

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        latest_nav = float(latest["单位净值"])
        prev_nav = float(prev["单位净值"])
        # 计算日增长率
        daily_change = ((latest_nav - prev_nav) / prev_nav * 100) if prev_nav > 0 else 0

        return latest_nav, prev_nav, daily_change
    except Exception as e:
        logger.error(f"获取基金 {asset_code} 净值失败: {e}")
        return None, None, None


def calculate_holding_from_screenshot(fund_name, profit_amount, profit_rate):
    """根据截图信息计算持仓数据

    Args:
        fund_name: 基金名称
        profit_amount: 昨日收益（元）
        profit_rate: 持有收益率（%，如 5.67）

    Returns:
        dict with fund_code, fund_name, quantity, cost_price, current_price
    """
    # 1. 搜索基金代码
    fund_code, matched_name = search_fund_by_name(fund_name)
    if not fund_code:
        return {"error": f"未找到基金代码: {fund_name}"}

    # 2. 获取净值
    latest_nav, prev_nav, daily_change = get_fund_net_values(fund_code)
    if latest_nav is None or prev_nav is None:
        return {"error": f"获取净值失败: {fund_code}", "fund_code": fund_code}

    nav_diff = latest_nav - prev_nav

    # 3. 计算持有份额
    if abs(nav_diff) < 0.0001:
        # 净值没变，用日增长率推算
        if abs(daily_change) < 0.001:
            return {"error": f"净值无变化，无法计算份额", "fund_code": fund_code,
                    "current_price": latest_nav}
        prev_nav_calc = latest_nav / (1 + daily_change / 100)
        nav_diff = latest_nav - prev_nav_calc

    quantity = profit_amount / nav_diff if nav_diff != 0 else 0
    if quantity < 0:
        quantity = abs(quantity)

    # 4. 计算成本和成本价
    current_value = quantity * latest_nav
    # 持有收益率 = (当前市值 - 总成本) / 总成本
    total_cost = current_value / (1 + profit_rate / 100) if profit_rate != 0 else current_value
    cost_price = total_cost / quantity if quantity > 0 else 0

    return {
        "fund_code": fund_code,
        "fund_name": matched_name,
        "quantity": round(quantity, 2),
        "cost_price": round(cost_price, 4),
        "current_price": round(latest_nav, 4),
        "current_value": round(current_value, 2),
        "total_cost": round(total_cost, 2),
        "profit_rate": profit_rate,
        "profit_amount": profit_amount,
    }


def batch_parse_and_calculate(parsed_items):
    """批量解析OCR结果并计算持仓"""
    results = []
    for item in parsed_items:
        name = item.get("name", "")
        profit_amount = item.get("profit_amount")
        profit_rate = item.get("profit_rate")

        if not name or profit_amount is None or profit_rate is None:
            results.append({
                "fund_name": name or "未知",
                "error": "缺少必要数据（收益率或收益金额）",
            })
            continue

        result = calculate_holding_from_screenshot(name, profit_amount, profit_rate)
        result["fund_name"] = result.get("fund_name", name)
        results.append(result)

    return results

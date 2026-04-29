"""行情数据服务"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import logging
from datetime import date
from sqlalchemy.orm import Session

from app.models.models import Holding, DailyPrice

logger = logging.getLogger(__name__)


def _safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_stock_price(asset_code: str) -> float | None:
    try:
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=asset_code, period="daily", start_date="20200101")
        if df.empty:
            return None
        return _safe_float(df.iloc[-1]["收盘"])
    except Exception as e:
        logger.error(f"股票 {asset_code}: {e}")
        return None


def get_fund_net_value(asset_code: str) -> float | None:
    try:
        import akshare as ak
        df = ak.fund_open_fund_info_em(symbol=asset_code, indicator="单位净值走势")
        if df.empty:
            return None
        return _safe_float(df.iloc[-1]["单位净值"])
    except Exception as e:
        logger.error(f"基金 {asset_code}: {e}")
        return None


def get_bond_price(asset_code: str) -> float | None:
    try:
        import akshare as ak
        df = ak.bond_zh_cov()
        row = df[df["债券代码"] == asset_code]
        if row.empty:
            return None
        return _safe_float(row.iloc[0]["最新价"])
    except Exception as e:
        logger.error(f"债券 {asset_code}: {e}")
        return None


def get_gold_price() -> float | None:
    try:
        import akshare as ak
        df = ak.spot_gold_price_js()
        if df.empty:
            return None
        row = df[df["品种"].str.contains("AU99.99", na=False)]
        if row.empty:
            row = df.iloc[0:1]
        return _safe_float(row.iloc[0]["当前价格"])
    except Exception as e:
        logger.error(f"黄金: {e}")
        return None


ASSET_PROVIDERS = {
    "stock": get_stock_price,
    "fund": get_fund_net_value,
    "bond": get_bond_price,
}


def get_current_price(asset_code: str, asset_type: str) -> float | None:
    if asset_type == "gold":
        return get_gold_price()
    provider = ASSET_PROVIDERS.get(asset_type)
    return provider(asset_code) if provider else None


def save_price(db: Session, asset_code: str, asset_type: str, price: float):
    if price is None or price <= 0:
        return
    today = date.today()
    existing = (
        db.query(DailyPrice)
        .filter(DailyPrice.asset_code == asset_code, DailyPrice.asset_type == asset_type, DailyPrice.trade_date == today)
        .first()
    )
    if existing:
        existing.close_price = price
    else:
        db.add(DailyPrice(asset_code=asset_code, asset_type=asset_type, trade_date=today, close_price=price, source="akshare"))
    db.commit()


def update_all_prices(db: Session) -> list:
    holdings = db.query(Holding).all()
    results = []
    for h in holdings:
        price = get_current_price(h.asset_code, h.asset_type)
        if price and price > 0:
            save_price(db, h.asset_code, h.asset_type, price)
            results.append({"asset_code": h.asset_code, "asset_type": h.asset_type, "price": price, "success": True})
        else:
            results.append({"asset_code": h.asset_code, "asset_type": h.asset_type, "price": None, "success": False})
    return results


# 缓存基金名称列表
_fund_cache = None


def _get_fund_list():
    global _fund_cache
    if _fund_cache is not None:
        return _fund_cache
    import akshare as ak
    df = ak.fund_name_em()
    _fund_cache = df
    return df


def search_asset(query: str) -> list:
    results = []
    q = query.strip().upper()

    # 1. 搜索基金（使用 fund_name_em 全量列表，带缓存）
    try:
        df = _get_fund_list()
        match = df[df["基金代码"].str.contains(q, na=False) | df["基金简称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(5).iterrows():
            results.append({"code": str(row["基金代码"]), "name": row["基金简称"], "type": "fund", "type_label": "基金"})
    except Exception:
        pass

    # 2. 搜索可转债
    try:
        import akshare as ak
        bond_df = ak.bond_zh_cov()
        match = bond_df[bond_df["债券代码"].str.contains(q, na=False) | bond_df["债券简称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(3).iterrows():
            results.append({"code": str(row["债券代码"]), "name": row["债券简称"], "type": "bond", "type_label": "可转债"})
    except Exception:
        pass

    # 3. 搜索股票（逐个尝试查询）
    try:
        import akshare as ak
        df = ak.stock_zh_a_hist(symbol=q, period="daily", start_date="20250101")
        if not df.empty:
            name_col = df.columns[0]
            results.append({"code": q, "name": f"A股-{q}", "type": "stock", "type_label": "股票"})
    except Exception:
        pass

    # 4. 尝试通过 ETF 列表搜索股票
    try:
        import akshare as ak
        df = ak.fund_etf_spot_em()
        match = df[df["代码"].str.contains(q, na=False) | df["名称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(3).iterrows():
            if not any(r["code"] == str(row["代码"]) for r in results):
                results.append({"code": str(row["代码"]), "name": row["名称"], "type": "stock", "type_label": row.get("类型", "ETF")})
    except Exception:
        pass

    return results

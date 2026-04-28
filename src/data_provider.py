"""行情数据提供层 - 封装 AKShare"""
import os
import logging
from datetime import datetime, date
from src.database import get_session, DailyPrice

logger = logging.getLogger(__name__)


def _safe_float(val, default=0.0):
    """安全转换浮点数"""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default


def get_stock_price(asset_code):
    """获取A股最新行情"""
    try:
        df = _get_stock_list()
        row = df[df["代码"] == asset_code]
        if row.empty:
            logger.warning(f"未找到股票 {asset_code}")
            return None
        return _safe_float(row.iloc[0]["最新价"])
    except Exception as e:
        logger.error(f"获取股票 {asset_code} 行情失败: {e}")
        return None


def get_fund_net_value(asset_code):
    """获取公募基金最新净值"""
    try:
        import akshare as ak
        df = ak.fund_open_fund_info_em(symbol=asset_code, indicator="单位净值走势")
        if df.empty:
            logger.warning(f"未找到基金 {asset_code}")
            return None
        latest = df.iloc[-1]
        return _safe_float(latest["单位净值"])
    except Exception as e:
        logger.error(f"获取基金 {asset_code} 净值失败: {e}")
        return None


def get_gold_spot_price():
    """获取黄金现货价格（人民币/克）"""
    try:
        import akshare as ak
        df = ak.spot_gold_price_js()
        if df.empty:
            return None
        # 取 AU99.99 的价格
        row = df[df["品种"].str.contains("AU99.99", na=False)]
        if row.empty:
            row = df.iloc[0:1]
        return _safe_float(row.iloc[0]["当前价格"])
    except Exception as e:
        logger.error(f"获取黄金价格失败: {e}")
        return None


def get_bond_price(asset_code):
    """获取可转债最新价格"""
    try:
        df = _get_bond_list()
        row = df[df["债券代码"] == asset_code]
        if row.empty:
            logger.warning(f"未找到债券 {asset_code}")
            return None
        return _safe_float(row.iloc[0]["最新价"])
    except Exception as e:
        logger.error(f"获取债券 {asset_code} 价格失败: {e}")
        return None


ASSET_PROVIDERS = {
    "stock": get_stock_price,
    "fund": get_fund_net_value,
    "bond": get_bond_price,
}


# 本地文件缓存目录（跨重启持久化）
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def _load_or_fetch(name, fetch_func, ttl_hours=24):
    """本地文件缓存：优先读文件，过期或不存则调用 API 并写入文件"""
    import pandas as pd
    cache_file = os.path.join(CACHE_DIR, f"{name}.parquet")
    cache_valid = False

    if os.path.exists(cache_file):
        mtime = os.path.getmtime(cache_file)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        if age_hours < ttl_hours:
            cache_valid = True

    if cache_valid:
        try:
            return pd.read_parquet(cache_file)
        except Exception:
            pass

    # 缓存过期或读取失败 → 重新下载
    df = fetch_func()
    if df is not None and not df.empty:
        try:
            df.to_parquet(cache_file, index=False)
        except Exception:
            pass
    return df


def _fetch_stocks():
    import akshare as ak
    return ak.stock_zh_a_spot_em()


def _fetch_etfs():
    import akshare as ak
    return ak.fund_etf_spot_em()


def _fetch_bonds():
    import akshare as ak
    return ak.bond_zh_cov()


def _get_stock_list():
    return _load_or_fetch("stocks", _fetch_stocks)


def _get_etf_list():
    return _load_or_fetch("etfs", _fetch_etfs, ttl_hours=24)


def _get_bond_list():
    return _load_or_fetch("bonds", _fetch_bonds, ttl_hours=24)


def search_asset(query):
    """根据代码或名称搜索匹配的资产，返回 [{code, name, type}, ...]"""
    import pandas as pd

    results = []
    q = query.strip().upper()

    # 1. 搜索 A股
    try:
        df = _get_stock_list()
        match = df[df["代码"].str.contains(q, na=False) | df["名称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(5).iterrows():
            results.append({
                "code": str(row["代码"]),
                "name": row["名称"],
                "type": "stock",
                "type_label": "股票",
            })
    except Exception:
        pass

    # 2. 搜索基金（ETF）
    try:
        etf_df = _get_etf_list()
        match = etf_df[etf_df["代码"].str.contains(q, na=False) | etf_df["名称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(3).iterrows():
            results.append({
                "code": str(row["代码"]),
                "name": row["名称"],
                "type": "fund",
                "type_label": "基金(ETF)",
            })
    except Exception:
        pass

    # 3. 搜索可转债
    try:
        bond_df = _get_bond_list()
        match = bond_df[bond_df["债券代码"].str.contains(q, na=False) | bond_df["债券简称"].str.contains(query.strip(), na=False)]
        for _, row in match.head(3).iterrows():
            results.append({
                "code": str(row["债券代码"]),
                "name": row["债券简称"],
                "type": "bond",
                "type_label": "可转债",
            })
    except Exception:
        pass

    return results


def lookup_name_by_code(asset_code, asset_type):
    """根据代码和类型查询资产名称"""
    import akshare as ak
    try:
        if asset_type == "stock":
            df = _get_stock_list()
            row = df[df["代码"] == asset_code]
            if not row.empty:
                return row.iloc[0]["名称"]
        elif asset_type == "fund":
            df = _get_etf_list()
            row = df[df["代码"] == asset_code]
            if not row.empty:
                return row.iloc[0]["名称"]
            # 尝试场外基金
            info = ak.fund_open_fund_info_em(symbol=asset_code, indicator="单位净值走势")
            if not info.empty:
                return f"基金{asset_code}"
        elif asset_type == "bond":
            df = _get_bond_list()
            row = df[df["债券代码"] == asset_code]
            if not row.empty:
                return row.iloc[0]["债券简称"]
    except Exception:
        pass
    return asset_code


def get_current_price(asset_code, asset_type):
    """通用接口：获取某资产当前价格"""
    if asset_type == "gold":
        return get_gold_spot_price()
    provider = ASSET_PROVIDERS.get(asset_type)
    if provider:
        return provider(asset_code)
    return None


def save_price(asset_code, asset_type, price, trade_date=None):
    """保存价格到数据库"""
    if trade_date is None:
        trade_date = date.today()
    if price is None:
        return False

    db = get_session()
    try:
        existing = db.query(DailyPrice).filter(
            DailyPrice.asset_code == asset_code,
            DailyPrice.asset_type == asset_type,
            DailyPrice.trade_date == trade_date,
        ).first()

        if existing:
            existing.close_price = price
        else:
            dp = DailyPrice(
                asset_code=asset_code,
                asset_type=asset_type,
                trade_date=trade_date,
                close_price=price,
                source="akshare",
            )
            db.add(dp)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"保存价格失败: {e}")
        return False
    finally:
        db.close()


def update_all_prices(holdings):
    """批量更新所有持仓的最新价格"""
    results = []
    for h in holdings:
        price = get_current_price(h.asset_code, h.asset_type)
        if price is not None and price > 0:
            save_price(h.asset_code, h.asset_type, price)
            results.append((h.asset_code, h.asset_type, price, True))
        else:
            results.append((h.asset_code, h.asset_type, price, False))
    return results

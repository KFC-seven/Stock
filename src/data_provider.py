"""行情数据提供层 - 封装 AKShare"""
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
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
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
        import akshare as ak
        df = ak.bond_zh_cov()
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

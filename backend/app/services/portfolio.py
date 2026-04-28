"""持仓业务逻辑"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import datetime
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.models import Holding, DailyPrice, User
from app.schemas.models import HoldingItem, PortfolioSummary


def get_latest_price(db: Session, asset_code: str, asset_type: str) -> float:
    price = (
        db.query(DailyPrice)
        .filter(DailyPrice.asset_code == asset_code, DailyPrice.asset_type == asset_type)
        .order_by(DailyPrice.trade_date.desc())
        .first()
    )
    return price.close_price if price else 0


def calc_portfolio(holdings: list) -> PortfolioSummary:
    items = []
    total_cost = total_value = 0
    for h in holdings:
        current_price = h.cost_price  # fallback; will be updated by market service
        value = h.quantity * current_price
        cost = h.quantity * h.cost_price
        profit = value - cost
        profit_pct = (profit / cost * 100) if cost > 0 else 0
        total_cost += cost
        total_value += value
        items.append(HoldingItem(
            id=h.id, user_id=h.user_id,
            asset_type=h.asset_type, asset_code=h.asset_code,
            asset_name=h.asset_name, quantity=h.quantity,
            cost_price=h.cost_price, current_price=current_price,
            cost=cost, value=value, profit=profit, profit_pct=profit_pct,
            buy_date=h.buy_date, notes=h.notes or "",
        ))
    total_profit = total_value - total_cost
    total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
    return PortfolioSummary(
        items=items, total_cost=total_cost, total_value=total_value,
        total_profit=total_profit, total_profit_pct=total_profit_pct,
    )


def get_user_portfolio(db: Session, user_id: int) -> PortfolioSummary:
    holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
    result = calc_portfolio(holdings)
    # 填充最新价格
    for item in result.items:
        price = get_latest_price(db, item.asset_code, item.asset_type)
        if price:
            item.current_price = price
            item.value = item.quantity * price
            item.cost = item.quantity * item.cost_price
            item.profit = item.value - item.cost
            item.profit_pct = (item.profit / item.cost * 100) if item.cost > 0 else 0
    # 重新计算汇总
    total_cost = sum(i.cost for i in result.items)
    total_value = sum(i.value for i in result.items)
    result.total_cost = total_cost
    result.total_value = total_value
    result.total_profit = total_value - total_cost
    result.total_profit_pct = (result.total_profit / total_cost * 100) if total_cost > 0 else 0
    return result


def get_family_portfolio(db: Session) -> list:
    users = db.query(User).all()
    result = []
    for user in users:
        portfolio = get_user_portfolio(db, user.id)
        result.append({
            "user_id": user.id,
            "user_name": user.display_name,
            "portfolio": portfolio.model_dump(),
        })
    return result


def get_asset_distribution(portfolio: PortfolioSummary) -> dict:
    by_type = defaultdict(lambda: {"cost": 0, "value": 0, "profit": 0})
    for item in portfolio.items:
        t = item.asset_type
        by_type[t]["cost"] += item.cost
        by_type[t]["value"] += item.value
        by_type[t]["profit"] += item.profit
    return dict(by_type)

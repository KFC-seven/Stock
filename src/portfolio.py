import datetime
from collections import defaultdict
from sqlalchemy import func
from src.database import get_session, Holding, DailyPrice, Transaction, User
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

# 设置 Plotly 暗色主题
pio.templates["premium_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, -apple-system, sans-serif", size=13, color="#c8ccd8"),
        title=dict(font=dict(size=16, color="#e8ecf4", weight=600)),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="rgba(255,255,255,0.4)", size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zerolinecolor="rgba(255,255,255,0.06)",
            tickfont=dict(color="rgba(255,255,255,0.4)", size=11),
        ),
        legend=dict(font=dict(size=12, color="#c8ccd8")),
        margin=dict(l=40, r=20, t=40, b=40),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="rgba(20,22,30,0.95)",
            font_size=12,
            font_color="#e8ecf4",
            bordercolor="rgba(255,255,255,0.1)",
        ),
    )
)
pio.templates.default = "premium_dark"


def get_user_holdings(user_id):
    """获取用户的所有持仓"""
    db = get_session()
    try:
        holdings = db.query(Holding).filter(Holding.user_id == user_id).all()
        return holdings
    finally:
        db.close()


def get_family_holdings():
    """获取所有用户持仓（家庭版）"""
    db = get_session()
    try:
        # 关联用户表获取显示名称
        results = db.query(Holding, User.display_name).join(
            User, Holding.user_id == User.id
        ).all()
        return results
    finally:
        db.close()


def get_latest_price(asset_code, asset_type):
    """获取某资产的最新价格"""
    db = get_session()
    try:
        price = db.query(DailyPrice).filter(
            DailyPrice.asset_code == asset_code,
            DailyPrice.asset_type == asset_type
        ).order_by(DailyPrice.trade_date.desc()).first()
        return price.close_price if price else None
    finally:
        db.close()


def get_price_trend(asset_code, asset_type, days=90):
    """获取某资产的近期价格走势"""
    db = get_session()
    try:
        since = datetime.date.today() - datetime.timedelta(days=days)
        prices = db.query(DailyPrice).filter(
            DailyPrice.asset_code == asset_code,
            DailyPrice.asset_type == asset_type,
            DailyPrice.trade_date >= since
        ).order_by(DailyPrice.trade_date).all()
        return [(p.trade_date, p.close_price) for p in prices]
    finally:
        db.close()


def calculate_portfolio(holdings):
    """计算持仓市值和盈亏"""
    portfolio = []
    total_cost = 0
    total_value = 0

    for h in holdings:
        latest_price = get_latest_price(h.asset_code, h.asset_type)
        if latest_price is None:
            latest_price = h.cost_price  # 没有行情数据时用成本价

        current_value = h.quantity * latest_price
        cost = h.quantity * h.cost_price
        profit = current_value - cost
        profit_pct = (profit / cost * 100) if cost > 0 else 0

        total_cost += cost
        total_value += current_value

        portfolio.append({
            "id": h.id,
            "asset_type": h.asset_type,
            "asset_code": h.asset_code,
            "asset_name": h.asset_name,
            "quantity": h.quantity,
            "cost_price": h.cost_price,
            "current_price": latest_price,
            "cost": cost,
            "value": current_value,
            "profit": profit,
            "profit_pct": profit_pct,
            "buy_date": h.buy_date,
            "notes": h.notes,
        })

    total_profit = total_value - total_cost
    total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

    return {
        "items": portfolio,
        "total_cost": total_cost,
        "total_value": total_value,
        "total_profit": total_profit,
        "total_profit_pct": total_profit_pct,
    }


def get_asset_distribution(portfolio_result):
    """按资产类型分类汇总"""
    by_type = defaultdict(lambda: {"cost": 0, "value": 0, "profit": 0})
    for item in portfolio_result["items"]:
        t = item["asset_type"]
        by_type[t]["cost"] += item["cost"]
        by_type[t]["value"] += item["value"]
        by_type[t]["profit"] += item["profit"]

    return dict(by_type)


def get_family_summary():
    """家庭总持仓汇总"""
    db = get_session()
    try:
        # 获取所有用户
        users = db.query(User).all()
        family_data = []
        for user in users:
            holdings = db.query(Holding).filter(Holding.user_id == user.id).all()
            portfolio = calculate_portfolio(holdings)
            family_data.append({
                "user_id": user.id,
                "user_name": user.display_name,
                "portfolio": portfolio,
            })
        return family_data
    finally:
        db.close()


def add_holding(user_id, asset_type, asset_code, asset_name,
                quantity, cost_price, buy_date=None, notes=""):
    """添加持仓"""
    db = get_session()
    try:
        holding = Holding(
            user_id=user_id,
            asset_type=asset_type,
            asset_code=asset_code,
            asset_name=asset_name,
            quantity=quantity,
            cost_price=cost_price,
            buy_date=buy_date,
            notes=notes,
        )
        db.add(holding)
        db.commit()
        return True, "添加成功"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def update_holding(holding_id, **kwargs):
    """更新持仓"""
    db = get_session()
    try:
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if not holding:
            return False, "持仓不存在"
        for k, v in kwargs.items():
            if hasattr(holding, k) and v is not None:
                setattr(holding, k, v)
        holding.updated_at = datetime.datetime.now()
        db.commit()
        return True, "更新成功"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def delete_holding(holding_id):
    """删除持仓"""
    db = get_session()
    try:
        holding = db.query(Holding).filter(Holding.id == holding_id).first()
        if not holding:
            return False, "持仓不存在"
        db.delete(holding)
        db.commit()
        return True, "删除成功"
    except Exception as e:
        db.rollback()
        return False, str(e)
    finally:
        db.close()


def plot_portfolio_pie(portfolio_result):
    """资产分布饼图"""
    dist = get_asset_distribution(portfolio_result)
    type_names = {"stock": "股票", "fund": "基金", "bond": "债券", "gold": "黄金"}
    labels = [type_names.get(k, k) for k in dist.keys()]
    values = [v["value"] for v in dist.values()]

    fig = px.pie(
        values=values, names=labels,
        title="资产分布",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def plot_profit_bar(portfolio_result):
    """各持仓盈亏条形图"""
    items = sorted(portfolio_result["items"], key=lambda x: x["profit"])
    names = [f"{i['asset_name']}({i['asset_code']})" for i in items]
    profits = [i["profit"] for i in items]
    colors = ["#22c55e" if p < 0 else "#ef4444" for p in profits]  # 中国红涨绿跌

    fig = go.Figure(data=[
        go.Bar(x=names, y=profits, marker_color=colors)
    ])
    fig.update_layout(
        title="持仓盈亏",
        xaxis_tickangle=-45,
        height=400,
    )
    return fig


def plot_trend_chart(asset_code, asset_name, asset_type, days=90):
    """价格走势图"""
    trend = get_price_trend(asset_code, asset_type, days)
    if not trend:
        return None

    df = pd.DataFrame(trend, columns=["date", "price"])
    fig = px.line(df, x="date", y="price", title=f"{asset_name}({asset_code}) 走势")
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig



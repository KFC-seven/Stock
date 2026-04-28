"""持仓 CRUD API"""
import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.models.models import Holding, User
from app.schemas.models import HoldingCreate, HoldingUpdate, HoldingItem
from app.services.auth import get_current_user
from app.services.market import get_current_price, save_price

router = APIRouter(prefix="/api/holdings", tags=["持仓"])


@router.get("", response_model=List[HoldingItem])
def list_holdings(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    holdings = db.query(Holding).filter(Holding.user_id == user.id).all()
    items = []
    for h in holdings:
        price = get_current_price(h.asset_code, h.asset_type) or h.cost_price
        value = h.quantity * price
        cost = h.quantity * h.cost_price
        profit = value - cost
        items.append(HoldingItem(
            id=h.id, user_id=h.user_id,
            asset_type=h.asset_type, asset_code=h.asset_code,
            asset_name=h.asset_name, quantity=h.quantity,
            cost_price=h.cost_price, current_price=price,
            cost=cost, value=value, profit=profit,
            profit_pct=(profit / cost * 100) if cost > 0 else 0,
            buy_date=h.buy_date, notes=h.notes or "",
        ))
    return items


@router.post("", response_model=HoldingItem)
def create_holding(req: HoldingCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = Holding(
        user_id=user.id,
        asset_type=req.asset_type,
        asset_code=req.asset_code,
        asset_name=req.asset_name or req.asset_code,
        quantity=req.quantity,
        cost_price=req.cost_price,
        buy_date=req.buy_date,
        notes=req.notes,
    )
    db.add(h)
    db.commit()
    db.refresh(h)

    # 异步拉取最新价格
    price = get_current_price(h.asset_code, h.asset_type)
    if price and price > 0:
        save_price(db, h.asset_code, h.asset_type, price)
        current_price = price
    else:
        current_price = h.cost_price

    value = h.quantity * current_price
    cost = h.quantity * h.cost_price
    profit = value - cost
    return HoldingItem(
        id=h.id, user_id=h.user_id,
        asset_type=h.asset_type, asset_code=h.asset_code,
        asset_name=h.asset_name, quantity=h.quantity,
        cost_price=h.cost_price, current_price=current_price,
        cost=cost, value=value, profit=profit,
        profit_pct=(profit / cost * 100) if cost > 0 else 0,
        buy_date=h.buy_date, notes=h.notes or "",
    )


@router.put("/{holding_id}", response_model=HoldingItem)
def update_holding(holding_id: int, req: HoldingUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == user.id).first()
    if not h:
        raise HTTPException(status_code=404, detail="持仓不存在")
    for k, v in req.model_dump(exclude_none=True).items():
        if hasattr(h, k):
            setattr(h, k, v)
    h.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(h)

    price = get_current_price(h.asset_code, h.asset_type) or h.cost_price
    value = h.quantity * price
    cost = h.quantity * h.cost_price
    profit = value - cost
    return HoldingItem(
        id=h.id, user_id=h.user_id,
        asset_type=h.asset_type, asset_code=h.asset_code,
        asset_name=h.asset_name, quantity=h.quantity,
        cost_price=h.cost_price, current_price=price,
        cost=cost, value=value, profit=profit,
        profit_pct=(profit / cost * 100) if cost > 0 else 0,
        buy_date=h.buy_date, notes=h.notes or "",
    )


@router.delete("/{holding_id}")
def delete_holding(holding_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    h = db.query(Holding).filter(Holding.id == holding_id, Holding.user_id == user.id).first()
    if not h:
        raise HTTPException(status_code=404, detail="持仓不存在")
    db.delete(h)
    db.commit()
    return {"message": "删除成功"}

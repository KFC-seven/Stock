"""行情查询 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import User
from app.services.auth import get_current_user
from app.services.market import search_asset, get_current_price

router = APIRouter(prefix="/api/market", tags=["行情"])


@router.get("/search")
def search(q: str, user: User = Depends(get_current_user)):
    return search_asset(q)


@router.get("/price")
def price(asset_code: str, asset_type: str, user: User = Depends(get_current_user)):
    p = get_current_price(asset_code, asset_type)
    return {"asset_code": asset_code, "asset_type": asset_type, "price": p}

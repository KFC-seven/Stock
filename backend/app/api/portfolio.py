"""看板 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.models import User
from app.services.auth import get_current_user
from app.services.portfolio import get_user_portfolio, get_family_portfolio, get_asset_distribution
from app.services.market import update_all_prices

router = APIRouter(prefix="/api/portfolio", tags=["看板"])


@router.get("/summary")
def portfolio_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio = get_user_portfolio(db, user.id)
    dist = get_asset_distribution(portfolio)
    return {
        "portfolio": portfolio.model_dump(),
        "distribution": {k: {"value": v["value"], "cost": v["cost"], "profit": v["profit"]} for k, v in dist.items()},
    }


@router.get("/family")
def family_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_family_portfolio(db)


@router.post("/refresh-prices")
def refresh_prices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = update_all_prices(db)
    return {"message": "更新完成", "results": results}

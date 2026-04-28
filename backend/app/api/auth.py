"""认证 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.database import get_db
from app.schemas.models import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth import login, register, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=TokenResponse)
def login_route(req: LoginRequest, db: Session = Depends(get_db)):
    return login(req.username, req.password, db)


@router.post("/register", response_model=TokenResponse)
def register_route(req: RegisterRequest, db: Session = Depends(get_db)):
    return register(req.username, req.password, req.display_name, db)


@router.get("/me")
def me_route(user=Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "display_name": user.display_name}

"""FastAPI 主入口"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import CORS_ORIGINS
from app.models.database import Base, engine
from app.api import auth, holdings, portfolio, market

app = FastAPI(title="投资管家 API", version="2.0.0")


@app.on_event("startup")
def init_db():
    """首次启动时初始化数据库表"""
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(holdings.router)
app.include_router(portfolio.router)
app.include_router(market.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "2.0.0"}

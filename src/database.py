"""数据库模型和连接管理"""
import os
from datetime import datetime, date
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Date, DateTime,
    Boolean, Text, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
import enum

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "investments.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class AssetType(str, enum.Enum):
    STOCK = "stock"
    FUND = "fund"
    BOND = "bond"
    GOLD = "gold"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    display_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    news_keywords = relationship("NewsKeyword", back_populates="user", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)  # stock/fund/bond/gold
    asset_code = Column(String(20), nullable=False)
    asset_name = Column(String(100), nullable=False, default="")
    quantity = Column(Float, nullable=False, default=0)
    cost_price = Column(Float, nullable=False, default=0)
    buy_date = Column(Date, nullable=True)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", back_populates="holdings")


class DailyPrice(Base):
    __tablename__ = "daily_prices"

    id = Column(Integer, primary_key=True)
    asset_code = Column(String(20), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)
    trade_date = Column(Date, nullable=False)
    close_price = Column(Float, nullable=False)
    source = Column(String(50), default="akshare")

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    holding_id = Column(Integer, ForeignKey("holdings.id"), nullable=True)
    trans_type = Column(String(10), nullable=False)  # buy / sell
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    trans_date = Column(Date, nullable=False, default=date.today)
    commission = Column(Float, default=0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="transactions")


class NewsKeyword(Base):
    __tablename__ = "news_keywords"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyword = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="news_keywords")


class NewsCache(Base):
    __tablename__ = "news_cache"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, default="")
    url = Column(String(1000), default="")
    source = Column(String(100), default="")
    pushed_at = Column(Date, nullable=False, default=date.today)


def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(engine)


def get_session():
    """获取数据库会话"""
    return SessionLocal()

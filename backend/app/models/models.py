"""SQLAlchemy 模型"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.models.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    display_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    holdings = relationship("Holding", back_populates="user", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)
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

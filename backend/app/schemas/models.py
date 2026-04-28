"""Pydantic 请求/响应模型"""
from datetime import date
from pydantic import BaseModel, Field
from typing import Optional, List


# === Auth ===
class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    display_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    display_name: str


# === Holdings ===
class HoldingCreate(BaseModel):
    asset_type: str = Field(..., pattern="^(stock|fund|bond|gold)$")
    asset_code: str
    asset_name: str = ""
    quantity: float = Field(gt=0)
    cost_price: float = Field(gt=0)
    buy_date: Optional[date] = None
    notes: str = ""


class HoldingUpdate(BaseModel):
    asset_type: Optional[str] = None
    asset_code: Optional[str] = None
    asset_name: Optional[str] = None
    quantity: Optional[float] = None
    cost_price: Optional[float] = None
    buy_date: Optional[date] = None
    notes: Optional[str] = None


class HoldingItem(BaseModel):
    id: int
    user_id: int
    asset_type: str
    asset_code: str
    asset_name: str
    quantity: float
    cost_price: float
    current_price: float = 0
    cost: float = 0
    value: float = 0
    profit: float = 0
    profit_pct: float = 0
    buy_date: Optional[date] = None
    notes: str = ""


class PortfolioSummary(BaseModel):
    items: List[HoldingItem]
    total_cost: float = 0
    total_value: float = 0
    total_profit: float = 0
    total_profit_pct: float = 0


class FamilyMember(BaseModel):
    user_id: int
    user_name: str
    portfolio: PortfolioSummary


class SearchResult(BaseModel):
    code: str
    name: str
    type: str
    type_label: str


# === OCR ===
class OCRResult(BaseModel):
    fund_name: str
    fund_code: str = ""
    quantity: float = 0
    cost_price: float = 0
    current_price: float = 0
    current_value: float = 0
    total_cost: float = 0
    profit_rate: float = 0
    profit_amount: float = 0


# === Market ===
class PriceUpdateResult(BaseModel):
    asset_code: str
    asset_type: str
    price: Optional[float] = None
    success: bool = False

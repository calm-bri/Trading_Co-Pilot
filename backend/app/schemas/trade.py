from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeBase(BaseModel):
    symbol: str
    trade_type: str  # 'buy' or 'sell'
    quantity: float
    price: float
    notes: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class Trade(TradeBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

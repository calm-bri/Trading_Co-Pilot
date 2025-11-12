from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertBase(BaseModel):
    symbol: str
    alert_type: str  # 'price_above', 'price_below', 'volume_spike', 'sentiment_change'
    threshold_value: Optional[float] = None
    condition: Optional[str] = None  # 'above', 'below', 'spike'
    message: Optional[str] = None

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    triggered_at: Optional[datetime] = None

    class Config:
        from_attributes = True

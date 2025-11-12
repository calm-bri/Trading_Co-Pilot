from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    alert_type = Column(String(20), nullable=False)  # 'price_above', 'price_below', 'volume_spike', 'sentiment_change'
    threshold_value = Column(Float, nullable=True)  # For price/volume alerts
    condition = Column(String(20), nullable=True)  # 'above', 'below', 'spike'
    is_active = Column(Boolean, default=True)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    triggered_at = Column(DateTime(timezone=True), nullable=True)

    # Relationship
    user = relationship("User", back_populates="alerts")

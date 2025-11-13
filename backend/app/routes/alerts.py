from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Alert
from app.schemas.alert import Alert as AlertSchema, AlertCreate
from app.services.data_fetcher import DataFetcher
from app.services.sentiment_analysis import SentimentAnalysis
from app.services.alert_checker import check_and_trigger_alerts

router = APIRouter()

@router.post("/", response_model=AlertSchema)
async def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new alert for the current user."""
    db_alert = Alert(
        user_id=current_user.id,
        symbol=alert.symbol.upper(),
        alert_type=alert.alert_type,
        threshold_value=alert.threshold_value,
        condition=alert.condition,
        message=alert.message
    )
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

@router.get("/active", response_model=List[AlertSchema])
async def get_active_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all active alerts for the current user."""
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_active == True
    ).all()
    return alerts

@router.get("/", response_model=List[AlertSchema])
async def get_all_alerts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all alerts for the current user."""
    alerts = db.query(Alert).filter(Alert.user_id == current_user.id).offset(skip).limit(limit).all()
    return alerts

@router.put("/{alert_id}", response_model=AlertSchema)
async def update_alert(
    alert_id: int,
    alert_update: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    for field, value in alert_update.dict().items():
        setattr(alert, field, value)

    db.commit()
    db.refresh(alert)
    return alert

@router.delete("/{alert_id}")
async def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alert)
    db.commit()
    return {"message": "Alert deleted successfully"}

@router.post("/{alert_id}/deactivate")
async def deactivate_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_active = False
    db.commit()
    db.refresh(alert)
    return {"message": "Alert deactivated successfully"}

@router.post("/check-triggers")
async def check_alert_triggers(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually check and trigger alerts (can be called by a scheduler)."""
    # Get all active alerts for the user
    alerts = db.query(Alert).filter(
        Alert.user_id == current_user.id,
        Alert.is_active == True
    ).all()

    triggered_alerts = []

    for alert in alerts:
        try:
            is_triggered = await check_single_alert(alert)
            if is_triggered:
                alert.triggered_at = func.now()
                alert.is_active = False  # Deactivate after triggering
                triggered_alerts.append(alert)
        except Exception as e:
            # Log error but continue with other alerts
            continue

    if triggered_alerts:
        db.commit()

    return {
        "message": f"Checked {len(alerts)} alerts, {len(triggered_alerts)} triggered",
        "triggered_alerts": [alert.id for alert in triggered_alerts]
    }

async def check_single_alert(alert: Alert) -> bool:
    """Check if a single alert should be triggered."""
    data_fetcher = DataFetcher()

    if alert.alert_type in ['price_above', 'price_below']:
        # Get current price
        try:
            current_price = await data_fetcher.get_current_price(alert.symbol)
            if current_price is None:
                return False

            if alert.alert_type == 'price_above' and current_price > alert.threshold_value:
                return True
            elif alert.alert_type == 'price_below' and current_price < alert.threshold_value:
                return True
        except Exception:
            return False

    elif alert.alert_type == 'volume_spike':
        # Check for volume spike (simplified)
        try:
            volume_data = await data_fetcher.get_volume_data(alert.symbol)
            if volume_data and len(volume_data) >= 2:
                current_volume = volume_data[-1]
                avg_volume = sum(volume_data[-10:]) / len(volume_data[-10:]) if len(volume_data) >= 10 else sum(volume_data[:-1]) / len(volume_data[:-1])
                if current_volume > avg_volume * 2:  # 2x average volume
                    return True
        except Exception:
            return False

    elif alert.alert_type == 'sentiment_change':
        # Check for sentiment change
        try:
            sentiment_analyzer = SentimentAnalysis()
            sentiment_data = await data_fetcher.get_twitter_sentiment(alert.symbol)
            if sentiment_data:
                sentiment = sentiment_analyzer.analyze_text(sentiment_data)
                sentiment_score = sentiment.get('sentiment_score', 0)
                # Trigger if sentiment becomes very negative
                if sentiment_score < -0.5:
                    return True
        except Exception:
            return False

    return False

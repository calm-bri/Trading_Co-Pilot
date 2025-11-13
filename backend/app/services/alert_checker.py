from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Alert, User


def check_and_trigger_alerts(
    db: Session,
    symbol: str,
    current_price: float,
    current_volume: float = None,
    sentiment_score: float = None,
    user: User = None
):
    """
    Checks all active alerts for the user and triggers them
    when conditions are met. Supports:
      - price_above
      - price_below
      - volume_spike
      - sentiment_change
    """
    
    # Fetch active alerts for this user + symbol
    alerts = (
        db.query(Alert)
        .filter(
            Alert.user_id == user.id,
            Alert.symbol == symbol,
            Alert.is_active == True
        )
        .all()
    )

    triggered_alerts = []

    for alert in alerts:
        triggered = False

        # PRICE ABOVE
        if alert.alert_type == "price_above" and alert.threshold_value is not None:
            if current_price >= alert.threshold_value:
                triggered = True
                alert.message = f"{symbol} price is above {alert.threshold_value}. Current: {current_price}"

        # PRICE BELOW
        elif alert.alert_type == "price_below" and alert.threshold_value is not None:
            if current_price <= alert.threshold_value:
                triggered = True
                alert.message = f"{symbol} price is below {alert.threshold_value}. Current: {current_price}"

        # VOLUME SPIKE (compared to threshold_value)
        elif alert.alert_type == "volume_spike" and current_volume is not None:
            if current_volume >= alert.threshold_value:
                triggered = True
                alert.message = (
                    f"{symbol} volume spike detected. "
                    f"Volume: {current_volume}, Threshold: {alert.threshold_value}"
                )

        # SENTIMENT CHANGE
        elif alert.alert_type == "sentiment_change" and sentiment_score is not None:
            if abs(sentiment_score) >= alert.threshold_value:
                triggered = True
                alert.message = (
                    f"{symbol} sentiment change detected. "
                    f"Sentiment Score: {sentiment_score}, Threshold: {alert.threshold_value}"
                )

        # If triggered, update alert status
        if triggered:
            alert.is_active = False
            alert.triggered_at = datetime.utcnow()
            triggered_alerts.append({
                "alert_id": alert.id,
                "symbol": symbol,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "triggered_at": alert.triggered_at
            })

    if triggered_alerts:
        db.commit()

    return triggered_alerts

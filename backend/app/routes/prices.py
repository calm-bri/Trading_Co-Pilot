from fastapi import APIRouter, WebSocket, WebSocketDisconnect , Depends
from app.services.price_stream import stream_prices
from app.services.alert_checker import check_and_trigger_alerts
from app.core.database import get_db
import asyncio

router = APIRouter()

@router.websocket("/ws/prices")
async def websocket_prices(websocket: WebSocket, db=Depends(get_db)):
    await websocket.accept()

    async def send_price_to_client(data):
        for item in data:
            # broadcast live price ticks
            await websocket.send_json(item)

            # trigger alerts (IMPORTANT)
            symbol = item["s"]
            price = item["p"]

            triggered = await check_and_trigger_alerts(symbol, price, db)

            # send triggered alerts to user in real-time
            for alert in triggered:
                await websocket.send_json({
                    "type": "alert_triggered",
                    "id": alert.id,
                    "symbol": alert.symbol,
                    "message": alert.message,
                    "trigger_price": price
                })

    symbols = ["AAPL", "MSFT", "TSLA"]  # temp
    await stream_prices(symbols, send_price_to_client)
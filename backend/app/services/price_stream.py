# backend/app/services/price_stream.py
import asyncio
import websockets
import json
import os

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

async def stream_prices(symbols, callback):
    url = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"

    async with websockets.connect(url) as ws:
        # Subscribe to each symbol
        for symbol in symbols:
            await ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                if "data" in data:
                    await callback(data["data"])
            except Exception as e:
                print("Error:", e)
                await asyncio.sleep(3)

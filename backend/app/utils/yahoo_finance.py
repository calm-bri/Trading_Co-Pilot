import yfinance as yf
import pandas as pd
from typing import Dict, Any

async def get_stock_info(symbol: str) -> Dict[str, Any]:
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "symbol": symbol,
        "name": info.get("longName", ""),
        "sector": info.get("sector", ""),
        "industry": info.get("industry", ""),
        "market_cap": info.get("marketCap", 0),
        "current_price": info.get("currentPrice", 0),
        "previous_close": info.get("previousClose", 0),
        "open": info.get("open", 0),
        "day_high": info.get("dayHigh", 0),
        "day_low": info.get("dayLow", 0),
        "volume": info.get("volume", 0),
    }

async def get_historical_data(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period, interval=interval)
    return data

async def get_options_data(symbol: str) -> Dict[str, Any]:
    ticker = yf.Ticker(symbol)
    options = ticker.options
    return {"expiration_dates": options}

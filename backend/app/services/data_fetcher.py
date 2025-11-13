import asyncio
from typing import Dict, Any, List
import httpx
import time
import pandas as pd
from app.core.config import settings
from app.utils.twitter_api import TwitterAPI
from app.utils.rss_parser import get_financial_news


class DataFetcher:
    FINNHUB_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.twitter_api = TwitterAPI()

    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Only market profile info + sentiment.
        No OHLC here.
        """
        twitter_task = self.twitter_api.get_sentiment_data(symbol)
        news_task = get_financial_news()

        twitter_sentiment, news = await asyncio.gather(
            twitter_task,
            news_task
        )

        return {
            "symbol": symbol,
            "twitter_sentiment": twitter_sentiment,
            "news": news
        }

    async def get_ohlcv_series(self, symbol: str, resolution="D", days=180):
        """
        Main Finnhub OHLC fetcher.
        resolution: 1,5,15,30,60,D,W,M
        """
        try:
            end = int(time.time())
            start = end - (days * 24 * 60 * 60)

            params = {
                "symbol": symbol.upper(),
                "resolution": resolution,
                "from": start,
                "to": end,
                "token": settings.FINNHUB_API_KEY
            }

            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.FINNHUB_URL}/stock/candle", params=params)

            data = res.json()

            # Finnhub returns s="no_data" if no OHLC exists
            if data.get("s") != "ok":
                return pd.DataFrame()

            df = pd.DataFrame({
                "date": pd.to_datetime(data["t"], unit="s").astype(str),
                "open": data["o"],
                "high": data["h"],
                "low": data["l"],
                "close": data["c"],
                "volume": data["v"],
            })

            return df

        except Exception as e:
            print("❌ Finnhub OHLC Error:", e)
            return pd.DataFrame()

    # Legacy fallback — technical analysis & series expect this
    async def get_historical_data(self, symbol: str, period="6mo"):
        return await self.get_ohlcv_series(symbol)


data_fetcher = DataFetcher()

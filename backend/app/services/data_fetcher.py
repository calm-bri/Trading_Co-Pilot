import asyncio
from typing import Dict, Any, List
import pandas as pd
import yfinance as yf
import httpx
from app.core.config import settings
from app.utils.twitter_api import TwitterAPI
from app.utils.rss_parser import get_financial_news


class DataFetcher:
    FINNHUB_URL = "https://finnhub.io/api/v1"

    def __init__(self):
        self.twitter_api = TwitterAPI()

    # ------------------------------------------------------------
    # REAL-TIME PRICE (Finnhub)
    # ------------------------------------------------------------
    async def get_realtime_price(self, symbol: str) -> Dict[str, Any]:
        """
        Free tier API: works only for quote endpoint.
        """
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(
                    f"{self.FINNHUB_URL}/quote",
                    params={"symbol": symbol.upper(), "token": settings.FINNHUB_API_KEY}
                )
            return res.json()
        except Exception as e:
            print("❌ Finnhub realtime error:", e)
            return {}

    # ------------------------------------------------------------
    # HISTORICAL CANDLES (Yahoo Finance)
    # ------------------------------------------------------------
    async def get_ohlcv_series(self, symbol: str, resolution="1d", days=180):
        """
        Main OHLC fetcher for charts + technical analysis.
        Works fully free using Yahoo Finance.
        """

        try:
            # Map resolution
            interval_map = {
                "1": "1m",
                "5": "5m",
                "15": "15m",
                "30": "30m",
                "60": "60m",
                "D": "1d",
                "W": "1wk",
                "M": "1mo"
            }

            yf_interval = interval_map.get(resolution, "1d")

            df = yf.download(
                symbol,
                period=f"{days}d",
                interval=yf_interval,
                progress=False
            )

            if df.empty:
                print(f"⚠ Yahoo returned empty OHLC for {symbol}")
                return pd.DataFrame()

            df = df.reset_index()

            # Standardize column names
            df.rename(columns={
                "Date": "date",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume",
            }, inplace=True)

            df["date"] = df["date"].astype(str)
            return df

        except Exception as e:
            print("❌ Yahoo OHLCV error:", e)
            return pd.DataFrame()

    # ------------------------------------------------------------
    # FOR TECHNICAL ANALYSIS COMPATIBILITY
    # ------------------------------------------------------------
    async def get_historical_data(self, symbol: str, period="6mo"):
        """
        Backwards compatibility for your technical indicators.
        """
        return await self.get_ohlcv_series(symbol, resolution="D", days=180)

    # ------------------------------------------------------------
    # SENTIMENT + NEWS
    # ------------------------------------------------------------
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
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


data_fetcher = DataFetcher()

import aiohttp
from app.core.config import settings

async def get_stock_data(symbol: str, api_key: str = settings.alpha_vantage_api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("Time Series (Daily)", {})
            else:
                raise Exception(f"Failed to fetch data for {symbol}")

async def get_intraday_data(symbol: str, interval: str = "5min", api_key: str = settings.alpha_vantage_api_key):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data.get(f"Time Series ({interval})", {})
            else:
                raise Exception(f"Failed to fetch intraday data for {symbol}")

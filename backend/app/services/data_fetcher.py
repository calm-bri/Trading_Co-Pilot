from typing import Dict, Any, List
import asyncio
from app.utils.alpha_vantage import get_stock_data, get_intraday_data
from app.utils.yahoo_finance import get_stock_info, get_historical_data
from app.utils.twitter_api import TwitterAPI
from app.utils.rss_parser import get_financial_news

class DataFetcher:
    def __init__(self):
        self.twitter_api = TwitterAPI()

    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        # Fetch data from multiple sources concurrently
        yahoo_task = get_stock_info(symbol)
        alpha_task = get_stock_data(symbol)
        twitter_task = self.twitter_api.get_sentiment_data(symbol)

        yahoo_info, alpha_data, twitter_sentiment = await asyncio.gather(
            yahoo_task, alpha_task, twitter_task
        )

        return {
            "symbol": symbol,
            "yahoo_info": yahoo_info,
            "alpha_vantage_data": alpha_data,
            "twitter_sentiment": twitter_sentiment,
        }

    async def get_market_news(self) -> List[Dict[str, Any]]:
        return await get_financial_news()

    async def get_historical_prices(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        data = await get_historical_data(symbol, period)
        return {
            "symbol": symbol,
            "data": data.to_dict('records') if not data.empty else [],
            "period": period,
        }

data_fetcher = DataFetcher()

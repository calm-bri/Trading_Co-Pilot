import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import pandas as pd
import yfinance as yf
import httpx
from app.core.config import settings
from app.utils.twitter_api import TwitterAPI
from app.utils.rss_parser import get_financial_news
import structlog

logger = structlog.get_logger()


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
            logger.error("❌ Finnhub realtime error:", error=str(e))
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
                logger.warning(f"⚠ Yahoo returned empty OHLC for {symbol}")
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
            logger.error("❌ Yahoo OHLCV error:", error=str(e))
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
    # SENTIMENT + NEWS (Existing Methods - Kept for Compatibility)
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

    async def get_rss_sentiment(self) -> str:
        """
        LEGACY METHOD - Kept for backward compatibility
        Get combined text from RSS feeds for sentiment analysis.
        
        ⚠️ For new code, use get_rss_articles() instead for better accuracy
        """
        try:
            articles = await get_financial_news()
            if not articles:
                return "No RSS data available"

            # Combine article titles and summaries for sentiment analysis
            combined_text = ""
            for article in articles[:10]:  # Limit to 10 most recent
                title = article.get('title', '')
                summary = article.get('summary', '')
                combined_text += f"{title}. {summary} "

            return combined_text.strip() if combined_text.strip() else "No RSS data available"
        except Exception as e:
            logger.error(f"Error fetching RSS sentiment: {e}")
            return "No RSS data available"

    async def get_news_data(self, symbol: str) -> str:
        """
        LEGACY METHOD - Kept for backward compatibility
        Get news data for a specific symbol.
        
        ⚠️ For new code, use get_symbol_articles() instead
        """
        try:
            # For now, return general market news since we don't have symbol-specific RSS
            return await self.get_rss_sentiment()
        except Exception as e:
            logger.error(f"Error fetching news data for {symbol}: {e}")
            return ""

    async def get_twitter_sentiment(self, query: str) -> str:
        """Get Twitter sentiment data (placeholder implementation)."""
        try:
            sentiment_data = await self.twitter_api.get_sentiment_data(query)
            if sentiment_data and 'recent_tweets' in sentiment_data:
                # Combine tweet texts for sentiment analysis
                combined_tweets = " ".join([tweet.get('text', '') for tweet in sentiment_data['recent_tweets'][:10]])
                return combined_tweets if combined_tweets else ""
            return ""
        except Exception as e:
            logger.error(f"Error fetching Twitter sentiment: {e}")
            return ""

    # ------------------------------------------------------------
    # NEW METHODS - Article-Level Parsing for Improved Sentiment
    # ------------------------------------------------------------
    
    async def get_rss_articles(
        self,
        hours_back: int = 24,
        max_articles: int = 50
    ) -> List[Dict]:
        """
        Get structured RSS articles for improved sentiment analysis.
        
        Returns:
            List of article dicts with structure:
            {
                'title': str,
                'description': str,
                'link': str,
                'published': datetime,
                'source': str
            }
        """
        try:
            # Get raw articles from your RSS parser
            raw_articles = await get_financial_news()
            
            if not raw_articles:
                logger.warning("No RSS articles available")
                return []
            
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            structured_articles = []
            
            for article in raw_articles[:max_articles]:
                # Parse the article into structured format
                parsed_article = self._parse_rss_article(article)
                
                # Filter by time if published date is available
                if parsed_article['published'] < cutoff_time:
                    continue
                
                structured_articles.append(parsed_article)
            
            logger.info(f"📰 Fetched {len(structured_articles)} RSS articles")
            return structured_articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS articles: {e}")
            return []
    
    async def get_symbol_articles(
        self,
        symbol: str,
        hours_back: int = 24,
        max_articles: int = 30
    ) -> List[Dict]:
        """
        Get articles filtered for a specific stock symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')
            hours_back: How many hours back to fetch
            max_articles: Maximum articles to return
        
        Returns:
            List of articles related to the symbol
        """
        try:
            # Get all articles
            all_articles = await self.get_rss_articles(
                hours_back=hours_back,
                max_articles=max_articles * 3  # Fetch more since we'll filter
            )
            
            if not all_articles:
                return []
            
            # Filter for symbol mentions
            symbol_upper = symbol.upper()
            symbol_articles = []
            
            for article in all_articles:
                title = article['title'].upper()
                description = article['description'].upper()
                
                # Check if symbol is mentioned
                if symbol_upper in title or symbol_upper in description:
                    symbol_articles.append(article)
                
                # Stop if we have enough
                if len(symbol_articles) >= max_articles:
                    break
            
            logger.info(f"🔍 Found {len(symbol_articles)} articles for {symbol}")
            return symbol_articles
            
        except Exception as e:
            logger.error(f"Error fetching symbol articles for {symbol}: {e}")
            return []
    
    async def get_historical_articles(
        self,
        symbol: Optional[str] = None,
        days: int = 7
    ) -> List[Dict]:
        """
        Get historical articles from the past N days.
        
        Note: This currently fetches recent articles only.
        For true historical data, you'd need to store articles in a database.
        
        Args:
            symbol: Optional stock symbol to filter for
            days: Number of days back to fetch
        
        Returns:
            List of historical articles
        """
        try:
            # For now, just fetch articles from the past N days
            hours_back = days * 24
            
            if symbol:
                articles = await self.get_symbol_articles(
                    symbol=symbol,
                    hours_back=hours_back,
                    max_articles=100
                )
            else:
                articles = await self.get_rss_articles(
                    hours_back=hours_back,
                    max_articles=100
                )
            
            logger.info(f"📅 Fetched {len(articles)} historical articles ({days} days)")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching historical articles: {e}")
            return []
    
    def _parse_rss_article(self, raw_article: Dict) -> Dict:
        """
        Parse raw RSS article into standardized format.
        Handles different RSS feed structures.
        """
        import email.utils
        
        # Extract title
        title = raw_article.get('title', raw_article.get('headline', ''))
        
        # Extract description/summary
        description = (
            raw_article.get('summary', '') or
            raw_article.get('description', '') or
            raw_article.get('content', '') or
            ''
        )
        
        # Extract link
        link = raw_article.get('link', raw_article.get('url', ''))
        
        # Extract source
        source = raw_article.get('source', raw_article.get('feed', 'Unknown'))
        
        # Parse published date
        published = self._parse_article_date(raw_article)
        
        return {
            'title': title,
            'description': description,
            'link': link,
            'published': published,
            'source': source
        }
    
    def _parse_article_date(self, article: Dict) -> datetime:
        """Parse article date from various possible fields"""
        import email.utils
        
        # Try different date fields
        date_str = (
            article.get('published') or
            article.get('pubDate') or
            article.get('updated') or
            article.get('date') or
            None
        )
        
        if not date_str:
            return datetime.now(timezone.utc)
        
        try:
            # If it's already a datetime object
            if isinstance(date_str, datetime):
                if date_str.tzinfo is None:
                    return date_str.replace(tzinfo=timezone.utc)
                return date_str
            
            # Parse RFC 2822 format (common in RSS)
            parsed = email.utils.parsedate_to_datetime(str(date_str))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
            
        except Exception:
            # Fallback to current time
            return datetime.now(timezone.utc)


# Singleton instance
data_fetcher = DataFetcher()
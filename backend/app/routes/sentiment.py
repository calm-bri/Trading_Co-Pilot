from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.sentiment_analysis import SentimentAnalysis
from app.services.data_fetcher import DataFetcher
from app.core.config import settings

router = APIRouter()

@router.get("/latest")
async def get_latest_sentiment(
    symbol: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get latest sentiment analysis for a symbol or general market."""
    try:
        sentiment_analyzer = SentimentAnalysis()
        data_fetcher = DataFetcher()

        sentiment_data = []

        if symbol:
            # Get sentiment for specific symbol
            try:
                # Fetch recent news/articles for the symbol
                news_data = await data_fetcher.get_news_data(symbol)
                if news_data:
                    sentiment = sentiment_analyzer.analyze_text(news_data)
                    sentiment_data.append({
                        "symbol": symbol,
                        "sentiment_score": sentiment.get('sentiment_score', 0),
                        "sentiment_label": sentiment.get('sentiment_label', 'neutral'),
                        "confidence": sentiment.get('confidence', 0),
                        "source": "news"
                    })
            except Exception as e:
                # Fallback to general market sentiment
                pass

        # Get general market sentiment from RSS feeds
        try:
            rss_data = await data_fetcher.get_rss_sentiment()
            if rss_data:
                sentiment = sentiment_analyzer.analyze_text(rss_data)
                sentiment_data.append({
                    "symbol": "MARKET",
                    "sentiment_score": sentiment.get('sentiment_score', 0),
                    "sentiment_label": sentiment.get('sentiment_label', 'neutral'),
                    "confidence": sentiment.get('confidence', 0),
                    "source": "rss"
                })
        except Exception as e:
            pass

        # Get Twitter sentiment if available
        try:
            twitter_data = await data_fetcher.get_twitter_sentiment(symbol or "trading")
            if twitter_data:
                sentiment = sentiment_analyzer.analyze_text(twitter_data)
                sentiment_data.append({
                    "symbol": symbol or "SOCIAL",
                    "sentiment_score": sentiment.get('sentiment_score', 0),
                    "sentiment_label": sentiment.get('sentiment_label', 'neutral'),
                    "confidence": sentiment.get('confidence', 0),
                    "source": "twitter"
                })
        except Exception as e:
            pass

        if not sentiment_data:
            return {
                "message": "No sentiment data available",
                "data": []
            }

        return {
            "data": sentiment_data,
            "timestamp": "latest"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sentiment data: {str(e)}")

@router.get("/historical/{symbol}")
async def get_historical_sentiment(
    symbol: str,
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical sentiment analysis for a symbol."""
    try:
        sentiment_analyzer = SentimentAnalysis()
        data_fetcher = DataFetcher()

        # This would typically fetch historical data and analyze sentiment over time
        # For now, return mock historical data
        historical_data = []

        for i in range(days):
            # Mock sentiment data - in real implementation, fetch historical news/twitter data
            mock_sentiment = {
                "date": f"2024-01-{str(15+i).zfill(2)}",
                "sentiment_score": 0.1 * (i % 3 - 1),  # Alternating positive/negative
                "sentiment_label": "positive" if i % 3 == 0 else "negative" if i % 3 == 1 else "neutral",
                "confidence": 0.7 + 0.1 * (i % 3)
            }
            historical_data.append(mock_sentiment)

        return {
            "symbol": symbol,
            "period_days": days,
            "data": historical_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching historical sentiment: {str(e)}")

@router.get("/market-overview")
async def get_market_sentiment_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overall market sentiment overview."""
    try:
        sentiment_analyzer = SentimentAnalysis()
        data_fetcher = DataFetcher()

        # Get general market sentiment from multiple sources
        sources = ["news", "rss", "social"]
        market_sentiment = {}

        for source in sources:
            try:
                if source == "news":
                    data = await data_fetcher.get_news_data("market")
                elif source == "rss":
                    data = await data_fetcher.get_rss_sentiment()
                else:  # social
                    data = await data_fetcher.get_twitter_sentiment("trading OR stocks")

                if data:
                    sentiment = sentiment_analyzer.analyze_text(data)
                    market_sentiment[source] = {
                        "sentiment_score": sentiment.get('sentiment_score', 0),
                        "sentiment_label": sentiment.get('sentiment_label', 'neutral'),
                        "confidence": sentiment.get('confidence', 0)
                    }
            except Exception as e:
                continue

        # Calculate weighted average sentiment
        if market_sentiment:
            total_score = sum(s['sentiment_score'] * s['confidence'] for s in market_sentiment.values())
            total_confidence = sum(s['confidence'] for s in market_sentiment.values())
            avg_sentiment = total_score / total_confidence if total_confidence > 0 else 0

            overall_label = "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral"
        else:
            avg_sentiment = 0
            overall_label = "neutral"

        return {
            "overall_sentiment": {
                "score": round(avg_sentiment, 3),
                "label": overall_label,
                "confidence": round(total_confidence / len(market_sentiment), 3) if market_sentiment else 0
            },
            "sources": market_sentiment
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market overview: {str(e)}")

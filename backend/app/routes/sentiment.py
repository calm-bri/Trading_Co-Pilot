from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.sentiment_analysis import SentimentAnalysis
from app.services.data_fetcher import DataFetcher
from app.core.config import settings
import anyio # Standard FastAPI dependency for thread bridging

router = APIRouter()

# ✅ FIX: Change 'async def' to 'def' to prevent event loop crashes
@router.get("/latest")
def get_latest_sentiment(symbol: str = None, db: Session = Depends(get_db)):
    """
    Sync route: Safe for DB sessions and won't crash the event loop.
    Uses a thread-safe bridge to call the AI service.
    """
    try:
        analyzer = SentimentAnalysis(settings.GEMINI_API_KEY)
        data_fetcher = DataFetcher()

        # 1. Fetch RSS (Bridge async fetch to sync route)
        # We use anyio.from_thread.run_sync to safely await the fetcher
        articles = anyio.from_thread.run_sync(data_fetcher.get_rss_articles)

        if not articles:
            return {"sentiment": "neutral", "score": 0}

        # 2. Analyze (Bridge async analyzer to sync route)
        sentiment_result = anyio.from_thread.run_sync(
            analyzer.analyze_rss_articles, articles, symbol
        )

        return sentiment_result

    except Exception as e:
        import structlog
        structlog.get_logger().error(f"Route failed: {e}")
        return {"sentiment": "neutral", "score": 0, "error": str(e)}
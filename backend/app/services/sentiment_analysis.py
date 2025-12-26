from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import structlog
import httpx
import asyncio
import json

logger = structlog.get_logger()

class SentimentAnalysis:
    def __init__(self, gemini_api_key: str):
        self.api_key = gemini_api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"
        self.model = "gemini-1.5-flash" # Default to flash for speed

    async def analyze_rss_articles(self, articles: List[Dict], symbol: Optional[str] = None, max_articles: int = 10) -> Dict[str, Any]:
        """Analyzes multiple articles concurrently without blocking."""
        if not articles:
            return self._fallback_sentiment()

        # Limit to the most recent articles
        sample = articles[:max_articles]
        
        # Create tasks for parallel execution
        tasks = [self._analyze_single_article(art, symbol) for art in sample]
        
        # ✅ FIX: Properly await the results
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out failed analyses
        valid_results = [r for r in results if isinstance(r, dict) and "score" in r]
        
        if not valid_results:
            return self._fallback_sentiment()

        # Calculate average score
        avg_score = sum(r["score"] for r in valid_results) / len(valid_results)
        
        return {
            "score": avg_score,
            "sentiment": "bullish" if avg_score > 0.1 else "bearish" if avg_score < -0.1 else "neutral",
            "confidence": 0.8,
            "article_count": len(valid_results),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def _analyze_single_article(self, article: Dict, symbol: str = None) -> Dict:
        """Call Gemini for a single article."""
        prompt = f"Analyze financial sentiment for {symbol or 'market'}: {article.get('title')}"
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, timeout=10.0)
                if response.status_code == 200:
                    raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(raw_text)
            except Exception as e:
                logger.error(f"Gemini call failed: {e}")
            return {"score": 0, "sentiment": "neutral"}

    def _fallback_sentiment(self):
        return {"score": 0, "sentiment": "neutral", "confidence": 0, "article_count": 0, "timestamp": datetime.now(timezone.utc).isoformat()}
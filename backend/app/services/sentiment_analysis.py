import torch
from transformers import pipeline
from typing import Dict, Any, List
import asyncio
import structlog

class SentimentAnalysis:
    def __init__(self):
        # Load pre-trained sentiment analysis model
        try:
            self.sentiment_pipeline = pipeline("sentiment-analysis")
        except Exception as e:
            # Fallback if model loading fails
            self.sentiment_pipeline = None
            logger = structlog.get_logger()
            logger.warning("Sentiment analysis model failed to load", error=str(e))

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        if not self.sentiment_pipeline:
            return {"label": "NEUTRAL", "score": 0.5, "sentiment": "neutral"}
        result = self.sentiment_pipeline(text)[0]
        return {
            "label": result["label"],
            "score": result["score"],
            "sentiment": "positive" if result["label"] == "POSITIVE" else "negative",
        }

    async def analyze_texts_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        if not self.sentiment_pipeline:
            return [{"label": "NEUTRAL", "score": 0.5, "sentiment": "neutral"} for _ in texts]
        results = self.sentiment_pipeline(texts)
        return [
            {
                "label": result["label"],
                "score": result["score"],
                "sentiment": "positive" if result["label"] == "POSITIVE" else "negative",
            }
            for result in results
        ]

    async def calculate_overall_sentiment(self, texts: List[str]) -> Dict[str, Any]:
        if not texts:
            return {"overall_sentiment": "neutral", "average_score": 0.5, "positive_ratio": 0.5}

        results = await self.analyze_texts_batch(texts)

        positive_count = sum(1 for r in results if r["sentiment"] == "positive")
        total_score = sum(r["score"] for r in results)
        average_score = total_score / len(results)

        overall_sentiment = "positive" if average_score > 0.6 else "negative" if average_score < 0.4 else "neutral"

        return {
            "overall_sentiment": overall_sentiment,
            "average_score": average_score,
            "positive_ratio": positive_count / len(results),
            "analysis_count": len(results),
        }

sentiment_analysis = SentimentAnalysis()

from fastapi import APIRouter
from typing import Dict, Optional, List
from pydantic import BaseModel

from app.services.copilot import get_trading_copilot

router = APIRouter()


# ---------- Schemas ----------

class QuestionRequest(BaseModel):
    question: str
    symbols: Optional[List[str]] = None


# ---------- Routes ----------

@router.post("/ask")
async def ask_copilot(request: QuestionRequest):
    """
    Ask the Trading Copilot (Gemini powered)
    NEVER crashes, always responds
    """
    try:
        copilot = get_trading_copilot()

        result = await copilot.chat(
            query=request.question,
            symbols=request.symbols
        )

        return result

    except Exception as e:
        # Absolute safety net
        return {
            "answer": "⚠️ Copilot backend error handled safely.",
            "error": str(e),
            "market_bias": "neutral",
            "sentiment_score": 0.0
        }

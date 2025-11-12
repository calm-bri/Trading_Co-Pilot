from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User
from app.services.copilot import TradingCopilot
from pydantic import BaseModel

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str
    context: Optional[Dict] = None

class StrategyRequest(BaseModel):
    risk_tolerance: str = "MEDIUM"
    investment_amount: Optional[float] = None
    time_horizon: str = "MEDIUM"
    experience: str = "INTERMEDIATE"
    sectors: Optional[str] = "DIVERSIFIED"

@router.get("/insights/{symbol}")
async def get_symbol_insights(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered trading insights for a symbol."""
    try:
        copilot = TradingCopilot()

        # Get user context from their trades
        user_trades = db.query(db.query(User).filter(User.id == current_user.id).first()).first().trades
        user_context = {
            "total_trades": len(user_trades),
            "symbols_traded": list(set([trade.symbol for trade in user_trades]))
        }

        insights = await copilot.get_insights(symbol, user_context)
        return insights

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@router.post("/ask")
async def ask_copilot(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ask the trading copilot a question."""
    try:
        copilot = TradingCopilot()

        # Add user context
        context = request.context or {}
        context["user_id"] = current_user.id
        context["username"] = current_user.username

        answer = await copilot.answer_question(request.question, context)
        return {
            "question": request.question,
            "answer": answer,
            "timestamp": "now"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@router.post("/strategy")
async def generate_strategy(
    request: StrategyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a personalized trading strategy."""
    try:
        copilot = TradingCopilot()

        user_profile = {
            "risk_tolerance": request.risk_tolerance,
            "investment_amount": request.investment_amount,
            "time_horizon": request.time_horizon,
            "experience": request.experience,
            "sectors": request.sectors,
            "user_id": current_user.id
        }

        strategy = await copilot.generate_strategy(user_profile)
        return strategy

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating strategy: {str(e)}")

@router.get("/market-overview")
async def get_market_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered market overview and general insights."""
    try:
        copilot = TradingCopilot()

        # Get insights for major indices
        indices = ["SPY", "QQQ", "IWM"]  # S&P 500, Nasdaq 100, Russell 2000
        market_insights = []

        for symbol in indices:
            try:
                insights = await copilot.get_insights(symbol)
                market_insights.append({
                    "symbol": symbol,
                    "recommendation": insights.get("recommendation", "HOLD"),
                    "confidence": insights.get("confidence", 0.5)
                })
            except:
                continue

        # Generate overall market summary
        prompt = f"""
        Based on the following market data, provide a brief market overview:

        {market_insights}

        Give a 2-3 sentence summary of the current market sentiment and key takeaways.
        """

        response = copilot.model.generate_content(prompt)
        summary = response.text.strip()

        return {
            "market_summary": summary,
            "indices": market_insights,
            "overall_sentiment": "BULLISH" if sum([i['confidence'] for i in market_insights]) / len(market_insights) > 0.6 else "BEARISH" if sum([i['confidence'] for i in market_insights]) / len(market_insights) < 0.4 else "NEUTRAL"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating market overview: {str(e)}")

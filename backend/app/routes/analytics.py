from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Trade
from app.services.technical_analysis import TechnicalAnalysis
from app.services.risk_management import RiskManagement
from app.services.data_fetcher import DataFetcher
from app.core.config import settings

router = APIRouter()

@router.get("/summary")
async def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get portfolio summary with performance metrics."""
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()

    if not trades:
        return {
            "total_trades": 0,
            "total_value": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "sharpe_ratio": 0
        }

    # Calculate basic metrics
    total_trades = len(trades)
    total_value = sum(trade.quantity * trade.price for trade in trades)

    # Calculate P&L (simplified - assuming all trades are closed)
    pnl = 0
    winning_trades = 0

    # Group trades by symbol for analysis
    symbol_trades = {}
    for trade in trades:
        if trade.symbol not in symbol_trades:
            symbol_trades[trade.symbol] = []
        symbol_trades[trade.symbol].append(trade)

    # Calculate performance metrics
    for symbol, symbol_trades_list in symbol_trades.items():
        # Simple P&L calculation (buy low, sell high)
        buys = [t for t in symbol_trades_list if t.trade_type == 'buy']
        sells = [t for t in symbol_trades_list if t.trade_type == 'sell']

        if buys and sells:
            avg_buy_price = sum(t.price for t in buys) / len(buys)
            avg_sell_price = sum(t.price for t in sells) / len(sells)
            symbol_pnl = (avg_sell_price - avg_buy_price) * min(sum(t.quantity for t in buys), sum(t.quantity for t in sells))
            pnl += symbol_pnl
            if symbol_pnl > 0:
                winning_trades += 1

    win_rate = (winning_trades / len(symbol_trades)) * 100 if symbol_trades else 0

    # Calculate Sharpe ratio (simplified)
    sharpe_ratio = pnl / total_value if total_value > 0 else 0

    return {
        "total_trades": total_trades,
        "total_value": round(total_value, 2),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(pnl, 2),
        "sharpe_ratio": round(sharpe_ratio, 4)
    }

@router.get("/technical/{symbol}")
async def get_technical_analysis(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get technical analysis for a symbol."""
    try:
        data_fetcher = DataFetcher()
        technical_analysis = TechnicalAnalysis()

        # Fetch historical data
        data = await data_fetcher.get_historical_data(symbol)

        if data.empty:
            raise HTTPException(status_code=404, detail="No data available for symbol")

        # Calculate indicators
        indicators = technical_analysis.calculate_indicators(data)

        return {
            "symbol": symbol,
            "indicators": indicators,
            "latest": {
                "rsi": indicators['rsi'].iloc[-1] if not indicators['rsi'].empty else None,
                "macd": indicators['macd'].iloc[-1] if not indicators['macd'].empty else None,
                "macd_signal": indicators['macd_signal'].iloc[-1] if not indicators['macd_signal'].empty else None,
                "bollinger_upper": indicators['bollinger_upper'].iloc[-1] if not indicators['bollinger_upper'].empty else None,
                "bollinger_lower": indicators['bollinger_lower'].iloc[-1] if not indicators['bollinger_lower'].empty else None,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching technical analysis: {str(e)}")

@router.get("/risk-metrics")
async def get_risk_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get risk metrics for the portfolio."""
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()

    if not trades:
        return {
            "max_drawdown": 0,
            "sharpe_ratio": 0,
            "volatility": 0,
            "var_95": 0
        }

    # Extract returns from trades (simplified)
    returns = []
    for trade in trades:
        # Simplified return calculation
        if trade.trade_type == 'sell':
            returns.append(trade.price * trade.quantity)

    risk_manager = RiskManagement()
    metrics = risk_manager.calculate_risk_metrics(returns)

    return {
        "max_drawdown": round(metrics.get('max_drawdown', 0), 4),
        "sharpe_ratio": round(metrics.get('sharpe_ratio', 0), 4),
        "volatility": round(metrics.get('volatility', 0), 4),
        "var_95": round(metrics.get('var_95', 0), 4)
    }

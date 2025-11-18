from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback
from typing import Dict, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, Trade
from app.services.technical_analysis import TechnicalAnalysis
from app.services.risk_management import RiskManagement
from app.services.data_fetcher import DataFetcher

router = APIRouter()


# -------------------------------------------------------------------
# PORTFOLIO SUMMARY
# -------------------------------------------------------------------
@router.get("/summary")
async def get_portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()

    if not trades:
        return {
            "total_trades": 0,
            "total_value": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "sharpe_ratio": 0
        }

    total_value = sum(trade.quantity * trade.price for trade in trades)
    total_trades = len(trades)

    pnl = 0
    winning_trades = 0

    symbol_trades = {}
    for trade in trades:
        symbol_trades.setdefault(trade.symbol, []).append(trade)

    for symbol, s_trades in symbol_trades.items():
        buys = [t for t in s_trades if t.trade_type == "buy"]
        sells = [t for t in s_trades if t.trade_type == "sell"]

        if buys and sells:
            avg_buy = sum(t.price for t in buys) / len(buys)
            avg_sell = sum(t.price for t in sells) / len(sells)
            qty = min(sum(t.quantity for t in buys), sum(t.quantity for t in sells))
            symbol_pnl = (avg_sell - avg_buy) * qty
            pnl += symbol_pnl
            if symbol_pnl > 0:
                winning_trades += 1

    win_rate = (winning_trades / len(symbol_trades)) * 100 if symbol_trades else 0
    sharpe_ratio = pnl / total_value if total_value > 0 else 0

    return {
        "total_trades": total_trades,
        "total_value": round(total_value, 2),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(pnl, 2),
        "sharpe_ratio": round(sharpe_ratio, 4)
    }


# -------------------------------------------------------------------
# TECHNICAL ANALYSIS
# -------------------------------------------------------------------
@router.get("/technical/{symbol}")
async def get_technical_analysis(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get technical indicators using Finnhub OHLC data.
    """
    try:
        fetcher = DataFetcher()
        ta = TechnicalAnalysis()
        
        #cleaner symbols
        symbol = symbol.upper().strip()


        df = await fetcher.get_ohlcv_series(symbol, resolution="D", days=30)


        # FIX: df.empty is unreliable → use len(df)
        if df is None or len(df) == 0:
            print("⚠ TECH: DF EMPTY OR NONE")
            raise HTTPException(status_code=404, detail="No OHLC data available.")


        # Rename columns to match TechnicalAnalysis expectations
        df = df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
            "date": "Date",
        })

        df["Date"] = df["Date"].astype(str)

        # Check required columns
        for col in ["Open", "High", "Low", "Close"]:
            if col not in df.columns:
                raise Exception(f"Missing column: {col}")

        # Minimum candles required
        if len(df) < 50:
            raise Exception("Not enough OHLC data (need 50+ candles)")

        indicators = ta.calculate_indicators(df)

        # Return full arrays for frontend to use
        return {
            "symbol": symbol,
            "indicators": {
                "date": indicators["Date"].tolist(),
                "rsi": indicators["rsi"].tolist(),
                "macd": indicators["macd"].tolist(),
                "macd_signal": indicators["macd_signal"].tolist(),
                "bollinger_upper": indicators["bollinger_upper"].tolist(),
                "bollinger_lower": indicators["bollinger_lower"].tolist(),
                "sma": indicators.get("sma", []).tolist() if "sma" in indicators else [],
                "ema": indicators.get("ema", []).tolist() if "ema" in indicators else [],
            }
        }

    except Exception:
        import traceback
        print("\n\n❌ TECHNICAL / TRACEBACK ❌")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Technical indicator calculation failed."
        )


# -------------------------------------------------------------------
# RISK METRICS
# -------------------------------------------------------------------
@router.get("/risk-metrics")
async def get_risk_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        trades = db.query(Trade).filter(Trade.user_id == current_user.id).all()

        if not trades:
            return {
                "max_drawdown": 0,
                "sharpe_ratio": 0,
                "volatility": 0,
                "var_95": 0
            }

        # Simple risk calculations
        pnls = []
        cumulative = 0
        peak = 0
        max_drawdown = 0

        for trade in trades:
            pnl = trade.quantity * trade.price * (1 if trade.trade_type == "sell" else -1)
            cumulative += pnl
            pnls.append(cumulative)

            if cumulative > peak:
                peak = cumulative
            drawdown = peak - cumulative
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        volatility = sum(p**2 for p in pnls) / len(pnls) if pnls else 0
        sharpe_ratio = sum(pnls) / len(pnls) / volatility if volatility > 0 else 0
        var_95 = sorted(pnls)[int(len(pnls) * 0.05)] if pnls else 0

        return {
            "max_drawdown": round(max_drawdown, 2),
            "sharpe_ratio": round(sharpe_ratio, 4),
            "volatility": round(volatility, 4),
            "var_95": round(var_95, 2)
        }

    except Exception as e:
        print("❌ RISK METRICS ERROR:", e)
        raise HTTPException(status_code=500, detail="Risk metrics calculation failed.")


# -------------------------------------------------------------------
# OHLCV SERIES
# -------------------------------------------------------------------
@router.get("/series/{symbol}")
async def get_candle_series(
    symbol: str,
    resolution: str = "D",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        fetcher = DataFetcher()
        df = await fetcher. get_ohlcv_series(symbol)

        if df is None or df.empty:
            return {"symbol": symbol, "series": []}

        df["date"] = df["date"].astype(str)

        series = [
            {
                "date": row["date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"]),
            }
            for _, row in df.iterrows()
        ]

        return {"symbol": symbol, "series": series}

    except Exception as e:
        print("❌ ERROR /series:", e)
        raise HTTPException(status_code=500, detail=f"Error fetching OHLCV series: {str(e)}")

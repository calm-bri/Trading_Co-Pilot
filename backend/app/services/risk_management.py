import numpy as np
from typing import List, Dict, Any

class RiskManagement:
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> Dict[str, Any]:
        if len(prices) < 2:
            return {"max_drawdown": 0, "peak": prices[0] if prices else 0, "trough": prices[0] if prices else 0}

        prices_array = np.array(prices)
        cumulative = np.maximum.accumulate(prices_array)
        drawdowns = (cumulative - prices_array) / cumulative

        max_drawdown_idx = np.argmax(drawdowns)
        peak_idx = np.where(cumulative == cumulative[max_drawdown_idx])[0][0]

        return {
            "max_drawdown": float(drawdowns[max_drawdown_idx]),
            "peak": float(prices_array[peak_idx]),
            "trough": float(prices_array[max_drawdown_idx]),
            "drawdown_period": max_drawdown_idx - peak_idx,
        }

    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.02) -> float:
        if len(returns) < 2:
            return 0.0

        returns_array = np.array(returns)
        excess_returns = returns_array - risk_free_rate / 252  # Assuming daily returns
        avg_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)

        if std_excess_return == 0:
            return 0.0

        return float(avg_excess_return / std_excess_return * np.sqrt(252))  # Annualized

    @staticmethod
    def calculate_win_rate(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not trades:
            return {"win_rate": 0, "total_trades": 0, "winning_trades": 0, "losing_trades": 0}

        winning_trades = sum(1 for trade in trades if trade.get("pnl", 0) > 0)
        total_trades = len(trades)

        return {
            "win_rate": winning_trades / total_trades if total_trades > 0 else 0,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
        }

    @staticmethod
    def calculate_portfolio_metrics(prices: List[float], trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i] - prices[i-1]) / prices[i-1])

        return {
            "max_drawdown": RiskManagement.calculate_max_drawdown(prices),
            "sharpe_ratio": RiskManagement.calculate_sharpe_ratio(returns),
            "win_rate": RiskManagement.calculate_win_rate(trades),
            "total_return": (prices[-1] - prices[0]) / prices[0] if prices else 0,
            "volatility": float(np.std(returns)) * np.sqrt(252) if returns else 0,
        }

risk_management = RiskManagement()

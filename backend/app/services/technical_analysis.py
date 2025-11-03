import pandas as pd
import numpy as np
from typing import Dict, Any, List

class TechnicalAnalysis:
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        if len(prices) < period:
            return []

        gains = []
        losses = []

        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))

        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period

        rsi_values = []
        for i in range(period, len(prices)):
            if i > period:
                avg_gain = (avg_gain * (period - 1) + gains[i-1]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i-1]) / period

            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(rsi)

        return rsi_values

    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, List[float]]:
        if len(prices) < slow_period:
            return {"macd": [], "signal": [], "histogram": []}

        fast_ema = pd.Series(prices).ewm(span=fast_period).mean()
        slow_ema = pd.Series(prices).ewm(span=slow_period).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period).mean()
        histogram = macd - signal

        return {
            "macd": macd.tolist(),
            "signal": signal.tolist(),
            "histogram": histogram.tolist(),
        }

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2) -> Dict[str, List[float]]:
        if len(prices) < period:
            return {"upper": [], "middle": [], "lower": []}

        sma = pd.Series(prices).rolling(window=period).mean()
        std = pd.Series(prices).rolling(window=period).std()

        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        return {
            "upper": upper.tolist(),
            "middle": sma.tolist(),
            "lower": lower.tolist(),
        }

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        if len(prices) < period:
            return []
        return pd.Series(prices).ewm(span=period).mean().tolist()

    def analyze_stock(self, prices: List[float]) -> Dict[str, Any]:
        return {
            "rsi": self.calculate_rsi(prices),
            "macd": self.calculate_macd(prices),
            "bollinger_bands": self.calculate_bollinger_bands(prices),
            "ema_20": self.calculate_ema(prices, 20),
            "ema_50": self.calculate_ema(prices, 50),
        }

technical_analysis = TechnicalAnalysis()

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

    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators and return DataFrame with indicators.
        """
        if df.empty or len(df) < 50:
            return pd.DataFrame()

        # Ensure we have the required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume", "Date"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # Convert to numeric if needed
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Calculate indicators
        close_prices = df["Close"].tolist()

        # RSI
        rsi_values = self.calculate_rsi(close_prices)
        df["rsi"] = [np.nan] * (len(df) - len(rsi_values)) + rsi_values

        # MACD
        macd_data = self.calculate_macd(close_prices)
        df["macd"] = [np.nan] * (len(df) - len(macd_data["macd"])) + macd_data["macd"]
        df["macd_signal"] = [np.nan] * (len(df) - len(macd_data["signal"])) + macd_data["signal"]

        # Bollinger Bands
        bb_data = self.calculate_bollinger_bands(close_prices)
        df["bollinger_upper"] = [np.nan] * (len(df) - len(bb_data["upper"])) + bb_data["upper"]
        df["bollinger_lower"] = [np.nan] * (len(df) - len(bb_data["lower"])) + bb_data["lower"]

        # Moving Averages
        df["sma"] = pd.Series(close_prices).rolling(window=20).mean()
        df["ema"] = self.calculate_ema(close_prices, 20)

        return df

    def analyze_stock(self, prices: List[float]) -> Dict[str, Any]:
        return {
            "rsi": self.calculate_rsi(prices),
            "macd": self.calculate_macd(prices),
            "bollinger_bands": self.calculate_bollinger_bands(prices),
            "ema_20": self.calculate_ema(prices, 20),
            "ema_50": self.calculate_ema(prices, 50),
        }

technical_analysis = TechnicalAnalysis()

"""
Feature Engineering for ML Trading

Extracts technical indicators and price features from market data
to create feature vectors for machine learning models.

Uses TA-Lib for technical analysis calculations.
"""

import logging

import numpy as np
import pandas as pd


try:
    import ta
    from ta.momentum import RSIIndicator, StochasticOscillator
    from ta.trend import MACD, ADXIndicator, EMAIndicator, SMAIndicator
    from ta.volatility import AverageTrueRange, BollingerBands
    from ta.volume import OnBalanceVolumeIndicator
except ImportError:
    # Graceful degradation if TA library not installed yet
    ta = None

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """
    Extracts technical analysis features from price/volume data
    for machine learning models.
    """

    def __init__(self):
        """Initialize feature engineer"""
        if ta is None:
            logger.warning("TA library not installed. Install with: pip install ta>=0.11.0")

    def extract_features(self, df: pd.DataFrame, symbol: str = "UNKNOWN") -> pd.DataFrame:
        """
        Extract all features from OHLCV dataframe

        Args:
            df: DataFrame with columns: open, high, low, close, volume
            symbol: Stock symbol for logging

        Returns:
            DataFrame with original data + extracted features
        """
        if df.empty or len(df) < 50:
            logger.warning(f"Insufficient data for {symbol}: {len(df)} rows (need 50+)")
            return df

        logger.info(f"Extracting features for {symbol} ({len(df)} data points)")

        try:
            # Create copy to avoid modifying original
            features_df = df.copy()

            # Ensure column names are lowercase
            features_df.columns = features_df.columns.str.lower()

            # Extract each feature group
            features_df = self._add_trend_features(features_df)
            features_df = self._add_momentum_features(features_df)
            features_df = self._add_volatility_features(features_df)
            features_df = self._add_volume_features(features_df)
            features_df = self._add_price_features(features_df)

            # Drop rows with NaN (from indicator warmup periods)
            features_df = features_df.dropna()

            logger.info(f"✅ Extracted {len(features_df.columns)} features for {symbol}")

            return features_df

        except Exception as e:
            logger.error(f"❌ Feature extraction failed for {symbol}: {e}")
            return df

    def _add_trend_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add trend indicators (moving averages, MACD, ADX)"""
        try:
            close = df["close"]

            # Simple Moving Averages
            df["sma_20"] = SMAIndicator(close=close, window=20).sma_indicator()
            df["sma_50"] = SMAIndicator(close=close, window=50).sma_indicator()
            df["sma_200"] = SMAIndicator(close=close, window=200).sma_indicator()

            # Exponential Moving Averages
            df["ema_12"] = EMAIndicator(close=close, window=12).ema_indicator()
            df["ema_26"] = EMAIndicator(close=close, window=26).ema_indicator()

            # MACD
            macd = MACD(close=close)
            df["macd"] = macd.macd()
            df["macd_signal"] = macd.macd_signal()
            df["macd_diff"] = macd.macd_diff()

            # ADX (trend strength)
            adx = ADXIndicator(high=df["high"], low=df["low"], close=close)
            df["adx"] = adx.adx()

            # Price position relative to moving averages
            df["price_above_sma20"] = (close > df["sma_20"]).astype(int)
            df["price_above_sma50"] = (close > df["sma_50"]).astype(int)
            df["price_above_sma200"] = (close > df["sma_200"]).astype(int)

            return df

        except Exception as e:
            logger.error(f"Trend features failed: {e}")
            return df

    def _add_momentum_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add momentum indicators (RSI, Stochastic)"""
        try:
            close = df["close"]
            high = df["high"]
            low = df["low"]

            # RSI
            rsi = RSIIndicator(close=close, window=14)
            df["rsi"] = rsi.rsi()

            # Stochastic Oscillator
            stoch = StochasticOscillator(high=high, low=low, close=close)
            df["stoch_k"] = stoch.stoch()
            df["stoch_d"] = stoch.stoch_signal()

            # RSI overbought/oversold flags
            df["rsi_oversold"] = (df["rsi"] < 30).astype(int)
            df["rsi_overbought"] = (df["rsi"] > 70).astype(int)

            # Rate of change
            df["roc_10"] = close.pct_change(periods=10) * 100

            return df

        except Exception as e:
            logger.error(f"Momentum features failed: {e}")
            return df

    def _add_volatility_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volatility indicators (ATR, Bollinger Bands)"""
        try:
            close = df["close"]
            high = df["high"]
            low = df["low"]

            # Average True Range
            atr = AverageTrueRange(high=high, low=low, close=close)
            df["atr"] = atr.average_true_range()

            # Bollinger Bands
            bb = BollingerBands(close=close)
            df["bb_upper"] = bb.bollinger_hband()
            df["bb_middle"] = bb.bollinger_mavg()
            df["bb_lower"] = bb.bollinger_lband()
            df["bb_width"] = bb.bollinger_wband()

            # Price position relative to Bollinger Bands
            df["price_vs_bb"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

            # Historical volatility (20-day)
            df["volatility_20"] = close.pct_change().rolling(window=20).std() * np.sqrt(252)

            return df

        except Exception as e:
            logger.error(f"Volatility features failed: {e}")
            return df

    def _add_volume_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add volume-based features"""
        try:
            close = df["close"]
            volume = df["volume"]

            # On-Balance Volume
            obv = OnBalanceVolumeIndicator(close=close, volume=volume)
            df["obv"] = obv.on_balance_volume()

            # Volume moving average
            df["volume_sma_20"] = volume.rolling(window=20).mean()

            # Volume relative to average
            df["volume_ratio"] = volume / df["volume_sma_20"]

            # Price-volume trend
            df["price_volume_trend"] = (close.pct_change() * volume).cumsum()

            return df

        except Exception as e:
            logger.error(f"Volume features failed: {e}")
            return df

    def _add_price_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add price-based features"""
        try:
            close = df["close"]
            high = df["high"]
            low = df["low"]
            open_price = df["open"]

            # Price changes
            df["price_change"] = close.pct_change()
            df["price_change_5d"] = close.pct_change(periods=5)
            df["price_change_20d"] = close.pct_change(periods=20)

            # High-low range
            df["hl_range"] = (high - low) / close

            # Close position within daily range
            df["close_position"] = (close - low) / (high - low + 1e-10)

            # Gap (open vs previous close)
            df["gap"] = (open_price - close.shift(1)) / close.shift(1)

            # Trend direction (1 = up, -1 = down, 0 = flat)
            df["trend_direction"] = np.sign(close - close.shift(5))

            return df

        except Exception as e:
            logger.error(f"Price features failed: {e}")
            return df

    def get_feature_names(self) -> list[str]:
        """
        Get list of all feature names that will be extracted

        Returns:
            List of feature column names
        """
        return [
            # Trend features
            "sma_20",
            "sma_50",
            "sma_200",
            "ema_12",
            "ema_26",
            "macd",
            "macd_signal",
            "macd_diff",
            "adx",
            "price_above_sma20",
            "price_above_sma50",
            "price_above_sma200",
            # Momentum features
            "rsi",
            "stoch_k",
            "stoch_d",
            "rsi_oversold",
            "rsi_overbought",
            "roc_10",
            # Volatility features
            "atr",
            "bb_upper",
            "bb_middle",
            "bb_lower",
            "bb_width",
            "price_vs_bb",
            "volatility_20",
            # Volume features
            "obv",
            "volume_sma_20",
            "volume_ratio",
            "price_volume_trend",
            # Price features
            "price_change",
            "price_change_5d",
            "price_change_20d",
            "hl_range",
            "close_position",
            "gap",
            "trend_direction",
        ]


# Convenience function for quick feature extraction
def extract_features_from_dict(data: list[dict]) -> pd.DataFrame:
    """
    Extract features from list of OHLCV dictionaries

    Args:
        data: List of dicts with keys: date, open, high, low, close, volume

    Returns:
        DataFrame with features
    """
    df = pd.DataFrame(data)

    # Ensure datetime index
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.set_index("date")

    engineer = FeatureEngineer()
    return engineer.extract_features(df)

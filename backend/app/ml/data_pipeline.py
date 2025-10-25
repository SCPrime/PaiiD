"""
Data Pipeline for ML Models

Fetches historical market data, preprocesses it, and prepares
feature matrices for machine learning training and prediction.
"""

import logging
from datetime import datetime, timedelta

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from ..services.tradier_client import get_tradier_client
from .feature_engineering import FeatureEngineer


logger = logging.getLogger(__name__)


class MLDataPipeline:
    """
    End-to-end data pipeline for ML model training and inference
    """

    def __init__(self):
        """Initialize data pipeline"""
        self.tradier_client = get_tradier_client()
        self.feature_engineer = FeatureEngineer()
        self.scaler = StandardScaler()
        self.feature_columns = None

    def fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        interval: str = "daily",
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Tradier

        Args:
            symbol: Stock symbol (e.g., "AAPL")
            start_date: Start date (default: 2 years ago)
            end_date: End date (default: today)
            interval: Data interval ("daily", "weekly")

        Returns:
            DataFrame with columns: date, open, high, low, close, volume
        """
        try:
            # Default date range: 2 years of history
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=730)  # 2 years

            logger.info(
                f"Fetching historical data for {symbol} ({start_date.date()} to {end_date.date()})"
            )

            # Fetch from Tradier
            data = self.tradier_client.get_historical_quotes(
                symbol=symbol,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                interval=interval,
            )

            if not data or len(data) == 0:
                logger.warning(f"No historical data returned for {symbol}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame(data)

            # Ensure required columns
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_cols):
                logger.error(f"Missing required columns for {symbol}: {df.columns}")
                return pd.DataFrame()

            # Convert date to datetime
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")

            # Sort by date
            df = df.sort_index()

            # Convert to float
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Drop rows with NaN
            df = df.dropna()

            logger.info(
                f"✅ Fetched {len(df)} data points for {symbol} "
                f"({df.index[0].date()} to {df.index[-1].date()})"
            )

            return df

        except Exception as e:
            logger.error(f"❌ Failed to fetch historical data for {symbol}: {e}")
            return pd.DataFrame()

    def prepare_features(self, symbol: str, lookback_days: int = 730) -> pd.DataFrame | None:
        """
        Fetch data and extract features for a symbol

        Args:
            symbol: Stock symbol
            lookback_days: Days of history to fetch (default: 2 years)

        Returns:
            DataFrame with features, or None if failed
        """
        try:
            # Fetch historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days)

            df = self.fetch_historical_data(symbol, start_date, end_date)

            if df.empty:
                return None

            # Extract features
            features_df = self.feature_engineer.extract_features(df, symbol)

            if features_df.empty:
                logger.warning(f"Feature extraction returned empty for {symbol}")
                return None

            logger.info(
                f"✅ Prepared {len(features_df)} feature rows for {symbol} "
                f"with {len(features_df.columns)} columns"
            )

            return features_df

        except Exception as e:
            logger.error(f"❌ Feature preparation failed for {symbol}: {e}")
            return None

    def create_training_dataset(
        self,
        symbols: list[str],
        target_column: str = "future_return",
        lookback: int = 5,
        test_size: float = 0.2,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series] | None:
        """
        Create train/test split for multiple symbols

        Args:
            symbols: List of stock symbols
            target_column: Name of target variable to predict
            lookback: Days to look ahead for target (default: 5 days)
            test_size: Fraction of data for testing (default: 0.2)

        Returns:
            Tuple of (X_train, X_test, y_train, y_test) or None if failed
        """
        try:
            all_features = []

            # Fetch and process each symbol
            for symbol in symbols:
                logger.info(f"Processing {symbol} for training dataset...")

                features_df = self.prepare_features(symbol)

                if features_df is None or features_df.empty:
                    logger.warning(f"Skipping {symbol} - no features extracted")
                    continue

                # Create target variable (future return)
                features_df[target_column] = (
                    features_df["close"].pct_change(periods=lookback).shift(-lookback)
                )

                # Add symbol column
                features_df["symbol"] = symbol

                all_features.append(features_df)

            if not all_features:
                logger.error("No features extracted from any symbol")
                return None

            # Combine all symbols
            combined_df = pd.concat(all_features, ignore_index=True)

            # Drop rows with NaN target
            combined_df = combined_df.dropna(subset=[target_column])

            logger.info(f"✅ Combined dataset: {len(combined_df)} rows from {len(symbols)} symbols")

            # Separate features and target
            feature_cols = self.feature_engineer.get_feature_names()
            # Filter to only existing columns
            feature_cols = [col for col in feature_cols if col in combined_df.columns]

            # ruff: noqa: N806  # X and y follow ML convention
            X = combined_df[feature_cols]
            y = combined_df[target_column]

            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, shuffle=True
            )

            # Fit scaler on training data
            X_train_scaled = pd.DataFrame(
                self.scaler.fit_transform(X_train),
                columns=X_train.columns,
                index=X_train.index,
            )

            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index,
            )

            logger.info(f"✅ Train/test split: {len(X_train)} train, {len(X_test)} test")

            # Store feature columns for later use
            self.feature_columns = feature_cols

            return X_train_scaled, X_test_scaled, y_train, y_test

        except Exception as e:
            logger.error(f"❌ Training dataset creation failed: {e}")
            return None

    def prepare_prediction_features(
        self, symbol: str, current_data: pd.DataFrame | None = None
    ) -> pd.DataFrame | None:
        """
        Prepare features for real-time prediction

        Args:
            symbol: Stock symbol
            current_data: Optional pre-fetched OHLCV data
                          If None, will fetch recent data

        Returns:
            DataFrame with scaled features ready for prediction
        """
        try:
            # Fetch recent data if not provided
            if current_data is None:
                current_data = self.prepare_features(symbol, lookback_days=365)

            if current_data is None or current_data.empty:
                logger.warning(f"No data available for prediction: {symbol}")
                return None

            # Get latest row
            latest_features = current_data.iloc[-1:]

            # Select feature columns
            if self.feature_columns is None:
                # Use all available feature columns
                self.feature_columns = self.feature_engineer.get_feature_names()

            # Filter to existing columns
            available_cols = [col for col in self.feature_columns if col in latest_features.columns]

            features = latest_features[available_cols]

            # Scale features (assumes scaler was fit during training)
            if hasattr(self.scaler, "mean_"):
                features_scaled = pd.DataFrame(
                    self.scaler.transform(features),
                    columns=features.columns,
                    index=features.index,
                )
            else:
                logger.warning("Scaler not fitted yet - using unscaled features")
                features_scaled = features

            logger.info(
                f"✅ Prepared prediction features for {symbol}: "
                f"{len(features_scaled.columns)} features"
            )

            return features_scaled

        except Exception as e:
            logger.error(f"❌ Prediction feature preparation failed for {symbol}: {e}")
            return None


# Singleton instance
_data_pipeline = None


def get_data_pipeline() -> MLDataPipeline:
    """Get or create ML data pipeline singleton"""
    global _data_pipeline
    if _data_pipeline is None:
        _data_pipeline = MLDataPipeline()
    return _data_pipeline

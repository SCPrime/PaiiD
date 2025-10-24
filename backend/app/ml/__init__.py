"""
Machine Learning Module for PaiiD

Provides intelligent strategy recommendations, pattern recognition,
and market regime detection using scikit-learn and technical analysis.

Phase 2: ML Strategy Engine
"""

from .data_pipeline import MLDataPipeline, get_data_pipeline
from .feature_engineering import FeatureEngineer
from .market_regime import MarketRegimeDetector, get_regime_detector


__all__ = [
    "FeatureEngineer",
    "MLDataPipeline",
    "MarketRegimeDetector",
    "get_data_pipeline",
    "get_regime_detector",
]

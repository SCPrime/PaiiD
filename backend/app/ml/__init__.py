"""
Machine Learning Module for PaiiD

Provides intelligent strategy recommendations, pattern recognition,
and market regime detection using scikit-learn and technical analysis.

Phase 2: ML Strategy Engine
"""

from .feature_engineering import FeatureEngineer
from .market_regime import MarketRegimeDetector
from .pattern_recognition import PatternDetector
from .strategy_selector import StrategySelector


__all__ = [
    "FeatureEngineer",
    "MarketRegimeDetector",
    "PatternDetector",
    "StrategySelector",
]

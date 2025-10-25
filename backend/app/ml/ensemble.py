"""
Ensemble ML Models

Combines multiple ML models for more robust predictions.
Uses voting, averaging, and stacking techniques.

Phase 3A: Advanced ML Features - Ensemble Models
"""

import logging
from typing import Any

import numpy as np
from sklearn.ensemble import VotingClassifier, VotingRegressor


logger = logging.getLogger(__name__)


class EnsemblePredictor:
    """
    Ensemble model that combines predictions from multiple base models

    Supports:
    - Hard/soft voting for classification
    - Mean/median averaging for regression
    - Weighted combinations
    - Confidence-based weighting
    """

    def __init__(self, ensemble_type: str = "voting"):
        """
        Initialize ensemble predictor

        Args:
            ensemble_type: Type of ensemble (voting, averaging, stacking, weighted)
        """
        self.ensemble_type = ensemble_type
        self.models: dict[str, Any] = {}
        self.weights: dict[str, float] = {}
        self.is_fitted = False

    def add_model(self, name: str, model: Any, weight: float = 1.0):
        """
        Add a model to the ensemble

        Args:
            name: Model identifier (e.g., "regime_detector", "strategy_selector")
            model: Trained model object
            weight: Weight for weighted ensemble (default: 1.0)
        """
        self.models[name] = model
        self.weights[name] = weight
        logger.info(f"Added model to ensemble: {name} (weight: {weight})")

    def predict_classification(
        self,
        features: dict[str, Any],
        method: str = "soft",
    ) -> dict[str, Any]:
        """
        Ensemble classification prediction

        Args:
            features: Input features for prediction
            method: Voting method (soft=probability, hard=class label)

        Returns:
            Ensemble prediction with confidence and individual votes
        """
        if not self.models:
            raise ValueError("No models added to ensemble")

        try:
            predictions = {}
            confidences = {}

            # Get predictions from each model
            for name, model in self.models.items():
                try:
                    pred = model.predict(features)
                    predictions[name] = pred.get("regime") or pred.get("class")
                    confidences[name] = pred.get("confidence", 0.5)
                except Exception as e:
                    logger.warning(f"Model {name} failed to predict: {e}")
                    continue

            if not predictions:
                raise ValueError("All models failed to predict")

            # Perform ensemble voting
            if method == "soft":
                # Weighted soft voting based on confidence
                class_votes: dict[str, float] = {}

                for name, prediction in predictions.items():
                    confidence = confidences[name]
                    weight = self.weights.get(name, 1.0)
                    vote_weight = confidence * weight

                    if prediction not in class_votes:
                        class_votes[prediction] = 0
                    class_votes[prediction] += vote_weight

                # Get winner
                winner = max(class_votes, key=class_votes.get)  # type: ignore
                total_votes = sum(class_votes.values())
                ensemble_confidence = class_votes[winner] / total_votes if total_votes > 0 else 0

            else:  # Hard voting
                # Simple majority vote with weights
                class_votes = {}

                for name, prediction in predictions.items():
                    weight = self.weights.get(name, 1.0)

                    if prediction not in class_votes:
                        class_votes[prediction] = 0
                    class_votes[prediction] += weight

                winner = max(class_votes, key=class_votes.get)  # type: ignore
                total_votes = sum(class_votes.values())
                ensemble_confidence = class_votes[winner] / total_votes if total_votes > 0 else 0

            return {
                "prediction": winner,
                "confidence": ensemble_confidence,
                "method": method,
                "individual_predictions": predictions,
                "individual_confidences": confidences,
                "vote_distribution": class_votes,
                "num_models": len(predictions),
            }

        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            raise

    def predict_regression(
        self,
        features: dict[str, Any],
        method: str = "mean",
    ) -> dict[str, Any]:
        """
        Ensemble regression prediction

        Args:
            features: Input features for prediction
            method: Aggregation method (mean, median, weighted)

        Returns:
            Ensemble prediction with variance and individual predictions
        """
        if not self.models:
            raise ValueError("No models added to ensemble")

        try:
            predictions = []
            model_names = []

            # Get predictions from each model
            for name, model in self.models.items():
                try:
                    pred = model.predict(features)
                    value = pred.get("value") or pred.get("prediction")

                    if value is not None:
                        weight = self.weights.get(name, 1.0)
                        predictions.append((value, weight))
                        model_names.append(name)
                except Exception as e:
                    logger.warning(f"Model {name} failed to predict: {e}")
                    continue

            if not predictions:
                raise ValueError("All models failed to predict")

            values = [p[0] for p in predictions]
            weights = [p[1] for p in predictions]

            # Perform ensemble aggregation
            if method == "mean":
                ensemble_value = np.mean(values)
            elif method == "median":
                ensemble_value = np.median(values)
            elif method == "weighted":
                ensemble_value = np.average(values, weights=weights)
            else:
                raise ValueError(f"Unknown aggregation method: {method}")

            # Calculate uncertainty
            variance = np.var(values)
            std_dev = np.std(values)

            return {
                "prediction": float(ensemble_value),
                "variance": float(variance),
                "std_dev": float(std_dev),
                "method": method,
                "individual_predictions": {
                    name: value for name, (value, _) in zip(model_names, predictions)
                },
                "num_models": len(predictions),
                "min_prediction": float(min(values)),
                "max_prediction": float(max(values)),
            }

        except Exception as e:
            logger.error(f"Ensemble regression failed: {e}")
            raise

    def get_model_performance_weights(
        self,
        performance_metrics: dict[str, float],
    ) -> dict[str, float]:
        """
        Calculate optimal weights based on model performance

        Args:
            performance_metrics: Dict of {model_name: accuracy/r2_score}

        Returns:
            Optimal weights for each model
        """
        try:
            # Normalize performance to weights
            total_performance = sum(performance_metrics.values())

            if total_performance == 0:
                # Equal weights if no performance data
                return {name: 1.0 / len(performance_metrics) for name in performance_metrics}

            weights = {
                name: performance / total_performance
                for name, performance in performance_metrics.items()
            }

            # Update internal weights
            self.weights.update(weights)

            logger.info(f"Updated ensemble weights: {weights}")
            return weights

        except Exception as e:
            logger.error(f"Failed to calculate performance weights: {e}")
            return {name: 1.0 for name in performance_metrics}


class MarketRegimeEnsemble:
    """
    Specialized ensemble for market regime detection

    Combines:
    - K-Means clustering (geometric patterns)
    - Random Forest (feature importance)
    - Time series analysis (momentum/trend)
    """

    def __init__(self):
        self.ensemble = EnsemblePredictor(ensemble_type="voting")
        self.performance_history: dict[str, list[float]] = {}

    def predict_regime(
        self,
        symbol: str,
        lookback_days: int = 90,
    ) -> dict[str, Any]:
        """
        Predict market regime using ensemble

        Args:
            symbol: Stock symbol
            lookback_days: Days of historical data

        Returns:
            Ensemble regime prediction with confidence
        """
        try:
            from .regime_detector import get_regime_detector
            from .strategy_selector import get_strategy_selector

            # Add base models to ensemble
            regime_detector = get_regime_detector()
            strategy_selector = get_strategy_selector()

            self.ensemble.add_model("regime_detector", regime_detector, weight=1.5)
            self.ensemble.add_model("strategy_selector", strategy_selector, weight=1.0)

            # Get ensemble prediction
            features = {"symbol": symbol, "lookback_days": lookback_days}
            result = self.ensemble.predict_classification(features, method="soft")

            logger.info(
                f"Ensemble regime prediction for {symbol}: {result['prediction']} "
                f"(confidence: {result['confidence']:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"Ensemble regime prediction failed: {e}")
            raise


# Singleton instances
_ensemble_predictor = None
_regime_ensemble = None


def get_ensemble_predictor() -> EnsemblePredictor:
    """Get or create ensemble predictor instance"""
    global _ensemble_predictor
    if _ensemble_predictor is None:
        _ensemble_predictor = EnsemblePredictor()
    return _ensemble_predictor


def get_regime_ensemble() -> MarketRegimeEnsemble:
    """Get or create market regime ensemble instance"""
    global _regime_ensemble
    if _regime_ensemble is None:
        _regime_ensemble = MarketRegimeEnsemble()
    return _regime_ensemble

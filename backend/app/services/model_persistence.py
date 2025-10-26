"""
Model Persistence Service
Handles saving/loading trained ML models to/from disk
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib


logger = logging.getLogger(__name__)

# Model storage directory
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)


class ModelPersistence:
    """Service for persisting ML models to disk"""

    def __init__(self):
        self.model_dir = MODEL_DIR
        logger.info(f"Model persistence initialized: {self.model_dir.absolute()}")

    def save_model(
        self,
        model: Any,
        model_id: str,
        version: str = "1.0.0",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Save a trained model to disk

        Args:
            model: Trained model object (scikit-learn, keras, etc.)
            model_id: Unique identifier (e.g., "regime_detector")
            version: Model version string
            metadata: Optional metadata (accuracy, training date, etc.)

        Returns:
            Path to saved model file
        """
        try:
            # Create model-specific directory
            model_path = self.model_dir / model_id
            model_path.mkdir(exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{model_id}_v{version}_{timestamp}.joblib"
            filepath = model_path / filename

            # Prepare model bundle
            model_bundle = {
                "model": model,
                "model_id": model_id,
                "version": version,
                "saved_at": datetime.now().isoformat(),
                "metadata": metadata or {},
            }

            # Save using joblib (better for sklearn models)
            joblib.dump(model_bundle, filepath, compress=3)

            logger.info(f"✅ Model saved: {filepath}")

            # Save metadata separately for quick lookups
            metadata_file = model_path / f"{model_id}_latest_metadata.json"
            import json
            with open(metadata_file, "w") as f:
                json.dump(
                    {
                        "model_id": model_id,
                        "version": version,
                        "latest_file": filename,
                        "saved_at": model_bundle["saved_at"],
                        "metadata": metadata or {},
                    },
                    f,
                    indent=2,
                )

            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to save model {model_id}: {e}")
            raise

    def load_model(self, model_id: str, version: str | None = None) -> dict[str, Any]:
        """
        Load a trained model from disk

        Args:
            model_id: Model identifier
            version: Specific version to load (None = latest)

        Returns:
            Model bundle dict with 'model', 'metadata', etc.
        """
        try:
            model_path = self.model_dir / model_id

            if not model_path.exists():
                raise FileNotFoundError(f"No models found for {model_id}")

            # Load latest by default
            if version is None:
                metadata_file = model_path / f"{model_id}_latest_metadata.json"
                if metadata_file.exists():
                    import json
                    with open(metadata_file) as f:
                        metadata = json.load(f)
                        latest_file = metadata["latest_file"]
                        filepath = model_path / latest_file
                else:
                    # Fallback: find most recent file
                    model_files = sorted(model_path.glob(f"{model_id}_*.joblib"), reverse=True)
                    if not model_files:
                        raise FileNotFoundError(f"No model files found for {model_id}")
                    filepath = model_files[0]
            else:
                # Load specific version
                model_files = list(model_path.glob(f"{model_id}_v{version}_*.joblib"))
                if not model_files:
                    raise FileNotFoundError(f"Model version {version} not found for {model_id}")
                filepath = sorted(model_files, reverse=True)[0]

            # Load model bundle
            model_bundle = joblib.load(filepath)

            logger.info(f"✅ Model loaded: {filepath}")
            return model_bundle

        except Exception as e:
            logger.error(f"Failed to load model {model_id}: {e}")
            raise

    def list_models(self, model_id: str | None = None) -> list[dict[str, Any]]:
        """
        List all saved models

        Args:
            model_id: Filter by specific model ID (None = all models)

        Returns:
            List of model info dicts
        """
        try:
            models = []

            if model_id:
                model_paths = [self.model_dir / model_id] if (self.model_dir / model_id).exists() else []
            else:
                model_paths = [p for p in self.model_dir.iterdir() if p.is_dir()]

            for model_path in model_paths:
                model_files = list(model_path.glob("*.joblib"))
                for filepath in model_files:
                    # Extract info from filename
                    parts = filepath.stem.split("_")
                    models.append(
                        {
                            "model_id": parts[0] if len(parts) > 0 else "unknown",
                            "version": parts[1].replace("v", "") if len(parts) > 1 else "unknown",
                            "timestamp": parts[2] if len(parts) > 2 else "unknown",
                            "filepath": str(filepath),
                            "size_mb": filepath.stat().st_size / (1024 * 1024),
                        }
                    )

            return sorted(models, key=lambda x: x["timestamp"], reverse=True)

        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []

    def delete_old_versions(self, model_id: str, keep_latest: int = 3) -> int:
        """
        Delete old model versions, keeping only the latest N

        Args:
            model_id: Model identifier
            keep_latest: Number of versions to keep

        Returns:
            Number of models deleted
        """
        try:
            model_path = self.model_dir / model_id
            if not model_path.exists():
                return 0

            model_files = sorted(model_path.glob(f"{model_id}_*.joblib"), reverse=True)

            # Keep latest N, delete the rest
            files_to_delete = model_files[keep_latest:]
            for filepath in files_to_delete:
                filepath.unlink()
                logger.info(f"🗑️ Deleted old model: {filepath.name}")

            return len(files_to_delete)

        except Exception as e:
            logger.error(f"Failed to delete old versions: {e}")
            return 0


# Singleton instance
_persistence_service = None


def get_model_persistence() -> ModelPersistence:
    """Get or create model persistence service"""
    global _persistence_service
    if _persistence_service is None:
        _persistence_service = ModelPersistence()
    return _persistence_service

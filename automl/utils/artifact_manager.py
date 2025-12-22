"""
Artifact Manager Module
=======================
Handles persistence and loading of trained models and preprocessing artifacts
following industry standards. Saves models using joblib and metadata as JSON.

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4
from datetime import datetime

import joblib
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_run_id() -> str:
    """Generate a unique run ID combining timestamp and UUID.
    
    Returns
    -------
    str
        Unique run identifier in format: <timestamp>_<uuid>
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid4())[:8]
    return f"{timestamp}_{unique_id}"


def create_artifacts_directory(base_dir: Path = None, run_id: str = None) -> Path:
    """Create artifacts directory structure for model storage.
    
    Creates: artifacts/<run_id>/
    
    Parameters
    ----------
    base_dir : Path, optional
        Base directory for artifacts. Defaults to 'artifacts/' in current working directory.
    run_id : str, optional
        Unique run identifier. If None, a new one is generated.
    
    Returns
    -------
    Path
        Path to the run-specific artifacts directory.
    """
    if base_dir is None:
        base_dir = Path("artifacts")
    
    if run_id is None:
        run_id = generate_run_id()
    
    artifacts_dir = base_dir / run_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Artifacts directory created: {artifacts_dir.resolve()}")
    return artifacts_dir


def save_artifacts(
    run_id: str,
    model: Any,
    preprocessors: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
    feature_metadata: Optional[Dict[str, Any]] = None,
    base_dir: Path = None,
) -> Dict[str, str]:
    """Save trained model and preprocessing artifacts to disk.
    
    Persists:
    - model.pkl: Trained model object
    - preprocessing.pkl: Preprocessor artifacts (scaler, encoders, vectorizer)
    - feature_metadata.json: Feature names and selection info
    - metrics.json: Evaluation metrics and performance data
    
    Parameters
    ----------
    run_id : str
        Unique identifier for this training run.
    model : Any
        Trained model object (sklearn or TensorFlow).
    preprocessors : Dict[str, Any], optional
        Dictionary of preprocessing artifacts:
        - 'scaler': StandardScaler object
        - 'encoders': Dict of fitted encoders
        - 'vectorizer': TfidfVectorizer object
        - 'selected_features': List of selected feature names
        - 'selected_indices': Array of selected feature indices
    metrics : Dict[str, Any], optional
        Evaluation metrics and performance data.
    feature_metadata : Dict[str, Any], optional
        Feature information:
        - 'feature_names': List of all feature names
        - 'feature_count': Number of features
        - 'data_type': Data type (tabular, text, timeseries, image)
        - 'selected_count': Number of selected features (if feature selection applied)
    base_dir : Path, optional
        Base directory for artifacts. Defaults to 'artifacts/'.
    
    Returns
    -------
    Dict[str, str]
        Dictionary with keys:
        - 'artifacts_dir': Path to artifacts directory (relative)
        - 'model_path': Path to saved model (relative)
        - 'preprocessing_path': Path to preprocessing artifacts (relative)
        - 'feature_metadata_path': Path to feature metadata (relative)
        - 'metrics_path': Path to metrics file (relative)
    
    Raises
    ------
    ValueError
        If model is None.
    
    Examples
    --------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> model = RandomForestClassifier().fit(X_train, y_train)
    >>> preprocessors = {'scaler': scaler, 'encoders': encoders}
    >>> metrics = {'accuracy': 0.95, 'precision': 0.93}
    >>> paths = save_artifacts(run_id, model, preprocessors, metrics)
    >>> print(paths['model_path'])
    artifacts/20250222_150330_a1b2c3d4/model.pkl
    """
    if model is None:
        raise ValueError("Model cannot be None")
    
    if base_dir is None:
        base_dir = Path("artifacts")
    
    # Create artifacts directory
    artifacts_dir = create_artifacts_directory(base_dir, run_id)
    
    # Prepare paths
    model_path = artifacts_dir / "model.pkl"
    preprocessing_path = artifacts_dir / "preprocessing.pkl"
    feature_metadata_path = artifacts_dir / "feature_metadata.json"
    metrics_path = artifacts_dir / "metrics.json"
    
    # 1. Save model using joblib
    try:
        joblib.dump(model, model_path, protocol=4)
        logger.info(f"Model persisted at: {model_path}")
    except Exception as e:
        logger.error(f"Failed to save model: {e}")
        raise
    
    # 2. Save preprocessing artifacts using joblib
    if preprocessors:
        try:
            joblib.dump(preprocessors, preprocessing_path, protocol=4)
            logger.info(f"Preprocessing artifacts saved: {preprocessing_path}")
        except Exception as e:
            logger.error(f"Failed to save preprocessors: {e}")
            raise
    
    # 3. Save feature metadata as JSON
    feature_metadata = feature_metadata or {}
    try:
        with open(feature_metadata_path, 'w') as f:
            json.dump(feature_metadata, f, indent=2)
        logger.info(f"Feature metadata saved: {feature_metadata_path}")
    except Exception as e:
        logger.error(f"Failed to save feature metadata: {e}")
        raise
    
    # 4. Save metrics as JSON
    metrics = metrics or {}
    try:
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved: {metrics_path}")
    except Exception as e:
        logger.error(f"Failed to save metrics: {e}")
        raise
    
    logger.info("Artifacts saved successfully")
    
    # Return relative paths for portability
    try:
        artifacts_rel = artifacts_dir.relative_to(Path.cwd())
        model_rel = model_path.relative_to(Path.cwd())
        preprocessing_rel = preprocessing_path.relative_to(Path.cwd())
        feature_metadata_rel = feature_metadata_path.relative_to(Path.cwd())
        metrics_rel = metrics_path.relative_to(Path.cwd())
    except ValueError:
        # If relative_to fails, use absolute paths
        artifacts_rel = artifacts_dir
        model_rel = model_path
        preprocessing_rel = preprocessing_path
        feature_metadata_rel = feature_metadata_path
        metrics_rel = metrics_path
    
    return {
        "artifacts_dir": str(artifacts_rel).replace("\\", "/"),
        "model_path": str(model_rel).replace("\\", "/"),
        "preprocessing_path": str(preprocessing_rel).replace("\\", "/"),
        "feature_metadata_path": str(feature_metadata_rel).replace("\\", "/"),
        "metrics_path": str(metrics_rel).replace("\\", "/"),
    }


def load_artifacts(
    run_id: str,
    base_dir: Path = None,
) -> Dict[str, Any]:
    """Load previously saved model and preprocessing artifacts.
    
    Parameters
    ----------
    run_id : str
        Unique identifier for the training run.
    base_dir : Path, optional
        Base directory where artifacts are stored. Defaults to 'artifacts/'.
    
    Returns
    -------
    Dict[str, Any]
        Dictionary with keys:
        - 'model': Loaded trained model
        - 'preprocessors': Dict of preprocessing artifacts (if available)
        - 'feature_metadata': Feature information (if available)
        - 'metrics': Evaluation metrics (if available)
    
    Raises
    ------
    FileNotFoundError
        If artifact files do not exist.
    
    Examples
    --------
    >>> artifacts = load_artifacts(run_id)
    >>> model = artifacts['model']
    >>> preprocessors = artifacts['preprocessors']
    """
    if base_dir is None:
        base_dir = Path("artifacts")
    
    artifacts_dir = base_dir / run_id
    
    if not artifacts_dir.exists():
        raise FileNotFoundError(f"Artifacts directory not found: {artifacts_dir}")
    
    result = {}
    
    # Load model
    model_path = artifacts_dir / "model.pkl"
    if model_path.exists():
        try:
            result['model'] = joblib.load(model_path)
            logger.info(f"Model loaded from: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    else:
        logger.warning(f"Model file not found: {model_path}")
    
    # Load preprocessing artifacts
    preprocessing_path = artifacts_dir / "preprocessing.pkl"
    if preprocessing_path.exists():
        try:
            result['preprocessors'] = joblib.load(preprocessing_path)
            logger.info(f"Preprocessors loaded from: {preprocessing_path}")
        except Exception as e:
            logger.error(f"Failed to load preprocessors: {e}")
            raise
    
    # Load feature metadata
    feature_metadata_path = artifacts_dir / "feature_metadata.json"
    if feature_metadata_path.exists():
        try:
            with open(feature_metadata_path, 'r') as f:
                result['feature_metadata'] = json.load(f)
            logger.info(f"Feature metadata loaded from: {feature_metadata_path}")
        except Exception as e:
            logger.error(f"Failed to load feature metadata: {e}")
            raise
    
    # Load metrics
    metrics_path = artifacts_dir / "metrics.json"
    if metrics_path.exists():
        try:
            with open(metrics_path, 'r') as f:
                result['metrics'] = json.load(f)
            logger.info(f"Metrics loaded from: {metrics_path}")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            raise
    
    return result


__all__ = [
    "generate_run_id",
    "create_artifacts_directory",
    "save_artifacts",
    "load_artifacts",
]

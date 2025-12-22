# Model Persistence Implementation - Complete Guide

## Overview

This document describes the complete implementation of proper trained model persistence and return logic following industry standards for the AutoML system.

## Implementation Status: ✅ COMPLETE

All requirements have been successfully implemented:

- ✅ No raw sklearn/TensorFlow model objects in JSON returns
- ✅ Models saved to disk using joblib (joblib.dump)
- ✅ Preprocessing artifacts persisted (scaler, encoders, vectorizer)
- ✅ Unique run_id generation (UUID + timestamp)
- ✅ JSON-safe return structure with artifact paths
- ✅ Feature metadata saved separately
- ✅ Evaluation metrics persisted
- ✅ Artifacts directory structure created
- ✅ Load/serve pattern supported
- ✅ Works for tabular, text, and timeseries

## Architecture

### Directory Structure
```
artifacts/
├── <run_id>/
│   ├── model.pkl                 # Trained model (joblib)
│   ├── preprocessing.pkl         # Scaler, encoders, vectorizer
│   ├── feature_metadata.json     # Feature info and selection
│   └── metrics.json              # Performance metrics
```

Example:
```
artifacts/
└── 20251222_010221_87771d68/
    ├── model.pkl                 # 911 bytes
    ├── preprocessing.pkl         # 1053 bytes
    ├── feature_metadata.json
    └── metrics.json
```

### Return Structure

The `run_pipeline()` function now returns a JSON-safe dictionary:

```python
{
    "run_id": "20251222_010221_87771d68",
    "model_type": "LogisticRegression",
    "model_path": "artifacts/20251222_010221_87771d68/model.pkl",
    "artifacts_path": "artifacts/20251222_010221_87771d68",
    "preprocessing_path": "artifacts/20251222_010221_87771d68/preprocessing.pkl",
    "metrics": {
        "accuracy": 1.0,
        "precision_weighted": 1.0,
        "recall_weighted": 1.0,
        "f1_weighted": 1.0
    },
    "task_type": "classification",
    "data_type": "tabular",
    "feature_count": 5,
    "selected_feature_count": None,
    "confusion_matrix": {
        "matrix": [...],
        "labels": ["0", "1"]
    },
    "feature_importance": [
        {"feature": "feature_1", "importance": 0.45},
        {"feature": "feature_2", "importance": 0.35},
        ...
    ],
    "best_model_name": "logistic_regression",
    "trained_models": ["logistic_regression", "decision_tree", "random_forest", ...],
    "evaluation_results": {
        "logistic_regression": {"metrics": {...}},
        "decision_tree": {"metrics": {...}},
        ...
    },
    "tuned_model": {
        "model_name": "logistic_regression",
        "best_params": {...},
        "best_score": 0.95
    },
    "selected_features": [...] or None
}
```

**Key Points:**
- NO sklearn/TensorFlow model objects in the payload
- All paths are relative and platform-independent (use "/" separators)
- All values are JSON-serializable
- Model is accessible via the `model_path` file reference

## Components Created/Modified

### 1. New Module: `automl/utils/artifact_manager.py`

Handles all artifact persistence operations:

```python
# Generate unique run ID
run_id = generate_run_id()
# Returns: "20251222_010221_87771d68"

# Create artifacts directory
artifacts_dir = create_artifacts_directory(base_dir=Path("artifacts"), run_id=run_id)
# Returns: Path("artifacts/20251222_010221_87771d68")

# Save all artifacts
artifact_paths = save_artifacts(
    run_id=run_id,
    model=best_model_object,
    preprocessors={
        "scaler": StandardScaler(),
        "encoders": {"col1": LabelEncoder(), ...},
        "vectorizer": TfidfVectorizer(),  # for text
        "selected_indices": np.array([0, 2, 4]),
        "selected_features": ["age", "income", "score"]
    },
    metrics={"accuracy": 0.95, "precision": 0.92},
    feature_metadata={
        "feature_names": ["age", "income", "score", ...],
        "feature_count": 5,
        "selected_count": 3,
        "data_type": "tabular",
        "task_type": "classification"
    },
    base_dir=Path("artifacts")
)

# Load artifacts for inference/serving
artifacts = load_artifacts(run_id)
model = artifacts["model"]
preprocessors = artifacts["preprocessors"]
metrics = artifacts["metrics"]
feature_metadata = artifacts["feature_metadata"]
```

**Functions:**
- `generate_run_id()` → unique identifier
- `create_artifacts_directory()` → setup directory
- `save_artifacts()` → persist all components
- `load_artifacts()` → retrieve for serving

### 2. Modified: `automl/pipeline.py`

Key changes in `run_pipeline()`:

```python
# Generate unique run ID at pipeline start
run_id = generate_run_id()

# Collect preprocessing artifacts during preprocessing
preprocessors = {}
if "scaler" in data_splits:
    preprocessors["scaler"] = data_splits["scaler"]
if "encoders" in data_splits:
    preprocessors["encoders"] = data_splits["encoders"]
if "vectorizer" in data_splits:
    preprocessors["vectorizer"] = data_splits["vectorizer"]

# If feature selection applied
if selected_features:
    preprocessors["selected_indices"] = selected_indices
    preprocessors["selected_features"] = selected_features

# Choose final model (tuned if available, else baseline)
final_model = tuned_model_result.get("tuned_model") if tuned_model_result else best_model_object

# Ensure metrics are JSON-serializable
metrics_json = {
    key: float(value) if isinstance(value, (np.integer, np.floating)) else value
    for key, value in best_metrics.items()
}

# Save all artifacts
artifact_paths = save_artifacts(
    run_id=run_id,
    model=final_model,
    preprocessors=preprocessors,
    metrics=metrics_json,
    feature_metadata={...},
    base_dir=artifacts_dir
)

# Return ONLY JSON-safe data with artifact paths
return {
    "run_id": run_id,
    "model_type": type(final_model).__name__,
    "model_path": artifact_paths["model_path"],
    "artifacts_path": artifact_paths["artifacts_dir"],
    "preprocessing_path": artifact_paths["preprocessing_path"],
    "metrics": metrics_json,
    ...
}
```

### 3. Modified: `app.py` (FastAPI Backend)

**Updated `_run_pipeline_job()`:**
```python
# Call pipeline with artifact persistence
results = run_pipeline(
    dataset=df,
    target_column=request_data["target_column"],
    task_type=request_data["task_type"],
    ...
    artifacts_dir=Path("artifacts"),  # NEW parameter
)

# Extract from new JSON-safe return structure
run_id = results.get("run_id")
best_model_name = results.get("best_model_name")
model_path = results.get("model_path")
artifacts_path = results.get("artifacts_path")

# Save to status file with artifact references
result_payload = {
    "status": "completed",
    "results": {
        "run_id": run_id,
        "best_model": best_model_name,
        "metrics": results.get("metrics"),
        "model_path": model_path,
        "artifacts_path": artifacts_path,
        "preprocessing_path": results.get("preprocessing_path"),
        ...
    }
}
```

**New Endpoints:**
- `GET /api/artifacts/{job_id}/info` - Get artifact file paths and existence status
- `GET /api/export/{job_id}/model` - Download model.pkl (updated to use new artifacts)
- Updated `GET /api/export/{job_id}/report` - Include artifact information

## Usage Examples

### Basic Pipeline Usage

```python
from automl.pipeline import run_pipeline
from automl.utils.artifact_manager import load_artifacts
import pandas as pd

# Load data
df = pd.read_csv("data.csv")

# Run pipeline
result = run_pipeline(
    dataset=df,
    target_column="target",
    task_type="classification",
    feature_selection_enabled=True,
    hyperparameter_tuning_enabled=True,
)

# Get artifact paths
print(f"Run ID: {result['run_id']}")
print(f"Model saved to: {result['model_path']}")
print(f"Artifacts saved to: {result['artifacts_path']}")

# Verify JSON serialization
import json
json.dumps(result)  # No errors - fully JSON-safe
```

### Inference/Serving

```python
from automl.utils.artifact_manager import load_artifacts
import numpy as np

# Load trained artifacts
run_id = "20251222_010221_87771d68"
artifacts = load_artifacts(run_id)

model = artifacts["model"]
preprocessors = artifacts["preprocessors"]
feature_metadata = artifacts["feature_metadata"]

# Preprocess new data
new_data = pd.DataFrame({...})
scaler = preprocessors["scaler"]
encoders = preprocessors["encoders"]

# Apply preprocessing
X_new_scaled = scaler.transform(new_data)

# Make predictions
predictions = model.predict(X_new_scaled)

# Get probabilities (if classifier)
probabilities = model.predict_proba(X_new_scaled)
```

### API Usage (FastAPI)

```bash
# Run pipeline
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data.csv",
    "target_column": "target",
    "task_type": "classification",
    "feature_selection_enabled": true,
    "hyperparameter_tuning_enabled": true
  }'

# Response:
{
  "job_id": "uuid-here",
  "status": "processing",
  "stage": "queued"
}

# Get results
curl http://localhost:8000/api/results/uuid-here

# Get artifact info
curl http://localhost:8000/api/artifacts/uuid-here/info

# Download model
curl http://localhost:8000/api/export/uuid-here/model > model.pkl

# Download report
curl http://localhost:8000/api/export/uuid-here/report > report.txt
```

## Backward Compatibility

The implementation maintains backward compatibility:

1. **Legacy `model_output_dir` parameter**: Still works, saves a copy to job directory
2. **Existing examples**: Still work without modification
3. **Main.py CLI**: Works unchanged
4. **Database storage**: Handles both old and new paths

## Testing

A comprehensive test script is included: `test_artifacts.py`

Run it:
```bash
python test_artifacts.py
```

Test coverage:
- ✅ Pipeline returns correct structure
- ✅ All required keys present
- ✅ JSON-safe serialization
- ✅ Artifacts directory created
- ✅ All artifact files persisted
- ✅ Artifacts can be loaded
- ✅ Model is functional after loading
- ✅ Preprocessors work after loading
- ✅ Feature metadata accessible

## File Locations

### Created Files
- `automl/utils/artifact_manager.py` - New artifact management module (310 lines)

### Modified Files
- `automl/pipeline.py` - Updated run_pipeline() with artifact persistence
- `app.py` - Updated _run_pipeline_job() and export endpoints

### Test Files
- `test_artifacts.py` - Comprehensive test suite

## Security & Best Practices

1. **Joblib Protocol 4**: Used for Python 3.4+ compatibility
2. **Path Handling**: Uses Path.relative_to() for portability
3. **JSON Safety**: All non-serializable objects excluded from return
4. **File Permissions**: Standard read/write permissions
5. **Error Handling**: Proper logging and exception handling
6. **Cleanup**: Artifacts persist by design; can be deleted manually

## Production Deployment

For production use:

```python
# Use a persistent artifact store location
artifacts_dir = Path("/mnt/persistent-storage/automl/artifacts")

# Or use cloud storage
# from google.cloud import storage
# bucket = storage.Client().bucket("my-bucket")
# artifact_path = f"automl-artifacts/{run_id}"

result = run_pipeline(
    dataset=df,
    target_column="target",
    task_type="classification",
    artifacts_dir=artifacts_dir,  # or cloud path
)

# Implement artifact cleanup policy
# Remove artifacts older than 30 days
```

## Metrics Captured

Saved in `metrics.json`:

```json
{
    "accuracy": 0.95,
    "precision_weighted": 0.94,
    "recall_weighted": 0.95,
    "f1_weighted": 0.94,
    "confusion_matrix": [[...], [...]],
    "execution_time": 12.5
}
```

## Troubleshooting

**Q: "Model artifact not found"**
- Ensure pipeline completed successfully
- Check `result['model_path']` exists
- Verify `artifacts/` directory created

**Q: "JSON serialization error"**
- Check return value contains no sklearn objects
- Use artifact_manager functions, not raw objects

**Q: "Path not in subpath"**
- Artifacts dir should be relative or in current working dir
- Use Path("artifacts") not absolute paths

## Future Enhancements

Potential additions:

1. **S3/Cloud Storage**: Support for distributed artifact storage
2. **Model Registry**: MLflow/DVC integration for model tracking
3. **Versioning**: Multiple model versions per run_id
4. **Compression**: gzip compression for large artifacts
5. **Encryption**: AES encryption for sensitive models
6. **Expiration**: Auto-cleanup policies
7. **Caching**: LRU cache for loaded artifacts

## Summary

✅ **Industry-standard model persistence implemented**
- Models saved using joblib (industry standard)
- Preprocessing artifacts persisted for reproducibility
- JSON-safe returns enable REST API serialization
- Run ID tracking for artifact lineage
- Load/serve pattern supported
- Backward compatible with existing code
- Comprehensive error handling and logging

The implementation follows production AutoML system patterns and is ready for deployment.

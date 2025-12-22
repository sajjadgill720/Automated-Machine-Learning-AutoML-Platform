"""FastAPI Backend for AutoML System.

This API exposes the AutoML pipeline to web clients (React UI).
Endpoints:
  - POST /api/upload: Upload CSV dataset
  - POST /api/run: Run AutoML pipeline
  - GET /api/results/{job_id}: Get results for a job
  - GET /api/health: Health check

Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8000
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from threading import Thread
import io

import pandas as pd
import joblib
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from automl.pipeline import run_pipeline
from automl.utils.sampling import sample_dataset


# FastAPI app
app = FastAPI(
    title="AutoML System API",
    description="REST API for automated machine learning pipeline",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage paths
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results_api")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


def _sanitize_tuned_model(tuned_model: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Strip non-serializable objects from tuned_model payload."""

    if tuned_model is None:
        return None

    tuned_estimator = tuned_model.get("tuned_model") if isinstance(tuned_model, dict) else None
    model_name = type(tuned_estimator).__name__ if tuned_estimator is not None else None

    return {
        "model_name": model_name,
        "best_params": tuned_model.get("best_params") if isinstance(tuned_model, dict) else None,
        "best_score": tuned_model.get("best_score") if isinstance(tuned_model, dict) else None,
    }


def _safe_list(value: Any) -> Optional[list]:
    """Convert array-like to list for JSON serialization."""

    if value is None:
        return None
    try:
        return list(value)
    except Exception:
        return None


# Request models
class RunPipelineRequest(BaseModel):
    """Request model for running AutoML pipeline."""
    filename: str
    target_column: str
    task_type: str = "classification"  # "classification" or "regression"
    feature_selection_enabled: bool = True
    hyperparameter_tuning_enabled: bool = True
    search_method: str = "grid"  # "grid", "random", "bayesian"
    data_type_override: Optional[str] = None  # "tabular", "text", "timeseries", "image"
    max_sample_rows: int = 10000  # Maximum rows to process; set to 0 to disable sampling


class PipelineResult(BaseModel):
    """Response model for pipeline results."""
    job_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[int] = None
    best_model: Optional[str] = None
    metrics: Optional[dict] = None
    selected_features: Optional[list] = None
    trained_models: Optional[list] = None
    error: Optional[str] = None


# Health check
@app.get("/api/health")
def health_check():
    """Check if API is running."""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


# Upload CSV
@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload a CSV dataset.
    
    Returns:
        dict: Contains filename, size, columns, and row count
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    # Save file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Read and validate
    try:
        df = pd.read_csv(file_path)
        return {
            "filename": file.filename,
            "size_bytes": len(content),
            "rows": len(df),
            "columns": list(df.columns),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {str(e)}")


# Run pipeline
@app.post("/api/run", response_model=PipelineResult)
def run_automl_pipeline(request: RunPipelineRequest):
    """Run the AutoML pipeline asynchronously and return a job id."""

    job_id = str(uuid.uuid4())
    csv_path = UPLOAD_DIR / request.filename

    # Validate file exists before queuing
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")

    request_data = request.dict()

    # Kick off background job
    thread = Thread(target=_run_pipeline_job, args=(job_id, request_data), daemon=True)
    thread.start()

    # Initial response indicates processing
    return PipelineResult(
        job_id=job_id,
        status="processing",
        stage="queued",
        progress=0,
    )


def _write_status(job_id: str, payload: Dict[str, Any]) -> None:
    """Persist job status/result to disk in a JSON-safe way."""

    payload_with_meta = {"job_id": job_id, **payload}
    payload_with_meta.setdefault("timestamp", datetime.now().isoformat())
    result_path = RESULTS_DIR / f"{job_id}.json"
    with open(result_path, "w") as f:
        json.dump(payload_with_meta, f, indent=2)


def _run_pipeline_job(job_id: str, request_data: Dict[str, Any]) -> None:
    """Execute pipeline work in background and stream progress to status file."""

    csv_path = UPLOAD_DIR / request_data["filename"]

    # Initial status
    _write_status(job_id, {
        "status": "processing",
        "stage": "queued",
        "progress": 0,
        "request": request_data,
    })

    try:
        if not csv_path.exists():
            raise FileNotFoundError(f"File not found: {request_data['filename']}")

        _write_status(job_id, {
            "status": "processing",
            "stage": "loading_dataset",
            "progress": 5,
            "request": request_data,
        })

        df = pd.read_csv(csv_path)

        if request_data["target_column"] not in df.columns:
            raise ValueError(
                f"Target column '{request_data['target_column']}' not found. Available: {list(df.columns)}"
            )

        # Apply sampling if enabled
        max_sample_rows = request_data.get("max_sample_rows", 10000)
        original_rows = len(df)
        
        if max_sample_rows > 0 and original_rows > max_sample_rows:
            _write_status(job_id, {
                "status": "processing",
                "stage": "sampling_dataset",
                "progress": 10,
                "request": request_data,
                "message": f"Sampling {original_rows} rows down to {max_sample_rows}"
            })
            
            df = sample_dataset(
                df=df,
                target_col=request_data["target_column"],
                max_rows=max_sample_rows,
                task_type=request_data["task_type"],
            )
            print(f"Sampled dataset from {original_rows} to {len(df)} rows")
        elif max_sample_rows <= 0:
            print(f"Sampling disabled - processing all {original_rows} rows")
        else:
            print(f"Dataset size ({original_rows} rows) within limit - no sampling needed")

        preprocessing_params: Dict[str, Any] = {}
        if request_data.get("data_type_override"):
            preprocessing_params["data_type_override"] = request_data["data_type_override"]

        hyperparameter_params: Dict[str, Any] = {"search_method": request_data.get("search_method", "grid")}

        _write_status(job_id, {
            "status": "processing",
            "stage": "running_pipeline",
            "progress": 25,
            "request": request_data,
        })

        # Create job output directory (for backward compatibility)
        job_output_dir = RESULTS_DIR / job_id
        job_output_dir.mkdir(parents=True, exist_ok=True)

        # Use artifacts directory for persistent model storage
        artifacts_dir = Path("artifacts")

        results = run_pipeline(
            dataset=df,
            target_column=request_data["target_column"],
            task_type=request_data["task_type"],
            feature_selection_enabled=request_data.get("feature_selection_enabled", True),
            hyperparameter_tuning_enabled=request_data.get("hyperparameter_tuning_enabled", True),
            preprocessing_params=preprocessing_params,
            hyperparameter_params=hyperparameter_params,
            job_id=job_id,
            model_output_dir=job_output_dir,
            artifacts_dir=artifacts_dir,
        )

        # Extract data from new return structure (JSON-safe)
        run_id = results.get("run_id")
        best_model_name = results.get("best_model_name")
        best_metrics = results.get("metrics", {})
        trained_models_list = results.get("trained_models", [])
        selected_features = results.get("selected_features")
        evaluation_results = results.get("evaluation_results", {})
        tuned_result = results.get("tuned_model")
        
        # Construct result payload with artifact paths
        result_payload = {
            "status": "completed",
            "stage": "completed",
            "progress": 100,
            "request": request_data,
            "results": {
                "run_id": run_id,
                "best_model": best_model_name,
                "metrics": best_metrics,
                "selected_features": selected_features,
                "trained_models": trained_models_list,
                "tuned_model": tuned_result,
                "confusion_matrix": results.get("confusion_matrix"),
                "feature_importance": results.get("feature_importance"),
                "evaluation_results": evaluation_results,
                "model_path": results.get("model_path"),
                "artifacts_path": results.get("artifacts_path"),
                "preprocessing_path": results.get("preprocessing_path"),
                "data_type": results.get("data_type"),
                "feature_count": results.get("feature_count"),
                "selected_feature_count": results.get("selected_feature_count"),
            },
        }

        _write_status(job_id, result_payload)

    except Exception as e:
        _write_status(job_id, {
            "status": "error",
            "stage": "failed",
            "progress": 100,
            "error": str(e),
            "request": request_data,
        })


# Get job status (compatible with frontend polling)
@app.get("/api/status/{job_id}", response_model=PipelineResult)
def get_status(job_id: str):
    """Return job status; uses saved result file if present."""

    result_path = RESULTS_DIR / f"{job_id}.json"

    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    with open(result_path, "r") as f:
        data = json.load(f)

    status = data.get("status", "completed" if data.get("results") else "processing")
    stage = data.get("stage")
    progress = data.get("progress")

    if status == "error":
        return PipelineResult(
            job_id=job_id,
            status="error",
            stage=stage,
            progress=progress,
            error=data.get("error")
        )

    results_data = data.get("results", {})
    return PipelineResult(
        job_id=job_id,
        status=status,
        stage=stage,
        progress=progress,
        best_model=results_data.get("best_model"),
        metrics=results_data.get("metrics"),
        selected_features=results_data.get("selected_features"),
        trained_models=results_data.get("trained_models"),
    )


# Get results
@app.get("/api/results/{job_id}", response_model=PipelineResult)
def get_results(job_id: str):
    """Retrieve results for a completed job.
    
    Args:
        job_id: Unique job identifier
        
    Returns:
        PipelineResult: Job results or error
    """
    result_path = RESULTS_DIR / f"{job_id}.json"
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    if data.get("status") == "error":
        return PipelineResult(
            job_id=job_id,
            status="error",
            stage=data.get("stage"),
            progress=data.get("progress"),
            error=data.get("error")
        )
    
    results_data = data.get("results", {})
    return PipelineResult(
        job_id=job_id,
        status="completed",
        stage=data.get("stage"),
        progress=data.get("progress"),
        best_model=results_data.get("best_model"),
        metrics=results_data.get("metrics"),
        selected_features=results_data.get("selected_features"),
        trained_models=results_data.get("trained_models")
    )


# Export endpoints
@app.get("/api/export/{job_id}/json")
def export_json(job_id: str):
    """Export job results as JSON."""
    result_path = RESULTS_DIR / f"{job_id}.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=automl-{job_id}.json"}
    )


@app.get("/api/export/{job_id}/csv")
def export_csv(job_id: str):
    """Export metrics comparison as CSV."""
    result_path = RESULTS_DIR / f"{job_id}.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    # Extract evaluation results
    results = data.get("results", {})
    evaluation_results = results.get("evaluation_results", {})
    
    # Build metrics table
    metrics_data = []
    for model_name, result in evaluation_results.items():
        row = {"model": model_name}
        row.update(result.get("metrics", {}))
        metrics_data.append(row)
    
    if not metrics_data:
        raise HTTPException(status_code=404, detail="No evaluation metrics found")
    
    df = pd.DataFrame(metrics_data)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    return Response(
        content=csv_buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=automl-metrics-{job_id}.csv"}
    )


@app.get("/api/export/{job_id}/model")
def export_model(job_id: str):
    """Download trained model artifact.
    
    First attempts to load from new artifacts structure (run_id),
    then falls back to legacy location for backward compatibility.
    """
    result_path = RESULTS_DIR / f"{job_id}.json"
    
    if not result_path.exists():
        raise HTTPException(status_code=404, detail="Job not found")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    results = data.get("results", {})
    
    # Try new artifacts structure first
    model_path_str = results.get("model_path")
    if model_path_str:
        model_path = Path(model_path_str)
        if model_path.exists():
            def iter_file():
                with open(model_path, "rb") as f:
                    yield from f
            
            return StreamingResponse(
                iter_file(),
                media_type="application/octet-stream",
                headers={"Content-Disposition": f"attachment; filename=automl-model-{job_id}.pkl"}
            )
    
    # Fall back to legacy location
    job_dir = RESULTS_DIR / job_id
    legacy_model_path = job_dir / "best_model.pkl"
    
    if legacy_model_path.exists():
        def iter_file():
            with open(legacy_model_path, "rb") as f:
                yield from f
        
        return StreamingResponse(
            iter_file(),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename=automl-model-{job_id}.pkl"}
        )
    
    raise HTTPException(status_code=404, detail="Model artifact not found")


@app.get("/api/export/{job_id}/report")
def export_report(job_id: str):
    """Generate and download a text report with artifact information."""
    result_path = RESULTS_DIR / f"{job_id}.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    results = data.get("results", {})
    
    # Generate report with artifact information
    report_content = f"""AutoML Report
================
Job ID: {job_id}
Run ID: {results.get('run_id', 'N/A')}
Timestamp: {data.get('timestamp', 'N/A')}

Configuration:
--------------
Dataset: {data.get('request', {}).get('filename', 'N/A')}
Task Type: {data.get('request', {}).get('task_type', 'N/A')}
Target Column: {data.get('request', {}).get('target_column', 'N/A')}
Data Type: {results.get('data_type', 'N/A')}
Feature Selection: {data.get('request', {}).get('feature_selection_enabled', False)}
Hyperparameter Tuning: {data.get('request', {}).get('hyperparameter_tuning_enabled', False)}

Artifacts:
----------
Model Path: {results.get('model_path', 'N/A')}
Artifacts Directory: {results.get('artifacts_path', 'N/A')}
Preprocessing Artifacts: {results.get('preprocessing_path', 'N/A')}

Feature Information:
--------------------
Total Features: {results.get('feature_count', 'N/A')}
Selected Features: {results.get('selected_feature_count', 'N/A')}
Selected Feature Names: {', '.join(results.get('selected_features', [])[:10])}{'...' if len(results.get('selected_features', [])) > 10 else ''}

Results:
--------
Best Model: {results.get('best_model', 'N/A')}
Trained Models: {', '.join(results.get('trained_models', []))}
Metrics: {json.dumps(results.get('metrics', {}), indent=2)}

Tuned Model:
{json.dumps(results.get('tuned_model', {}), indent=2) if results.get('tuned_model') else 'Not applied'}

This report contains references to persisted model artifacts following industry standards.
All model objects and preprocessing transformers are stored on disk using joblib.
Load artifacts with: from automl.utils.artifact_manager import load_artifacts
"""
    
    return Response(
        content=report_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=automl-report-{job_id}.txt"}
    )


@app.get("/api/artifacts/{job_id}/info")
def get_artifacts_info(job_id: str):
    """Get information about saved artifacts for a job."""
    result_path = RESULTS_DIR / f"{job_id}.json"
    if not result_path.exists():
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
    
    with open(result_path, "r") as f:
        data = json.load(f)
    
    results = data.get("results", {})
    
    # Verify artifact files actually exist
    artifacts_info = {
        "run_id": results.get("run_id"),
        "artifacts_path": results.get("artifacts_path"),
        "model_path": results.get("model_path"),
        "preprocessing_path": results.get("preprocessing_path"),
    }
    
    # Check if files exist
    for key in ["model_path", "preprocessing_path"]:
        path_str = results.get(key)
        if path_str:
            exists = Path(path_str).exists()
            artifacts_info[f"{key}_exists"] = exists
    
    return artifacts_info


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

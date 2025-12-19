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
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from automl.pipeline import run_pipeline


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


class PipelineResult(BaseModel):
    """Response model for pipeline results."""
    job_id: str
    status: str
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
    """Run the AutoML pipeline on uploaded dataset.
    
    Args:
        request: Pipeline configuration
        
    Returns:
        PipelineResult: Job ID and initial status (processing starts async)
    """
    job_id = str(uuid.uuid4())
    csv_path = UPLOAD_DIR / request.filename
    
    # Validate file exists
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"File not found: {request.filename}")
    
    try:
        # Load dataset
        df = pd.read_csv(csv_path)
        
        # Validate target column
        if request.target_column not in df.columns:
            raise HTTPException(
                status_code=400,
                detail=f"Target column '{request.target_column}' not found. Available: {list(df.columns)}"
            )
        
        # Run pipeline
        preprocessing_params = {}
        if request.data_type_override:
            preprocessing_params["data_type_override"] = request.data_type_override
            
        hyperparameter_params = {"search_method": request.search_method}
        
        results = run_pipeline(
            dataset=df,
            target_column=request.target_column,
            task_type=request.task_type,
            feature_selection_enabled=request.feature_selection_enabled,
            hyperparameter_tuning_enabled=request.hyperparameter_tuning_enabled,
            preprocessing_params=preprocessing_params,
            hyperparameter_params=hyperparameter_params,
        )
        
        # Extract summary
        best_model_name = results["best_model"]["name"]
        evaluation_results = results["evaluation_results"]
        best_metrics = evaluation_results[best_model_name].get("metrics", {})
        
        # Save results
        result_path = RESULTS_DIR / f"{job_id}.json"
        with open(result_path, "w") as f:
            json.dump({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "request": request.dict(),
                "results": {
                    "best_model": best_model_name,
                    "metrics": best_metrics,
                    "selected_features": results.get("selected_features"),
                    "trained_models": list(results["trained_models"].keys()),
                    "tuned_model": results.get("tuned_model")
                }
            }, f, indent=2)
        
        return PipelineResult(
            job_id=job_id,
            status="completed",
            best_model=best_model_name,
            metrics=best_metrics,
            selected_features=results.get("selected_features"),
            trained_models=list(results["trained_models"].keys())
        )
        
    except Exception as e:
        # Save error
        result_path = RESULTS_DIR / f"{job_id}.json"
        with open(result_path, "w") as f:
            json.dump({
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }, f, indent=2)
        
        return PipelineResult(
            job_id=job_id,
            status="error",
            error=str(e)
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
            error=data.get("error")
        )
    
    results_data = data.get("results", {})
    return PipelineResult(
        job_id=job_id,
        status="completed",
        best_model=results_data.get("best_model"),
        metrics=results_data.get("metrics"),
        selected_features=results_data.get("selected_features"),
        trained_models=results_data.get("trained_models")
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

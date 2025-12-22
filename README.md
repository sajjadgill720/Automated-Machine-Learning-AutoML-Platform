# AutoML System - Complete Documentation

Professional automated machine learning platform with comprehensive model persistence, REST API, and modern web UI.

## 📋 Quick Links

- **Quick Start**: See [Getting Started](#getting-started) below
- **API Documentation**: See [API Reference](#api-reference)
- **Architecture**: See [Architecture](#architecture)
- **Deployment**: See [Deployment Guide](#deployment-guide)
- **Feature Documentation**: See [Features](#features)

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- pip, npm
- Git (for cloning)

### System Requirements
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space
- **OS**: Windows, macOS, Linux

### Dependencies & Installation

**All dependencies are listed in [requirements.txt](requirements.txt)**

Core packages (auto-installed):
- **scikit-learn** 1.3.2 - Machine learning models
- **pandas** 2.0.3 - Data manipulation
- **numpy** 1.24.3 - Numerical computing
- **FastAPI** 0.104.1 - REST API framework
- **joblib** 1.3.2 - Model persistence
- **optuna** 3.13.0 - Hyperparameter optimization

Optional packages:
- **TensorFlow** 2.13.0 - Deep learning (images, advanced)
- **PyTorch** 2.0.1 - Neural networks
- **OpenCV** 4.8.0.76 - Image processing
- **NLTK** 3.8.1 - NLP utilities

Full installation includes dev/testing tools (pytest, black, mypy, etc.)

### Backend Setup (5 minutes)

```bash
# 1. Navigate to project root
cd AutoML_System

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend runs at: **http://localhost:8000**

### Frontend Setup (5 minutes)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

Frontend runs at: **http://localhost:5173**

### Run CLI Examples

```bash
# Run with built-in Iris dataset
python main.py --builtin iris --task classification

# Run with custom CSV
python main.py --dataset data.csv --target target_col --task classification

# Enable hyperparameter tuning
python main.py --builtin breast_cancer --no-tuning=false --search-method bayesian

# Save results
python main.py --builtin iris --save results.json
```

---

## Features

### Data Type Support
- ✅ **Tabular Data** - CSV with numeric/categorical features
- ✅ **Text Data** - NLP with TF-IDF vectorization
- ✅ **Time Series** - Temporal data with lag features
- ✅ **Image Data** - CNN preprocessing (224x224)

### Model Selection
Automatically trains and selects from:
- Logistic Regression / Linear Regression
- Decision Trees
- Random Forests
- Gradient Boosting
- SVM
- KNN
- Naive Bayes (text)
- Neural Networks (optional)

### Preprocessing
- Automatic numeric/categorical detection
- Missing value imputation (mean/mode)
- Categorical encoding (one-hot, label)
- Feature scaling (StandardScaler)
- TF-IDF vectorization (text)
- Lag feature generation (time series)

### Feature Selection
- Correlation analysis
- Mutual information scoring
- Combined selection methods
- Applied to train/val/test

### Model Tuning
Search methods:
- Grid Search (exhaustive)
- Random Search (efficient)
- Bayesian Optimization (smart)

Parameters auto-selected per model type

### Evaluation
Comprehensive metrics:
- **Classification**: Accuracy, Precision, Recall, F1, AUC-ROC
- **Regression**: R², MSE, RMSE, MAE
- Confusion matrices (classification)
- Feature importance (tree-based)

### Data Sampling
- Stratified sampling for classification
- Preserves class distribution
- Optional max row limit (configurable)

### Model Persistence ⭐ NEW
- **Artifact Storage**: Models saved to disk using joblib
- **Run Tracking**: Unique run_id per pipeline execution
- **Preprocessing Artifacts**: Scalers, encoders, vectorizers saved
- **JSON-Safe Returns**: No raw model objects in API responses
- **Feature Metadata**: Feature names and selection info persisted
- **Load/Serve Pattern**: Load artifacts for inference

See [Artifact Persistence Guide](readme/ARTIFACT_PERSISTENCE_IMPLEMENTATION.md)

---

## Project Structure

```
AutoML_System/
├── automl/                          # Core ML package
│   ├── pipeline.py                  # Main orchestrator
│   ├── preprocessing.py             # Data dispatcher
│   ├── tabular_preprocessing.py     # Tabular handling
│   ├── text_preprocessing.py        # Text handling
│   ├── timeseries_preprocessing.py  # Time series
│   ├── Image_preprocessing.py       # Image handling
│   ├── feature_selection.py         # Feature selection
│   ├── model_trainer.py             # Model training
│   ├── model_selector.py            # Model selection
│   ├── evaluator.py                 # Evaluation
│   ├── hyperparameter_tuner.py      # HPO
│   └── utils/
│       ├── sampling.py              # Data sampling
│       └── artifact_manager.py       # Model persistence ⭐ NEW
│
├── frontend/                        # React/TypeScript UI
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── pages/                   # Page layouts
│   │   ├── api/                     # API client
│   │   ├── types/                   # TypeScript types
│   │   └── App.tsx                  # Main app
│   ├── package.json
│   └── vite.config.js
│
├── app.py                           # FastAPI backend
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── artifacts/                       # Saved models (auto-created)
├── uploads/                         # Uploaded CSVs
├── results_api/                     # Job results (JSON)
└── readme/                          # Documentation
```

---

## API Reference

### Core Endpoints

#### Health Check
```http
GET /api/health

Response:
{
  "status": "ok",
  "timestamp": "2025-12-22T10:30:00"
}
```

#### Upload Dataset
```http
POST /api/upload
Content-Type: multipart/form-data

Request:
- file: CSV file

Response:
{
  "filename": "data.csv",
  "rows": 1000,
  "columns": ["age", "income", "target"],
  "dtypes": {"age": "int64", "income": "float64", ...}
}
```

#### Run Pipeline
```http
POST /api/run
Content-Type: application/json

Request:
{
  "filename": "data.csv",
  "target_column": "target",
  "task_type": "classification",
  "feature_selection_enabled": true,
  "hyperparameter_tuning_enabled": true,
  "search_method": "grid",
  "max_sample_rows": 10000
}

Response:
{
  "job_id": "uuid-xxx",
  "status": "processing",
  "stage": "queued"
}
```

#### Get Status
```http
GET /api/status/{job_id}

Response:
{
  "job_id": "uuid-xxx",
  "status": "completed",
  "progress": 100,
  "results": {
    "run_id": "20251222_010221_87771d68",
    "best_model": "logistic_regression",
    "metrics": {...},
    "model_path": "artifacts/.../model.pkl",
    "artifacts_path": "artifacts/..."
  }
}
```

#### Get Full Results
```http
GET /api/results/{job_id}
```

#### Export Model
```http
GET /api/export/{job_id}/model

Downloads: model.pkl (binary file)
```

#### Export Report
```http
GET /api/export/{job_id}/report

Downloads: report.txt with artifact paths
```

#### Get Artifact Info
```http
GET /api/artifacts/{job_id}/info

Response:
{
  "run_id": "20251222_010221_87771d68",
  "artifacts_path": "artifacts/...",
  "model_path": "artifacts/.../model.pkl",
  "preprocessing_path": "artifacts/.../preprocessing.pkl",
  "model_path_exists": true,
  "preprocessing_path_exists": true
}
```

See full API docs at: http://localhost:8000/docs

---

## Architecture

### Data Flow

```
User Input
    ↓
[Upload CSV] → Validate Format
    ↓
[Data Preprocessing]
    ├→ Detect Data Type (tabular/text/timeseries/image)
    ├→ Handle Missing Values
    ├→ Encode Categorical Features
    ├→ Scale Numeric Features
    └→ Split Train/Val/Test
    ↓
[Optional Feature Selection]
    ├→ Correlation Analysis
    ├→ Mutual Information
    └→ Apply to All Splits
    ↓
[Baseline Model Training]
    ├→ Train Multiple Models
    ├→ Evaluate on Test Set
    ├→ Compare Metrics
    └→ Select Best
    ↓
[Optional Hyperparameter Tuning]
    ├→ Grid/Random/Bayesian Search
    ├→ Cross-Validation
    └→ Return Tuned Model
    ↓
[Artifact Persistence] ⭐ NEW
    ├→ Generate run_id
    ├→ Save Model (joblib)
    ├→ Save Preprocessors
    ├→ Save Feature Metadata
    └→ Save Metrics (JSON)
    ↓
[Return Results]
    └→ JSON with artifact paths (NO model objects)
    ↓
[Visualization]
    └→ Display Metrics, Features, Confusion Matrix
```

### Model Persistence Architecture

```
Pipeline Execution
    ↓
[Collect Artifacts]
    ├→ Trained Model
    ├→ Scaler/Encoders
    ├→ Vectorizer (text)
    ├→ Feature Selection Info
    └→ Evaluation Metrics
    ↓
[Save to Disk]
    artifacts/
    └── 20251222_010221_87771d68/
        ├── model.pkl (joblib)
        ├── preprocessing.pkl (joblib)
        ├── feature_metadata.json
        └── metrics.json
    ↓
[Return JSON]
    {
        "run_id": "20251222_010221_87771d68",
        "model_path": "artifacts/.../model.pkl",
        "artifacts_path": "artifacts/...",
        ...
    }
    ↓
[Load for Inference]
    artifacts = load_artifacts(run_id)
    model = artifacts['model']
    predictions = model.predict(X_new)
```

See [detailed architecture](readme/ARCHITECTURE_DIAGRAMS.md)

---

## Deployment Guide

### Development Mode
```bash
# Backend
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev
```

### Production Mode

#### Backend
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Or use Docker
docker build -t automl-backend .
docker run -p 8000:8000 automl-backend
```

#### Frontend
```bash
# Build optimized bundle
npm run build

# Serve with Node
npm run preview

# Or use static hosting (AWS S3, Netlify, Vercel)
```

#### Production Artifacts Storage
```python
# Use persistent location
artifacts_dir = Path("/mnt/persistent-storage/artifacts")
# or cloud storage (S3, GCS, etc.)
```

See [deployment guide](readme/DEPLOYMENT.md) for detailed instructions

---

## Configuration

### Backend (.env or environment variables)
```ini
# Server
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Paths
UPLOADS_DIR=uploads
RESULTS_DIR=results_api
ARTIFACTS_DIR=artifacts

# Limits
MAX_SAMPLE_ROWS=10000
MAX_UPLOAD_SIZE=100MB

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend (.env.local)
```ini
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=300000
```

---

## Common Tasks

### Load a Saved Model
```python
from automl.utils.artifact_manager import load_artifacts

# Load artifacts
run_id = "20251222_010221_87771d68"
artifacts = load_artifacts(run_id)

# Use model
model = artifacts["model"]
preprocessors = artifacts["preprocessors"]

# Preprocess new data and predict
X_new = preprocess(new_data, preprocessors)
predictions = model.predict(X_new)
```

### Run Full Pipeline Programmatically
```python
from automl.pipeline import run_pipeline
import pandas as pd

df = pd.read_csv("data.csv")

result = run_pipeline(
    dataset=df,
    target_column="target",
    task_type="classification",
    feature_selection_enabled=True,
    hyperparameter_tuning_enabled=True,
)

# All models and artifacts saved automatically
print(f"Model saved to: {result['model_path']}")
print(f"Run ID: {result['run_id']}")
```

### Use CLI
```bash
# Simple run
python main.py --builtin iris --task classification

# With tuning
python main.py --dataset data.csv --target target --no-tuning=false

# Save results
python main.py --builtin iris --save results.json --save-eval-csv metrics.csv
```

---

## Troubleshooting

### Backend Won't Start
```bash
# Check port 8000 is free
netstat -an | grep 8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Use different port
python -m uvicorn app:app --port 8001
```

### Frontend Won't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/api/health

# Update API URL in frontend
# Edit frontend/.env.local:
VITE_API_BASE_URL=http://localhost:8000/api
```

### Models Not Persisting
```bash
# Check artifacts directory exists
ls artifacts/

# Check file permissions
chmod -R 755 artifacts/

# Verify in job results
curl http://localhost:8000/api/results/{job_id}
# Should show "model_path" and "artifacts_path"
```

### Memory Issues
```bash
# Reduce sample size
max_sample_rows: 1000

# Use smaller models
# Disable feature selection
feature_selection_enabled: false

# Reduce cross-validation folds
hyperparameter_params: {"cv": 3}
```

---

## Performance

### Typical Execution Times
- **Small dataset** (< 1000 rows): 5-15 seconds
- **Medium dataset** (1000-10000 rows): 15-60 seconds
- **Large dataset** (> 10000 rows): 1-5 minutes

### Model Performance Typical Ranges
- **Tabular Classification**: 85-98% accuracy
- **Tabular Regression**: 0.7-0.95 R²
- **Text Classification**: 80-95% accuracy
- **Time Series**: Varies by problem

---

## Testing

Run test suite:
```bash
# Test artifact persistence
python test_artifacts.py

# Test individual modules
python -m pytest automl/ -v

# Test API
pytest tests/test_api.py -v
```

---

## Examples

### Jupyter Notebooks
- [Tabular Data](Notebooks/Demo_tabular.ipynb)
- [Text Data](Notebooks/Demo_text.ipynb)
- [Time Series](Notebooks/Demo_timeseries.ipynb)
- [Image Data](Notebooks/Demo_image.ipynb)
- [Experiments](Notebooks/Experiments.ipynb)

### Python Examples
- [Iris Classification](examples/demo_iris.py)
- [Breast Cancer Classification](examples/demo_breast_cancer.py)
- [Custom Dataset](examples/demo_custom_dataset.py)

---

## Documentation Files

- [Artifact Persistence Guide](readme/ARTIFACT_PERSISTENCE_IMPLEMENTATION.md) - Model persistence details
- [Architecture Diagrams](readme/ARCHITECTURE_DIAGRAMS.md) - System design
- [Deployment Guide](readme/DEPLOYMENT.md) - Production setup
- [API Documentation](http://localhost:8000/docs) - Swagger UI (when running)

---

## Technologies

### Backend
- **FastAPI** - Web framework
- **scikit-learn** - ML algorithms
- **TensorFlow/Keras** - Deep learning (optional)
- **pandas** - Data manipulation
- **joblib** - Model persistence
- **numpy** - Numerical computing

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Recharts** - Visualizations
- **Axios** - HTTP client

### DevOps
- **Docker** - Containerization
- **GitHub** - Version control
- **CI/CD** - Automated testing (optional)

---

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

## License

See LICENSE file

---

## Support

- 📧 Email: (contact info)
- 💬 Issues: GitHub Issues
- 📚 Docs: This file + readme/ folder

---

## Version

**Current Version**: 2.0.0 (with artifact persistence)

**Last Updated**: December 22, 2025

---

## Acknowledgments

Built with modern best practices for production AutoML systems.

Inspired by:
- Auto-sklearn
- H2O AutoML
- AutoGluon
- TPOT


# Architecture & System Design

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTOML WEB PLATFORM                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend (React + TypeScript)  ←→  Backend (FastAPI)            │
│         http://localhost:5173           http://localhost:8000    │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend Layer
- React 18 with TypeScript (strict mode)
- Step-based workflow (Upload → Configure → Review → Run → Visualize)
- Real-time status polling
- Recharts visualizations (metrics, feature importance, confusion matrix)
- Responsive design (mobile, tablet, desktop)

### Backend Layer (REST API)
- FastAPI with async support
- Job-based execution (background tasks)
- CORS enabled for frontend communication
- Comprehensive error handling

### ML Pipeline
```
CSV Input
    ↓
[Data Sampling] - Stratified/Random sampling
    ↓
[Preprocessing] - Type detection → Missing values → Encoding → Scaling
    ↓
[Feature Selection] - Correlation, Mutual Information
    ↓
[Model Training] - Multiple baseline models
    ↓
[Evaluation] - Metrics, confusion matrix, feature importance
    ↓
[Selection] - Best model by performance
    ↓
[Tuning] - Grid/Random/Bayesian search (optional)
    ↓
[Artifact Persistence] ⭐ - Save model, preprocessors, metadata
    ↓
Results (JSON + artifact paths)
```

## Data Flow

1. **Upload**: User selects CSV → Validated → Stored in `uploads/`
2. **Configuration**: Task type, target column, options selected
3. **Processing**: Pipeline orchestrator routes to appropriate modules
4. **Sampling**: If dataset > 10,000 rows, apply stratified sampling (5,000 default)
5. **Training**: Train 6 baseline models in parallel
6. **Selection**: Compare metrics, select best by F1 (classification) or R² (regression)
7. **Tuning**: If enabled, tune hyperparameters (3x slower but 2-5% better performance)
8. **Persistence**: Save model artifacts with unique run_id
9. **Return**: JSON with artifact paths (no model objects)
10. **Visualization**: Display metrics, feature importance, confusion matrix

## Module Organization

```
automl/
├── pipeline.py              # Main orchestrator
│   └─ Coordinates all stages
├── preprocessing.py         # Type dispatcher
│   └─ Routes to specific preprocessor
├── tabular_preprocessing.py # Handles CSV data
├── text_preprocessing.py    # TF-IDF vectorization
├── timeseries_preprocessing.py # Lag features
├── Image_preprocessing.py   # CNN preprocessing
├── feature_selection.py     # Selection algorithms
├── model_trainer.py         # Train all models
├── model_selector.py        # Best model selection
├── evaluator.py             # Metrics calculation
├── hyperparameter_tuner.py  # Grid/Random/Bayesian search
└── utils/
    ├── sampling.py          # Stratified/random sampling
    └── artifact_manager.py   # ⭐ Save/load artifacts
```

## Model Persistence Architecture

### Artifact Structure
```
artifacts/
└── {run_id}/
    ├── model.pkl              # Trained model (joblib)
    ├── preprocessing.pkl      # Scalers, encoders, vectorizer
    ├── feature_metadata.json  # Feature names, selection info
    └── metrics.json           # Performance metrics
```

### Return Format (JSON-Safe)
```python
{
    "run_id": "20251222_010221_87771d68",      # Unique identifier
    "model_type": "LogisticRegression",         # Model class name
    "model_path": "artifacts/.../model.pkl",    # Path reference
    "artifacts_path": "artifacts/...",          # Directory reference
    "preprocessing_path": "artifacts/.../preprocessing.pkl",
    "metrics": {...},                           # Performance metrics
    ...
}
# ✅ Fully JSON-serializable (no sklearn objects)
```

### Load/Serve Pattern
```python
from automl.utils.artifact_manager import load_artifacts

artifacts = load_artifacts(run_id)
model = artifacts["model"]
preprocessors = artifacts["preprocessors"]

X_new = preprocess(data, preprocessors)
predictions = model.predict(X_new)
```

## Supported Data Types

| Type | Preprocessor | Vectorization | Special Handling |
|------|--------------|----------------|-----------------|
| Tabular | StandardScaler + LabelEncoder | - | Auto numeric/categorical detection |
| Text | TfidfVectorizer | TF-IDF (5000 features) | Removes punctuation, lowercase |
| Time Series | StandardScaler + Lag | Temporal features | Preserves temporal order in splits |
| Image | Resize + Normalize | CNN input (224x224) | Optional augmentation |

## Model Selection Strategy

### Baseline Models Trained
- LogisticRegression / LinearRegression
- DecisionTreeClassifier / DecisionTreeRegressor
- RandomForestClassifier / RandomForestRegressor
- GradientBoostingClassifier / GradientBoostingRegressor
- SVC / SVR
- KNeighborsClassifier / KNeighborsRegressor

### Selection Criteria
- **Classification**: F1-weighted (primary), Accuracy (tiebreaker), Precision (final tiebreaker)
- **Regression**: R² (primary), MAE (tiebreaker)

### Hyperparameter Tuning (Optional)
- **Grid Search**: Exhaustive combination search (slow but thorough)
- **Random Search**: Random sampling (faster)
- **Bayesian Optimization**: Sequential model-based (intelligent, recommended)

## Performance Characteristics

### Execution Time (by dataset size)
- < 1,000 rows: 5-15 seconds
- 1,000-10,000 rows: 15-60 seconds (with sampling: 15-30 seconds)
- > 10,000 rows: 1-5 minutes (with sampling: 30-120 seconds)

### Memory Usage
- Baseline training: ~500MB for 10,000 rows
- With feature selection: +100MB
- With tuning: +200MB

### Typical Accuracy Gains
- Baseline model: 85-95% accuracy
- With feature selection: +1-3%
- With hyperparameter tuning: +2-5%

## API Contract

### Core Request/Response
```
POST /api/run
Request: {
  "filename": "data.csv",
  "target_column": "target",
  "task_type": "classification|regression",
  "feature_selection_enabled": boolean,
  "hyperparameter_tuning_enabled": boolean,
  "search_method": "grid|random|bayesian",
  "max_sample_rows": 5000
}

Response: {
  "job_id": "uuid",
  "status": "processing|completed|error"
}

GET /api/results/{job_id}
Response: {
  "job_id": "uuid",
  "status": "completed",
  "results": {
    "run_id": "...",
    "model_path": "artifacts/.../model.pkl",
    "metrics": {...},
    ...
  }
}
```

## Extensibility Points

1. **Add New Model**: Edit `model_trainer.py`
2. **Add New Preprocessor**: Create new module, update `preprocessing.py`
3. **Add New Search Method**: Edit `hyperparameter_tuner.py`
4. **Add New Evaluation Metric**: Edit `evaluator.py`
5. **Add New API Endpoint**: Edit `app.py`

## Security Considerations

- File upload validation (CSV only)
- Input sanitization (SQL injection prevention via pandas)
- CORS enabled for frontend only
- No sensitive data in logs or responses
- Joblib protocol 4 for compatibility

## Scalability Considerations

- **Horizontal**: Deploy multiple backend instances with load balancer
- **Vertical**: Increase CPU/RAM for larger models
- **Data**: Use sampling for > 1M rows
- **Storage**: Archive old artifacts to cloud storage
- **Caching**: Use Redis for job status if needed

## Future Enhancements

- [ ] MLflow integration for model registry
- [ ] DVC for data versioning
- [ ] Distributed training (Ray, Spark)
- [ ] Model explanation (SHAP, LIME)
- [ ] Ensemble methods
- [ ] AutoML stacking
- [ ] GPU support
- [ ] Cloud deployment templates

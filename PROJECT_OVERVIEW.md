# AutoML System - Complete Project Overview

## 🎯 What Is This Project?

**AutoML System** is a **professional-grade automated machine learning platform** that automatically:
- 🎯 Selects the best machine learning model for your data
- ⚙️ Preprocesses data (scaling, encoding, vectorization)
- 🔍 Performs feature selection to improve performance
- 🔧 Tunes hyperparameters automatically
- 💾 **Persists trained models to disk** for inference
- 📊 Evaluates and provides comprehensive metrics
- 🚀 Serves everything via REST API + Web UI

Think of it as: **"Give me data → Get trained model + predictions"**

---

## 📊 What Data Can It Handle?

### 1. **Tabular Data** (CSV files, spreadsheets)
- Numbers, categories, mixed features
- Example: Customer data, sales predictions, housing prices
- Flow: CSV → numeric/categorical detection → scaling/encoding → training

### 2. **Text Data** (NLP)
- Blog posts, product reviews, customer feedback
- Example: Sentiment analysis, document classification
- Flow: Text → TF-IDF vectorization → training

### 3. **Time Series** (Temporal data)
- Stock prices, sensor readings, weather data
- Example: Price forecasting, anomaly detection
- Flow: Time series → lag features → training

### 4. **Image Data** (Coming)
- Photos, diagrams, satellite images
- Example: Object classification, quality inspection
- Flow: Images → CNN preprocessing → training

---

## 🔄 What Does It Do? (Complete Workflow)

### Step 1: **Data Upload**
```
User uploads CSV → Backend receives file → Analyzed for type (tabular/text/time-series)
```

### Step 2: **Preprocessing** 🔧
The system automatically handles:
- **Numeric features**: StandardScaler normalization
- **Categorical features**: One-hot or label encoding
- **Missing values**: Mean (numeric) or mode (categorical) imputation
- **Text data**: TF-IDF vectorization (converts text to numbers)
- **Time series**: Lag feature generation (past values as features)

Example:
```python
# INPUT:
age, income, occupation, target
25,  50000,  Engineer,    1
30,  60000,  Doctor,      1
22,  35000,  Student,     0

# AFTER PREPROCESSING:
age_scaled, income_scaled, occupation_Engineer, occupation_Doctor, occupation_Student
   0.1,        -0.5,             1,                  0,                0
   0.5,         0.3,             0,                  1,                0
  -0.2,        -1.2,             0,                  0,                1
```

### Step 3: **Feature Selection** 🔍 (Optional)
Selects the most important features to:
- Reduce noise
- Improve model accuracy
- Speed up training

Methods:
- Correlation analysis (how strongly related to target)
- Mutual information scoring (information gain)

Example: *"These 5 features matter most, drop the rest"*

### Step 4: **Model Training** 🤖
Trains **multiple models in parallel**:

| Model | Best For | Example |
|-------|----------|---------|
| Logistic Regression | Binary classification | Spam/Not spam |
| Linear Regression | Continuous prediction | House price |
| Decision Tree | Interpretable decisions | Loan approval |
| Random Forest | Robust, accurate predictions | Customer churn |
| Gradient Boosting | Maximum accuracy | Competition datasets |
| SVM | Complex boundaries | Image classification |
| KNN | Simple, local patterns | Recommendation |
| Naive Bayes | Text, probability-based | Email filtering |

The system trains all applicable models simultaneously using your data.

### Step 5: **Model Evaluation** 📈
Evaluates each model and computes metrics:

**For Classification:**
- Accuracy (% correct predictions)
- Precision (of positive predictions, how many correct)
- Recall (of actual positives, how many found)
- F1 Score (balance between precision & recall)
- AUC-ROC (performance across thresholds)
- Confusion Matrix (detailed true/false breakdowns)

**For Regression:**
- R² Score (variance explained, 0-1)
- MSE (Mean Squared Error)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)

### Step 6: **Model Selection** ✨
**Automatically picks the best model** based on primary metric:
- Classification: Highest F1 score
- Regression: Highest R² score

Example: *"Random Forest is best with 92% accuracy"*

### Step 7: **Hyperparameter Tuning** 🎯 (Optional)
Fine-tunes the **best model's settings** for maximum performance.

Search methods:
- **Grid Search**: Tries all combinations (slower, thorough)
- **Random Search**: Tries random combinations (faster)
- **Bayesian Optimization**: Smart selection of combinations (fastest)

Example: *"Best Random Forest: max_depth=10, n_estimators=200"*

### Step 8: **Model Persistence** 💾 **[NEW - KEY FEATURE]**
Saves everything to disk:

```
artifacts/
└── 20251222_010221_87771d68/  (unique run_id)
    ├── model.pkl              # Trained model (joblib format)
    ├── preprocessing.pkl      # Scalers, encoders, vectorizer
    ├── feature_metadata.json  # Feature names, selection info
    └── metrics.json           # Accuracy, precision, recall, etc.
```

Each model gets a unique **run_id** for tracking and loading later.

---

## ✅ Does It Return Trained Models?

### **YES! ✅ ABSOLUTELY!**

The trained model is:

#### 1. **Saved to Disk**
```
artifacts/{run_id}/model.pkl
```
Using joblib (industry standard for scikit-learn models)

#### 2. **Returned in API Response**
```json
{
  "job_id": "uuid-xxx",
  "status": "completed",
  "run_id": "20251222_010221_87771d68",
  "best_model": "random_forest",
  "model_path": "artifacts/20251222_010221_87771d68/model.pkl",
  "artifacts_path": "artifacts/20251222_010221_87771d68/",
  "metrics": {
    "accuracy": 0.92,
    "f1_score": 0.91,
    "precision": 0.89,
    "recall": 0.93
  }
}
```

#### 3. **Can Be Loaded & Used**
```python
from automl.utils.artifact_manager import load_artifacts

# Load after training
artifacts = load_artifacts("20251222_010221_87771d68")

# Get the model
model = artifacts["model"]

# Make predictions
predictions = model.predict(new_data)

# Or get preprocessors
scaler = artifacts["preprocessors"]["scaler"]
encoders = artifacts["preprocessors"]["encoders"]

# Transform new data before predicting
scaled_data = scaler.transform(new_data)
```

---

## 🏗️ System Architecture

### Three-Tier Architecture

```
┌─────────────────────────────────────────┐
│        FRONTEND (React/TypeScript)      │
│  - Dataset upload                       │
│  - Configuration UI                     │
│  - Results visualization                │
│  - Model export                         │
└──────────────┬──────────────────────────┘
               │ HTTP/REST API
               ↓
┌─────────────────────────────────────────┐
│       BACKEND (FastAPI/Python)          │
│  - API endpoints                        │
│  - Job management                       │
│  - File upload handling                 │
│  - Results storage                      │
└──────────────┬──────────────────────────┘
               │ Function calls
               ↓
┌─────────────────────────────────────────┐
│     ML PIPELINE (automl package)        │
│  1. Preprocessing                       │
│  2. Feature selection                   │
│  3. Model training                      │
│  4. Evaluation                          │
│  5. Model selection                     │
│  6. Hyperparameter tuning               │
│  7. Artifact persistence                │
└─────────────────────────────────────────┘
```

### Data Flow

```
CSV File Upload
    ↓
Analyze (type detection)
    ↓
Preprocess (scale, encode, vectorize)
    ↓
Feature Selection (optional)
    ↓
Train Multiple Models
    ↓
Evaluate Each Model
    ↓
Select Best Model
    ↓
Hyperparameter Tuning (optional)
    ↓
Save Artifacts (model.pkl, metadata, etc.)
    ↓
Return Results & Paths
```

---

## 📁 Project Structure

```
AutoML_System/
├── automl/                          # Core ML package
│   ├── pipeline.py                  # ⭐ Main orchestrator (Steps 1-8 above)
│   ├── preprocessing.py             # Step 1: Data preprocessing
│   ├── tabular_preprocessing.py     # Tabular-specific preprocessing
│   ├── text_preprocessing.py        # Text-specific preprocessing
│   ├── timeseries_preprocessing.py  # Time-series preprocessing
│   ├── feature_selection.py         # Step 2: Feature selection
│   ├── model_trainer.py             # Step 3: Model training
│   ├── evaluator.py                 # Step 4: Evaluation
│   ├── model_selector.py            # Step 5: Model selection
│   ├── hyperparameter_tuner.py      # Step 6: Hyperparameter tuning
│   └── utils/
│       ├── artifact_manager.py      # ⭐ Step 7: Model persistence
│       └── sampling.py              # Data sampling
│
├── frontend/                        # React/TypeScript web UI
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── pages/                   # Dashboard, results pages
│   │   ├── api/                     # API client
│   │   └── App.tsx                  # Main app
│   └── package.json
│
├── app.py                           # ⭐ FastAPI backend server
├── main.py                          # CLI entry point
├── requirements.txt                 # Python dependencies
├── artifacts/                       # 💾 Saved models (created by pipeline)
├── uploads/                         # 📁 Uploaded CSVs
└── readme/                          # 📚 Documentation
```

---

## 🔌 API Endpoints

Base URL (Production):
```
https://automated-machine-learning-automl-platform-production.up.railway.app
```

### Upload Dataset
```http
POST /api/upload
Content-Type: multipart/form-data

file: your_data.csv
```

### Run Pipeline
```http
POST /api/run
Content-Type: application/json

{
  "filename": "data.csv",
  "target_column": "target_column_name",
  "task_type": "classification",  # or "regression"
  "feature_selection_enabled": true,
  "hyperparameter_tuning_enabled": true,
  "search_method": "bayesian",  # grid, random, or bayesian
  "max_sample_rows": 10000
}
```

### Get Status & Results
```http
GET /api/status/{job_id}

# Response includes:
{
  "run_id": "20251222_010221_87771d68",
  "best_model": "random_forest",
  "model_path": "artifacts/20251222_010221_87771d68/model.pkl",
  "metrics": { ... }
}
```

### Download Model
```http
GET /api/export/{job_id}/model

# Returns: model.pkl (joblib file for inference)
```

---

## 🎯 Usage Examples

### Example 1: Classify Iris Flowers
```bash
# Using CLI
python main.py --builtin iris --task classification

# Output: Best model trained, metrics displayed, model saved
```

### Example 2: Predict House Prices
```bash
# Using CLI
python main.py --dataset house_prices.csv \
                --target price \
                --task regression

# Output: Model trained, R² score shown, model saved
```

### Example 3: Use in Python Code
```python
from automl.pipeline import run_pipeline
from pathlib import Path

# Run pipeline
results = run_pipeline(
    dataset="customer_data.csv",
    target_column="bought_product",
    task_type="classification",
    feature_selection_enabled=True,
    hyperparameter_tuning_enabled=True
)

# Access results
print(f"Best model: {results['best_model']}")
print(f"Accuracy: {results['metrics']['accuracy']}")

# Load and use model later
from automl.utils.artifact_manager import load_artifacts
artifacts = load_artifacts(results["run_id"])
predictions = artifacts["model"].predict(new_data)
```

### Example 4: Use REST API
```bash
# 1. Upload dataset
curl -X POST -F "file=@data.csv" http://localhost:8000/api/upload

# 2. Run pipeline
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "data.csv",
    "target_column": "target",
    "task_type": "classification"
  }'

# 3. Get results
curl http://localhost:8000/api/status/job-uuid-here

# 4. Download model
curl http://localhost:8000/api/export/job-uuid-here/model --output model.pkl
```

---

## 🎨 Web UI Features

### Dashboard
- 📊 Dataset statistics
- 📈 Feature distributions
- 🎯 Target variable analysis

### Configuration
- Select task type (classification/regression)
- Enable/disable feature selection
- Configure hyperparameter tuning
- Set advanced options (sampling, scaling, etc.)

### Results
- 📊 Model metrics (accuracy, F1, etc.)
- 📈 Confusion matrix (classification)
- 🔝 Feature importance chart
- 📁 Download model as pickle file
- 📄 Export comprehensive report

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| **Multi-data support** | Tabular, Text, Time-series, Image |
| **Automatic preprocessing** | Scaling, encoding, vectorization |
| **Feature selection** | Correlation, mutual information |
| **Multi-model training** | 8+ models trained in parallel |
| **Automatic evaluation** | Comprehensive metrics computed |
| **Model selection** | Best model picked automatically |
| **Hyperparameter tuning** | Grid/Random/Bayesian search |
| **Model persistence** ⭐ | Joblib format, unique run_id tracking |
| **REST API** | Full ML pipeline accessible via HTTP |
| **Web UI** | React dashboard for easy usage |
| **Data sampling** | Handle large datasets efficiently |
| **CLI support** | Command-line entry point |
| **Jupyter notebooks** | Demo notebooks for each data type |

---

## 💡 How Does It Know What Model Is Best?

1. **Trains all applicable models** for your data type
2. **Evaluates each model** with same metrics
3. **Picks best by primary metric**:
   - Classification: F1 score (balance of precision/recall)
   - Regression: R² score (variance explained)
4. **Further tunes** the best model if enabled

**Result: Best model automatically chosen, no manual selection needed!**

---

## 🔒 Model Persistence Details

### What Gets Saved?

```
artifacts/{run_id}/
├── model.pkl              # Trained sklearn model
├── preprocessing.pkl      # Scalers, encoders, vectorizers
├── feature_metadata.json  # Feature names, selection info
└── metrics.json           # Performance metrics
```

### Why Joblib?
- ✅ Handles sklearn models perfectly
- ✅ Efficient binary format (fast save/load)
- ✅ Python 3.4+ compatible
- ✅ Industry standard for scikit-learn

### How to Use Saved Model?

```python
from automl.utils.artifact_manager import load_artifacts

# 1. Load
artifacts = load_artifacts("20251222_010221_87771d68")

# 2. Get model and preprocessors
model = artifacts["model"]
scaler = artifacts["preprocessors"]["scaler"]
encoders = artifacts["preprocessors"]["encoders"]

# 3. Process new data
new_data_scaled = scaler.transform(new_data)

# 4. Predict
predictions = model.predict(new_data_scaled)
```

---

## 📊 Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Upload CSV (10K rows) | <1s | Depends on file size |
| Preprocessing | 1-5s | Scaling, encoding |
| Train 8 models | 5-30s | Depends on data size |
| Feature selection | 2-10s | Correlation calculation |
| Hyperparameter tuning | 30-300s | Search method & budget |
| **TOTAL** | **1-10 minutes** | Typical small-medium dataset |

---

## ✨ Summary

### What It Does:
1. ✅ Accepts your data (CSV, text, time-series, images)
2. ✅ Preprocesses automatically (scales, encodes, vectorizes)
3. ✅ Trains multiple ML models
4. ✅ Evaluates each model
5. ✅ Picks the best one
6. ✅ Fine-tunes it (optional)
7. ✅ **Returns the trained model** (saved to disk + metadata)
8. ✅ Serves via REST API + Web UI

### Does It Return Trained Models?
**YES! ✅**
- Saved to: `artifacts/{run_id}/model.pkl`
- Returned in API response with path
- Can be loaded and used for predictions
- Can be downloaded as a file
- Can be used in Python code directly

### Why This Matters:
Instead of knowing ML, you just:
1. Upload data
2. Wait for training
3. Get a working model
4. Use it to make predictions

**The entire ML complexity is hidden behind a simple interface!** 🎉

---

## 🤔 Questions?

See the documentation:
- 📖 [README.md](README.md) - Quick reference
- 🏗️ [readme/ARCHITECTURE.md](readme/ARCHITECTURE.md) - System design
- 💾 [readme/ARTIFACT_PERSISTENCE_IMPLEMENTATION.md](readme/ARTIFACT_PERSISTENCE_IMPLEMENTATION.md) - Model persistence details
- 🚀 [readme/DEPLOYMENT.md](readme/DEPLOYMENT.md) - Production deployment


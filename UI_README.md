# AutoML System with React UI

A full-stack AutoML system with FastAPI backend and React frontend for automated machine learning workflows.

## 🏗️ Architecture

```
React UI (Port 3000)
       ↓
FastAPI Backend (Port 8000)
       ↓
AutoML Pipeline (Python)
```

## 📦 Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- Required Python packages (see `requirements.txt`)

---

## 🚀 Quick Start

### 1. Backend Setup (FastAPI)

```powershell
# Install Python dependencies
pip install -r requirements.txt

# Start the API server
python app.py
# Or with uvicorn:
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**

API Docs (interactive): **http://localhost:8000/docs**

### 2. Frontend Setup (React)

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run at: **http://localhost:3000**

---

## 🎯 Usage

### Web UI (Recommended)

1. Open **http://localhost:3000** in your browser
2. Upload a CSV dataset
3. Select target column and configure options
4. Click "Run AutoML Pipeline"
5. View results (best model, metrics, trained models)

### CLI (Alternative)

```powershell
# Run with built-in datasets
python -m examples.demo_iris
python -m examples.demo_breast_cancer

# Run with custom CSV
python -m examples.demo_custom_dataset --csv dataset/sample_data.csv --target approved
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/upload` | Upload CSV dataset |
| POST | `/api/run` | Run AutoML pipeline |
| GET | `/api/results/{job_id}` | Get job results |

### Example API Request

```bash
# Upload CSV
curl -X POST http://localhost:8000/api/upload -F "file=@dataset/sample_data.csv"

# Run pipeline
curl -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "sample_data.csv",
    "target_column": "approved",
    "task_type": "classification",
    "feature_selection_enabled": true,
    "hyperparameter_tuning_enabled": true,
    "search_method": "grid"
  }'
```

---

## 📁 Project Structure

```
AutoML_System/
├── app.py                      # FastAPI backend
├── requirements.txt            # Python dependencies
├── main.py                     # CLI entry point
├── automl/                     # Core AutoML package
│   ├── __init__.py
│   ├── pipeline.py
│   ├── preprocessing.py
│   ├── feature_selection.py
│   ├── model_trainer.py
│   ├── evaluator.py
│   ├── hyperparameter_tuner.py
│   └── ...
├── examples/                   # Demo scripts
│   ├── demo_iris.py
│   ├── demo_breast_cancer.py
│   └── demo_custom_dataset.py
├── frontend/                   # React UI
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── App.css
│       └── index.css
├── dataset/                    # Sample datasets
├── uploads/                    # Uploaded files (auto-created)
├── results_api/                # API job results (auto-created)
└── results/                    # CLI results
```

---

## ⚙️ Configuration

### Backend (app.py)

- **Port:** 8000 (default)
- **CORS Origins:** `http://localhost:3000`, `http://localhost:5173`
- **Upload Directory:** `uploads/`
- **Results Directory:** `results_api/`

### Frontend (vite.config.js)

- **Port:** 3000
- **API Proxy:** `/api` → `http://localhost:8000`

---

## 🔧 Development

### Backend Development

```powershell
# Run with auto-reload
uvicorn app:app --reload

# View API docs
# Open http://localhost:8000/docs
```

### Frontend Development

```powershell
cd frontend

# Dev server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 🧪 Testing

### Test Backend

```powershell
# Health check
curl http://localhost:8000/api/health

# Run demo
python -m examples.demo_iris
```

### Test Frontend

1. Start backend: `python app.py`
2. Start frontend: `cd frontend && npm run dev`
3. Open browser: `http://localhost:3000`
4. Upload `dataset/sample_data.csv` and run pipeline

---

## 📊 Supported Data Types

- **Tabular:** CSV files with numeric/categorical features
- **Text:** NLP datasets (via preprocessing modules)
- **Timeseries:** Sequential data
- **Image:** Computer vision tasks (via preprocessing modules)

---

## 🎨 Features

### Backend
- ✅ RESTful API with FastAPI
- ✅ File upload validation
- ✅ Async pipeline execution
- ✅ Result caching
- ✅ Error handling
- ✅ CORS enabled

### Frontend
- ✅ Drag-and-drop file upload
- ✅ Interactive configuration
- ✅ Real-time results display
- ✅ Responsive design
- ✅ Error notifications
- ✅ Metric visualization

---

## 🚧 Roadmap

- [ ] Background task queue (Celery/RQ)
- [ ] Progress bars for long-running jobs
- [ ] Model comparison charts
- [ ] Feature importance visualization
- [ ] Confusion matrix plots
- [ ] Export trained models
- [ ] Multi-file dataset support
- [ ] User authentication

---

## 📝 License

This project is for educational purposes.

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

---

## 📧 Support

For issues or questions, please open an issue on GitHub.

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- React for the frontend library
- scikit-learn for ML algorithms
- All contributors and users

---

**Happy AutoML! 🚀**

import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [file, setFile] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [columns, setColumns] = useState([])
  const [config, setConfig] = useState({
    target_column: '',
    task_type: 'classification',
    feature_selection_enabled: true,
    hyperparameter_tuning_enabled: true,
    search_method: 'grid'
  })
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setResults(null)
    setError(null)
  }

  const handleUpload = async () => {
    if (!file) return
    
    setLoading(true)
    setError(null)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setUploadedFile(response.data)
      setColumns(response.data.columns)
      setConfig({ ...config, target_column: '' })
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    if (!uploadedFile || !config.target_column) {
      setError('Please upload a file and select target column')
      return
    }

    setLoading(true)
    setError(null)
    setResults(null)

    try {
      const response = await axios.post(`${API_BASE}/run`, {
        filename: uploadedFile.filename,
        ...config
      })
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Pipeline execution failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AutoML System</h1>
        <p>Automated Machine Learning Pipeline</p>
      </header>

      <div className="container">
        {/* File Upload Section */}
        <section className="card">
          <h2>📁 Upload Dataset</h2>
          <div className="upload-section">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              className="file-input"
            />
            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="btn btn-primary"
            >
              {loading ? 'Uploading...' : 'Upload CSV'}
            </button>
          </div>

          {uploadedFile && (
            <div className="file-info">
              <p><strong>File:</strong> {uploadedFile.filename}</p>
              <p><strong>Rows:</strong> {uploadedFile.rows}</p>
              <p><strong>Columns:</strong> {uploadedFile.columns.length}</p>
            </div>
          )}
        </section>

        {/* Configuration Section */}
        {columns.length > 0 && (
          <section className="card">
            <h2>⚙️ Configuration</h2>
            <div className="config-form">
              <div className="form-group">
                <label>Target Column</label>
                <select
                  value={config.target_column}
                  onChange={(e) => setConfig({ ...config, target_column: e.target.value })}
                  className="select"
                >
                  <option value="">Select target column</option>
                  {columns.map(col => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Task Type</label>
                <select
                  value={config.task_type}
                  onChange={(e) => setConfig({ ...config, task_type: e.target.value })}
                  className="select"
                >
                  <option value="classification">Classification</option>
                  <option value="regression">Regression</option>
                </select>
              </div>

              <div className="form-group">
                <label>Search Method</label>
                <select
                  value={config.search_method}
                  onChange={(e) => setConfig({ ...config, search_method: e.target.value })}
                  className="select"
                >
                  <option value="grid">Grid Search</option>
                  <option value="random">Random Search</option>
                  <option value="bayesian">Bayesian Optimization</option>
                </select>
              </div>

              <div className="checkboxes">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.feature_selection_enabled}
                    onChange={(e) => setConfig({ ...config, feature_selection_enabled: e.target.checked })}
                  />
                  Feature Selection
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={config.hyperparameter_tuning_enabled}
                    onChange={(e) => setConfig({ ...config, hyperparameter_tuning_enabled: e.target.checked })}
                  />
                  Hyperparameter Tuning
                </label>
              </div>

              <button
                onClick={handleRun}
                disabled={!config.target_column || loading}
                className="btn btn-success"
              >
                {loading ? '⏳ Running Pipeline...' : '🚀 Run AutoML Pipeline'}
              </button>
            </div>
          </section>
        )}

        {/* Error Display */}
        {error && (
          <section className="card error">
            <h3>❌ Error</h3>
            <p>{error}</p>
          </section>
        )}

        {/* Results Section */}
        {results && (
          <section className="card">
            <h2>✅ Results</h2>
            {results.status === 'completed' ? (
              <div className="results">
                <div className="result-item">
                  <h3>Best Model</h3>
                  <p className="highlight">{results.best_model}</p>
                </div>

                {results.metrics && (
                  <div className="result-item">
                    <h3>Metrics</h3>
                    <div className="metrics-grid">
                      {Object.entries(results.metrics).map(([key, value]) => (
                        <div key={key} className="metric">
                          <span className="metric-name">{key}:</span>
                          <span className="metric-value">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {results.trained_models && (
                <div className="result-item">
                  <h3>Trained Models ({results.trained_models.length})</h3>
                  <ul className="models-list">
                    {results.trained_models.map(model => (
                      <li key={model}>{model}</li>
                    ))}
                  </ul>
                </div>
              )}

              {results.selected_features && (
                <div className="result-item">
                  <h3>Selected Features ({results.selected_features.length})</h3>
                  <div className="features-list">
                    {results.selected_features.slice(0, 10).map(feature => (
                      <span key={feature} className="feature-badge">{feature}</span>
                    ))}
                    {results.selected_features.length > 10 && (
                      <span className="feature-badge">+{results.selected_features.length - 10} more</span>
                    )}
                  </div>
                </div>
              )}
            </div>
            ) : (
              <div className="result-item">
                <p>Status: {results.status}</p>
                {results.error && <p className="error-message">{results.error}</p>}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  )
}

export default App

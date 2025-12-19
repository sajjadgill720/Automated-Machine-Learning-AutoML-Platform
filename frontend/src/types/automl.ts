/**
 * AutoML Type Definitions
 * Comprehensive TypeScript interfaces for all AutoML data structures
 */

// Dataset-related types
export interface DatasetInfo {
  filename: string
  size_bytes: number
  rows: number
  columns: string[]
  dtypes: Record<string, string>
}

export interface DatasetPreview {
  headers: string[]
  rows: Array<Record<string, any>>
  total_rows: number
}

// Configuration types
export type TaskType = 'classification' | 'regression'
export type SearchMethod = 'grid' | 'random' | 'bayesian'
export type DataTypeOverride = 'tabular' | 'text' | 'timeseries' | 'image'

export interface AutoMLConfig {
  target_column: string
  task_type: TaskType
  feature_selection_enabled: boolean
  hyperparameter_tuning_enabled: boolean
  search_method: SearchMethod
  data_type_override?: DataTypeOverride
}

// Pipeline execution types
export interface RunPipelineRequest {
  filename: string
  target_column: string
  task_type: TaskType
  feature_selection_enabled: boolean
  hyperparameter_tuning_enabled: boolean
  search_method: SearchMethod
  data_type_override?: DataTypeOverride
}

export type JobStatus = 'pending' | 'processing' | 'completed' | 'error'

export interface PipelineResult {
  job_id: string
  status: JobStatus
  stage?: string
  progress?: number
  best_model?: string
  metrics?: MetricsObject
  selected_features?: string[]
  trained_models?: string[]
  error?: string
  timestamp?: string
}

// Metrics types
export interface MetricsObject {
  accuracy?: number
  precision?: number
  recall?: number
  f1?: number
  auc?: number
  mse?: number
  mae?: number
  rmse?: number
  r2?: number
  cv_score?: number
  [key: string]: number | undefined
}

// Results and visualization types
export interface ConfusionMatrixData {
  matrix: number[][]
  labels: string[]
}

export interface FeatureImportanceData {
  feature: string
  importance: number
}

export interface DetailedResults {
  job_id: string
  request: AutoMLConfig
  best_model: string
  metrics: MetricsObject
  trained_models: string[]
  selected_features?: string[]
  confusion_matrix?: ConfusionMatrixData
  feature_importance?: FeatureImportanceData[]
  timestamp: string
}

// UI State types
export interface UIState {
  currentStep: number
  isLoading: boolean
  error: string | null
  success: string | null
}

// API Error response
export interface APIError {
  detail: string
  [key: string]: any
}

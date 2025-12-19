/**
 * Utility Functions for AutoML
 */

import { MetricsObject } from '@types/automl'

/**
 * Format metric values for display (2-4 decimal places)
 */
export const formatMetric = (value: number | undefined): string => {
  if (value === undefined || value === null) return 'N/A'
  // For percentages (0-1), show as percentage
  if (value <= 1 && value >= 0) {
    return `${(value * 100).toFixed(2)}%`
  }
  // For other numbers, show 4 decimal places
  return value.toFixed(4)
}

/**
 * Format bytes to human-readable format
 */
export const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

/**
 * Validate CSV file (check extension and size)
 */
export const validateCSVFile = (
  file: File,
  maxSizeMB: number = 500
): { valid: boolean; error?: string } => {
  const maxBytes = maxSizeMB * 1024 * 1024

  if (!file.name.endsWith('.csv')) {
    return { valid: false, error: 'Only CSV files are supported' }
  }

  if (file.size > maxBytes) {
    return {
      valid: false,
      error: `File size exceeds ${maxSizeMB}MB limit (current: ${formatBytes(file.size)})`,
    }
  }

  return { valid: true }
}

/**
 * Get primary metrics based on task type
 */
export const getPrimaryMetrics = (taskType: 'classification' | 'regression'): string[] => {
  if (taskType === 'classification') {
    return ['accuracy', 'precision', 'recall', 'f1', 'auc']
  }
  return ['r2', 'mse', 'rmse', 'mae']
}

/**
 * Get metric description/tooltip for ML concepts
 */
export const getMetricDescription = (metric: string): string => {
  const descriptions: Record<string, string> = {
    accuracy: 'Percentage of correct predictions out of total predictions',
    precision: 'Of predicted positives, how many are actually positive',
    recall: 'Of actual positives, how many we correctly identified',
    f1: 'Harmonic mean of precision and recall (0-1 scale)',
    auc: 'Area Under the ROC Curve (0-1 scale, higher is better)',
    r2: 'Coefficient of determination (how well model explains variance)',
    mse: 'Mean Squared Error (lower is better)',
    rmse: 'Root Mean Squared Error (in original units)',
    mae: 'Mean Absolute Error (average prediction error)',
    cv_score: 'Cross-validation score (averaged across folds)',
  }
  return descriptions[metric] || 'No description available'
}

/**
 * Parse CSV data from text
 */
export const parseCSVData = (text: string, limit: number = 5): string[][] => {
  const lines = text.trim().split('\n')
  return lines.slice(0, limit + 1).map((line) => line.split(',').map((cell) => cell.trim()))
}

/**
 * Check if a string looks like a numeric column
 */
export const isNumericColumnName = (name: string): boolean => {
  // Heuristic: if column name contains 'id', 'index', or 'num', it might be numeric
  const numericPatterns = ['id', 'count', 'amount', 'price', 'age', 'year', 'score', 'value']
  return numericPatterns.some((pattern) => name.toLowerCase().includes(pattern))
}

/**
 * Get color for feature importance bar
 */
export const getImportanceColor = (importance: number, maxImportance: number): string => {
  const ratio = importance / maxImportance
  // Gradient from light blue to dark blue
  if (ratio > 0.7) return '#1e40af' // Dark blue
  if (ratio > 0.5) return '#3b82f6' // Medium blue
  if (ratio > 0.3) return '#60a5fa' // Light blue
  return '#bfdbfe' // Very light blue
}

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number = 30): string => {
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

/**
 * Get step display name
 */
export const getStepName = (step: number): string => {
  const steps = ['Dataset', 'Configuration', 'Pipeline', 'Review', 'Results']
  return steps[step] || 'Unknown'
}

/**
 * Calculate progress percentage
 */
export const getProgressPercentage = (currentStep: number, totalSteps: number = 5): number => {
  return Math.round(((currentStep + 1) / totalSteps) * 100)
}

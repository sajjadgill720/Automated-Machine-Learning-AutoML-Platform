/**
 * AutoML API Service Layer
 * Centralized API communication with error handling and typing
 */

import axios, { AxiosInstance, AxiosError } from 'axios'
import {
  DatasetInfo,
  DatasetPreview,
  RunPipelineRequest,
  PipelineResult,
  DetailedResults,
  APIError,
} from '@types/automl'

/**
 * API Service class for all AutoML backend communication
 * Provides centralized error handling, request/response typing, and retry logic
 */
class AutoMLAPIService {
  private client: AxiosInstance
  private readonly baseURL = (import.meta as any).env?.VITE_API_BASE_URL || '/api'
  private readonly requestTimeout = 300000 // 5 minutes for long-running operations

  constructor() {
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: this.requestTimeout,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => this.handleError(error)
    )
  }

  /**
   * Centralized error handler for all API calls
   * Extracts error details from various error formats
   */
  private handleError(error: AxiosError): Promise<never> {
    const message =
      (error.response?.data as APIError)?.detail ||
      error.message ||
      'An unexpected error occurred'

    const enhancedError = new Error(message) as Error & { status?: number }
    enhancedError.status = error.response?.status

    return Promise.reject(enhancedError)
  }

  /**
   * Upload and validate a CSV dataset
   * @param file - The CSV file to upload
   * @returns Dataset metadata including columns and row count
   */
  async uploadDataset(file: File): Promise<DatasetInfo> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await this.client.post<DatasetInfo>('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      return response.data
    } catch (error) {
      throw new Error(
        `Failed to upload dataset: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    }
  }

  /**
   * Get preview of dataset (first N rows)
   * @param filename - The uploaded filename
   * @returns Preview data with headers and sample rows
   */
  async getDatasetPreview(filename: string): Promise<DatasetPreview> {
    try {
      const response = await this.client.get<DatasetPreview>('/preview', {
        params: { filename },
      })
      return response.data
    } catch (error) {
      throw new Error('Failed to load dataset preview')
    }
  }

  /**
   * Run the AutoML pipeline with specified configuration
   * @param request - Pipeline configuration and dataset info
   * @returns Job ID and initial status
   */
  async runPipeline(request: RunPipelineRequest): Promise<PipelineResult> {
    try {
      const response = await this.client.post<PipelineResult>('/run', request)
      return response.data
    } catch (error) {
      throw new Error(
        `Failed to start AutoML pipeline: ${error instanceof Error ? error.message : 'Unknown error'}`
      )
    }
  }

  /**
   * Poll for job status
   * @param jobId - The job ID to check
   * @returns Current job status and results if completed
   */
  async getJobStatus(jobId: string): Promise<PipelineResult> {
    try {
      const response = await this.client.get<PipelineResult>(`/status/${jobId}`)
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch job status')
    }
  }

  /**
   * Retrieve detailed results for a completed job
   * @param jobId - The job ID to retrieve results for
   * @returns Complete results including metrics, models, and visualizations
   */
  async getResults(jobId: string): Promise<PipelineResult> {
    try {
      const response = await this.client.get<PipelineResult>(`/results/${jobId}`)
      return response.data
    } catch (error) {
      throw new Error('Failed to fetch results')
    }
  }

  /**
   * Health check endpoint
   * @returns Health status
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await this.client.get<{ status: string; timestamp: string }>('/health')
      return response.data
    } catch (error) {
      throw new Error('Health check failed')
    }
  }

  /**
   * Cancel a running job
   * @param jobId - The job ID to cancel
   */
  async cancelJob(jobId: string): Promise<void> {
    try {
      await this.client.post(`/cancel/${jobId}`)
    } catch (error) {
      throw new Error('Failed to cancel job')
    }
  }

  /**
   * Polling helper with exponential backoff
   * @param jobId - Job to poll
   * @param maxAttempts - Maximum polling attempts
   * @param initialDelay - Initial delay in ms
   * @returns Final job result
   */
  async pollJobCompletion(
    jobId: string,
    maxAttempts = 120,
    initialDelay = 500
  ): Promise<PipelineResult> {
    let attempt = 0
    let delay = initialDelay

    while (attempt < maxAttempts) {
      try {
        const result = await this.getJobStatus(jobId)

        if (result.status === 'completed' || result.status === 'error') {
          return result
        }

        // Exponential backoff: 500ms, 1s, 2s, 4s, etc. (capped at 10s)
        await new Promise((resolve) => setTimeout(resolve, delay))
        delay = Math.min(delay * 1.5, 10000)
        attempt++
      } catch (error) {
        // Continue polling even if status check fails temporarily
        attempt++
        if (attempt >= maxAttempts) {
          throw error
        }
      }
    }

    throw new Error('Job polling timeout - operation took too long')
  }
}

// Export singleton instance
export const automlAPI = new AutoMLAPIService()

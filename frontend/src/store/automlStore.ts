/**
 * AutoML Zustand Store
 * Centralized state management for AutoML workflow
 */

import { create } from 'zustand'
import {
  DatasetInfo,
  AutoMLConfig,
  PipelineResult,
  TaskType,
  SearchMethod,
} from '@types/automl'

interface AutoMLState {
  // Dataset state
  uploadedFile: DatasetInfo | null
  setUploadedFile: (file: DatasetInfo | null) => void

  // Configuration state
  config: AutoMLConfig
  updateConfig: (partial: Partial<AutoMLConfig>) => void
  resetConfig: () => void

  // Execution state
  currentJobId: string | null
  jobResult: PipelineResult | null
  setCurrentJobId: (jobId: string | null) => void
  setJobResult: (result: PipelineResult | null) => void

  // UI state
  currentStep: number
  setCurrentStep: (step: number) => void
  nextStep: () => void
  prevStep: () => void

  isLoading: boolean
  setIsLoading: (loading: boolean) => void

  error: string | null
  setError: (error: string | null) => void

  success: string | null
  setSuccess: (success: string | null) => void

  // Reset entire state
  reset: () => void
}

const defaultConfig: AutoMLConfig = {
  target_column: '',
  task_type: 'classification',
  feature_selection_enabled: true,
  hyperparameter_tuning_enabled: true,
  search_method: 'grid',
}

export const useAutoMLStore = create<AutoMLState>((set) => ({
  // Dataset state
  uploadedFile: null,
  setUploadedFile: (file) => set({ uploadedFile: file }),

  // Configuration state
  config: defaultConfig,
  updateConfig: (partial) =>
    set((state) => ({
      config: { ...state.config, ...partial },
    })),
  resetConfig: () => set({ config: defaultConfig }),

  // Execution state
  currentJobId: null,
  jobResult: null,
  setCurrentJobId: (jobId) => set({ currentJobId: jobId }),
  setJobResult: (result) => set({ jobResult: result }),

  // UI state
  currentStep: 0,
  setCurrentStep: (step) => set({ currentStep: step }),
  nextStep: () => set((state) => ({ currentStep: state.currentStep + 1 })),
  prevStep: () => set((state) => ({ currentStep: Math.max(0, state.currentStep - 1) })),

  isLoading: false,
  setIsLoading: (loading) => set({ isLoading: loading }),

  error: null,
  setError: (error) => set({ error }),

  success: null,
  setSuccess: (success) => set({ success }),

  // Reset entire state
  reset: () =>
    set({
      uploadedFile: null,
      config: defaultConfig,
      currentJobId: null,
      jobResult: null,
      currentStep: 0,
      isLoading: false,
      error: null,
      success: null,
    }),
}))

/**
 * Utility hook to derive canProceedToNextStep based on current step
 */
export const useCanProceedToNextStep = (): boolean => {
  const { uploadedFile, config, currentStep } = useAutoMLStore()

  switch (currentStep) {
    case 0: // Dataset upload
      return uploadedFile !== null
    case 1: // Task configuration
      return config.target_column !== ''
    case 2: // Pipeline options
      return true
    case 3: // Review and run
      return true
    default:
      return false
  }
}

/**
 * Utility hook to get step validation errors
 */
export const useStepValidationError = (): string | null => {
  const { uploadedFile, config, currentStep } = useAutoMLStore()

  switch (currentStep) {
    case 0:
      return !uploadedFile ? 'Please upload a CSV dataset first' : null
    case 1:
      return !config.target_column ? 'Please select a target column' : null
    default:
      return null
  }
}

/**
 * Run Page
 * Main AutoML wizard with step-based workflow
 */

import React, { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Button,
  Card,
  CardContent,
  Container,
  Stack,
  Typography,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { ChevronLeft, ChevronRight, Play } from 'lucide-react'
import { useSnackbar } from 'notistack'
import { useAutoMLStore, useCanProceedToNextStep } from '@store/automlStore'
import { automlAPI } from '@api/automl'
import {
  StepIndicator,
  DatasetUpload,
  TaskConfig,
  PipelineConfig,
  LoadingSkeleton,
} from '@components/index'

interface StepComponentProps {
  onNext: () => void
  onBack: () => void
}

export const Run: React.FC = () => {
  const navigate = useNavigate()
  const { enqueueSnackbar } = useSnackbar()
  const {
    currentStep,
    nextStep,
    prevStep,
    uploadedFile,
    config,
    setCurrentJobId,
    setIsLoading,
    isLoading,
    error,
    setError,
    success,
    setSuccess,
  } = useAutoMLStore()

  const [confirmDialogOpen, setConfirmDialogOpen] = useState(false)
  const canProceed = useCanProceedToNextStep()

  // Step components mapping
  const stepComponents: Record<number, React.ComponentType<StepComponentProps>> = {
    0: DatasetUpload,
    1: TaskConfig,
    2: PipelineConfig,
  }

  const CurrentStepComponent = stepComponents[currentStep]

  const handleNext = () => {
    if (canProceed) {
      if (currentStep < 2) {
        nextStep()
      } else if (currentStep === 2) {
        // Show review step
        nextStep()
      }
    } else {
      setError('Please complete this step before proceeding')
      setTimeout(() => setError(null), 3000)
    }
  }

  const handleRun = async () => {
    if (!uploadedFile || !config.target_column) {
      setError('Missing dataset or target column')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const result = await automlAPI.runPipeline({
        filename: uploadedFile.filename,
        ...config,
      })

      setCurrentJobId(result.job_id)
      enqueueSnackbar('AutoML pipeline started successfully!', { variant: 'success' })

      // Navigate to results after a short delay
      setTimeout(() => {
        navigate('/results')
      }, 1000)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to start pipeline'
      setError(errorMessage)
      enqueueSnackbar(errorMessage, { variant: 'error' })
    } finally {
      setIsLoading(false)
    }
  }

  const reviewContent = (
    <Card>
      <CardContent>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h6" gutterBottom>
              📋 Review Configuration
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Please review your settings before starting the AutoML pipeline.
            </Typography>
          </Box>

          {/* Dataset Summary */}
          <Box sx={{ p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Dataset
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="body2">
                <strong>File:</strong> {uploadedFile?.filename}
              </Typography>
              <Typography variant="body2">
                <strong>Rows:</strong> {uploadedFile?.rows.toLocaleString()}
              </Typography>
              <Typography variant="body2">
                <strong>Columns:</strong> {uploadedFile?.columns.length}
              </Typography>
            </Stack>
          </Box>

          {/* Task Configuration Summary */}
          <Box sx={{ p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Task Configuration
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="body2">
                <strong>Task Type:</strong> {config.task_type.charAt(0).toUpperCase() + config.task_type.slice(1)}
              </Typography>
              <Typography variant="body2">
                <strong>Target Column:</strong> {config.target_column}
              </Typography>
              {config.data_type_override && (
                <Typography variant="body2">
                  <strong>Data Type Override:</strong> {config.data_type_override}
                </Typography>
              )}
            </Stack>
          </Box>

          {/* Pipeline Options Summary */}
          <Box sx={{ p: 2, backgroundColor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
              Pipeline Options
            </Typography>
            <Stack spacing={0.5}>
              <Typography variant="body2">
                <strong>Feature Selection:</strong> {config.feature_selection_enabled ? '✓ Enabled' : '✗ Disabled'}
              </Typography>
              <Typography variant="body2">
                <strong>Hyperparameter Tuning:</strong>{' '}
                {config.hyperparameter_tuning_enabled ? '✓ Enabled' : '✗ Disabled'}
              </Typography>
              {config.hyperparameter_tuning_enabled && (
                <Typography variant="body2">
                  <strong>Search Method:</strong>{' '}
                  {config.search_method.charAt(0).toUpperCase() + config.search_method.slice(1)}
                </Typography>
              )}
            </Stack>
          </Box>

          <Alert severity="info">
            🚀 Ready to start? Click "Run AutoML Pipeline" to begin the automated machine learning process.
          </Alert>
        </Stack>
      </CardContent>
    </Card>
  )

  const stepContent = currentStep < 3 ? <CurrentStepComponent onNext={handleNext} onBack={prevStep} /> : reviewContent

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <StepIndicator />

      {/* Error Alert */}
      {error && (
        <Alert
          severity="error"
          onClose={() => setError(null)}
          sx={{ mb: 3 }}
        >
          {error}
        </Alert>
      )}

      {/* Success Alert */}
      {success && (
        <Alert
          severity="success"
          onClose={() => setSuccess(null)}
          sx={{ mb: 3 }}
        >
          {success}
        </Alert>
      )}

      {/* Step Content */}
      {isLoading && currentStep < 3 ? <LoadingSkeleton /> : stepContent}

      {/* Navigation Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4, gap: 2 }}>
        <Button
          variant="outlined"
          startIcon={<ChevronLeft size={20} />}
          onClick={prevStep}
          disabled={currentStep === 0 || isLoading}
        >
          Back
        </Button>

        <Stack direction="row" spacing={2}>
          {currentStep < 3 && (
            <Button
              variant="contained"
              endIcon={<ChevronRight size={20} />}
              onClick={handleNext}
              disabled={!canProceed || isLoading}
            >
              Next
            </Button>
          )}
          {currentStep === 3 && (
            <>
              <Button
                variant="outlined"
                onClick={() => setConfirmDialogOpen(true)}
                disabled={isLoading}
              >
                Edit Configuration
              </Button>
              <Button
                variant="contained"
                color="success"
                startIcon={isLoading ? <CircularProgress size={20} /> : <Play size={20} />}
                onClick={handleRun}
                disabled={isLoading}
              >
                {isLoading ? 'Starting...' : 'Run AutoML Pipeline'}
              </Button>
            </>
          )}
        </Stack>
      </Box>

      {/* Confirmation Dialog */}
      <Dialog open={confirmDialogOpen} onClose={() => setConfirmDialogOpen(false)}>
        <DialogTitle>Edit Configuration?</DialogTitle>
        <DialogContent>
          <Typography>
            Going back will allow you to modify the configuration. Do you want to proceed?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={() => {
              setConfirmDialogOpen(false)
              prevStep()
            }}
            variant="contained"
          >
            Go Back
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

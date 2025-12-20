/**
 * Results Page
 * Display AutoML results, metrics, and visualizations
 */

import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Button,
  Card,
  CardContent,
  Grid,
  Typography,
  Stack,
  Alert,
  LinearProgress,
  Paper,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import { Download, RotateCcw, Home } from 'lucide-react'
import { useSnackbar } from 'notistack'
import { useAutoMLStore } from '@store/automlStore'
import { useJobPolling, useElapsedTime } from '@hooks/useAutoML'
import { automlAPI } from '@api/automl'
import {
  MetricsTable,
  ConfusionMatrix,
  FeatureImportance,
  LoadingSkeleton,
  ChartLoadingSkeleton,
  MetricsBarChart,
  ConfusionMatrixChart,
  FeatureImportanceChart,
  ExportActions,
  InterpretationPanel,
} from '@components/index'

export const Results: React.FC = () => {
  const navigate = useNavigate()
  const { enqueueSnackbar } = useSnackbar()
  const { currentJobId, jobResult, setJobResult, uploadedFile, config, reset } = useAutoMLStore()
  const [jobStartTime] = useState(Date.now())
  const elapsedTime = useElapsedTime(jobResult ? null : jobStartTime)
  const [downloadDialogOpen, setDownloadDialogOpen] = useState(false)

  // Poll for job status if still processing
  const { data: polledResult, isLoading: isPolling } = useJobPolling(
    currentJobId,
    !jobResult || jobResult.status !== 'completed'
  )

  // Update job result when polling returns data
  useEffect(() => {
    if (polledResult) {
      // Persist intermediate status to show progress
      setJobResult(polledResult)

      if (polledResult.status === 'completed') {
        enqueueSnackbar('AutoML pipeline completed successfully!', { variant: 'success' })
      } else if (polledResult.status === 'error') {
        enqueueSnackbar('Pipeline failed: ' + polledResult.error, { variant: 'error' })
      }
    }
  }, [polledResult, setJobResult, enqueueSnackbar])

  const isComplete = jobResult?.status === 'completed'
  const isError = jobResult?.status === 'error'
  const isProcessing = jobResult?.status === 'processing'
  const currentStage = jobResult?.stage || (isProcessing ? 'running_pipeline' : undefined)
  const currentProgress = jobResult?.progress

  const handleDownloadResults = async () => {
    if (!currentJobId) return

    try {
      // In a real implementation, you'd fetch detailed results from the backend
      const data = jobResult
      const jsonString = JSON.stringify(data, null, 2)
      const blob = new Blob([jsonString], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `automl-results-${currentJobId}.json`
      link.click()
      enqueueSnackbar('Results downloaded successfully', { variant: 'success' })
    } catch (err) {
      enqueueSnackbar('Failed to download results', { variant: 'error' })
    }
  }

  const handleNewRun = () => {
    reset()
    navigate('/')
  }

  if (!currentJobId) {
    return (
      <Container maxWidth="lg" sx={{ py: 4, textAlign: 'center' }}>
        <Alert severity="warning" sx={{ mb: 3 }}>
          No active job. Please start a new AutoML run.
        </Alert>
        <Button variant="contained" onClick={() => navigate('/run')}>
          Start New Run
        </Button>
      </Container>
    )
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Paper sx={{ p: 3, mb: 4, backgroundColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: 'white', mb: 1 }}>
              🎯 AutoML Pipeline Results
            </Typography>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              Job ID: {currentJobId.slice(0, 8)}...
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Button
              variant="outlined"
              startIcon={<Home size={20} />}
              onClick={() => navigate('/')}
              sx={{ color: 'white', borderColor: 'white', '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' } }}
            >
              Home
            </Button>
            <Button
              variant="outlined"
              startIcon={<RotateCcw size={20} />}
              onClick={handleNewRun}
              sx={{ color: 'white', borderColor: 'white', '&:hover': { backgroundColor: 'rgba(255,255,255,0.1)' } }}
            >
              New Run
            </Button>
          </Stack>
        </Stack>
      </Paper>

      {/* Status Section */}
      {isProcessing && (
        <Card sx={{ mb: 4, backgroundColor: '#e8f5e9' }}>
          <CardContent>
            <Stack spacing={2}>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                  ⏳ Pipeline Running...
                </Typography>
                <LinearProgress
                  sx={{ mb: 2 }}
                  variant={typeof currentProgress === 'number' ? 'determinate' : 'indeterminate'}
                  value={typeof currentProgress === 'number' ? currentProgress : undefined}
                />
                <Stack direction="row" spacing={2}>
                  <Typography variant="caption" color="textSecondary">
                    Elapsed time: <strong>{elapsedTime}</strong>
                  </Typography>
                  <Typography variant="caption" color="textSecondary">
                    Stage: <strong>{currentStage || 'Processing'}</strong>
                  </Typography>
                  {typeof currentProgress === 'number' && (
                    <Typography variant="caption" color="textSecondary">
                      Progress: <strong>{currentProgress}%</strong>
                    </Typography>
                  )}
                </Stack>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      )}

      {isError && (
        <Alert severity="error" sx={{ mb: 4 }}>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
            ❌ Pipeline Failed
          </Typography>
          <Typography variant="body2">{jobResult?.error || 'Unknown error occurred'}</Typography>
          <Button
            variant="text"
            onClick={() => navigate('/run')}
            sx={{ mt: 2 }}
          >
            Try Again
          </Button>
        </Alert>
      )}

      {isComplete && jobResult && (
        <>
          {/* Success Alert */}
          <Alert severity="success" sx={{ mb: 4 }}>
            ✓ AutoML pipeline completed successfully! Processing took {elapsedTime}.
          </Alert>

          {/* Interpretation Panel */}
          {jobResult.metrics && jobResult.best_model && (
            <Box sx={{ mb: 4 }}>
              <InterpretationPanel
                bestModel={jobResult.best_model}
                metrics={jobResult.metrics}
                taskType={config.task_type}
                topFeatures={jobResult.feature_importance?.slice(0, 3)}
              />
            </Box>
          )}

          {/* Best Model Section */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                    🏆 Best Model
                  </Typography>
                  <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#667eea', mb: 2 }}>
                    {jobResult.best_model || 'N/A'}
                  </Typography>
                  <Stack spacing={1}>
                    {jobResult.metrics && (
                      <>
                        <Box>
                          <Typography variant="caption" color="textSecondary">
                            Primary Metric
                          </Typography>
                          <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                            {jobResult.metrics.accuracy
                              ? `Accuracy: ${(jobResult.metrics.accuracy * 100).toFixed(2)}%`
                              : jobResult.metrics.r2
                                ? `R² Score: ${jobResult.metrics.r2.toFixed(4)}`
                                : 'See metrics below'}
                          </Typography>
                        </Box>
                      </>
                    )}
                  </Stack>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                    📊 Pipeline Configuration
                  </Typography>
                  <Stack spacing={1}>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Task Type
                      </Typography>
                      <Chip
                        label={config.task_type}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </Box>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Features
                      </Typography>
                      <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mt: 0.5 }}>
                        {config.feature_selection_enabled && (
                          <Chip label="Feature Selection" size="small" />
                        )}
                        {config.hyperparameter_tuning_enabled && (
                          <Chip label="Hyperparameter Tuning" size="small" />
                        )}
                      </Stack>
                    </Box>
                  </Stack>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Metrics Section */}
          {jobResult.metrics && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  📈 Performance Metrics
                </Typography>
                <MetricsTable metrics={jobResult.metrics} taskType={config.task_type} />
              </CardContent>
            </Card>
          )}

          {/* Metrics Comparison Chart */}
          {jobResult.evaluation_results && (
            <Box sx={{ mb: 4 }}>
              <MetricsBarChart
                data={Object.entries(jobResult.evaluation_results).map(([model, result]) => ({
                  model,
                  ...result.metrics,
                }))}
                taskType={config.task_type}
              />
            </Box>
          )}

          {/* Models Trained */}
          {jobResult.trained_models && jobResult.trained_models.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  🤖 Trained Models ({jobResult.trained_models.length})
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {jobResult.trained_models.map((model) => (
                    <Chip
                      key={model}
                      label={model}
                      variant={model === jobResult.best_model ? 'filled' : 'outlined'}
                      color={model === jobResult.best_model ? 'success' : 'default'}
                    />
                  ))}
                </Stack>
              </CardContent>
            </Card>
          )}

          {/* Feature Importance */}
          {jobResult.selected_features && jobResult.selected_features.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
                  ⭐ Selected Features ({jobResult.selected_features.length})
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {jobResult.selected_features.slice(0, 20).map((feature) => (
                    <Chip key={feature} label={feature} />
                  ))}
                  {jobResult.selected_features.length > 20 && (
                    <Chip label={`+${jobResult.selected_features.length - 20} more`} disabled />
                  )}
                </Stack>
              </CardContent>
            </Card>
          )}

          {/* Confusion Matrix Chart */}
          {config.task_type === 'classification' && jobResult.confusion_matrix && (
            <Box sx={{ mb: 4 }}>
              <ConfusionMatrixChart data={jobResult.confusion_matrix} />
            </Box>
          )}

          {/* Feature Importance Chart */}
          {jobResult.feature_importance && jobResult.feature_importance.length > 0 && (
            <Box sx={{ mb: 4 }}>
              <FeatureImportanceChart data={jobResult.feature_importance} />
            </Box>
          )}

          {/* Export Results */}
          <Box sx={{ mb: 4 }}>
            <ExportActions jobId={currentJobId} />
          </Box>

          {/* CTA Buttons */}
          <Stack direction="row" spacing={2} sx={{ justifyContent: 'center' }}>
            <Button
              variant="outlined"
              startIcon={<RotateCcw size={20} />}
              onClick={handleNewRun}
            >
              Start New Run
            </Button>
            <Button
              variant="contained"
              startIcon={<Home size={20} />}
              onClick={() => navigate('/')}
            >
              Back to Home
            </Button>
          </Stack>
        </>
      )}

      {/* Loading State */}
      {isPolling && !jobResult && (
        <Box>
          <LoadingSkeleton count={3} />
        </Box>
      )}

      {/* Download Confirmation Dialog */}
      <Dialog open={downloadDialogOpen} onClose={() => setDownloadDialogOpen(false)}>
        <DialogTitle>Download Results</DialogTitle>
        <DialogContent>
          <Typography>
            This will download your AutoML results as a JSON file containing all metrics, models, and configuration.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDownloadDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={() => {
              handleDownloadResults()
              setDownloadDialogOpen(false)
            }}
          >
            Download
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  )
}

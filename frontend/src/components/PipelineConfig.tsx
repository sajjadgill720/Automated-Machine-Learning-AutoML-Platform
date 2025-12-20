/**
 * PipelineConfig Component
 * Configure feature selection, hyperparameter tuning, and search method
 */

import React from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  FormControlLabel,
  Switch,
  Paper,
  Alert,
  Grid,
  TextField,
  Tooltip,
} from '@mui/material'
import { Info } from 'lucide-react'
import { useAutoMLStore } from '@store/automlStore'
import { SearchMethod } from '@types/automl'

interface PipelineConfigProps {
  onNext: () => void
  onBack: () => void
}

export const PipelineConfig: React.FC<PipelineConfigProps> = ({ onNext, onBack }) => {
  const { config, updateConfig } = useAutoMLStore()

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" gutterBottom>
                🔧 Pipeline Configuration
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Configure advanced options for AutoML processing.
              </Typography>
            </Box>

            {/* Feature Selection */}
            <Paper sx={{ p: 2.5, backgroundColor: '#fafafa', borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info size={20} color="#1976d2" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    Dataset Sampling
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" gutterBottom>
                    Maximum rows to process
                  </Typography>
                  <TextField
                    type="number"
                    fullWidth
                    size="small"
                    value={config.max_sample_rows || 10000}
                    onChange={(e) => {
                      const value = parseInt(e.target.value) || 0
                      updateConfig({ max_sample_rows: value })
                    }}
                    inputProps={{ min: 0, step: 1000 }}
                    helperText={
                      <Box component="span">
                        {config.max_sample_rows === 0 || !config.max_sample_rows ? (
                          <span style={{ color: '#d32f2f' }}>
                            ⚠️ No limit - will process all rows (may be slow for large datasets)
                          </span>
                        ) : (
                          <span>
                            Large datasets will be sampled to {config.max_sample_rows?.toLocaleString()} rows.
                            Set to 0 to disable sampling.
                          </span>
                        )}
                      </Box>
                    }
                  />
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 1, display: 'block' }}>
                    Recommended: 5,000-10,000 for faster processing. Use 50,000+ for more accuracy.
                  </Typography>
                </Box>
              </Stack>
            </Paper>

            {/* Feature Selection */}
            <Paper sx={{ p: 2.5, backgroundColor: '#fafafa', borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info size={20} color="#1976d2" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    Feature Selection
                  </Typography>
                </Box>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.feature_selection_enabled}
                      onChange={(e) => updateConfig({ feature_selection_enabled: e.target.checked })}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">Automatically select relevant features</Typography>
                      <Typography variant="caption" color="textSecondary" component="div" sx={{ mt: 0.5 }}>
                        Removes irrelevant or redundant columns. Improves model performance and reduces training
                        time.
                      </Typography>
                    </Box>
                  }
                />
              </Stack>
            </Paper>

            {/* Hyperparameter Tuning */}
            <Paper sx={{ p: 2.5, backgroundColor: '#fafafa', borderRadius: 1, border: '1px solid #e0e0e0' }}>
              <Stack spacing={2}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Info size={20} color="#1976d2" />
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    Hyperparameter Tuning
                  </Typography>
                </Box>
                <FormControlLabel
                  control={
                    <Switch
                      checked={config.hyperparameter_tuning_enabled}
                      onChange={(e) => updateConfig({ hyperparameter_tuning_enabled: e.target.checked })}
                    />
                  }
                  label={
                    <Box>
                      <Typography variant="body2">Optimize model hyperparameters</Typography>
                      <Typography variant="caption" color="textSecondary" component="div" sx={{ mt: 0.5 }}>
                        Automatically finds best parameter combinations. Takes longer but improves results.
                      </Typography>
                    </Box>
                  }
                />

                {config.hyperparameter_tuning_enabled && (
                  <FormControl fullWidth sx={{ mt: 2 }}>
                    <InputLabel>Search Method</InputLabel>
                    <Select
                      value={config.search_method}
                      onChange={(e) => updateConfig({ search_method: e.target.value as SearchMethod })}
                      label="Search Method"
                    >
                      <MenuItem value="grid">
                        <Box>
                          <Typography variant="body2">Grid Search</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Tests all combinations (thorough, slower)
                          </Typography>
                        </Box>
                      </MenuItem>
                      <MenuItem value="random">
                        <Box>
                          <Typography variant="body2">Random Search</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Tests random combinations (faster, good)
                          </Typography>
                        </Box>
                      </MenuItem>
                      <MenuItem value="bayesian">
                        <Box>
                          <Typography variant="body2">Bayesian Optimization</Typography>
                          <Typography variant="caption" color="textSecondary">
                            Smart sampling (fastest, state-of-art)
                          </Typography>
                        </Box>
                      </MenuItem>
                    </Select>
                    <FormHelperText sx={{ mt: 1 }}>
                      {config.search_method === 'grid' &&
                        'Grid Search: Exhaustive search through all parameter combinations. Best when parameter space is small.'}
                      {config.search_method === 'random' &&
                        'Random Search: Samples random parameter combinations. Good balance between speed and thoroughness.'}
                      {config.search_method === 'bayesian' &&
                        'Bayesian Optimization: Uses probabilistic model to guide search. Most efficient for large spaces.'}
                    </FormHelperText>
                  </FormControl>
                )}
              </Stack>
            </Paper>

            {/* Configuration Summary */}
            <Paper sx={{ p: 2, backgroundColor: '#f0f4ff', borderLeft: '4px solid #3f51b5' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1 }}>
                ✓ Configuration Summary
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6} sm={6}>
                  <Typography variant="caption" color="textSecondary">
                    Max Rows:
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {config.max_sample_rows === 0 || !config.max_sample_rows 
                      ? 'Unlimited' 
                      : config.max_sample_rows.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} sm={6}>
                  <Typography variant="caption" color="textSecondary">
                    Feature Selection:
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
                    {config.feature_selection_enabled ? '✓ Enabled' : '✗ Disabled'}
                  </Typography>
                </Grid>6
                <Grid item xs={6} sm={6}>
                  <Typography variant="caption" color="textSecondary">
                    Hyperparameter Tuning:
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#2e7d32' }}>
                    {config.hyperparameter_tuning_enabled ? '✓ Enabled' : '✗ Disabled'}
                  </Typography>
                </Grid>
                {config.hyperparameter_tuning_enabled && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="textSecondary">
                      Search Method:
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                      {config.search_method.charAt(0).toUpperCase() + config.search_method.slice(1)}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Paper>

            {/* Recommendation Alert */}
            <Alert severity="info">
              For best results, we recommend enabling both feature selection and hyperparameter tuning with Bayesian
              Optimization. Processing time will be longer but results will be significantly better.
            </Alert>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}

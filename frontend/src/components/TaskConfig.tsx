/**
 * TaskConfig Component
 * Configure task type, target column, and data type override
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
  Paper,
  Alert,
  Tooltip,
  InfoIcon,
} from '@mui/material'
import { Info } from 'lucide-react'
import { useAutoMLStore } from '@store/automlStore'
import { TaskType, DataTypeOverride } from '@types/automl'

interface TaskConfigProps {
  onNext: () => void
  onBack: () => void
}

export const TaskConfig: React.FC<TaskConfigProps> = ({ onNext, onBack }) => {
  const { uploadedFile, config, updateConfig } = useAutoMLStore()

  if (!uploadedFile) {
    return null
  }

  const canProceed = config.target_column !== ''

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" gutterBottom>
                ⚙️ Task Configuration
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Define your machine learning task and target variable.
              </Typography>
            </Box>

            {/* Task Type Selection */}
            <FormControl fullWidth>
              <InputLabel>Task Type</InputLabel>
              <Select
                value={config.task_type}
                onChange={(e) => updateConfig({ task_type: e.target.value as TaskType })}
                label="Task Type"
              >
                <MenuItem value="classification">
                  Classification - Predict categories/classes
                </MenuItem>
                <MenuItem value="regression">Regression - Predict continuous values</MenuItem>
              </Select>
              <FormHelperText>
                {config.task_type === 'classification'
                  ? 'Use for categorical target variables (e.g., Yes/No, Spam/Not Spam)'
                  : 'Use for numeric target variables (e.g., price, temperature)'}
              </FormHelperText>
            </FormControl>

            {/* Target Column Selection */}
            <FormControl fullWidth error={config.target_column === ''}>
              <InputLabel>Target Column (Required)</InputLabel>
              <Select
                value={config.target_column}
                onChange={(e) => updateConfig({ target_column: e.target.value })}
                label="Target Column (Required)"
              >
                <MenuItem value="">
                  <em>Select a column...</em>
                </MenuItem>
                {uploadedFile.columns.map((col) => (
                  <MenuItem key={col} value={col}>
                    {col}
                  </MenuItem>
                ))}
              </Select>
              <FormHelperText>
                {config.target_column === ''
                  ? 'This is required - select the column you want to predict'
                  : `Using "${config.target_column}" as target variable (${uploadedFile.dtypes[config.target_column]})`}
              </FormHelperText>
            </FormControl>

            {/* Data Type Override (Optional) */}
            <FormControl fullWidth>
              <InputLabel>Data Type (Optional)</InputLabel>
              <Select
                value={config.data_type_override || ''}
                onChange={(e) => updateConfig({ data_type_override: e.target.value as DataTypeOverride })}
                label="Data Type (Optional)"
              >
                <MenuItem value="">Auto-detect</MenuItem>
                <MenuItem value="tabular">Tabular (structured data)</MenuItem>
                <MenuItem value="text">Text (NLP)</MenuItem>
                <MenuItem value="timeseries">Time Series</MenuItem>
                <MenuItem value="image">Image</MenuItem>
              </Select>
              <FormHelperText>
                Leave as "Auto-detect" to let the system determine the data type automatically.
              </FormHelperText>
            </FormControl>

            {/* Info Card */}
            <Paper sx={{ p: 2, backgroundColor: '#e3f2fd', borderLeft: '4px solid #1976d2' }}>
              <Stack direction="row" spacing={2}>
                <Info size={24} style={{ color: '#1976d2', flexShrink: 0 }} />
                <Box>
                  <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold' }}>
                    About Task Selection
                  </Typography>
                  <Typography variant="caption" component="div">
                    <strong>Classification:</strong> Predicts discrete categories. Best for binary or multi-class
                    outcomes.
                  </Typography>
                  <Typography variant="caption" component="div" sx={{ mt: 0.5 }}>
                    <strong>Regression:</strong> Predicts numeric values. Best for continuous numeric outcomes.
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}

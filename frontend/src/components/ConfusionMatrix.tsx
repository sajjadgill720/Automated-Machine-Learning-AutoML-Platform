/**
 * ConfusionMatrix Component
 * Visualize classification confusion matrix as heatmap
 */

import React from 'react'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Stack,
} from '@mui/material'
import { ConfusionMatrixData } from '@types/automl'

interface ConfusionMatrixProps {
  data: ConfusionMatrixData | undefined
}

// Get color intensity based on value
const getColorForValue = (value: number, max: number): string => {
  const ratio = value / max
  if (ratio === 0) return '#ffffff'
  if (ratio < 0.3) return '#bbdefb'
  if (ratio < 0.6) return '#64b5f6'
  if (ratio < 0.9) return '#1e88e5'
  return '#0d47a1'
}

export const ConfusionMatrix: React.FC<ConfusionMatrixProps> = ({ data }) => {
  if (!data || !data.matrix || data.matrix.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="textSecondary">Confusion matrix data not available</Typography>
      </Paper>
    )
  }

  const maxValue = Math.max(...data.matrix.flat())
  const labels = data.labels || data.matrix.map((_, i) => `Class ${i}`)

  return (
    <Paper sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            🎯 Confusion Matrix
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Shows actual vs predicted classifications. Darker colors = more predictions.
          </Typography>
        </Box>

        <TableContainer>
          <Table size="small" sx={{ maxWidth: 400 }}>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 'bold' }}>Actual \ Predicted</TableCell>
                {labels.map((label) => (
                  <TableCell key={label} align="center" sx={{ fontWeight: 'bold', minWidth: 60 }}>
                    {label}
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {data.matrix.map((row, i) => (
                <TableRow key={i}>
                  <TableCell sx={{ fontWeight: 'bold' }}>{labels[i]}</TableCell>
                  {row.map((value, j) => (
                    <TableCell
                      key={`${i}-${j}`}
                      align="center"
                      sx={{
                        backgroundColor: getColorForValue(value, maxValue),
                        fontWeight: 'bold',
                        color: getColorForValue(value, maxValue) !== '#ffffff' ? '#fff' : '#000',
                        minWidth: 60,
                      }}
                    >
                      {value}
                    </TableCell>
                  ))}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Box sx={{ backgroundColor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="caption" color="textSecondary">
            💡 <strong>How to read:</strong> Diagonal values (top-left to bottom-right) represent correct
            predictions. Off-diagonal values represent misclassifications.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  )
}

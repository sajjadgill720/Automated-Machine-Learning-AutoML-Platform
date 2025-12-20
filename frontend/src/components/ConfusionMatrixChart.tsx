/**
 * Confusion Matrix Heatmap Component
 * Visualizes classification confusion matrix with color coding
 */

import React from 'react'
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from '@mui/material'

export interface ConfusionMatrixData {
  matrix: number[][]
  labels: string[]
}

interface ConfusionMatrixProps {
  data: ConfusionMatrixData
}

export const ConfusionMatrixChart: React.FC<ConfusionMatrixProps> = ({ data }) => {
  if (!data || !data.matrix || data.matrix.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="textSecondary">No confusion matrix available</Typography>
      </Paper>
    )
  }

  const { matrix, labels } = data
  const maxValue = Math.max(...matrix.flat())

  const getCellColor = (value: number) => {
    const intensity = value / maxValue
    return `rgba(102, 126, 234, ${intensity * 0.8 + 0.1})`
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
        🎯 Confusion Matrix
      </Typography>
      <TableContainer>
        <Table size="small" sx={{ maxWidth: 600 }}>
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', borderBottom: 2 }}>Actual \ Predicted</TableCell>
              {labels.map((label) => (
                <TableCell key={label} align="center" sx={{ fontWeight: 'bold', borderBottom: 2 }}>
                  {label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {matrix.map((row, rowIndex) => (
              <TableRow key={labels[rowIndex]}>
                <TableCell sx={{ fontWeight: 'bold', borderRight: 2 }}>{labels[rowIndex]}</TableCell>
                {row.map((value, colIndex) => (
                  <TableCell
                    key={colIndex}
                    align="center"
                    sx={{
                      backgroundColor: getCellColor(value),
                      fontWeight: rowIndex === colIndex ? 'bold' : 'normal',
                      color: value > maxValue * 0.5 ? 'white' : 'inherit',
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
      <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
        Darker cells indicate higher counts. Diagonal cells represent correct predictions.
      </Typography>
    </Paper>
  )
}

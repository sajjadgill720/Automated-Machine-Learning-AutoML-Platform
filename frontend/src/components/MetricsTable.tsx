/**
 * MetricsTable Component
 * Display model performance metrics in a professional table
 */

import React from 'react'
import {
  Box,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Tooltip,
  Typography,
  Stack,
} from '@mui/material'
import { Info } from 'lucide-react'
import { MetricsObject } from '@types/automl'
import { formatMetric, getMetricDescription } from '@utils/helpers'

interface MetricsTableProps {
  metrics: MetricsObject
  taskType: 'classification' | 'regression'
}

export const MetricsTable: React.FC<MetricsTableProps> = ({ metrics, taskType }) => {
  // Filter and sort metrics
  const relevantMetrics = Object.entries(metrics)
    .filter(([key]) => {
      if (taskType === 'classification') {
        return ['accuracy', 'precision', 'recall', 'f1', 'auc', 'cv_score'].includes(key)
      } else {
        return ['r2', 'mse', 'rmse', 'mae', 'cv_score'].includes(key)
      }
    })
    .sort(([a], [b]) => a.localeCompare(b))

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead sx={{ backgroundColor: '#f5f5f5' }}>
          <TableRow>
            <TableCell sx={{ fontWeight: 'bold' }}>
              <Stack direction="row" spacing={1} alignItems="center">
                <span>Metric</span>
                <Tooltip title="Performance metrics for your trained model">
                  <Info size={16} color="#999" />
                </Tooltip>
              </Stack>
            </TableCell>
            <TableCell align="right" sx={{ fontWeight: 'bold' }}>
              Value
            </TableCell>
            <TableCell sx={{ fontWeight: 'bold', width: '40%' }}>Description</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {relevantMetrics.length > 0 ? (
            relevantMetrics.map(([key, value]) => (
              <TableRow key={key} hover>
                <TableCell sx={{ fontWeight: '500' }}>
                  {key.charAt(0).toUpperCase() + key.slice(1).replace(/_/g, ' ')}
                </TableCell>
                <TableCell align="right">
                  <Typography
                    variant="body2"
                    sx={{
                      fontWeight: 'bold',
                      color: '#1976d2',
                      fontSize: '1.1rem',
                    }}
                  >
                    {formatMetric(value)}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Typography variant="caption" color="textSecondary">
                    {getMetricDescription(key)}
                  </Typography>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={3} align="center" sx={{ py: 3 }}>
                <Typography color="textSecondary">No metrics available</Typography>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </TableContainer>
  )
}

/**
 * Metrics Bar Chart Component
 * Displays model performance metrics as horizontal bars for comparison
 */

import React from 'react'
import { Box, Typography, Paper } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export interface MetricsChartData {
  model: string
  accuracy?: number
  f1_weighted?: number
  precision_weighted?: number
  recall_weighted?: number
  r2?: number
  rmse?: number
}

interface MetricsBarChartProps {
  data: MetricsChartData[]
  taskType: 'classification' | 'regression'
}

export const MetricsBarChart: React.FC<MetricsBarChartProps> = ({ data, taskType }) => {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="textSecondary">No metrics data available</Typography>
      </Paper>
    )
  }

  const metricKeys = taskType === 'classification'
    ? ['accuracy', 'f1_weighted', 'precision_weighted', 'recall_weighted']
    : ['r2', 'rmse']

  const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe']

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
        📊 Model Metrics Comparison
      </Typography>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 120, right: 20, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" domain={taskType === 'classification' ? [0, 1] : [0, 'auto']} />
          <YAxis type="category" dataKey="model" width={100} />
          <Tooltip formatter={(value: any) => (typeof value === 'number' ? value.toFixed(4) : value)} />
          <Legend />
          {metricKeys.map((key, idx) => (
            <Bar key={key} dataKey={key} fill={colors[idx % colors.length]} name={key.replace('_', ' ')} />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Paper>
  )
}

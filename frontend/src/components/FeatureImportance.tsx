/**
 * FeatureImportance Component
 * Visualize feature importance with bar chart
 */

import React from 'react'
import { Box, Paper, Typography, Stack, CircularProgress } from '@mui/material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { FeatureImportanceData } from '@types/automl'
import { getImportanceColor } from '@utils/helpers'

interface FeatureImportanceProps {
  features: FeatureImportanceData[] | undefined
  isLoading?: boolean
}

export const FeatureImportance: React.FC<FeatureImportanceProps> = ({ features, isLoading = false }) => {
  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (!features || features.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="textSecondary">Feature importance data not available</Typography>
      </Paper>
    )
  }

  // Sort by importance and take top 15
  const topFeatures = [...features]
    .sort((a, b) => b.importance - a.importance)
    .slice(0, 15)

  const maxImportance = Math.max(...topFeatures.map((f) => f.importance))

  const chartData = topFeatures.map((f) => ({
    name: f.feature,
    importance: parseFloat(f.importance.toFixed(4)),
    fill: getImportanceColor(f.importance, maxImportance),
  }))

  return (
    <Paper sx={{ p: 2 }}>
      <Stack spacing={2}>
        <Box>
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
            📊 Top Feature Importance
          </Typography>
          <Typography variant="caption" color="textSecondary">
            Shows which features have the most influence on model predictions (top {topFeatures.length})
          </Typography>
        </Box>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 200, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" width={190} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(value) => (typeof value === 'number' ? value.toFixed(4) : value)}
              contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', border: '1px solid #ccc' }}
            />
            <Bar dataKey="importance" fill="#3f51b5" radius={[0, 8, 8, 0]} />
          </BarChart>
        </ResponsiveContainer>

        <Box sx={{ backgroundColor: '#f5f5f5', p: 1.5, borderRadius: 1 }}>
          <Typography variant="caption" color="textSecondary">
            💡 <strong>Insight:</strong> Features at the top have stronger influence on predictions. Features with low
            importance may be candidates for removal in future iterations.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  )
}

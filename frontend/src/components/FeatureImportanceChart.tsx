/**
 * Feature Importance Chart Component
 * Displays top features by importance score as horizontal bars
 */

import React from 'react'
import { Box, Typography, Paper } from '@mui/material'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export interface FeatureImportanceItem {
  feature: string
  importance: number
}

interface FeatureImportanceChartProps {
  data: FeatureImportanceItem[]
  maxFeatures?: number
}

export const FeatureImportanceChart: React.FC<FeatureImportanceChartProps> = ({ 
  data, 
  maxFeatures = 15 
}) => {
  if (!data || data.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="textSecondary">Feature importance not available for this model</Typography>
      </Paper>
    )
  }

  // Take top N features
  const topFeatures = data.slice(0, maxFeatures)
  const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
        ⭐ Feature Importance (Top {Math.min(maxFeatures, data.length)})
      </Typography>
      <ResponsiveContainer width="100%" height={Math.max(300, topFeatures.length * 25)}>
        <BarChart data={topFeatures} layout="vertical" margin={{ left: 150, right: 20, top: 10, bottom: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="feature" width={130} />
          <Tooltip formatter={(value: any) => (typeof value === 'number' ? value.toFixed(4) : value)} />
          <Bar dataKey="importance" name="Importance">
            {topFeatures.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      {data.length > maxFeatures && (
        <Typography variant="caption" color="textSecondary" sx={{ mt: 2, display: 'block' }}>
          +{data.length - maxFeatures} more features not shown
        </Typography>
      )}
    </Paper>
  )
}

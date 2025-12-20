/**
 * Interpretation Panel Component
 * Provides plain-language summary of results for non-ML users
 */

import React from 'react'
import { Box, Typography, Paper, Stack, Chip } from '@mui/material'
import { CheckCircle, TrendingUp, Target } from 'lucide-react'

interface InterpretationPanelProps {
  bestModel: string
  metrics: Record<string, number>
  taskType: 'classification' | 'regression'
  topFeatures?: Array<{ feature: string; importance: number }>
}

export const InterpretationPanel: React.FC<InterpretationPanelProps> = ({
  bestModel,
  metrics,
  taskType,
  topFeatures,
}) => {
  const generateInterpretation = () => {
    const insights: string[] = []

    if (taskType === 'classification') {
      const accuracy = metrics.accuracy || metrics.accuracy_score
      if (accuracy !== undefined) {
        const percentage = (accuracy * 100).toFixed(1)
        insights.push(
          `The ${bestModel} model achieves ${percentage}% accuracy, meaning it correctly predicts the outcome ${percentage}% of the time.`
        )

        if (accuracy >= 0.9) {
          insights.push('This is excellent performance.')
        } else if (accuracy >= 0.75) {
          insights.push('This is good performance for most practical applications.')
        } else if (accuracy >= 0.6) {
          insights.push('This is moderate performance - consider collecting more data or trying different features.')
        } else {
          insights.push('This performance is relatively low - the model may need significant improvement.')
        }
      }

      const f1 = metrics.f1_weighted || metrics.f1
      if (f1 !== undefined && f1 < 0.7) {
        insights.push('The F1-score suggests the model may struggle with imbalanced classes.')
      }
    } else {
      const r2 = metrics.r2
      if (r2 !== undefined) {
        const percentage = (r2 * 100).toFixed(1)
        insights.push(
          `The ${bestModel} model explains ${percentage}% of the variance in the target variable (R² score).`
        )

        if (r2 >= 0.8) {
          insights.push('This indicates strong predictive power.')
        } else if (r2 >= 0.6) {
          insights.push('This shows moderate predictive ability.')
        } else {
          insights.push('The model has limited predictive power - consider feature engineering or more data.')
        }
      }

      const rmse = metrics.rmse
      if (rmse !== undefined) {
        insights.push(`The typical prediction error (RMSE) is ${rmse.toFixed(4)} units.`)
      }
    }

    if (topFeatures && topFeatures.length > 0) {
      const topThree = topFeatures.slice(0, 3).map((f) => f.feature)
      insights.push(
        `The most influential features are: ${topThree.join(', ')}. These have the greatest impact on predictions.`
      )
    }

    return insights
  }

  const insights = generateInterpretation()

  return (
    <Paper sx={{ p: 3, backgroundColor: '#f0f4ff' }}>
      <Stack spacing={2}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Target size={20} color="#667eea" />
          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#667eea' }}>
            📖 Results Interpretation
          </Typography>
        </Box>
        <Typography variant="body2" color="textSecondary" sx={{ fontStyle: 'italic', mb: 1 }}>
          Plain-language summary for decision makers:
        </Typography>
        <Stack spacing={1.5}>
          {insights.map((insight, index) => (
            <Box key={index} sx={{ display: 'flex', gap: 1.5, alignItems: 'flex-start' }}>
              <CheckCircle size={16} color="#4caf50" style={{ marginTop: 2, flexShrink: 0 }} />
              <Typography variant="body2">{insight}</Typography>
            </Box>
          ))}
        </Stack>
        <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
          <Typography variant="caption" color="textSecondary">
            💡 <strong>Next Steps:</strong> Review the charts below for detailed performance breakdown, compare with
            other models, and download the trained model for deployment.
          </Typography>
        </Box>
      </Stack>
    </Paper>
  )
}

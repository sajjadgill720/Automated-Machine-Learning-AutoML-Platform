/**
 * Step Indicator Component
 * Visual representation of current progress through AutoML workflow
 */

import React from 'react'
import { Box, Step, Stepper, StepLabel, Typography, Paper } from '@mui/material'
import { useAutoMLStore } from '@store/automlStore'

const STEPS = ['Dataset', 'Configuration', 'Pipeline', 'Review', 'Results']

export const StepIndicator: React.FC = () => {
  const { currentStep } = useAutoMLStore()

  return (
    <Paper sx={{ p: 3, mb: 4, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
      <Stepper activeStep={currentStep} orientation="horizontal">
        {STEPS.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Typography variant="caption" color="textSecondary">
          Step {currentStep + 1} of {STEPS.length}
        </Typography>
      </Box>
    </Paper>
  )
}

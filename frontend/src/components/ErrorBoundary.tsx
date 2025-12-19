/**
 * Error Boundary Component
 * Catches React errors and displays fallback UI
 */

import React, { ReactNode, ErrorInfo } from 'react'
import { Box, Card, CardContent, Typography, Button, Stack, Alert } from '@mui/material'
import { AlertCircle } from 'lucide-react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 4, display: 'flex', justifyContent: 'center', minHeight: '60vh' }}>
          <Card sx={{ maxWidth: 500, width: '100%' }}>
            <CardContent>
              <Stack spacing={2} alignItems="center">
                <AlertCircle size={48} color="#d32f2f" />
                <Typography variant="h5" color="error">
                  Something went wrong
                </Typography>
                <Alert severity="error">{this.state.error?.message || 'Unknown error'}</Alert>
                <Button variant="contained" onClick={this.handleReset}>
                  Try Again
                </Button>
                <Button variant="text" href="/">
                  Return Home
                </Button>
              </Stack>
            </CardContent>
          </Card>
        </Box>
      )
    }

    return this.props.children
  }
}

/**
 * Main Layout Component
 * Provides consistent header, navigation, and footer for all pages
 */

import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Box, Container, AppBar, Toolbar, Typography, Button, Stack } from '@mui/material'
import { Zap, Home, RotateCcw } from 'lucide-react'
import { useAutoMLStore } from '@store/automlStore'
import '../styles/layout.css'

interface LayoutProps {
  children: React.ReactNode
}

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const { currentStep, reset } = useAutoMLStore()

  const handleReset = () => {
    if (window.confirm('Are you sure you want to start a new AutoML run? This will clear all current data.')) {
      reset()
      navigate('/')
    }
  }

  return (
    <Box className="layout-container">
      <AppBar position="static" className="app-header">
        <Toolbar>
          <Stack direction="row" alignItems="center" spacing={1} sx={{ flexGrow: 1 }}>
            <Zap size={28} className="logo-icon" />
            <Typography variant="h6" className="app-title">
              AutoML Platform
            </Typography>
          </Stack>

          <Stack direction="row" spacing={1}>
            {location.pathname !== '/' && (
              <Button
                color="inherit"
                startIcon={<Home size={20} />}
                onClick={() => navigate('/')}
                variant="text"
              >
                Home
              </Button>
            )}
            {location.pathname !== '/' && (
              <Button
                color="inherit"
                startIcon={<RotateCcw size={20} />}
                onClick={handleReset}
                variant="outlined"
                size="small"
              >
                New Run
              </Button>
            )}
          </Stack>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" className="main-content">
        {children}
      </Container>

      <Box component="footer" className="app-footer">
        <Typography variant="body2" color="textSecondary" align="center">
          AutoML Platform v1.0 | Powered by FastAPI & React
        </Typography>
      </Box>
    </Box>
  )
}

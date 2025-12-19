/**
 * Home Page
 * Landing page with introduction and quick start guide
 */

import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Stack,
  Paper,
} from '@mui/material'
import { Zap, Upload, Settings, BarChart3, Rocket, ArrowRight } from 'lucide-react'
import { useAutoMLStore } from '@store/automlStore'

export const Home: React.FC = () => {
  const navigate = useNavigate()
  const { reset } = useAutoMLStore()

  useEffect(() => {
    // Reset state when landing on home
    reset()
  }, [reset])

  const features = [
    {
      icon: <Upload size={32} />,
      title: 'Easy Upload',
      description: 'Upload CSV files and let the platform analyze your data automatically',
    },
    {
      icon: <Zap size={32} />,
      title: 'Smart Detection',
      description: 'Automatic detection of data types, columns, and potential issues',
    },
    {
      icon: <Settings size={32} />,
      title: 'Customizable',
      description: 'Fine-tune feature selection, hyperparameter tuning, and search methods',
    },
    {
      icon: <BarChart3 size={32} />,
      title: 'Rich Metrics',
      description: 'Comprehensive evaluation metrics and feature importance analysis',
    },
  ]

  return (
    <Box sx={{ py: 6 }}>
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography
            variant="h3"
            component="h1"
            sx={{
              fontWeight: 'bold',
              mb: 2,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
            }}
          >
            Automated Machine Learning Made Simple
          </Typography>
          <Typography variant="h6" color="textSecondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
            Build, train, and deploy machine learning models in minutes. No ML expertise required.
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/run')}
            endIcon={<Rocket size={20} />}
            sx={{
              px: 4,
              py: 1.5,
              fontSize: '1.1rem',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            Start AutoML Run
          </Button>
        </Box>

        {/* Features Grid */}
        <Grid container spacing={3} sx={{ mb: 8 }}>
          {features.map((feature, idx) => (
            <Grid item xs={12} sm={6} md={3} key={idx}>
              <Card
                sx={{
                  height: '100%',
                  p: 2,
                  textAlign: 'center',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    boxShadow: 4,
                    transform: 'translateY(-4px)',
                  },
                }}
              >
                <Box sx={{ color: '#667eea', mb: 2 }}>{feature.icon}</Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
                  {feature.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {feature.description}
                </Typography>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* How It Works */}
        <Paper sx={{ p: 4, mb: 6, backgroundColor: '#f8f9fa', borderRadius: 2 }}>
          <Typography variant="h5" sx={{ fontWeight: 'bold', mb: 3, textAlign: 'center' }}>
            How It Works
          </Typography>
          <Grid container spacing={2} alignItems="stretch">
            {[
              { num: '1', title: 'Upload Dataset', desc: 'Upload your CSV file with training data' },
              { num: '2', title: 'Configure Task', desc: 'Select task type and target column' },
              { num: '3', title: 'Choose Options', desc: 'Enable feature selection & tuning' },
              { num: '4', title: 'Review & Run', desc: 'Review settings and start AutoML' },
              { num: '5', title: 'Get Results', desc: 'Analyze metrics and feature importance' },
            ].map((step, idx) => (
              <Grid item xs={12} sm={6} md={2.4} key={idx}>
                <Box
                  sx={{
                    textAlign: 'center',
                    p: 2,
                    backgroundColor: 'white',
                    borderRadius: 1,
                    border: '2px solid #667eea',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'center',
                  }}
                >
                  <Box
                    sx={{
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      backgroundColor: '#667eea',
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      fontSize: '1.2rem',
                      mx: 'auto',
                      mb: 1,
                    }}
                  >
                    {step.num}
                  </Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                    {step.title}
                  </Typography>
                  <Typography variant="caption" color="textSecondary" sx={{ mt: 0.5 }}>
                    {step.desc}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>

        {/* CTA Section */}
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Ready to build your first AutoML model?
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/run')}
            endIcon={<ArrowRight size={20} />}
            sx={{
              px: 4,
              py: 1.5,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }}
          >
            Get Started Now
          </Button>
        </Box>
      </Container>
    </Box>
  )
}

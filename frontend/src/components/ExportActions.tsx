/**
 * Export Actions Component
 * Provides download buttons for various export formats
 */

import React, { useState } from 'react'
import { Box, Button, Stack, Typography, Paper, CircularProgress } from '@mui/material'
import { Download, FileText, FileSpreadsheet, FileJson, Package } from 'lucide-react'
import { useSnackbar } from 'notistack'

interface ExportActionsProps {
  jobId: string
}

export const ExportActions: React.FC<ExportActionsProps> = ({ jobId }) => {
  const { enqueueSnackbar } = useSnackbar()
  const [loading, setLoading] = useState<string | null>(null)

  const handleDownload = async (format: string, endpoint: string, filename: string) => {
    setLoading(format)
    try {
      const response = await fetch(`/api/export/${jobId}/${endpoint}`)
      
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`)
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      enqueueSnackbar(`${format} downloaded successfully`, { variant: 'success' })
    } catch (error) {
      enqueueSnackbar(`Failed to download ${format}: ${error instanceof Error ? error.message : 'Unknown error'}`, {
        variant: 'error',
      })
    } finally {
      setLoading(null)
    }
  }

  const exports = [
    {
      format: 'JSON',
      endpoint: 'json',
      filename: `automl-${jobId}.json`,
      icon: <FileJson size={20} />,
      description: 'Raw results data',
    },
    {
      format: 'CSV',
      endpoint: 'csv',
      filename: `automl-metrics-${jobId}.csv`,
      icon: <FileSpreadsheet size={20} />,
      description: 'Metrics comparison table',
    },
    {
      format: 'Report',
      endpoint: 'report',
      filename: `automl-report-${jobId}.txt`,
      icon: <FileText size={20} />,
      description: 'Full experiment report',
    },
    {
      format: 'Model',
      endpoint: 'model',
      filename: `automl-model-${jobId}.pkl`,
      icon: <Package size={20} />,
      description: 'Trained model artifact',
    },
  ]

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2 }}>
        📥 Export Results
      </Typography>
      <Stack spacing={2}>
        {exports.map((exp) => (
          <Box
            key={exp.format}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: 2,
              backgroundColor: '#f5f5f5',
              borderRadius: 1,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              {exp.icon}
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                  {exp.format}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {exp.description}
                </Typography>
              </Box>
            </Box>
            <Button
              variant="outlined"
              size="small"
              startIcon={loading === exp.format ? <CircularProgress size={16} /> : <Download size={16} />}
              onClick={() => handleDownload(exp.format, exp.endpoint, exp.filename)}
              disabled={loading !== null}
            >
              Download
            </Button>
          </Box>
        ))}
      </Stack>
    </Paper>
  )
}

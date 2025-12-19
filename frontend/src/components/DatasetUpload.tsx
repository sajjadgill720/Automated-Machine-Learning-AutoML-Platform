/**
 * DatasetUpload Component
 * Handles CSV file upload with validation and preview
 */

import React, { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Stack,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
} from '@mui/material'
import { Upload, CheckCircle, AlertCircle } from 'lucide-react'
import { useAutoMLStore } from '@store/automlStore'
import { automlAPI } from '@api/automl'
import { DatasetInfo } from '@types/automl'
import { validateCSVFile, formatBytes } from '@utils/helpers'

interface DatasetUploadProps {
  onNext: () => void
}

export const DatasetUpload: React.FC<DatasetUploadProps> = ({ onNext }) => {
  const { setUploadedFile, uploadedFile, setError, setSuccess } = useAutoMLStore()
  const [loading, setLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const handleFileSelect = async (file: File) => {
    // Validate file
    const validation = validateCSVFile(file)
    if (!validation.valid) {
      setError(validation.error || 'Invalid file')
      return
    }

    setSelectedFile(file)
    setError(null)

    // Upload immediately
    await uploadFile(file)
  }

  const uploadFile = async (file: File) => {
    setLoading(true)
    setError(null)

    try {
      const datasetInfo = await automlAPI.uploadDataset(file)
      setUploadedFile(datasetInfo)
      setSuccess(`Successfully uploaded ${datasetInfo.rows} rows with ${datasetInfo.columns.length} columns`)
      // Delay proceeding to next step to show success message
      setTimeout(() => onNext(), 1000)
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      setError(errorMessage)
      setSelectedFile(null)
    } finally {
      setLoading(false)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileSelect(files[0])
    }
  }

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stack spacing={3}>
            <Box>
              <Typography variant="h6" gutterBottom>
                📁 Upload Your Dataset
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Upload a CSV file containing your data. The platform will automatically detect column types and
                statistics.
              </Typography>
            </Box>

            {!uploadedFile ? (
              <>
                {/* Drag and Drop Zone */}
                <Box
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  sx={{
                    border: '2px dashed',
                    borderColor: dragActive ? 'primary.main' : 'divider',
                    borderRadius: 2,
                    p: 4,
                    textAlign: 'center',
                    cursor: 'pointer',
                    backgroundColor: dragActive ? 'action.hover' : 'background.default',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: 'action.hover',
                    },
                  }}
                >
                  <Stack alignItems="center" spacing={2}>
                    <Upload size={40} color="#1976d2" />
                    <Box>
                      <Typography variant="subtitle1" gutterBottom>
                        Drag and drop your CSV file here
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        or click to select
                      </Typography>
                    </Box>
                    <input
                      type="file"
                      accept=".csv"
                      onChange={(e) => {
                        if (e.target.files?.[0]) {
                          handleFileSelect(e.target.files[0])
                        }
                      }}
                      style={{ display: 'none' }}
                      id="csv-input"
                    />
                    <Button
                      component="label"
                      variant="contained"
                      htmlFor="csv-input"
                      disabled={loading}
                      endIcon={loading ? <CircularProgress size={20} /> : <Upload size={20} />}
                    >
                      {loading ? 'Uploading...' : 'Select CSV File'}
                    </Button>
                  </Stack>
                </Box>

                {selectedFile && !uploadedFile && (
                  <Alert severity="info">
                    Selected: <strong>{selectedFile.name}</strong> ({formatBytes(selectedFile.size)})
                  </Alert>
                )}
              </>
            ) : (
              <>
                {/* Success State */}
                <Alert severity="success" icon={<CheckCircle />}>
                  Dataset uploaded successfully!
                </Alert>

                {/* Dataset Summary */}
                <Paper sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
                  <Stack spacing={2}>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          File Name
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {uploadedFile.filename}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Total Rows
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {uploadedFile.rows.toLocaleString()}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          Total Columns
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {uploadedFile.columns.length}
                        </Typography>
                      </Box>
                      <Box>
                        <Typography variant="caption" color="textSecondary">
                          File Size
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                          {formatBytes(uploadedFile.size_bytes)}
                        </Typography>
                      </Box>
                    </Box>

                    {/* Column Types */}
                    <Box>
                      <Typography variant="subtitle2" gutterBottom>
                        Column Types:
                      </Typography>
                      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                        {uploadedFile.columns.map((col) => (
                          <Typography
                            key={col}
                            variant="caption"
                            sx={{
                              px: 1.5,
                              py: 0.5,
                              backgroundColor: 'primary.light',
                              borderRadius: 1,
                              color: 'primary.contrastText',
                            }}
                          >
                            {col} <small>({uploadedFile.dtypes[col]})</small>
                          </Typography>
                        ))}
                      </Stack>
                    </Box>
                  </Stack>
                </Paper>

                {/* Action Buttons */}
                <Stack direction="row" spacing={2}>
                  <Button
                    variant="contained"
                    onClick={() => {
                      setUploadedFile(null)
                      setSelectedFile(null)
                    }}
                  >
                    Upload Different File
                  </Button>
                  <Button variant="contained" color="success" onClick={onNext}>
                    Continue to Configuration
                  </Button>
                </Stack>
              </>
            )}
          </Stack>
        </CardContent>
      </Card>
    </Box>
  )
}

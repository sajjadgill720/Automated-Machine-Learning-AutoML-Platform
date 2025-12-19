/**
 * Loading Skeleton Components
 * Provides visual feedback while data is loading
 */

import React from 'react'
import { Box, Skeleton, Card, CardContent, Stack } from '@mui/material'

export const LoadingSkeleton: React.FC<{ count?: number }> = ({ count = 1 }) => (
  <Box sx={{ width: '100%', pt: 2 }}>
    {Array.from({ length: count }).map((_, idx) => (
      <Card key={idx} sx={{ mb: 2 }}>
        <CardContent>
          <Skeleton variant="text" width="40%" height={32} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="100%" height={20} />
          <Skeleton variant="text" width="90%" height={20} sx={{ mt: 1 }} />
        </CardContent>
      </Card>
    ))}
  </Box>
)

export const TableLoadingSkeleton: React.FC<{ rows?: number; columns?: number }> = ({
  rows = 5,
  columns = 4,
}) => (
  <Box sx={{ width: '100%', overflow: 'auto' }}>
    <Stack spacing={1}>
      {/* Header */}
      <Box sx={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, 1fr)`, gap: 1 }}>
        {Array.from({ length: columns }).map((_, idx) => (
          <Skeleton key={`header-${idx}`} variant="text" width="100%" height={32} />
        ))}
      </Box>
      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <Box
          key={`row-${rowIdx}`}
          sx={{ display: 'grid', gridTemplateColumns: `repeat(${columns}, 1fr)`, gap: 1 }}
        >
          {Array.from({ length: columns }).map((_, colIdx) => (
            <Skeleton key={`cell-${rowIdx}-${colIdx}`} variant="text" width="100%" height={24} />
          ))}
        </Box>
      ))}
    </Stack>
  </Box>
)

export const ChartLoadingSkeleton: React.FC = () => (
  <Box sx={{ width: '100%', height: 300, mb: 2 }}>
    <Skeleton variant="rectangular" width="100%" height="100%" />
  </Box>
)

# Frontend Quick Reference Guide

## Project Structure Quick Lookup

```
frontend/
├── src/
│   ├── api/automl.ts              ← API service (all backend calls)
│   ├── components/                ← Reusable UI components
│   ├── hooks/useAutoML.ts         ← Custom React hooks
│   ├── pages/                     ← Full page components
│   ├── store/automlStore.ts       ← Zustand state management
│   ├── styles/                    ← CSS stylesheets
│   ├── types/automl.ts            ← TypeScript type definitions
│   ├── utils/helpers.ts           ← Utility functions
│   ├── App.tsx                    ← Main app (routing)
│   └── main.tsx                   ← Entry point
├── package.json                   ← Dependencies
├── tsconfig.json                  ← TypeScript config
├── vite.config.js                 ← Vite config
├── FRONTEND_README.md             ← Full documentation
└── IMPLEMENTATION_GUIDE.md        ← Architecture guide
```

## Common Tasks Cheat Sheet

### 1. Add a New Component

```bash
# Create file
touch src/components/MyComponent.tsx

# File template
import React from 'react'
import { Box, Card } from '@mui/material'

interface MyComponentProps {
  prop1: string
  onAction: () => void
}

export const MyComponent: React.FC<MyComponentProps> = ({ prop1, onAction }) => {
  return (
    <Card>
      <p>{prop1}</p>
      <button onClick={onAction}>Click</button>
    </Card>
  )
}
```

### 2. Add a Type Definition

```typescript
// In src/types/automl.ts
export interface MyType {
  id: string
  name: string
  data: any[]
}

export type MyEnum = 'option1' | 'option2'
```

### 3. Add to Zustand Store

```typescript
// In src/store/automlStore.ts
export const useAutoMLStore = create<AutoMLState>((set) => ({
  // ... existing state
  myValue: 'initial',
  setMyValue: (value) => set({ myValue: value }),
}))
```

### 4. Call the API

```typescript
import { automlAPI } from '@api/automl'

// In a component
try {
  const result = await automlAPI.uploadDataset(file)
  console.log(result)
} catch (error) {
  console.error(error.message)
}
```

### 5. Use React Query

```typescript
import { useQuery } from '@tanstack/react-query'
import { automlAPI } from '@api/automl'

export const MyComponent = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['jobResults', jobId],
    queryFn: () => automlAPI.getResults(jobId),
    enabled: !!jobId,
  })

  if (isLoading) return <div>Loading...</div>
  if (error) return <div>Error: {error.message}</div>
  return <div>{data?.best_model}</div>
}
```

### 6. Use Zustand Store

```typescript
import { useAutoMLStore } from '@store/automlStore'

export const MyComponent = () => {
  const { config, updateConfig } = useAutoMLStore()

  return (
    <button onClick={() => updateConfig({ target_column: 'new_value' })}>
      {config.target_column}
    </button>
  )
}
```

### 7. Add Form Validation

```typescript
interface FormData {
  email: string
  password: string
}

const validateForm = (data: FormData): Record<string, string> => {
  const errors: Record<string, string> = {}

  if (!data.email || !data.email.includes('@')) {
    errors.email = 'Invalid email'
  }

  if (!data.password || data.password.length < 8) {
    errors.password = 'Password too short'
  }

  return errors
}
```

### 8. Add Error Handling

```typescript
try {
  await apiCall()
} catch (err) {
  const message = err instanceof Error ? err.message : 'Unknown error'
  setError(message)
  enqueueSnackbar(message, { variant: 'error' })
}
```

### 9. Add Loading State

```typescript
import { LoadingSkeleton } from '@components/index'

export const MyComponent = () => {
  const { data, isLoading } = useQuery(...)

  if (isLoading) return <LoadingSkeleton count={3} />
  return <div>{/* content */}</div>
}
```

### 10. Add Toast Notification

```typescript
import { useSnackbar } from 'notistack'

export const MyComponent = () => {
  const { enqueueSnackbar } = useSnackbar()

  const handleSuccess = () => {
    enqueueSnackbar('Success!', { variant: 'success' })
  }

  const handleError = () => {
    enqueueSnackbar('Error!', { variant: 'error' })
  }

  return (
    <>
      <button onClick={handleSuccess}>Success</button>
      <button onClick={handleError}>Error</button>
    </>
  )
}
```

## State Management Patterns

### Zustand Store Pattern
```typescript
// Define state interface
interface MyState {
  value: string
  setValue: (v: string) => void
}

// Create store
export const useMyStore = create<MyState>((set) => ({
  value: 'initial',
  setValue: (v) => set({ value: v }),
}))

// Use in component
const { value, setValue } = useMyStore()
```

### React Query Pattern
```typescript
// Define query
const useMyQuery = (id: string) => {
  return useQuery({
    queryKey: ['myData', id],
    queryFn: () => api.fetchData(id),
  })
}

// Use in component
const { data, isLoading, error } = useMyQuery(id)
```

### Combined Pattern
```typescript
// Query for server state
const { data } = useQuery(...)

// Store for UI state
const { isModalOpen, setIsModalOpen } = useUIStore()

// Form validation
const [errors, setErrors] = useState({})
```

## Styling Patterns

### MUI Styling with sx prop
```typescript
<Box sx={{ 
  p: 2,                    // padding
  mb: 3,                   // margin-bottom
  backgroundColor: '#fff', 
  borderRadius: 1,
  '&:hover': { shadow: 2 }
}}>
  Content
</Box>
```

### CSS Classes
```typescript
<Box className="animate-slide-up" sx={{ /* ... */ }}>
  Content
</Box>
```

### Responsive Design
```typescript
<Grid container spacing={2}>
  <Grid item xs={12} sm={6} md={4}>
    Full width on mobile, half on tablet, 1/3 on desktop
  </Grid>
</Grid>
```

## Routing Patterns

### Navigation
```typescript
import { useNavigate } from 'react-router-dom'

const navigate = useNavigate()
navigate('/results')      // Go to page
navigate(-1)              // Go back
```

### Current Route
```typescript
import { useLocation } from 'react-router-dom'

const location = useLocation()
if (location.pathname === '/') { /* home */ }
```

## Data Flow Patterns

### Simple Component
```typescript
const MyComponent = () => {
  const [state, setState] = useState('')

  return (
    <input
      value={state}
      onChange={(e) => setState(e.target.value)}
    />
  )
}
```

### With API Call
```typescript
const MyComponent = () => {
  const { data } = useQuery({
    queryKey: ['data'],
    queryFn: () => api.fetchData(),
  })

  return <div>{data?.title}</div>
}
```

### With Global State
```typescript
const MyComponent = () => {
  const { value, setValue } = useAutoMLStore()

  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  )
}
```

### Complex Workflow
```typescript
const MyComponent = () => {
  // Global state
  const { config, updateConfig } = useAutoMLStore()

  // Server state
  const { data } = useQuery(...)

  // Local state
  const [local, setLocal] = useState('')

  // Effects
  useEffect(() => {
    if (data) {
      updateConfig({ ... })
    }
  }, [data])

  return (
    <div>
      {/* Form using local state */}
      {/* Display using global state */}
      {/* Show query data */}
    </div>
  )
}
```

## Common Imports

```typescript
// React
import React, { useState, useEffect, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'

// Material-UI
import { Box, Button, Card, Grid, Stack, Typography } from '@mui/material'

// Icons
import { Upload, Download, Settings } from 'lucide-react'

// Our code
import { useAutoMLStore } from '@store/automlStore'
import { automlAPI } from '@api/automl'
import { formatMetric } from '@utils/helpers'

// Third party
import { useQuery } from '@tanstack/react-query'
import { useSnackbar } from 'notistack'
```

## Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=300000
VITE_MAX_FILE_SIZE_MB=500
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL
const timeout = parseInt(import.meta.env.VITE_API_TIMEOUT)
```

## Development Commands

```bash
npm run dev          # Start dev server (localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # Check TypeScript
```

## Browser DevTools Tips

### React DevTools
- Inspect component hierarchy
- View props and state
- Trace renders

### Redux DevTools (works with Zustand)
- View state changes
- Time-travel debugging

### Network Tab
- Monitor API calls
- Check response codes
- View response payload

### Application Tab
- Check localStorage
- View cookies
- Clear cache

## Code Quality Checklist

- [ ] TypeScript strict mode enabled
- [ ] No `any` types without justification
- [ ] Proper error handling
- [ ] Loading states for async operations
- [ ] Comments for complex logic
- [ ] Reusable components
- [ ] Consistent naming conventions
- [ ] No console.logs in production
- [ ] Proper cleanup in useEffect
- [ ] Accessible markup (ARIA labels)

## Performance Tips

1. **Memoization**
   ```typescript
   const Component = React.memo(MyComponent)
   const callback = useCallback(() => {}, [deps])
   ```

2. **Lazy Loading**
   ```typescript
   const HeavyComponent = React.lazy(() => import('./Heavy'))
   ```

3. **Image Optimization**
   ```typescript
   <img src="..." loading="lazy" alt="..." />
   ```

4. **React Query Caching**
   ```typescript
   staleTime: 5 * 60 * 1000  // 5 min cache
   cacheTime: 10 * 60 * 1000 // 10 min memory
   ```

## Testing Commands

```bash
npm test              # Run tests (if configured)
npm run type-check    # TypeScript check
```

## Debugging Tips

```typescript
// Console logging
console.log({ variable })  // Object shorthand
console.table(data)        // Table format

// Debugger
debugger  // Browser will pause here

// React DevTools
// Inspect components, view props/state

// Network tab
// Check API requests and responses

// localStorage
localStorage.setItem('key', JSON.stringify(value))
```

---

**Last Updated**: 2025
**Version**: 1.0.0

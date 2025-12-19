# AutoML Frontend - Implementation Guide

## Overview

This guide provides comprehensive documentation for the production-grade AutoML frontend, including architecture decisions, implementation details, and deployment instructions.

## Quick Start

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Create environment file (optional)
cp .env.example .env.local

# 3. Start development server
npm run dev

# 4. Open browser to http://localhost:5173
```

## Architecture Decisions

### Technology Choices

#### React 18 + TypeScript
- **Why**: Industry standard for web UIs with type safety
- **Benefit**: Catches errors at compile time, better DX
- **Trade-off**: Slightly larger bundle, but worth the safety

#### Vite instead of Create React App
- **Why**: Faster HMR, smaller bundles, modern tooling
- **Benefit**: ~10x faster dev server, instant HMR updates
- **Trade-off**: Less ecosystem plugins, but most are unnecessary

#### Zustand for State Management
- **Why**: Minimal boilerplate, excellent TypeScript support
- **Benefit**: Simple API, no providers needed, small bundle
- **Trade-off**: Manual optimization for large apps (not an issue here)

#### React Query (TanStack Query)
- **Why**: Industry-standard server state management
- **Benefit**: Automatic caching, background refetching, deduplication
- **Trade-off**: Learning curve for complex patterns

#### Material-UI Components
- **Why**: Professional, accessible, highly customizable
- **Benefit**: Consistent design language, accessibility built-in
- **Trade-off**: Large bundle (but tree-shaken well)

#### Recharts for Visualizations
- **Why**: React-native, responsive, good for this use case
- **Benefit**: Easy to integrate, good defaults, composable
- **Trade-off**: Limited for very complex visualizations

### Design Patterns

#### 1. Container/Presentational Components
```typescript
// Container (logic)
export const MyFeature = () => {
  const [data, setData] = useState(...)
  return <MyFeaturePresentation data={data} />
}

// Presentation (UI)
const MyFeaturePresentation = ({ data }) => (
  <div>{data}</div>
)
```

#### 2. Custom Hooks for Logic
```typescript
// Logic isolated in hooks
export const useMyFeature = () => {
  const [state, setState] = useState(...)
  useEffect(() => { ... }, [])
  return { state, setState }
}

// Clean components
const MyComponent = () => {
  const { state } = useMyFeature()
  return <div>{state}</div>
}
```

#### 3. Centralized API Service
```typescript
// All API calls go through service
class AutoMLAPIService {
  async runPipeline(config) { ... }
  async getResults(jobId) { ... }
}

// Used consistently
const { data } = useQuery(() => automlAPI.getResults(jobId))
```

#### 4. Type-Driven Development
```typescript
// Types define contracts
interface DatasetInfo {
  filename: string
  rows: number
  columns: string[]
}

// Implementation follows types
const handleUpload = async (file): Promise<DatasetInfo> => {
  return automlAPI.uploadDataset(file)
}
```

### State Flow

```
┌─────────────────────────────────────┐
│   User Interaction                  │
│   (Click, Input, etc)               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Component Event Handlers          │
│   (onClick, onChange, etc)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Zustand Store Update              │
│   (useAutoMLStore.updateConfig)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Component Re-render               │
│   (via useAutoMLStore hook)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   Updated UI Display                │
└─────────────────────────────────────┘

API Calls:
┌─────────────────────────────────────┐
│   React Query / useQuery            │
│   (Server State)                    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   automlAPI Service                 │
│   (HTTP requests)                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   FastAPI Backend                   │
└─────────────────────────────────────┘
```

## Component Architecture

### 1. Layout Components

**Layout.tsx** - Main application shell
- App header with branding
- Navigation buttons
- Content area
- Footer
- Global error handling

### 2. Page Components

**Home.tsx** - Landing/marketing page
- Feature showcase
- Quick start guide
- Call-to-action

**Run.tsx** - AutoML wizard workflow
- Step indicator
- Dynamic step rendering
- Validation and navigation
- Error display

**Results.tsx** - Results display
- Job polling and status
- Metrics visualization
- Model information
- Export functionality

### 3. Step Components (called by Run.tsx)

**DatasetUpload.tsx** (Step 0)
- Drag-and-drop file zone
- File validation
- Dataset preview
- Column statistics

**TaskConfig.tsx** (Step 1)
- Task type selection
- Target column selection
- Data type override
- Help text and examples

**PipelineConfig.tsx** (Step 2)
- Feature selection toggle
- Hyperparameter tuning toggle
- Search method selection
- Configuration summary

### 4. Results Components (used by Results.tsx)

**MetricsTable.tsx**
- Task-aware metric selection
- Formatted values
- Metric descriptions
- Tooltip explanations

**FeatureImportance.tsx**
- Bar chart visualization
- Top-N feature filtering
- Color-coded importance
- Responsive sizing

**ConfusionMatrix.tsx**
- Matrix heatmap
- Color intensity mapping
- Readable labels
- Interpretation guide

### 5. Common Components

**ErrorBoundary.tsx**
- Catches React errors
- Displays fallback UI
- Recovery option

**LoadingSkeleton.tsx**
- Table skeleton
- Card skeleton
- Chart skeleton
- Smooth transitions

**StepIndicator.tsx**
- Visual progress indication
- Current step highlight
- Step count

## Data Flow Examples

### Example 1: File Upload Flow

```
User selects file
    ↓
DatasetUpload.handleFileChange()
    ↓
validateCSVFile() → ValidationResult
    ↓
automlAPI.uploadDataset(file) → DatasetInfo
    ↓
useAutoMLStore.setUploadedFile(datasetInfo)
    ↓
Store subscribers notified
    ↓
Run component re-renders
    ↓
User can proceed to next step
```

### Example 2: Job Status Polling Flow

```
useJobPolling(jobId) triggered
    ↓
React Query starts polling
    ↓
Every 2 seconds: automlAPI.getJobStatus(jobId)
    ↓
Status: "processing" → Keep polling
    ↓
Status: "completed" → Stop polling, update jobResult
    ↓
Results.tsx displays results
    ↓
useElapsedTime tracks time
    ↓
Final result rendered
```

### Example 3: Form Validation Flow

```
User changes target column
    ↓
TaskConfig.onChange() → updateConfig()
    ↓
Zustand updates config.target_column
    ↓
useCanProceedToNextStep() evaluates
    ↓
Returns true if target_column is set
    ↓
Next button becomes enabled
    ↓
User can click to proceed
```

## Error Handling Strategy

### Layer 1: API Service
```typescript
// Extract error details
private handleError(error: AxiosError) {
  const message = error.response?.data?.detail || error.message
  const enhancedError = new Error(message)
  enhancedError.status = error.response?.status
  return Promise.reject(enhancedError)
}
```

### Layer 2: Component-Level
```typescript
try {
  const result = await automlAPI.uploadDataset(file)
  setUploadedFile(result)
} catch (err) {
  setError(err instanceof Error ? err.message : 'Unknown error')
}
```

### Layer 3: Error Boundary
```typescript
// Catches unhandled React errors
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.error(error, errorInfo)
  }
}
```

### Layer 4: Toast Notifications
```typescript
// User-friendly feedback
enqueueSnackbar(errorMessage, { variant: 'error' })
```

## TypeScript Best Practices

### 1. Strict Mode Enabled
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### 2. Prop Typing for Components
```typescript
interface DatasetUploadProps {
  onNext: () => void
}

export const DatasetUpload: React.FC<DatasetUploadProps> = ({ onNext }) => {
  // Full type safety
}
```

### 3. API Response Typing
```typescript
interface PipelineResult {
  job_id: string
  status: JobStatus
  best_model?: string
  metrics?: MetricsObject
  error?: string
}

const { data } = useQuery<PipelineResult>(() => ...)
```

### 4. Union Types for State
```typescript
type JobStatus = 'pending' | 'processing' | 'completed' | 'error'

// Exhaustive checking in if statements
if (status === 'completed') { ... }
else if (status === 'error') { ... }
else if (status === 'processing') { ... }
```

## Performance Optimizations

### 1. Code Splitting
Vite automatically code-splits:
- Pages split into separate chunks
- Lazy loading via React.lazy()
- Dynamic imports

### 2. Image Optimization
- Use responsive images with srcset
- Lazy load images with loading="lazy"
- Compress images before deployment

### 3. Memoization
```typescript
const MemoizedComponent = React.memo(Component, (prevProps, nextProps) => {
  return prevProps.id === nextProps.id  // Return true if equal
})

const callback = useCallback(() => { ... }, [dependency])
```

### 4. React Query Optimization
```typescript
useQuery({
  queryKey: ['jobStatus', jobId],
  refetchInterval: 2000,  // Smart polling
  staleTime: 0,           // Always refetch
  cacheTime: 300000,      // Keep in cache 5 min
})
```

### 5. Bundle Size
- Tree-shaking unused code
- Dynamic imports for heavy libraries
- Polyfill only what's needed

## Testing Strategy

### Unit Tests (Components)
```typescript
// Test component rendering and interactions
describe('DatasetUpload', () => {
  it('should show file input', () => {
    render(<DatasetUpload onNext={jest.fn()} />)
    expect(screen.getByLabelText('Select CSV File')).toBeInTheDocument()
  })
})
```

### Integration Tests (Flows)
```typescript
// Test complete user workflows
describe('AutoML Workflow', () => {
  it('should complete full run', async () => {
    // Upload → Configure → Run → See Results
  })
})
```

### E2E Tests (Cypress)
```typescript
// Test full application in browser
describe('App', () => {
  it('should upload and run pipeline', () => {
    cy.visit('/')
    cy.get('input[type=file]').selectFile('data.csv')
    // ... continue workflow
  })
})
```

## Deployment Guide

### 1. Build for Production
```bash
npm run build
```

Creates optimized `dist/` folder:
- HTML minified
- CSS bundled and minified
- JavaScript bundled and minified
- Source maps generated

### 2. Deployment Options

#### Option A: Static Hosting (Vercel/Netlify)
```bash
# Deploy dist/ folder
vercel deploy dist/
```

#### Option B: Docker
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY . .
RUN npm ci && npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=build /app/dist ./dist
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

#### Option C: Nginx
```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /var/www/automl/frontend/dist;
    index index.html index.htm;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Environment Configuration

Create `.env.production` for production values:
```env
VITE_API_BASE_URL=https://api.your-domain.com
VITE_API_TIMEOUT=300000
```

### 4. Performance Checklist
- [ ] Minified bundles
- [ ] Gzip compression enabled
- [ ] CDN for assets
- [ ] HTTP/2 enabled
- [ ] Caching headers set
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Error tracking (Sentry)
- [ ] Analytics (Google Analytics)
- [ ] Performance monitoring

## Maintenance & Monitoring

### 1. Error Tracking
```typescript
// Integrate Sentry for error monitoring
import * as Sentry from "@sentry/react"

Sentry.init({
  dsn: process.env.VITE_SENTRY_DSN,
  environment: process.env.NODE_ENV,
})
```

### 2. Performance Monitoring
```typescript
// Web Vitals tracking
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals'

getCLS(console.log)
getFID(console.log)
// ... etc
```

### 3. Analytics
```typescript
// Track user interactions
gtag('event', 'pipeline_started', {
  task_type: config.task_type,
  feature_selection: config.feature_selection_enabled,
})
```

### 4. Dependency Updates
```bash
# Check for outdated packages
npm outdated

# Update to latest
npm update

# Audit for vulnerabilities
npm audit
npm audit fix
```

## Troubleshooting

### Build Issues
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm ci

# Check Node version
node --version  # Should be 16+

# Build with verbose output
npm run build -- --debug
```

### Runtime Issues
```bash
# Check console errors (F12 → Console)
# Check Network tab (F12 → Network)
# Check Application tab for localStorage

# Clear cache
rm -rf .next .vite dist node_modules
npm ci
npm run dev
```

### API Connection Issues
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check CORS headers in backend response
3. Verify proxy configuration in vite.config.ts
4. Check Network tab for actual request/response

## Future Enhancements

### Short-term (v1.1)
- [ ] Advanced data profiling
- [ ] Model comparison view
- [ ] Custom metric builder
- [ ] Export models

### Medium-term (v1.2)
- [ ] Dark mode
- [ ] Real-time collaboration
- [ ] Extended EDA charts
- [ ] A/B testing framework

### Long-term (v2.0)
- [ ] SHAP explanability
- [ ] AutoML Studio (advanced)
- [ ] Mobile app
- [ ] API for programmatic use

---

For questions or issues, refer to [FRONTEND_README.md](./FRONTEND_README.md)

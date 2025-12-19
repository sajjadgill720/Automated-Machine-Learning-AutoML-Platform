# AutoML Platform - Frontend

A production-grade React + TypeScript web interface for the AutoML System. Provides an enterprise-level user experience for building, configuring, and monitoring automated machine learning pipelines.

## Architecture Overview

```
src/
├── api/                    # API service layer
│   └── automl.ts          # Centralized API client with error handling
├── components/            # Reusable React components
│   ├── Layout.tsx         # Main app layout
│   ├── ErrorBoundary.tsx  # Error boundary for crash handling
│   ├── StepIndicator.tsx  # Workflow progress indicator
│   ├── DatasetUpload.tsx  # File upload component
│   ├── TaskConfig.tsx     # Task configuration form
│   ├── PipelineConfig.tsx # Pipeline options form
│   ├── MetricsTable.tsx   # Results metrics display
│   ├── ConfusionMatrix.tsx # Classification matrix heatmap
│   ├── FeatureImportance.tsx # Feature importance visualization
│   └── LoadingSkeleton.tsx # Loading state UI
├── hooks/                 # Custom React hooks
│   └── useAutoML.ts       # AutoML-specific hooks
├── pages/                 # Page components
│   ├── Home.tsx           # Landing page
│   ├── Run.tsx            # AutoML workflow wizard
│   └── Results.tsx        # Results display page
├── store/                 # State management
│   └── automlStore.ts     # Zustand store for app state
├── types/                 # TypeScript definitions
│   └── automl.ts          # Comprehensive type definitions
├── utils/                 # Utility functions
│   └── helpers.ts         # Formatting and validation helpers
├── styles/                # Global styles
│   ├── globals.css        # Global resets and animations
│   └── layout.css         # Layout component styles
├── App.tsx                # Main app component with routing
└── main.tsx               # Entry point
```

## Key Features

### 1. **Step-Based Workflow Wizard**
- **Step 1: Dataset Upload** - Drag-and-drop CSV upload with validation
- **Step 2: Task Configuration** - Select task type and target column
- **Step 3: Pipeline Options** - Configure feature selection and hyperparameter tuning
- **Step 4: Review** - Review all settings before running
- **Step 5: Results** - View metrics, models, and feature importance

### 2. **Enterprise UX Patterns**
- **Progressive Disclosure** - Show relevant options based on selections
- **Clear Validation** - Real-time feedback on form validity
- **Loading States** - Skeleton screens during data fetch
- **Error Boundaries** - Graceful error handling and recovery
- **Toast Notifications** - Non-intrusive feedback messages

### 3. **State Management**
- **Zustand Store** - Lightweight, performant state management
- **Persistent Workflow** - State preserved across navigation
- **Utility Hooks** - Derived state and validation

### 4. **API Integration**
- **Axios Client** - Typed HTTP requests with error handling
- **React Query** - Server state management with caching
- **Polling** - Long-running job status tracking with exponential backoff
- **Error Handling** - Comprehensive error extraction and user feedback

### 5. **Visualizations**
- **Recharts** - Feature importance bar charts
- **Heatmaps** - Confusion matrix visualization
- **Metrics Tables** - Formatted performance metrics with descriptions
- **Charts** - Classification and regression metrics

## Technology Stack

### Frontend Framework
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool (fast HMR, optimized bundles)
- **React Router** - Client-side routing

### State & Data
- **Zustand** - State management
- **React Query (@tanstack/react-query)** - Server state & caching
- **Axios** - HTTP client

### UI Components
- **Material-UI (MUI)** - Component library
- **Emotion** - CSS-in-JS styling
- **Recharts** - Data visualization
- **Lucide React** - Icon library

### Code Quality
- **TypeScript** - Static typing
- **ESLint** - Code linting (via Vite)
- **Prettier** - Code formatting

## Installation

### Prerequisites
- Node.js 16+ and npm/yarn
- Python 3.8+ (for backend)
- FastAPI backend running on `http://localhost:8000`

### Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local (optional, defaults to localhost:8000)
cp .env.example .env.local

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (Vite's default) or `http://localhost:3000` (if configured).

## Available Scripts

```bash
# Development server with HMR
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Type checking
npm run type-check
```

## API Endpoints

The frontend communicates with these backend endpoints:

### Dataset Management
- `POST /api/upload` - Upload CSV file
- `GET /api/preview` - Get dataset preview

### Pipeline Execution
- `POST /api/run` - Start AutoML pipeline
- `GET /api/status/{job_id}` - Poll job status
- `GET /api/results/{job_id}` - Get completed results
- `POST /api/cancel/{job_id}` - Cancel running job

### Health
- `GET /api/health` - Health check endpoint

## Configuration

### Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api      # Backend URL
VITE_API_TIMEOUT=300000                           # Request timeout (5min)
VITE_MAX_FILE_SIZE_MB=500                         # File upload limit
VITE_JOB_POLL_INTERVAL_MS=2000                    # Polling interval
```

### Theme Customization

Edit `src/App.tsx` theme object to customize:
- Primary/secondary colors
- Typography
- Component overrides
- Spacing and breakpoints

## Component Documentation

### DatasetUpload
Handles CSV file upload with drag-and-drop support.

```tsx
<DatasetUpload onNext={() => handleNext()} />
```

Features:
- Drag-and-drop file zone
- File validation (CSV only, size limit)
- Dataset preview and statistics
- Column type detection

### TaskConfig
Configuration for task type and target variable.

```tsx
<TaskConfig onNext={() => {}} onBack={() => {}} />
```

Features:
- Task type selection (classification/regression)
- Target column selection
- Data type override (optional)
- Inline help text

### PipelineConfig
Configure AutoML pipeline options.

```tsx
<PipelineConfig onNext={() => {}} onBack={() => {}} />
```

Features:
- Feature selection toggle
- Hyperparameter tuning toggle
- Search method selection (grid/random/bayesian)
- Configuration summary

### MetricsTable
Display evaluation metrics.

```tsx
<MetricsTable metrics={results.metrics} taskType="classification" />
```

Features:
- Task-aware metric selection
- Metric descriptions and tooltips
- Formatted numeric values
- Professional table layout

### FeatureImportance
Visualize feature importance.

```tsx
<FeatureImportance features={results.selected_features} />
```

Features:
- Top-N feature bar chart
- Color-coded importance levels
- Responsive sizing
- Export-ready visualization

### ConfusionMatrix
Classification confusion matrix heatmap.

```tsx
<ConfusionMatrix data={results.confusion_matrix} />
```

Features:
- Color-coded matrix cells
- Label-based indexing
- Interpretation guide
- Professional styling

## State Management (Zustand)

### Store Structure

```typescript
interface AutoMLState {
  // Dataset
  uploadedFile: DatasetInfo | null
  setUploadedFile: (file: DatasetInfo | null) => void

  // Configuration
  config: AutoMLConfig
  updateConfig: (partial: Partial<AutoMLConfig>) => void

  // Execution
  currentJobId: string | null
  jobResult: PipelineResult | null

  // UI State
  currentStep: number
  isLoading: boolean
  error: string | null
  success: string | null

  // Actions
  reset: () => void
}
```

### Usage

```typescript
import { useAutoMLStore } from '@store/automlStore'

function MyComponent() {
  const { config, updateConfig, currentStep } = useAutoMLStore()

  return (
    <button onClick={() => updateConfig({ target_column: 'value' })}>
      Update Config
    </button>
  )
}
```

## Custom Hooks

### useJobPolling
Poll job status with automatic refetching.

```typescript
const { data, isLoading } = useJobPolling(jobId, enabled)
```

### useJobResults
Fetch completed job results.

```typescript
const { data, error } = useJobResults(jobId)
```

### useElapsedTime
Track elapsed time since job start.

```typescript
const elapsed = useElapsedTime(startTime)  // "2m 30s"
```

### useLocalStorage
Persist state to browser storage.

```typescript
const [value, setValue] = useLocalStorage('key', defaultValue)
```

## Error Handling

### API Errors
The API service extracts and standardizes error messages:

```typescript
try {
  await automlAPI.uploadDataset(file)
} catch (err) {
  console.error(err.message)  // Extracted error detail
}
```

### Component Errors
Error Boundary catches and displays React errors gracefully.

### Form Validation
Real-time validation with step-based progression.

## Performance Optimizations

1. **Code Splitting** - Vite automatically splits code
2. **React Query Caching** - Prevents redundant API calls
3. **Zustand** - Minimal re-renders via fine-grained updates
4. **Lazy Loading** - Images and heavy components loaded on demand
5. **Memoization** - useCallback for stable references
6. **Production Build** - Optimized bundle with tree-shaking

## Development Workflow

1. **Component Development**
   - Create in `src/components/`
   - Add TypeScript typing
   - Export in `src/components/index.ts`

2. **State Management**
   - Use Zustand store for global state
   - Custom hooks for derived state

3. **API Integration**
   - Use `automlAPI` service
   - Add types to `src/types/automl.ts`
   - Handle errors gracefully

4. **Testing**
   - Unit tests (pytest for Python backend)
   - Integration tests (E2E with Cypress)
   - Manual testing in browser

## Deployment

### Build for Production

```bash
npm run build
```

Creates optimized build in `dist/` directory.

### Deployment Options

1. **Static Hosting** (Vercel, Netlify)
   ```bash
   npm run build
   # Deploy dist/ folder
   ```

2. **Docker**
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY . .
   RUN npm install && npm run build
   EXPOSE 3000
   CMD ["npm", "run", "preview"]
   ```

3. **Custom Server**
   - Serve `dist/` folder
   - Proxy `/api/` to backend
   - Configure CORS if needed

## Troubleshooting

### API Connection Issues
```
Check backend is running on http://localhost:8000
Check VITE_API_BASE_URL in .env.local
Check CORS configuration in backend
```

### Build Errors
```
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Type Errors
```
npm run type-check
Fix any TypeScript errors reported
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

- [ ] Model comparison view
- [ ] Custom metric creation
- [ ] Advanced filtering and search
- [ ] Dark mode support
- [ ] Data profiling and EDA
- [ ] Model explainability (SHAP)
- [ ] A/B testing framework
- [ ] Collaborative features
- [ ] Real-time collaboration with WebSockets
- [ ] Advanced visualization suite

## Contributing

1. Follow TypeScript strict mode
2. Write meaningful component names
3. Add JSDoc comments for complex logic
4. Keep components focused and reusable
5. Test thoroughly before pushing
6. Update types when adding features

## License

MIT - See LICENSE file

---

For backend documentation, see [../README.md](../README.md)

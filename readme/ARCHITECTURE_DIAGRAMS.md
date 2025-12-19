# AutoML Platform - Architecture Diagram

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTOML WEB PLATFORM                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + TypeScript)                │
│                     ✅ DELIVERED & COMPLETE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │    Home      │  │    Run       │  │   Results    │            │
│  │   Page       │  │   Page       │  │    Page      │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Step-Based Workflow Components                  │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ 1. DatasetUpload   → Drag-drop, validate, preview     │    │
│  │ 2. TaskConfig      → Select task, target, options     │    │
│  │ 3. PipelineConfig  → Feature selection, tuning        │    │
│  │ 4. Review          → Confirm settings                 │    │
│  │ 5. Results         → Metrics, charts, export          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Visualization Components                         │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ • MetricsTable       → Performance metrics              │    │
│  │ • FeatureImportance  → Bar chart visualization         │    │
│  │ • ConfusionMatrix    → Heatmap for classification      │    │
│  │ • LoadingSkeleton    → Smooth loading states           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │          State Management & Data                        │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ Zustand Store        → Global UI state                 │    │
│  │ React Query          → Server state (caching)          │    │
│  │ Custom Hooks         → useJobPolling, useElapsedTime  │    │
│  │ Validation           → Form validation, errors         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              API Service Layer (Axios)                  │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ • uploadDataset()     • runPipeline()                   │    │
│  │ • getResults()        • getJobStatus()                  │    │
│  │ • pollJobCompletion() • healthCheck()                   │    │
│  │ • Error handling      • Request/response typing         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │         Infrastructure & Utilities                      │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │ • Material-UI         → Component library               │    │
│  │ • Recharts            → Data visualization              │    │
│  │ • React Router        → Client-side routing             │    │
│  │ • Notistack           → Toast notifications             │    │
│  │ • TypeScript          → Type safety (strict mode)       │    │
│  │ • Vite                → Fast build & dev server         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI) - EXISTING                    │
│                  ✅ ALREADY PROVIDED                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │            REST API Endpoints                            │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ POST   /api/upload          → Upload CSV file           │   │
│  │ GET    /api/preview         → Dataset preview           │   │
│  │ POST   /api/run             → Start AutoML pipeline     │   │
│  │ GET    /api/status/{job_id} → Poll job status          │   │
│  │ GET    /api/results/{job_id}→ Get completed results    │   │
│  │ POST   /api/cancel/{job_id} → Cancel running job       │   │
│  │ GET    /api/health          → Health check             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │           AutoML Pipeline (Existing)                    │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │ • Data preprocessing   • Feature selection             │   │
│  │ • Model training       • Hyperparameter tuning         │   │
│  │ • Model evaluation     • Results aggregation           │   │
│  │ • Support for: Tabular, Text, Image, Time-Series      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Component Hierarchy

```
App
├── Layout
│   ├── AppBar (Header)
│   ├── Container (Main Content)
│   │   └── Routes
│   │       ├── Home Page
│   │       │   ├── Hero Section
│   │       │   ├── Features Grid
│   │       │   ├── How It Works
│   │       │   └── CTA Section
│   │       ├── Run Page (Wizard)
│   │       │   ├── StepIndicator
│   │       │   ├── Conditional Step Components
│   │       │   │   ├── Step 0: DatasetUpload
│   │       │   │   │   ├── DragDropZone
│   │       │   │   │   ├── FileInput
│   │       │   │   │   └── DatasetSummary
│   │       │   │   ├── Step 1: TaskConfig
│   │       │   │   │   ├── TaskTypeSelect
│   │       │   │   │   ├── TargetColumnSelect
│   │       │   │   │   └── DataTypeOverride
│   │       │   │   ├── Step 2: PipelineConfig
│   │       │   │   │   ├── FeatureSelectionToggle
│   │       │   │   │   ├── HyperparameterTuningToggle
│   │       │   │   │   └── SearchMethodSelect
│   │       │   │   └── Step 3: Review
│   │       │   │       ├── DatasetSummary
│   │       │   │       ├── ConfigurationSummary
│   │       │   │       └── PipelineOptionsSummary
│   │       │   └── Navigation (Back/Next/Run)
│   │       └── Results Page
│   │           ├── JobStatusMonitor
│   │           ├── BestModelCard
│   │           ├── MetricsTable
│   │           ├── FeatureImportance
│   │           ├── ConfusionMatrix
│   │           ├── TrainedModelsList
│   │           └── ExportButton
│   └── Footer
└── ErrorBoundary (Catch React Errors)
```

## Data Flow

```
User Action
    │
    ▼
Component Event Handler
    │
    ▼
Store Update (Zustand)
    │
    ├─→ Local State Update
    │       │
    │       ▼
    │   Component Re-render
    │
    └─→ API Call (if needed)
            │
            ▼
        API Service (Axios)
            │
            ▼
        Backend (FastAPI)
            │
            ▼
        Process/Return Data
            │
            ▼
        React Query Update
            │
            ▼
        Component Re-render
            │
            ▼
        UI Updated
```

## File Organization

```
src/
├── api/
│   └── automl.ts
│       ├── AutoMLAPIService class
│       │   ├── uploadDataset()
│       │   ├── runPipeline()
│       │   ├── getResults()
│       │   ├── getJobStatus()
│       │   ├── pollJobCompletion()
│       │   └── Error handling
│       └── Singleton instance export
│
├── components/
│   ├── Layout.tsx           (Header + Navigation)
│   ├── ErrorBoundary.tsx    (Error catching)
│   ├── LoadingSkeleton.tsx  (Loading UI)
│   ├── StepIndicator.tsx    (Progress)
│   ├── DatasetUpload.tsx    (Step 0)
│   ├── TaskConfig.tsx       (Step 1)
│   ├── PipelineConfig.tsx   (Step 2)
│   ├── MetricsTable.tsx     (Results)
│   ├── FeatureImportance.tsx (Results)
│   ├── ConfusionMatrix.tsx  (Results)
│   └── index.ts             (Exports)
│
├── hooks/
│   └── useAutoML.ts
│       ├── useJobPolling()
│       ├── useJobResults()
│       ├── useElapsedTime()
│       ├── useDebouncedValue()
│       ├── useLocalStorage()
│       ├── useMediaQuery()
│       └── useIsMobile()
│
├── pages/
│   ├── Home.tsx      (Landing page)
│   ├── Run.tsx       (Wizard workflow)
│   ├── Results.tsx   (Results display)
│   └── index.ts      (Exports)
│
├── store/
│   └── automlStore.ts
│       ├── Dataset state
│       ├── Configuration state
│       ├── Execution state
│       ├── UI state
│       ├── Actions
│       └── Validation helpers
│
├── types/
│   └── automl.ts
│       ├── Dataset types
│       ├── Configuration types
│       ├── Results types
│       ├── API types
│       └── UI types
│
├── utils/
│   └── helpers.ts
│       ├── formatMetric()
│       ├── formatBytes()
│       ├── validateCSVFile()
│       ├── getMetricDescription()
│       ├── getImportanceColor()
│       └── More helpers...
│
├── styles/
│   ├── globals.css   (Global styles + animations)
│   └── layout.css    (Layout-specific styles)
│
├── App.tsx           (Router + Theme)
└── main.tsx          (Entry point)
```

## Technology Stack Layers

```
┌─────────────────────────────────────────────┐
│  User Interface (React Components)          │
│  - Material-UI components                   │
│  - Recharts visualizations                  │
│  - Responsive layouts                       │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  State Management Layer                     │
│  - Zustand (local + global UI state)        │
│  - React Query (server state)               │
│  - Custom validation logic                  │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  API Service Layer (Axios)                  │
│  - Centralized API calls                    │
│  - Error handling & extraction              │
│  - Request/response typing                  │
│  - Polling with exponential backoff         │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  HTTP Client (Axios)                        │
│  - Request/response interceptors            │
│  - Timeout configuration                    │
│  - CORS handling                            │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  Backend API (FastAPI)                      │
│  - /api/upload                              │
│  - /api/run                                 │
│  - /api/results/{job_id}                    │
│  - /api/status/{job_id}                     │
└─────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│  ML Pipeline (Python)                       │
│  - Data preprocessing                       │
│  - Feature selection                        │
│  - Model training                           │
│  - Hyperparameter tuning                    │
│  - Model evaluation                         │
└─────────────────────────────────────────────┘
```

## Error Handling Flow

```
User Action
    │
    ▼
Try-Catch Block (Component)
    │
    ├─ Error caught
    │   │
    │   ▼
    │ setError(message)
    │ enqueueSnackbar(message, 'error')
    │
    └─ Success
        │
        ▼
    Update state / Navigate

API Error Path:
────────────────
API Service.handleError()
    │
    ▼
Extract error detail from response
    │
    ▼
Enhance with status code
    │
    ▼
Return rejected promise
    │
    ▼
Caught in component try-catch
    │
    ▼
User-friendly error shown

Unhandled Errors:
─────────────────
React Error Boundary catches
    │
    ▼
Displays error UI
    │
    ▼
Offers recovery button
```

## State Management Pattern

```
Global Zustand Store (useAutoMLStore)
│
├─ Dataset State
│  └─ uploadedFile: DatasetInfo | null
│
├─ Configuration State
│  └─ config: AutoMLConfig
│     ├─ target_column: string
│     ├─ task_type: 'classification' | 'regression'
│     ├─ feature_selection_enabled: boolean
│     ├─ hyperparameter_tuning_enabled: boolean
│     ├─ search_method: 'grid' | 'random' | 'bayesian'
│     └─ data_type_override?: string
│
├─ Execution State
│  ├─ currentJobId: string | null
│  └─ jobResult: PipelineResult | null
│
└─ UI State
   ├─ currentStep: number
   ├─ isLoading: boolean
   ├─ error: string | null
   └─ success: string | null

Plus Actions:
├─ updateConfig()
├─ nextStep() / prevStep()
├─ setError() / setSuccess()
└─ reset()
```

## Workflow State Transitions

```
START
  │
  ▼
Home Page
  │
  └─→ [Start AutoML Run]
      │
      ▼
    Run Page (Step 0)
      │
      ├─ DatasetUpload Component
      │  └─ User uploads CSV
      │      │
      │      └─→ [Next]
      │
      ▼
    Run Page (Step 1)
      │
      ├─ TaskConfig Component
      │  └─ User configures task
      │      │
      │      └─→ [Next]
      │
      ▼
    Run Page (Step 2)
      │
      ├─ PipelineConfig Component
      │  └─ User sets options
      │      │
      │      └─→ [Next]
      │
      ▼
    Run Page (Step 3)
      │
      ├─ Review Component
      │  └─ User confirms
      │      │
      │      └─→ [Run AutoML Pipeline]
      │
      ▼
    API Call: runPipeline()
      │
      ├─ Success: jobId returned
      │   │
      │   └─→ Navigate to Results
      │
      └─ Error: Show error message
          │
          └─→ Back to step 0
      
    ▼
  Results Page
    │
    ├─ useJobPolling(jobId)
    │  └─ Poll every 2 seconds
    │     │
    │     ├─ Status: "processing"
    │     │  └─ Keep polling
    │     │
    │     └─ Status: "completed"
    │        └─ Display results
    │
    ├─ MetricsTable (Performance)
    ├─ FeatureImportance (Chart)
    ├─ ConfusionMatrix (Heatmap)
    ├─ TrainedModels (List)
    │
    └─ Action Buttons
       ├─ [Download Results]
       ├─ [New Run]
       └─ [Home]
```

---

This diagram shows the complete architecture of the AutoML platform frontend.

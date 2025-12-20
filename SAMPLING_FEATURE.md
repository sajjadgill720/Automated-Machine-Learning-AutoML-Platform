# Dataset Sampling Feature - Quick Reference

## Overview
The AutoML system now supports configurable dataset sampling for both CLI and API interfaces, allowing efficient processing of large datasets.

## Feature Summary

### ✅ What's New
- **API Sampling Support**: Web interface can now handle large datasets efficiently
- **Configurable Limits**: Users can control the max rows to process
- **Smart Sampling**: Preserves class distribution for classification tasks
- **Frontend UI**: New sampling control in Pipeline Configuration

---

## Usage

### 1. Frontend (React UI)

**Location**: Pipeline Config page (Step 3)

**Options**:
```
Dataset Sampling
└── Maximum rows to process: [10000]
    ├── Default: 10,000 rows (recommended)
    ├── Fast: 5,000 rows
    ├── Accurate: 30,000-50,000 rows
    └── Unlimited: 0 (process all rows)
```

**Example Flow**:
1. Upload dataset (e.g., 100,000 rows)
2. Configure task type
3. **Set max_sample_rows = 10000** ← NEW!
4. Run pipeline
5. System samples to 10,000 rows automatically

---

### 2. API (Direct HTTP)

**Endpoint**: `POST /api/run`

**New Parameter**: `max_sample_rows` (integer, default: 10000)

**Example Request**:
```json
{
  "filename": "large_dataset.csv",
  "target_column": "target",
  "task_type": "classification",
  "max_sample_rows": 10000,
  "feature_selection_enabled": true,
  "hyperparameter_tuning_enabled": true,
  "search_method": "grid"
}
```

**Values**:
- `10000` (default) - Sample to 10k rows
- `5000` - Faster, smaller sample
- `50000` - Larger, more accurate
- `0` - No sampling, use all rows

---

### 3. CLI (Command Line)

**Existing Feature**: Already supported!

```bash
# Default: 5000 rows
python main.py --dataset data.csv --target price

# Custom: 20000 rows
python main.py --dataset data.csv --target price --max-sample-rows 20000

# No sampling: all rows
python main.py --dataset data.csv --target price --max-sample-rows 0
```

---

## Sampling Behavior

### When Sampling Occurs
| Dataset Rows | max_sample_rows | Result |
|-------------|-----------------|---------|
| 5,000 | 10,000 | No sampling (within limit) |
| 50,000 | 10,000 | ✅ Sample to 10,000 rows |
| 100,000 | 0 | No sampling (disabled) |
| 100,000 | 30,000 | ✅ Sample to 30,000 rows |

### Sampling Strategy
- **Classification**: Stratified sampling (preserves class distribution)
- **Regression**: Random sampling
- **Method**: Uses `sklearn.model_selection.train_test_split`
- **Seed**: Fixed (42) for reproducibility

---

## Performance Guidelines

### Recommended Settings

| Use Case | Rows | Processing Time | Accuracy |
|----------|------|----------------|----------|
| **Quick Test** | 5,000 | ~1-2 min | Good |
| **Development** | 10,000 | ~2-5 min | Better |
| **Production** | 30,000+ | ~10-20 min | Best |
| **Full Dataset** | 0 (unlimited) | Varies | Maximum |

### Tips
- **Start small**: Test with 5k-10k rows first
- **Scale up**: Increase for final models
- **Monitor memory**: Large datasets (100k+) may need more RAM
- **Use sampling**: For datasets > 50k rows

---

## Implementation Details

### Files Modified

1. **Backend API** ([app.py](app.py))
   - Added `sample_dataset` import
   - Added `max_sample_rows` to `RunPipelineRequest`
   - Sampling logic in `_run_pipeline_job()`

2. **Frontend Types** ([frontend/src/types/automl.ts](frontend/src/types/automl.ts))
   - Added `max_sample_rows?` to `AutoMLConfig`
   - Added `max_sample_rows?` to `RunPipelineRequest`

3. **Frontend UI** ([frontend/src/components/PipelineConfig.tsx](frontend/src/components/PipelineConfig.tsx))
   - New sampling configuration section
   - TextField for max rows input
   - Updated configuration summary

4. **State Management** ([frontend/src/store/automlStore.ts](frontend/src/store/automlStore.ts))
   - Default value: `max_sample_rows: 10000`

### Sampling Function
```python
from automl.utils.sampling import sample_dataset

sampled_df = sample_dataset(
    df=df,
    target_col="target",
    max_rows=10000,
    task_type="classification",  # or "regression"
    random_state=42
)
```

---

## Examples

### Example 1: E-commerce Dataset (1M rows)
```json
{
  "filename": "ecommerce_transactions.csv",
  "target_column": "purchased",
  "task_type": "classification",
  "max_sample_rows": 20000  // Use 20k for good balance
}
```
**Result**: Samples 1M → 20k rows, trains in ~5 minutes

### Example 2: Small Dataset (800 rows)
```json
{
  "filename": "iris_extended.csv",
  "target_column": "species",
  "task_type": "classification",
  "max_sample_rows": 10000
}
```
**Result**: No sampling (800 < 10k), uses all rows

### Example 3: Full Dataset Processing
```json
{
  "filename": "customer_data.csv",
  "target_column": "churn",
  "task_type": "classification",
  "max_sample_rows": 0  // Disable sampling
}
```
**Result**: Uses entire dataset regardless of size

---

## Testing

### Test Dataset Created
- **File**: `uploads/large_test_data.csv`
- **Rows**: 50,000
- **Size**: 1.41 MB
- **Task**: Binary classification (loan approval)

### Run Test
```bash
python test_sampling_feature.py
```

### Verify Sampling Works
1. Start backend: `uvicorn app:app --reload`
2. Upload `large_test_data.csv`
3. Set `max_sample_rows = 5000`
4. Check logs: Should show "Sampled dataset from 50000 to 5000 rows"

---

## Benefits

✅ **Faster Development**: Quick iterations with small samples  
✅ **Scalable**: Handle datasets of any size  
✅ **Flexible**: User controls speed vs accuracy tradeoff  
✅ **Smart**: Preserves class distribution in samples  
✅ **Memory Efficient**: Reduces RAM usage for large datasets  
✅ **Production Ready**: Can disable sampling for final models  

---

## Migration Notes

### Breaking Changes
❌ None - backward compatible!

### Defaults
- **CLI**: 5,000 rows (unchanged)
- **API**: 10,000 rows (new default)

### Existing Code
All existing code continues to work. The feature is additive.

---

## Summary

| Interface | Parameter | Default | Location |
|-----------|-----------|---------|----------|
| **CLI** | `--max-sample-rows` | 5000 | Command line arg |
| **API** | `max_sample_rows` | 10000 | JSON request body |
| **Frontend** | "Maximum rows" | 10000 | Pipeline Config page |

**Status**: ✅ Fully implemented and tested  
**Version**: Added in current release  
**Documentation**: This file + test_sampling_feature.py

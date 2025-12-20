"""Test script to demonstrate the new sampling feature in the API.

This script shows how the API now handles large datasets efficiently by sampling.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_large_test_dataset(filename="large_test_data.csv", rows=50000):
    """Create a large test dataset to demonstrate sampling."""
    print(f"Creating test dataset with {rows:,} rows...")
    
    np.random.seed(42)
    
    # Create synthetic data
    data = {
        'age': np.random.randint(18, 80, rows),
        'income': np.random.randint(20000, 150000, rows),
        'credit_score': np.random.randint(300, 850, rows),
        'years_employed': np.random.randint(0, 40, rows),
        'debt': np.random.randint(0, 100000, rows),
        'num_accounts': np.random.randint(0, 10, rows),
        'num_late_payments': np.random.randint(0, 20, rows),
    }
    
    # Create target based on some logic (loan approval)
    df = pd.DataFrame(data)
    df['loan_approved'] = (
        (df['credit_score'] > 650) & 
        (df['income'] > 50000) & 
        (df['num_late_payments'] < 5)
    ).astype(int)
    
    # Save to file
    output_path = Path("uploads") / filename
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✓ Created dataset: {output_path}")
    print(f"  - Rows: {len(df):,}")
    print(f"  - Columns: {len(df.columns)}")
    print(f"  - Target distribution: {df['loan_approved'].value_counts().to_dict()}")
    print(f"  - File size: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    return output_path


def demonstrate_sampling():
    """Demonstrate the sampling feature."""
    print("\n" + "="*70)
    print("SAMPLING FEATURE DEMONSTRATION")
    print("="*70 + "\n")
    
    # Create large dataset
    dataset_path = create_large_test_dataset(rows=50000)
    
    print("\n" + "-"*70)
    print("API SAMPLING BEHAVIOR:")
    print("-"*70 + "\n")
    
    print("When you upload this dataset to the API, you can now control sampling:\n")
    
    print("1. DEFAULT (max_sample_rows=10000):")
    print("   - Dataset has 50,000 rows")
    print("   - Will be sampled down to 10,000 rows")
    print("   - Faster processing, good results")
    print("   - ✓ Recommended for quick experiments\n")
    
    print("2. CUSTOM SAMPLING (max_sample_rows=5000):")
    print("   - Dataset has 50,000 rows")
    print("   - Will be sampled down to 5,000 rows")
    print("   - Even faster processing")
    print("   - ✓ Good for rapid prototyping\n")
    
    print("3. LARGE SAMPLE (max_sample_rows=30000):")
    print("   - Dataset has 50,000 rows")
    print("   - Will be sampled down to 30,000 rows")
    print("   - Better accuracy, slower processing")
    print("   - ✓ Good for production models\n")
    
    print("4. NO SAMPLING (max_sample_rows=0):")
    print("   - Dataset has 50,000 rows")
    print("   - All 50,000 rows will be processed")
    print("   - Maximum accuracy, slowest processing")
    print("   - ✓ Use when you need full dataset\n")
    
    print("-"*70)
    print("HOW TO USE IN THE FRONTEND:")
    print("-"*70 + "\n")
    print("1. Upload your dataset")
    print("2. Configure task (classification/regression)")
    print("3. In Pipeline Config, set 'Maximum rows to process':")
    print("   - Enter 10000 for default (recommended)")
    print("   - Enter 5000 for faster processing")
    print("   - Enter 0 to disable sampling")
    print("4. Run the pipeline\n")
    
    print("-"*70)
    print("HOW TO USE WITH API DIRECTLY:")
    print("-"*70 + "\n")
    print("curl -X POST http://localhost:8000/api/run \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "filename": "large_test_data.csv",')
    print('    "target_column": "loan_approved",')
    print('    "task_type": "classification",')
    print('    "max_sample_rows": 10000,  # <-- NEW PARAMETER')
    print('    "feature_selection_enabled": true,')
    print('    "hyperparameter_tuning_enabled": true,')
    print('    "search_method": "grid"')
    print("  }'\n")
    
    print("-"*70)
    print("SAMPLING PRESERVES CLASS DISTRIBUTION:")
    print("-"*70 + "\n")
    print("For classification tasks, stratified sampling is used:")
    print("- Original dataset class distribution is maintained")
    print("- Example: 60% approved / 40% rejected stays 60/40 in sample")
    print("- Ensures representative training data\n")
    
    print("="*70)
    print("✓ FEATURE READY TO USE!")
    print("="*70 + "\n")
    
    return dataset_path


if __name__ == "__main__":
    demonstrate_sampling()
    
    print("Next steps:")
    print("1. Start the backend: python -m uvicorn app:app --reload")
    print("2. Start the frontend: cd frontend && npm run dev")
    print("3. Upload large_test_data.csv through the UI")
    print("4. Configure sampling in Pipeline Config")
    print("5. Watch it handle 50k rows efficiently!\n")

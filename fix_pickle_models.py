"""Utility script to fix pickle protocol issues in saved models.

This script will:
1. Find all .pkl model files in the results_api directory
2. Attempt to load them
3. Re-save them with protocol=4 for better compatibility
"""

import joblib
from pathlib import Path
import sys

def fix_pickle_file(pkl_path: Path) -> bool:
    """Try to load and re-save a pickle file with protocol=4."""
    try:
        print(f"Processing: {pkl_path}")
        
        # Try to load the model
        model = joblib.load(pkl_path)
        
        # Re-save with protocol=4
        joblib.dump(model, pkl_path, protocol=4)
        
        print(f"  ✓ Successfully fixed: {pkl_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to fix {pkl_path}: {e}")
        return False


def main():
    results_dir = Path("results_api")
    
    if not results_dir.exists():
        print(f"Error: {results_dir} directory not found")
        return 1
    
    # Find all .pkl files recursively
    pkl_files = list(results_dir.rglob("*.pkl"))
    
    if not pkl_files:
        print("No .pkl files found in results_api directory")
        return 0
    
    print(f"Found {len(pkl_files)} pickle file(s)\n")
    
    success_count = 0
    fail_count = 0
    
    for pkl_file in pkl_files:
        if fix_pickle_file(pkl_file):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Successfully fixed: {success_count}")
    print(f"  Failed: {fail_count}")
    print(f"{'='*60}")
    
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

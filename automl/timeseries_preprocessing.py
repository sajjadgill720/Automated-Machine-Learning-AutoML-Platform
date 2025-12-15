"""
Time Series Data Preprocessing Module
======================================
Handles preprocessing for time series data with lag features.

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import logging
import warnings
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


def preprocess_timeseries(df: pd.DataFrame,
                         target_col: Optional[str] = None,
                         time_col: Optional[str] = None,
                         n_lags: int = 3,
                         test_size: float = 0.2,
                         val_size: float = 0.1) -> Tuple[dict, Optional[np.ndarray]]:
    """
    Preprocess time series data with lag features.
    
    Steps:
    1. Sort by time column
    2. Handle missing timestamps (interpolation)
    3. Generate lag features (previous n_lags time steps)
    4. Scale features using StandardScaler
    5. Split into train/validation/test sets (preserving temporal order)
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input time series dataset
    target_col : str, optional
        Name of the target column
    time_col : str, optional
        Name of the time/date column (if None, assumes data is already sorted)
    n_lags : int, default=3
        Number of lag features to create for each numeric column
    test_size : float, default=0.2
        Proportion of data for test set
    val_size : float, default=0.1
        Proportion of data for validation set
        
    Returns:
    --------
    data_splits : dict
        Dictionary containing:
        - 'X_train': Training features with lags
        - 'X_val': Validation features with lags
        - 'X_test': Test features with lags
        - 'y_train': Training target (if target_col provided)
        - 'y_val': Validation target (if target_col provided)
        - 'y_test': Test target (if target_col provided)
        - 'feature_names': List of feature names including lag features
        - 'scaler': Fitted StandardScaler object
        - 'n_lags': Number of lags used
    y : np.ndarray or None
        Full target array (if target_col provided)
        
    Notes:
    ------
    - Preserves temporal order in splits (no random shuffling)
    - Creates lag features for all numeric columns
    - Drops rows with NaN values created by lag features
    
    Examples:
    ---------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range('2024-01-01', periods=100),
    ...     'value': range(100),
    ...     'target': [0, 1] * 50
    ... })
    >>> result, y = preprocess_timeseries(df, target_col='target', time_col='date')
    >>> print(result['X_train'].shape)
    """
    logger.info("="*60)
    logger.info("Starting time series data preprocessing...")
    logger.info("="*60)
    
    df = df.copy()
    
    # Sort by time if time_col is provided
    if time_col:
        if time_col not in df.columns:
            raise ValueError(f"Time column '{time_col}' not found in DataFrame")
        
        logger.info(f"\n📅 Time Column Processing:")
        logger.info(f"  • Sorting by: '{time_col}'")
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(by=time_col).reset_index(drop=True)
        
        # Handle missing timestamps with interpolation
        if df[time_col].isnull().any():
            logger.info(f"  • Interpolating missing timestamps")
            df[time_col] = df[time_col].interpolate(method='time')
        
        logger.info(f"✓ Time range: {df[time_col].min()} to {df[time_col].max()}")
    else:
        logger.info("✓ No time column specified, assuming data is already sorted")
    
    # Separate target
    if target_col:
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        y_series = df[target_col]
        feature_cols = [col for col in df.columns if col not in [target_col, time_col]]
        logger.info(f"\n✓ Target column: '{target_col}'")
    else:
        y_series = None
        feature_cols = [col for col in df.columns if col != time_col]
        logger.info("\n✓ No target column specified")
    
    X_df = df[feature_cols].copy()
    
    # Detect numeric columns for lag features
    numeric_cols = X_df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    logger.info(f"\n📊 Feature Detection:")
    logger.info(f"  • Numeric columns: {len(numeric_cols)}")
    logger.info(f"  • Total features: {len(feature_cols)}")
    
    # Handle missing values in numeric columns before creating lags
    logger.info(f"\n🔧 Handling Missing Values:")
    missing_handled = 0
    for col in numeric_cols:
        if X_df[col].isnull().any():
            logger.info(f"  • {col}: interpolating missing values")
            X_df[col] = X_df[col].interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
            missing_handled += 1
    
    if missing_handled == 0:
        logger.info(f"  • No missing values found")
    else:
        logger.info(f"✓ Handled {missing_handled} columns with missing values")
    
    # Create lag features
    logger.info(f"\n🔄 Creating Lag Features:")
    logger.info(f"  • Number of lags: {n_lags}")
    logger.info(f"  • Columns to lag: {len(numeric_cols)}")
    
    lag_features = []
    lag_feature_names = []
    
    for col in numeric_cols:
        for lag in range(1, n_lags + 1):
            lag_col_name = f"{col}_lag_{lag}"
            X_df[lag_col_name] = X_df[col].shift(lag)
            lag_feature_names.append(lag_col_name)
    
    logger.info(f"✓ Created {len(lag_feature_names)} lag features")
    
    # Drop rows with NaN values created by lag features
    initial_rows = len(X_df)
    X_df = X_df.dropna()
    
    if y_series is not None:
        y_series = y_series.loc[X_df.index]
    
    dropped_rows = initial_rows - len(X_df)
    logger.info(f"  • Dropped {dropped_rows} rows with NaN from lag features")
    logger.info(f"  • Remaining rows: {len(X_df)}")
    
    # Reset index
    X_df = X_df.reset_index(drop=True)
    if y_series is not None:
        y_series = y_series.reset_index(drop=True)
        y = y_series.values
    else:
        y = None
    
    # Scale features
    logger.info(f"\n⚖️  Scaling Features:")
    logger.info(f"  • Using StandardScaler (mean=0, std=1)")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_df)
    
    feature_names = X_df.columns.tolist()
    logger.info(f"✓ Scaled {len(feature_names)} features")
    
    # Split into train/val/test sets (preserving temporal order)
    logger.info(f"\n✂️  Temporal Splitting:")
    logger.info(f"  • Test size: {test_size*100}%")
    logger.info(f"  • Validation size: {val_size*100}%")
    logger.info(f"  • Note: Preserving temporal order (no shuffling)")
    
    n_samples = len(X_scaled)
    test_start_idx = int(n_samples * (1 - test_size))
    val_start_idx = int(test_start_idx * (1 - val_size / (1 - test_size)))
    
    X_train = X_scaled[:val_start_idx]
    X_val = X_scaled[val_start_idx:test_start_idx]
    X_test = X_scaled[test_start_idx:]
    
    if y is not None:
        y_train = y[:val_start_idx]
        y_val = y[val_start_idx:test_start_idx]
        y_test = y[test_start_idx:]
        
        logger.info(f"\n✓ Split Complete:")
        logger.info(f"  • Train: {X_train.shape} (indices 0-{val_start_idx-1})")
        logger.info(f"  • Val:   {X_val.shape} (indices {val_start_idx}-{test_start_idx-1})")
        logger.info(f"  • Test:  {X_test.shape} (indices {test_start_idx}-{n_samples-1})")
        logger.info("="*60)
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'y_train': y_train,
            'y_val': y_val,
            'y_test': y_test,
            'feature_names': feature_names,
            'scaler': scaler,
            'n_lags': n_lags
        }, y
    else:
        logger.info(f"\n✓ Split Complete:")
        logger.info(f"  • Train: {X_train.shape} (indices 0-{val_start_idx-1})")
        logger.info(f"  • Val:   {X_val.shape} (indices {val_start_idx}-{test_start_idx-1})")
        logger.info(f"  • Test:  {X_test.shape} (indices {test_start_idx}-{n_samples-1})")
        logger.info("="*60)
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'feature_names': feature_names,
            'scaler': scaler,
            'n_lags': n_lags
        }, None


if __name__ == "__main__":
    # Example usage
    print("\nTime Series Preprocessing Module - Example Usage\n")
    
    # Create sample time series data
    df = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='D'),
        'temperature': np.sin(np.linspace(0, 10, 100)) * 20 + 15 + np.random.randn(100) * 2,
        'humidity': np.cos(np.linspace(0, 10, 100)) * 30 + 50 + np.random.randn(100) * 5,
        'target': np.random.randint(0, 2, 100)
    })
    
    print("Sample DataFrame (first 5 rows):")
    print(df.head())
    print()
    
    # Preprocess
    result, y = preprocess_timeseries(df, target_col='target', time_col='timestamp', n_lags=3)
    
    print("\n✅ Preprocessing Complete!")
    print(f"\nFeature names ({len(result['feature_names'])}):")
    print(f"  Original features: temperature, humidity")
    print(f"  Lag features: {result['n_lags']} lags per feature")
    print(f"  Total: {len(result['feature_names'])} features")
    
    print(f"\nTarget distribution:")
    print(f"  Class 0: {np.sum(y == 0)} samples")
    print(f"  Class 1: {np.sum(y == 1)} samples")
    
    print(f"\nTemporal split indices:")
    print(f"  Train uses earliest {result['X_train'].shape[0]} samples")
    print(f"  Val uses next {result['X_val'].shape[0]} samples")
    print(f"  Test uses latest {result['X_test'].shape[0]} samples")

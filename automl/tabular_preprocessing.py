"""
Tabular Data Preprocessing Module
==================================
Handles preprocessing for tabular/structured data with automatic feature detection.

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import logging
import warnings
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


def preprocess_tabular(df: pd.DataFrame, 
                       target_col: Optional[str] = None,
                       test_size: float = 0.2,
                       val_size: float = 0.1,
                       random_state: int = 42) -> Tuple[dict, Optional[np.ndarray]]:
    """
    Preprocess tabular data with automatic handling of numeric and categorical features.
    
    Steps:
    1. Separate features and target
    2. Detect numeric vs categorical columns
    3. Handle missing values (mean for numeric, mode for categorical)
    4. Encode categorical variables (One-Hot or Label Encoding)
    5. Scale numeric features using StandardScaler
    6. Split into train/validation/test sets
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input tabular dataset
    target_col : str, optional
        Name of the target column
    test_size : float, default=0.2
        Proportion of data for test set
    val_size : float, default=0.1
        Proportion of data for validation set (from training data)
    random_state : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    data_splits : dict
        Dictionary containing:
        - 'X_train': Training features
        - 'X_val': Validation features
        - 'X_test': Test features
        - 'y_train': Training target (if target_col provided)
        - 'y_val': Validation target (if target_col provided)
        - 'y_test': Test target (if target_col provided)
        - 'feature_names': List of feature names after encoding
        - 'scaler': Fitted StandardScaler object
        - 'encoders': Dictionary of fitted encoders
    y : np.ndarray or None
        Full target array (if target_col provided)
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'age': [25, 30, 35],
    ...     'city': ['NYC', 'LA', 'NYC'],
    ...     'target': [0, 1, 0]
    ... })
    >>> result, y = preprocess_tabular(df, target_col='target')
    >>> print(result['X_train'].shape)
    """
    logger.info("="*60)
    logger.info("Starting tabular data preprocessing...")
    logger.info("="*60)
    
    df = df.copy()
    
    # Separate features and target
    if target_col:
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        y = df[target_col].values
        X = df.drop(columns=[target_col])
        logger.info(f"✓ Target column '{target_col}' separated. Shape: {y.shape}")
    else:
        y = None
        X = df
        logger.info("✓ No target column specified (unsupervised learning)")
    
    # Detect column types
    numeric_cols = X.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
    
    logger.info(f"\n📊 Column Detection:")
    logger.info(f"  • Numeric columns: {len(numeric_cols)}")
    logger.info(f"  • Categorical columns: {len(categorical_cols)}")
    
    # Handle missing values
    logger.info(f"\n🔧 Handling Missing Values:")
    
    # Numeric columns: fill with mean
    for col in numeric_cols:
        if X[col].isnull().any():
            mean_val = X[col].mean()
            X[col].fillna(mean_val, inplace=True)
            logger.info(f"  • {col} (numeric): filled with mean = {mean_val:.2f}")
    
    # Categorical columns: fill with mode
    for col in categorical_cols:
        if X[col].isnull().any():
            mode_val = X[col].mode()[0] if not X[col].mode().empty else 'missing'
            X[col].fillna(mode_val, inplace=True)
            logger.info(f"  • {col} (categorical): filled with mode = '{mode_val}'")
    
    # Encode categorical variables
    logger.info(f"\n🔤 Encoding Categorical Variables:")
    encoders = {}
    encoded_dfs = []
    
    for col in categorical_cols:
        n_unique = X[col].nunique()
        
        if n_unique <= 10:
            # One-Hot Encoding for low cardinality
            logger.info(f"  • {col}: One-Hot Encoding ({n_unique} unique values)")
            dummies = pd.get_dummies(X[col], prefix=col, drop_first=True)
            encoded_dfs.append(dummies)
            encoders[col] = {'type': 'onehot', 'columns': dummies.columns.tolist()}
        else:
            # Label Encoding for high cardinality
            logger.info(f"  • {col}: Label Encoding ({n_unique} unique values)")
            le = LabelEncoder()
            encoded_values = le.fit_transform(X[col].astype(str))
            encoded_dfs.append(pd.DataFrame({col: encoded_values}, index=X.index))
            encoders[col] = {'type': 'label', 'encoder': le}
    
    # Combine numeric and encoded categorical features
    if encoded_dfs:
        X_encoded = pd.concat([X[numeric_cols]] + encoded_dfs, axis=1)
    else:
        X_encoded = X[numeric_cols]
    
    feature_names = X_encoded.columns.tolist()
    logger.info(f"\n✓ Total features after encoding: {len(feature_names)}")
    
    # Scale numeric features
    logger.info(f"\n⚖️  Scaling Features:")
    logger.info(f"  • Using StandardScaler (mean=0, std=1)")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_encoded)
    
    # Split into train/val/test sets
    logger.info(f"\n✂️  Splitting Data:")
    logger.info(f"  • Test size: {test_size*100}%")
    logger.info(f"  • Validation size: {val_size*100}%")
    
    if y is not None:
        # Detect if this is classification or regression
        n_unique = len(np.unique(y))
        is_int_dtype = np.issubdtype(y.dtype, np.integer)
        
        # Classification: < 20 unique values AND integer dtype (or small unique set)
        is_classification = n_unique < 20 and is_int_dtype
        
        stratify_param = y if is_classification else None
        
        logger.info(f"  • Task type: {'Classification' if is_classification else 'Regression'}")
        if is_classification:
            logger.info(f"  • Classes: {np.unique(y)}")
        
        # First split: train+val and test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state, stratify=stratify_param
        )
        
        # Second split: train and val
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=random_state, stratify=y_temp if is_classification else None
        )
        
        logger.info(f"\n✓ Split Complete:")
        logger.info(f"  • Train: {X_train.shape}")
        logger.info(f"  • Val:   {X_val.shape}")
        logger.info(f"  • Test:  {X_test.shape}")
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
            'encoders': encoders
        }, y
    else:
        # Unsupervised: just split features
        X_temp, X_test = train_test_split(
            X_scaled, test_size=test_size, random_state=random_state
        )
        
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val = train_test_split(
            X_temp, test_size=val_size_adjusted, random_state=random_state
        )
        
        logger.info(f"\n✓ Split Complete:")
        logger.info(f"  • Train: {X_train.shape}")
        logger.info(f"  • Val:   {X_val.shape}")
        logger.info(f"  • Test:  {X_test.shape}")
        logger.info("="*60)
        
        return {
            'X_train': X_train,
            'X_val': X_val,
            'X_test': X_test,
            'feature_names': feature_names,
            'scaler': scaler,
            'encoders': encoders
        }, None


if __name__ == "__main__":
    # Example usage
    print("\nTabular Preprocessing Module - Example Usage\n")
    
    # Create sample data
    df = pd.DataFrame({
        'age': [25, 30, np.nan, 40, 35, 28, 45, 50],
        'income': [50000, 60000, 55000, np.nan, 70000, 52000, 80000, 90000],
        'city': ['NYC', 'LA', 'NYC', 'Chicago', 'LA', 'NYC', 'Chicago', 'LA'],
        'education': ['Bachelor', 'Master', 'PhD', 'Bachelor', 'Master', 'Bachelor', 'PhD', 'Master'],
        'purchased': [0, 1, 0, 1, 1, 0, 1, 1]
    })
    
    print("Sample DataFrame:")
    print(df.head())
    print()
    
    # Preprocess
    result, y = preprocess_tabular(df, target_col='purchased')
    
    print("\n✅ Preprocessing Complete!")
    print(f"Feature names: {result['feature_names']}")
    print(f"\nTarget distribution:")
    print(f"  Class 0: {np.sum(y == 0)} samples")
    print(f"  Class 1: {np.sum(y == 1)} samples")

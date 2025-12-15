"""
AutoML Preprocessing Module - Dispatcher
=========================================
Main dispatcher that routes data to appropriate preprocessing modules.

This module acts as a central entry point for preprocessing different data types:
- Tabular data -> tabular_preprocessing.py
- Text data -> text_preprocessing.py
- Image data -> Image_preprocessing.py
- Time series data -> timeseries_preprocessing.py

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import logging
from typing import Tuple, Optional, Union, List
import pandas as pd

# Import modular preprocessing functions
from .tabular_preprocessing import preprocess_tabular
from .text_preprocessing import preprocess_text
from .Image_preprocessing import preprocess_image
from .timeseries_preprocessing import preprocess_timeseries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def preprocess_data(data: Union[pd.DataFrame, List], 
                    data_type: str, 
                    target_col: Optional[str] = None,
                    **kwargs) -> Tuple[dict, Optional[any]]:
    """
    Dispatcher function that routes data to the appropriate preprocessing module.
    
    This function serves as the main entry point for preprocessing different types of data.
    It automatically selects and calls the appropriate specialized preprocessing function
    based on the data_type parameter.
    
    Parameters:
    -----------
    data : pd.DataFrame or list
        Input data to preprocess
    data_type : str
        Type of data: 'tabular', 'text', 'image', or 'timeseries'
    target_col : str, optional
        Name of the target column (for supervised learning)
    **kwargs : dict
        Additional arguments to pass to specific preprocessing functions:
        
        For 'text':
            - text_col (str): Name of column containing text
            - max_features (int): Max TF-IDF features (default: 5000)
            
        For 'image':
            - labels (list): Image labels
            - target_size (tuple): Image size (default: (224, 224))
            - augment (bool): Apply augmentation (default: False)
            
        For 'timeseries':
            - time_col (str): Name of timestamp column
            - n_lags (int): Number of lag features (default: 3)
            
        For all types:
            - test_size (float): Test set proportion (default: 0.2)
            - val_size (float): Validation set proportion (default: 0.1)
            - random_state (int): Random seed (default: 42)
        
    Returns:
    --------
    data_splits : dict
        Dictionary containing train/val/test splits and preprocessing artifacts
        (scalers, encoders, vectorizers, etc.)
    y : np.ndarray or None
        Full target array (if applicable)
        
    Raises:
    -------
    ValueError
        If data_type is not recognized or required parameters are missing
        
    Examples:
    ---------
    >>> # Tabular data
    >>> df = pd.DataFrame({'feature': [1, 2, 3], 'target': [0, 1, 0]})
    >>> result, y = preprocess_data(df, 'tabular', target_col='target')
    
    >>> # Text data
    >>> df = pd.DataFrame({'text': ['hello world', 'foo bar'], 'label': [0, 1]})
    >>> result, y = preprocess_data(df, 'text', target_col='label', text_col='text')
    
    >>> # Image data
    >>> image_paths = ['img1.jpg', 'img2.jpg']
    >>> labels = [0, 1]
    >>> result, y = preprocess_data(image_paths, 'image', labels=labels)
    
    >>> # Time series data
    >>> df = pd.DataFrame({'date': [...], 'value': [...], 'target': [...]})
    >>> result, y = preprocess_data(df, 'timeseries', target_col='target', time_col='date')
    """
    logger.info("="*70)
    logger.info(f"🚀 AUTOML PREPROCESSING DISPATCHER")
    logger.info("="*70)
    logger.info(f"📌 Data type: {data_type}")
    
    data_type = data_type.lower().strip()
    
    if data_type == 'tabular':
        logger.info(f"📊 Routing to: tabular_preprocessing.preprocess_tabular()")
        logger.info("="*70)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Tabular data must be a pandas DataFrame")
        return preprocess_tabular(data, target_col, **kwargs)
    
    elif data_type == 'text':
        logger.info(f"📝 Routing to: text_preprocessing.preprocess_text()")
        logger.info("="*70)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Text data must be a pandas DataFrame")
        text_col = kwargs.get('text_col', None)
        if text_col is None:
            raise ValueError("text_col must be specified for text data")
        return preprocess_text(data, text_col, target_col, **kwargs)
    
    elif data_type == 'image':
        logger.info(f"🖼️  Routing to: Image_preprocessing.preprocess_image()")
        logger.info("="*70)
        
        image_paths = data if isinstance(data, list) else data
        labels = kwargs.get('labels', None)
        return preprocess_image(image_paths, labels, **kwargs)
    
    elif data_type == 'timeseries':
        logger.info(f"📈 Routing to: timeseries_preprocessing.preprocess_timeseries()")
        logger.info("="*70)
        
        if not isinstance(data, pd.DataFrame):
            raise ValueError("Time series data must be a pandas DataFrame")
        time_col = kwargs.get('time_col', None)
        return preprocess_timeseries(data, target_col, time_col, **kwargs)
    
    else:
        raise ValueError(
            f"❌ Unknown data_type: '{data_type}'\n"
            f"   Must be one of: 'tabular', 'text', 'image', 'timeseries'"
        )


# Re-export preprocessing functions for direct import
__all__ = [
    'preprocess_data',
    'preprocess_tabular',
    'preprocess_text',
    'preprocess_image',
    'preprocess_timeseries'
]


if __name__ == "__main__":
    """
    Example usage demonstrating the dispatcher for all data types.
    """
    import numpy as np
    
    print("\n" + "="*70)
    print("AutoML Preprocessing Dispatcher - Example Usage")
    print("="*70)
    
    # Example 1: Tabular data
    print("\n" + "="*70)
    print("Example 1: Tabular Data")
    print("="*70)
    df_tabular = pd.DataFrame({
        'age': [25, 30, np.nan, 40, 35],
        'income': [50000, 60000, 55000, np.nan, 70000],
        'city': ['NYC', 'LA', 'NYC', 'Chicago', 'LA'],
        'purchased': [0, 1, 0, 1, 1]
    })
    
    result, y = preprocess_data(df_tabular, 'tabular', target_col='purchased')
    print(f"\n✅ Tabular preprocessing complete!")
    print(f"   X_train shape: {result['X_train'].shape}")
    
    # Example 2: Text data
    print("\n" + "="*70)
    print("Example 2: Text Data")
    print("="*70)
    df_text = pd.DataFrame({
        'text': [
            'This is a great product!',
            'Terrible experience, would not recommend.',
            'Amazing quality and fast shipping.',
            'Not worth the price.',
            'Best purchase ever!'
        ],
        'sentiment': [1, 0, 1, 0, 1]
    })
    
    result, y = preprocess_data(df_text, 'text', target_col='sentiment', text_col='text')
    print(f"\n✅ Text preprocessing complete!")
    print(f"   X_train shape: {result['X_train'].shape}")
    
    # Example 3: Time series data
    print("\n" + "="*70)
    print("Example 3: Time Series Data")
    print("="*70)
    df_ts = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='D'),
        'value': np.sin(np.linspace(0, 10, 100)) + np.random.randn(100) * 0.1,
        'target': np.random.randint(0, 2, 100)
    })
    
    result, y = preprocess_data(df_ts, 'timeseries', target_col='target', time_col='timestamp')
    print(f"\n✅ Time series preprocessing complete!")
    print(f"   X_train shape: {result['X_train'].shape}")
    
    print("\n" + "="*70)
    print("All examples completed successfully!")
    print("="*70)


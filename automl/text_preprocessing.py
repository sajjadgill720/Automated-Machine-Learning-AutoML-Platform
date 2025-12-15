"""
Text Data Preprocessing Module
===============================
Handles preprocessing for text data using TF-IDF vectorization.

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import logging
import warnings
import string
from typing import Tuple, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


def preprocess_text(df: pd.DataFrame,
                   text_col: str,
                   target_col: Optional[str] = None,
                   max_features: int = 5000,
                   test_size: float = 0.2,
                   val_size: float = 0.1,
                   random_state: int = 42) -> Tuple[dict, Optional[np.ndarray]]:
    """
    Preprocess text data using TF-IDF vectorization.
    
    Steps:
    1. Lowercase and remove punctuation
    2. Tokenize and remove stopwords
    3. Convert to TF-IDF vectors
    4. Split into train/validation/test sets
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataset containing text
    text_col : str
        Name of the column containing text data
    target_col : str, optional
        Name of the target column
    max_features : int, default=5000
        Maximum number of TF-IDF features
    test_size : float, default=0.2
        Proportion of data for test set
    val_size : float, default=0.1
        Proportion of data for validation set
    random_state : int, default=42
        Random seed for reproducibility
        
    Returns:
    --------
    data_splits : dict
        Dictionary containing:
        - 'X_train': Training TF-IDF features
        - 'X_val': Validation TF-IDF features
        - 'X_test': Test TF-IDF features
        - 'y_train': Training target (if target_col provided)
        - 'y_val': Validation target (if target_col provided)
        - 'y_test': Test target (if target_col provided)
        - 'vectorizer': Fitted TfidfVectorizer object
        - 'feature_names': List of TF-IDF feature names
    y : np.ndarray or None
        Full target array (if target_col provided)
        
    Examples:
    ---------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'text': ['Great product!', 'Terrible service.'],
    ...     'sentiment': [1, 0]
    ... })
    >>> result, y = preprocess_text(df, text_col='text', target_col='sentiment')
    >>> print(result['X_train'].shape)
    """
    logger.info("="*60)
    logger.info("Starting text data preprocessing...")
    logger.info("="*60)
    
    df = df.copy()
    
    if text_col not in df.columns:
        raise ValueError(f"Text column '{text_col}' not found in DataFrame")
    
    # Separate target
    if target_col:
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        y = df[target_col].values
        logger.info(f"✓ Target column '{target_col}' separated. Shape: {y.shape}")
    else:
        y = None
        logger.info("✓ No target column specified")
    
    # Get text data
    texts = df[text_col].astype(str).tolist()
    logger.info(f"✓ Processing {len(texts)} text samples")
    
    # Clean text
    logger.info(f"\n🧹 Cleaning Text:")
    logger.info(f"  • Lowercase conversion")
    logger.info(f"  • Punctuation removal")
    logger.info(f"  • Whitespace normalization")
    
    cleaned_texts = []
    for text in texts:
        # Lowercase
        text = text.lower()
        # Remove punctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Remove extra whitespace
        text = ' '.join(text.split())
        cleaned_texts.append(text)
    
    logger.info(f"✓ Text cleaning complete")
    
    # TF-IDF Vectorization (includes tokenization and stopword removal)
    logger.info(f"\n📊 TF-IDF Vectorization:")
    logger.info(f"  • Max features: {max_features}")
    logger.info(f"  • N-gram range: (1, 2) - unigrams and bigrams")
    logger.info(f"  • Min document frequency: 2")
    logger.info(f"  • Max document frequency: 0.95")
    
    try:
        # Try to use NLTK stopwords
        import nltk
        try:
            from nltk.corpus import stopwords
            nltk.data.find('corpora/stopwords')
        except LookupError:
            logger.info("  • Downloading NLTK stopwords...")
            nltk.download('stopwords', quiet=True)
        
        stop_words = stopwords.words('english')
        logger.info(f"  • Using NLTK stopwords ({len(stop_words)} words)")
    except Exception as e:
        logger.warning(f"  • Could not load NLTK stopwords: {e}")
        logger.info(f"  • Using sklearn's default stopwords")
        stop_words = 'english'
    
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        stop_words=stop_words,
        ngram_range=(1, 2),  # Include bigrams
        min_df=2,  # Ignore terms that appear in fewer than 2 documents
        max_df=0.95  # Ignore terms that appear in more than 95% of documents
    )
    
    X = vectorizer.fit_transform(cleaned_texts).toarray()
    logger.info(f"\n✓ TF-IDF transformation complete")
    logger.info(f"  • Output shape: {X.shape}")
    logger.info(f"  • Actual features: {X.shape[1]}")
    
    # Split into train/val/test sets
    logger.info(f"\n✂️  Splitting Data:")
    logger.info(f"  • Test size: {test_size*100}%")
    logger.info(f"  • Validation size: {val_size*100}%")
    
    if y is not None:
        # First split: train+val and test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # Second split: train and val
        val_size_adjusted = val_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=val_size_adjusted, random_state=random_state, stratify=y_temp
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
            'vectorizer': vectorizer,
            'feature_names': vectorizer.get_feature_names_out().tolist()
        }, y
    else:
        # Unsupervised
        X_temp, X_test = train_test_split(
            X, test_size=test_size, random_state=random_state
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
            'vectorizer': vectorizer,
            'feature_names': vectorizer.get_feature_names_out().tolist()
        }, None


if __name__ == "__main__":
    # Example usage
    print("\nText Preprocessing Module - Example Usage\n")
    
    # Create sample data
    df = pd.DataFrame({
        'text': [
            'This is a great product! Highly recommend it.',
            'Terrible experience, would not recommend.',
            'Amazing quality and fast shipping. Love it!',
            'Not worth the price. Very disappointed.',
            'Best purchase ever! Five stars!',
            'Poor quality and slow delivery.',
            'Excellent service and great value.',
            'Waste of money. Do not buy!'
        ],
        'sentiment': [1, 0, 1, 0, 1, 0, 1, 0]
    })
    
    print("Sample DataFrame:")
    print(df.head())
    print()
    
    # Preprocess
    result, y = preprocess_text(df, text_col='text', target_col='sentiment', max_features=100)
    
    print("\n✅ Preprocessing Complete!")
    print(f"Number of TF-IDF features: {len(result['feature_names'])}")
    print(f"\nTop 10 features: {result['feature_names'][:10]}")
    print(f"\nTarget distribution:")
    print(f"  Class 0: {np.sum(y == 0)} samples")
    print(f"  Class 1: {np.sum(y == 1)} samples")

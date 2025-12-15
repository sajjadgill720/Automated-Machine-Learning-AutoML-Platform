"""
Image Data Preprocessing Module
================================
Handles preprocessing for image data from file paths.

Author: AutoML System
Date: December 2025
Python Version: 3.10+
"""

import logging
import warnings
from typing import Tuple, Optional, List
import numpy as np
from sklearn.model_selection import train_test_split

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

warnings.filterwarnings('ignore')


def preprocess_image(image_paths: List[str],
                    labels: Optional[List] = None,
                    target_size: Tuple[int, int] = (224, 224),
                    augment: bool = False,
                    test_size: float = 0.2,
                    val_size: float = 0.1,
                    random_state: int = 42) -> Tuple[dict, Optional[np.ndarray]]:
    """
    Preprocess image data from file paths.
    
    Steps:
    1. Load images from paths
    2. Resize to target size (default 224x224)
    3. Normalize pixel values to [0, 1]
    4. Optional: simple augmentation (horizontal flip)
    5. Split into train/validation/test sets
    
    Parameters:
    -----------
    image_paths : list of str
        List of file paths to images
    labels : list, optional
        List of labels corresponding to images
    target_size : tuple, default=(224, 224)
        Target size for resizing images (height, width)
    augment : bool, default=False
        Whether to apply data augmentation (horizontal flip)
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
        - 'X_train': Training images
        - 'X_val': Validation images
        - 'X_test': Test images
        - 'y_train': Training labels (if labels provided)
        - 'y_val': Validation labels (if labels provided)
        - 'y_test': Test labels (if labels provided)
        - 'image_shape': Shape of processed images
    y : np.ndarray or None
        Full label array (if labels provided)
        
    Notes:
    ------
    Requires PIL (Pillow) or OpenCV (cv2) to be installed.
    Install with: pip install Pillow  OR  pip install opencv-python
    
    Examples:
    ---------
    >>> image_paths = ['img1.jpg', 'img2.jpg', 'img3.jpg']
    >>> labels = [0, 1, 0]
    >>> result, y = preprocess_image(image_paths, labels)
    >>> print(result['X_train'].shape)
    """
    logger.info("="*60)
    logger.info("Starting image data preprocessing...")
    logger.info("="*60)
    
    # Try to import image libraries
    try:
        from PIL import Image
        use_pil = True
        logger.info("✓ Using PIL (Pillow) for image loading")
    except ImportError:
        try:
            import cv2
            use_pil = False
            logger.info("✓ Using OpenCV for image loading")
        except ImportError:
            raise ImportError(
                "Neither PIL nor OpenCV is installed.\n"
                "Please install one of the following:\n"
                "  - Pillow: pip install Pillow\n"
                "  - OpenCV: pip install opencv-python"
            )
    
    logger.info(f"\n📁 Loading {len(image_paths)} images...")
    logger.info(f"  • Target size: {target_size}")
    logger.info(f"  • Normalization: [0, 1]")
    
    images = []
    failed_count = 0
    
    for i, img_path in enumerate(image_paths):
        try:
            if use_pil:
                # Load with PIL
                img = Image.open(img_path)
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize
                img = img.resize((target_size[1], target_size[0]))  # PIL uses (width, height)
                # Convert to numpy array
                img_array = np.array(img)
            else:
                # Load with OpenCV
                import cv2
                img = cv2.imread(img_path)
                if img is None:
                    raise ValueError(f"Could not load image: {img_path}")
                # Convert BGR to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # Resize
                img = cv2.resize(img, (target_size[1], target_size[0]))
                img_array = img
            
            # Normalize to [0, 1]
            img_array = img_array.astype(np.float32) / 255.0
            images.append(img_array)
            
            # Progress logging
            if (i + 1) % 100 == 0:
                logger.info(f"  • Loaded {i + 1}/{len(image_paths)} images")
                
        except Exception as e:
            logger.error(f"  ✗ Error loading {img_path}: {e}")
            # Create a blank image as placeholder
            blank_img = np.zeros((*target_size, 3), dtype=np.float32)
            images.append(blank_img)
            failed_count += 1
    
    X = np.array(images)
    logger.info(f"\n✓ Image loading complete")
    logger.info(f"  • Successfully loaded: {len(image_paths) - failed_count}/{len(image_paths)}")
    logger.info(f"  • Failed: {failed_count}")
    logger.info(f"  • Shape: {X.shape}")
    
    # Handle labels
    if labels is not None:
        y = np.array(labels)
        logger.info(f"✓ Labels shape: {y.shape}")
    else:
        y = None
        logger.info("✓ No labels provided")
    
    # Apply augmentation if requested
    if augment and y is not None:
        logger.info(f"\n🔄 Applying Data Augmentation:")
        logger.info(f"  • Horizontal flip (doubles dataset)")
        
        X_aug = []
        y_aug = []
        
        for img, label in zip(X, y):
            # Original
            X_aug.append(img)
            y_aug.append(label)
            
            # Horizontal flip
            X_aug.append(np.fliplr(img))
            y_aug.append(label)
        
        X = np.array(X_aug)
        y = np.array(y_aug)
        logger.info(f"✓ Augmented dataset shape: {X.shape}")
    
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
            'image_shape': target_size + (3,)
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
            'image_shape': target_size + (3,)
        }, None


if __name__ == "__main__":
    # Example usage
    print("\nImage Preprocessing Module - Example Usage\n")
    
    # Create sample synthetic images (for demonstration without actual image files)
    print("Note: This example creates synthetic images for demonstration.")
    print("In practice, provide actual image file paths.\n")
    
    # Simulate image data
    num_samples = 20
    target_size = (224, 224)
    
    # Create random image arrays (simulating loaded images)
    synthetic_images = np.random.rand(num_samples, *target_size, 3).astype(np.float32)
    labels = np.random.randint(0, 2, num_samples)
    
    # For demonstration, we'll directly split without loading from paths
    logger.info("="*60)
    logger.info("Starting image data preprocessing...")
    logger.info("="*60)
    logger.info(f"\n✓ Created {num_samples} synthetic images")
    logger.info(f"  • Shape: {synthetic_images.shape}")
    
    # Split data
    test_size = 0.2
    val_size = 0.1
    random_state = 42
    
    logger.info(f"\n✂️  Splitting Data:")
    logger.info(f"  • Test size: {test_size*100}%")
    logger.info(f"  • Validation size: {val_size*100}%")
    
    X_temp, X_test, y_temp, y_test = train_test_split(
        synthetic_images, labels, test_size=test_size, random_state=random_state, stratify=labels
    )
    
    val_size_adjusted = val_size / (1 - test_size)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=val_size_adjusted, random_state=random_state, stratify=y_temp
    )
    
    logger.info(f"\n✓ Split Complete:")
    logger.info(f"  • Train: {X_train.shape}")
    logger.info(f"  • Val:   {X_val.shape}")
    logger.info(f"  • Test:  {X_test.shape}")
    logger.info("="*60)
    
    print("\n✅ Preprocessing Complete!")
    print(f"\nTarget distribution:")
    print(f"  Class 0: {np.sum(labels == 0)} samples")
    print(f"  Class 1: {np.sum(labels == 1)} samples")
    
    print("\nTo use with actual images:")
    print("  image_paths = ['path/to/img1.jpg', 'path/to/img2.jpg', ...]")
    print("  labels = [0, 1, 0, ...]")
    print("  result, y = preprocess_image(image_paths, labels)")

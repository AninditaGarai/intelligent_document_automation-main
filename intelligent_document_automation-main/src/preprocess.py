"""
Image Preprocessing Module

Prepares scanned images for OCR by:
- Converting to grayscale
- Applying denoising
- Adjusting contrast and brightness
- Thresholding to binary image
- Deskewing (if needed)
"""

import cv2
import numpy as np
import os
from pathlib import Path


def preprocess_image(image_path: str, output_path: str = None) -> np.ndarray:
    """
    Preprocess a single image for OCR.
    
    Steps:
    1. Read image in color
    2. Convert to grayscale
    3. Apply denoising
    4. Enhance contrast and brightness
    5. Apply binary thresholding
    6. Save preprocessed image (optional)
    
    Args:
        image_path (str): Path to input image
        output_path (str): Optional path to save preprocessed image
        
    Returns:
        np.ndarray: Preprocessed image (binary)
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        Exception: If preprocessing fails
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        # Read image
        print(f"Processing: {Path(image_path).name}")
        img = cv2.imread(image_path)
        
        if img is None:
            raise ValueError(f"Failed to read image: {image_path}")
        
        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Apply bilateral filtering for denoising while preserving edges
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # Step 3: Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # for better contrast especially in scanned documents
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrasted = clahe.apply(denoised)
        
        # Step 4: Apply binary thresholding using Otsu's method
        # Otsu's method automatically finds the best threshold value
        _, binary = cv2.threshold(contrasted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Step 5: Optional morphological operations to clean up
        # Remove small noise (white spots on black background)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        morph = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Save preprocessed image if output path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cv2.imwrite(output_path, morph)
            print(f"  Saved: {Path(output_path).name}")
        
        return morph
        
    except Exception as e:
        print(f"Error preprocessing image: {str(e)}")
        raise


def batch_preprocess_images(input_dir: str, output_dir: str) -> dict:
    """
    Preprocess all images in a directory.
    
    Args:
        input_dir (str): Directory with images to preprocess
        output_dir (str): Directory to save preprocessed images
        
    Returns:
        dict: Mapping of original image names to preprocessed image paths
    """
    
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    preprocessed_map = {}
    
    # Find all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    image_files = [f for f in os.listdir(input_dir) 
                   if Path(f).suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"Warning: No image files found in {input_dir}")
        return preprocessed_map
    
    print(f"Found {len(image_files)} image(s) to preprocess\n")
    
    # Process each image
    for image_file in image_files:
        input_path = os.path.join(input_dir, image_file)
        output_filename = Path(image_file).stem + "_preprocessed.png"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            preprocess_image(input_path, output_path)
            preprocessed_map[image_file] = output_path
        except Exception as e:
            print(f"Failed to preprocess {image_file}: {str(e)}")
            continue
    
    print()
    return preprocessed_map


def get_image_quality_metrics(image_path: str) -> dict:
    """
    Calculate quality metrics for an image (useful for validation).
    
    Args:
        image_path (str): Path to image
        
    Returns:
        dict: Quality metrics including brightness, contrast, etc.
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    if img is None:
        raise ValueError(f"Failed to read image: {image_path}")
    
    metrics = {
        'mean_brightness': float(np.mean(img)),
        'contrast': float(np.std(img)),
        'width': img.shape[1],
        'height': img.shape[0],
        'aspect_ratio': float(img.shape[1] / img.shape[0])
    }
    
    return metrics

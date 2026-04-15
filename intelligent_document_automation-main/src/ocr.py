"""
Optical Character Recognition (OCR) Module

Extracts text from preprocessed images using Tesseract OCR.
Produces both raw text and confidence-scored text for reliability analysis.
"""

import pytesseract
import os
from pathlib import Path


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from a single image using Tesseract OCR.
    
    Args:
        image_path (str): Path to preprocessed image
        
    Returns:
        str: Extracted text from the image
        
    Raises:
        FileNotFoundError: If image doesn't exist
        Exception: If OCR fails
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        print(f"OCR Processing: {Path(image_path).name}")
        
        # Tesseract configuration for better accuracy
        # psm modes:
        # 6 = Assume a single uniform block of text (default)
        # 11 = Sparse text (documents, receipts, etc.)
        custom_config = r'--psm 11 --oem 3'
        
        # Extract text with configuration
        text = pytesseract.image_to_string(image_path, config=custom_config)
        
        print(f"  Extracted {len(text)} characters\n")
        return text
        
    except Exception as e:
        print(f"Error extracting text from image: {str(e)}")
        raise


def extract_text_with_confidence(image_path: str) -> dict:
    """
    Extract text along with confidence scores for each word.
    
    Args:
        image_path (str): Path to preprocessed image
        
    Returns:
        dict: Contains:
            - 'full_text': Complete extracted text
            - 'confidence_data': List of dicts with word, confidence
            - 'average_confidence': Mean confidence score
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        # Get detailed information from Tesseract
        data = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT)
        
        # Extract words and their confidence scores
        confidence_data = []
        for i in range(len(data['text'])):
            word = data['text'][i]
            conf = int(data['conf'][i])
            
            if word.strip():  # Only include non-empty words
                confidence_data.append({
                    'word': word,
                    'confidence': conf
                })
        
        # Get full text
        full_text = pytesseract.image_to_string(image_path)
        
        # Calculate average confidence
        if confidence_data:
            avg_confidence = sum(d['confidence'] for d in confidence_data) / len(confidence_data)
        else:
            avg_confidence = 0
        
        result = {
            'full_text': full_text,
            'confidence_data': confidence_data,
            'average_confidence': avg_confidence,
            'total_words': len(confidence_data)
        }
        
        return result
        
    except Exception as e:
        print(f"Error extracting text with confidence: {str(e)}")
        raise


def batch_ocr_images(image_dir: str, output_dir: str) -> dict:
    """
    Perform OCR on all images in a directory.
    Saves extracted text to individual text files.
    
    Args:
        image_dir (str): Directory containing preprocessed images
        output_dir (str): Directory to save extracted text files
        
    Returns:
        dict: Mapping of image filenames to extracted text
    """
    
    if not os.path.exists(image_dir):
        raise FileNotFoundError(f"Image directory not found: {image_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    
    text_output = {}
    
    # Find all image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']
    image_files = sorted([f for f in os.listdir(image_dir) 
                         if Path(f).suffix.lower() in image_extensions])
    
    if not image_files:
        print(f"Warning: No image files found in {image_dir}")
        return text_output
    
    print(f"Found {len(image_files)} image(s) for OCR\n")
    
    # Process each image
    for image_file in image_files:
        image_path = os.path.join(image_dir, image_file)
        
        try:
            # Extract text
            extracted_text = extract_text_from_image(image_path)
            
            # Save to text file
            text_filename = Path(image_file).stem + ".txt"
            text_path = os.path.join(output_dir, text_filename)
            
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            
            text_output[image_file] = extracted_text
            
        except Exception as e:
            print(f"Failed to OCR {image_file}: {str(e)}")
            continue
    
    print()
    return text_output


def clean_ocr_text(text: str) -> str:
    """
    Clean OCR-extracted text by removing excessive whitespace and artifacts.
    
    Args:
        text (str): Raw OCR output
        
    Returns:
        str: Cleaned text
    """
    
    # Remove multiple consecutive spaces
    text = ' '.join(text.split())
    
    # Remove common OCR artifacts
    artifacts = ['|', '`', '~']
    for artifact in artifacts:
        text = text.replace(artifact, '')
    
    # Clean up line breaks
    text = text.replace('\n\n\n', '\n\n')
    
    return text.strip()

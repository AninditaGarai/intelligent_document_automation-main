"""
Optical Character Recognition (OCR) Module

Extracts text from preprocessed images using Tesseract OCR.
Produces both raw text and confidence-scored text for reliability analysis.
"""

import os
import sys
from pathlib import Path
from subprocess import TimeoutExpired
import threading


def _require_pytesseract():
    try:
        import pytesseract
        return pytesseract
    except Exception as e:
        raise ImportError(
            "Missing dependency: pytesseract. Install with 'pip install pytesseract' "
            "and ensure Tesseract OCR is installed and available on PATH."
        ) from e


def _ocr_with_timeout(image_path: str, timeout_sec: int = 10) -> str:
    """Execute OCR with timeout to prevent hanging."""
    result = [None]
    error = [None]
    
    def ocr_thread():
        try:
            import pytesseract
            custom_config = r'--psm 11 --oem 3 --timeout 10'
            text = pytesseract.image_to_string(image_path, config=custom_config, timeout=timeout_sec)
            result[0] = text
        except Exception as e:
            error[0] = str(e)
    
    thread = threading.Thread(target=ocr_thread, daemon=True)
    thread.start()
    thread.join(timeout=timeout_sec + 2)
    
    if thread.is_alive():
        # Timeout occurred
        return _fallback_text_extraction(image_path)
    
    if error[0]:
        print(f"  Warning: OCR failed - {error[0]}")
        return _fallback_text_extraction(image_path)
    
    return result[0] or ""


def _fallback_text_extraction(image_path: str) -> str:
    """Fallback text extraction when Tesseract is unavailable or times out."""
    try:
        from PIL import Image
        img = Image.open(image_path)
        # Return image filename as placeholder text
        filename = Path(image_path).stem
        return f"[Image: {filename}]\n[OCR not available - Tesseract not configured]"
    except Exception as e:
        return f"[Cannot extract text from image: {str(e)}]"


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from a single image using Tesseract OCR with fallback.
    
    Args:
        image_path (str): Path to preprocessed image
        
    Returns:
        str: Extracted text from the image
        
    Raises:
        FileNotFoundError: If image doesn't exist
    """
    
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    try:
        print(f"OCR Processing: {Path(image_path).name}")
        
        # Try OCR with timeout, fallback to placeholder if unavailable
        text = _ocr_with_timeout(image_path, timeout_sec=10)
        
        if text and "[Cannot extract" not in text and "[OCR not available" not in text:
            print(f"  Extracted {len(text)} characters\n")
        else:
            print(f"  Fallback mode: Using placeholder text\n")
        
        return text
        
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"  Error: {str(e)} - using fallback\n")
        return _fallback_text_extraction(image_path)


def extract_text_with_confidence(image_path: str) -> dict:
    """
    Extract text along with confidence scores for each word.
    Falls back to basic extraction if Tesseract unavailable.
    
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
        # Get text with timeout
        full_text = _ocr_with_timeout(image_path, timeout_sec=10)
        
        # If using fallback text, return simplified structure
        if "[OCR not available" in full_text or "[Cannot extract" in full_text:
            return {
                'full_text': full_text,
                'confidence_data': [],
                'average_confidence': 0,
                'total_words': 0,
                'fallback_mode': True
            }
        
        # Try to get detailed data if Tesseract is working
        try:
            import pytesseract
            data = pytesseract.image_to_data(image_path, output_type=pytesseract.Output.DICT)
            
            confidence_data = []
            for i in range(len(data['text'])):
                word = data['text'][i]
                conf = int(data['conf'][i])
                if word.strip():
                    confidence_data.append({'word': word, 'confidence': conf})
            
            avg_confidence = sum(d['confidence'] for d in confidence_data) / len(confidence_data) if confidence_data else 0
        except:
            confidence_data = []
            avg_confidence = 0
        
        result = {
            'full_text': full_text,
            'confidence_data': confidence_data,
            'average_confidence': avg_confidence,
            'total_words': len(confidence_data)
        }
        
        return result
        
    except FileNotFoundError:
        raise
    except Exception as e:
        print(f"  Fallback mode: {str(e)}")
        return {
            'full_text': _fallback_text_extraction(image_path),
            'confidence_data': [],
            'average_confidence': 0,
            'total_words': 0,
            'fallback_mode': True
        }


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

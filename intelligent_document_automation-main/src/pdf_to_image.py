"""
PDF to Image Converter Module

Converts scanned PDF documents into image files (PNG format) for further processing.
Each page in a PDF is converted to a separate image file.
"""

import os
from pathlib import Path

# Poppler path: allow override via environment variable `POPPLER_PATH`.
# Keep None as default so pdf2image will try to use PATH when available.
POPPLER_PATH = os.environ.get("POPPLER_PATH")


def convert_pdf_to_images(pdf_path: str, output_dir: str) -> list:
    """
    Convert all pages of a PDF to individual image files.
    
    Args:
        pdf_path (str): Full path to the PDF file
        output_dir (str): Directory to save the output images
        
    Returns:
        list: List of paths to generated image files
        
    Raises:
        FileNotFoundError: If PDF file does not exist
        Exception: If PDF conversion fails
    """
    
    # Validate input
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract filename without extension
    pdf_name = Path(pdf_path).stem
    
    try:
        # Lazy import to avoid hard failure when optional dependency is missing
        try:
            from pdf2image import convert_from_path
        except Exception as ie:
            raise ImportError(
                "Missing dependency: pdf2image. Install it with 'pip install pdf2image' "
                "and ensure Poppler is installed and its bin is on PATH or set POPPLER_PATH env var."
            ) from ie

        # Convert PDF to images with DPI 200 for better OCR accuracy
        print(f"Converting PDF: {pdf_path}")
        if POPPLER_PATH:
            images = convert_from_path(pdf_path, dpi=200, poppler_path=POPPLER_PATH)
        else:
            images = convert_from_path(pdf_path, dpi=200)
        
        image_paths = []
        
        # Save each page as PNG
        for idx, image in enumerate(images):
            # Generate output filename: document_name_page_001.png
            output_filename = f"{pdf_name}_page_{idx + 1:03d}.png"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save image
            image.save(output_path, "PNG")
            image_paths.append(output_path)
            
            print(f"  Saved: {output_filename}")
        
        print(f"Conversion complete: {len(image_paths)} pages converted\n")
        return image_paths
        
    except Exception as e:
        print(f"Error converting PDF to images: {str(e)}")
        raise


def batch_convert_pdfs(pdf_dir: str, output_dir: str) -> dict:
    """
    Convert all PDF files in a directory to images.
    
    Args:
        pdf_dir (str): Directory containing PDF files
        output_dir (str): Directory to save output images
        
    Returns:
        dict: Mapping of PDF filenames to lists of image paths
    """
    
    if not os.path.exists(pdf_dir):
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")
    
    pdf_to_images_map = {}
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print(f"Warning: No PDF files found in {pdf_dir}")
        return pdf_to_images_map
    
    print(f"Found {len(pdf_files)} PDF file(s) in {pdf_dir}\n")
    
    # Process each PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_dir, pdf_file)
        try:
            image_paths = convert_pdf_to_images(pdf_path, output_dir)
            pdf_to_images_map[pdf_file] = image_paths
        except Exception as e:
            print(f"Failed to convert {pdf_file}: {str(e)}")
            continue
    
    return pdf_to_images_map

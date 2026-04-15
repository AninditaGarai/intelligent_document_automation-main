"""
Main Orchestration Module

Coordinates the entire document processing pipeline:
1. Convert PDFs to images
2. Preprocess images
3. Extract text via OCR
4. Classify documents
5. Extract fields
6. Perform semantic matching
7. Export results to Excel

This is an academic prototype for Intelligent Document Automation
with Explainable Semantic Matching.
"""

import os
import sys
from pathlib import Path

# Import all modules
from src.pdf_to_image import batch_convert_pdfs
from src.preprocess import batch_preprocess_images
from src.ocr import batch_ocr_images
from src.document_classifier import classify_documents
from src.field_extractor import extract_fields_from_documents
from src.semantic_matcher import HybridMatchingEngine, perform_multi_document_matching
from src.export_excel import ExcelExporter


def setup_directories(base_path: str) -> dict:
    """
    Setup and verify all required directories.
    
    Args:
        base_path (str): Base project directory
        
    Returns:
        dict: Paths to all directories
    """
    
    dirs = {
        'input_pdfs': os.path.join(base_path, 'input_pdfs'),
        'images': os.path.join(base_path, 'images'),
        'extracted_text': os.path.join(base_path, 'extracted_text'),
        'output': os.path.join(base_path, 'output'),
        'preprocessed': os.path.join(base_path, 'images', 'preprocessed')
    }
    
    # Create all directories
    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    return dirs


def main():
    """
    Main execution function for document processing pipeline.
    """
    
    print("="*80)
    print("INTELLIGENT DOCUMENT AUTOMATION WITH EXPLAINABLE SEMANTIC MATCHING")
    print("="*80)
    print()
    
    # Get base project path (go up one level from src directory)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Setup directories
    print("Step 0: Setting up directories...")
    dirs = setup_directories(base_path)
    print(f"  Input PDFs: {dirs['input_pdfs']}")
    print(f"  Output: {dirs['output']}")
    print()
    
    # Step 1: Convert PDFs to Images
    print("="*80)
    print("STEP 1: Converting PDFs to Images...")
    print("="*80)
    print()
    
    if len(os.listdir(dirs['input_pdfs'])) == 0:
        print(f"WARNING: No PDF files found in {dirs['input_pdfs']}")
        print("Please add PDF files to the input_pdfs directory and run again.")
        print()
        return
    
    pdf_to_images = batch_convert_pdfs(
        dirs['input_pdfs'],
        dirs['images']
    )
    
    if not pdf_to_images:
        print("ERROR: No PDFs were successfully converted. Aborting.")
        return
    
    print(f"Successfully converted {len(pdf_to_images)} PDF(s) to images\n")
    
    # Step 2: Preprocess Images
    print("="*80)
    print("STEP 2: Preprocessing Images for OCR...")
    print("="*80)
    print()
    
    preprocessed_images = batch_preprocess_images(
        dirs['images'],
        dirs['preprocessed']
    )
    
    if not preprocessed_images:
        print("ERROR: No images were successfully preprocessed. Aborting.")
        return
    
    print(f"Successfully preprocessed {len(preprocessed_images)} image(s)\n")
    
    # Step 3: Extract Text via OCR
    print("="*80)
    print("STEP 3: Extracting Text via Tesseract OCR...")
    print("="*80)
    print()
    
    ocr_results = batch_ocr_images(
        dirs['preprocessed'],
        dirs['extracted_text']
    )
    
    if not ocr_results:
        print("ERROR: OCR extraction failed. Aborting.")
        return
    
    print(f"Successfully extracted text from {len(ocr_results)} image(s)\n")
    
    # Step 4: Classify Documents
    print("="*80)
    print("STEP 4: Classifying Documents...")
    print("="*80)
    print()
    
    classifications = classify_documents(ocr_results)
    
    print(f"Successfully classified {len(classifications)} document(s)\n")
    
    # Step 5: Extract Fields
    print("="*80)
    print("STEP 5: Extracting Key Fields...")
    print("="*80)
    print()
    
    extracted_fields = extract_fields_from_documents(ocr_results)
    
    print(f"Successfully extracted fields from {len(extracted_fields)} document(s)\n")
    
    # Step 6: Perform Semantic Matching with Hybrid Framework
    print("="*80)
    print("STEP 6: Performing Hybrid Pattern-Semantic Matching...")
    print("="*80)
    print()
    
    # Create documents dict for matching
    matching_input = {}
    for doc_name, fields in extracted_fields.items():
        matching_input[doc_name] = fields
    
    # Perform multi-document matching using hybrid matching engine
    if len(matching_input) >= 2:
        matching_results = perform_multi_document_matching(matching_input)
        print(f"Completed hybrid matching across {len(extracted_fields)} document(s)")
        print(f"  - Pattern Matching Layer: Applied")
        print(f"  - Rule-Based Validation Layer: Applied")
        print(f"  - Semantic Similarity Layer (LLM-inspired): Applied")
        print(f"  - Decision Fusion Engine: Applied")
        print()
    else:
        print("Warning: Less than 2 documents for matching. Matching skipped.")
        print()
        matching_results = {}
    
    # Step 7: Export Results
    print("="*80)
    print("STEP 7: Exporting Results to Excel...")
    print("="*80)
    print()
    
    exporter = ExcelExporter()
    
    # Export individual results
    extraction_output = os.path.join(dirs['output'], 'Extracted_Fields.xlsx')
    exporter.export_extraction_results(extracted_fields, extraction_output)
    
    classification_output = os.path.join(dirs['output'], 'Document_Classification.xlsx')
    exporter.export_classification_results(classifications, classification_output)
    
    # Export matching results with hybrid matching explanations
    if matching_results and 'details' in matching_results:
        matching_output = os.path.join(dirs['output'], 'Hybrid_Matching_Results.xlsx')
        exporter.export_hybrid_matching_results(matching_results, matching_output)
    
    # Step 8: Summary
    print("="*80)
    print("PROCESSING COMPLETE ✓")
    print("="*80)
    print()
    print("Summary of Results:")
    print(f"  Documents Processed: {len(classifications)}")
    print(f"  Document Types Identified: {len(set(c.get('document_type', 'Unknown') for c in classifications.values() if isinstance(c, dict)))}")
    print(f"  Fields Extracted: {sum(len(fields) for fields in extracted_fields.values() if isinstance(fields, dict))}")
    print(f"  Document Pairs Matched: {len(matching_results.get('details', {}))}")
    print()
    print("Hybrid Matching Framework Applied:")
    print("  ✓ Pattern Matching Layer (SequenceMatcher + company suffix normalization)")
    print("  ✓ Rule-Based Validation Layer (currency normalization)")
    print("  ✓ Semantic Similarity Layer (Token-based Jaccard, LLM-inspired)")
    print("  ✓ Decision Fusion Engine (0.6×Pattern + 0.4×Semantic)")
    print("  ✓ Explainable Output with numeric scores")
    print()
    print("Output Files Generated:")
    print(f"  - {extraction_output}")
    print(f"  - {classification_output}")
    if matching_results and 'details' in matching_results:
        print(f"  - {matching_output}")
    print()
    print("All files are ready in the 'output' directory.")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print("Please check your setup and try again.")
        sys.exit(1)

"""
Reusable document-processing pipeline.

This module centralizes the backend workflow so it can be used both by the
command-line entry point and the web frontend.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, List
from functools import lru_cache
import hashlib

logger = logging.getLogger(__name__)

from src.document_classifier import classify_documents
from src.export_excel import ExcelExporter
from src.field_extractor import extract_fields_from_documents
from src.ocr import batch_ocr_images
from src.pdf_to_image import batch_convert_pdfs
from src.preprocess import batch_preprocess_images
from src.semantic_matcher import perform_multi_document_matching


def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file for caching purposes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def get_cache_key(file_path: Path, operation: str) -> str:
    """
    Generate a cache key for a file and operation.
    
    Args:
        file_path: Path to the file
        operation: Operation being performed
        
    Returns:
        Cache key string
    """
    file_hash = get_file_hash(file_path)
    return f"{operation}_{file_hash}"


def setup_directories(base_path: str, input_pdf_dir: Optional[str] = None) -> Dict[str, str]:
    """Create and return the working directories used by the pipeline.
    
    Args:
        base_path: Base directory for all pipeline operations
        input_pdf_dir: Optional custom input directory for PDFs
        
    Returns:
        Dictionary mapping directory names to their absolute paths
        
    Raises:
        OSError: If directory creation fails
    """
    base_path = Path(base_path).resolve()
    
    dirs = {
        'input_pdfs': Path(input_pdf_dir) if input_pdf_dir else base_path / 'input_pdfs',
        'images': base_path / 'images',
        'extracted_text': base_path / 'extracted_text',
        'output': base_path / 'output',
        'preprocessed': base_path / 'images' / 'preprocessed',
    }

    for dir_name, dir_path in dirs.items():
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {dir_name} at {dir_path}")
        except OSError as e:
            logger.error(f"Failed to create directory {dir_name} at {dir_path}: {e}")
            raise

    return {k: str(v) for k, v in dirs.items()}


def run_pipeline(base_path: str, input_pdf_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run the full document-processing pipeline and return a structured summary.
    
    Args:
        base_path: Base directory for pipeline operations
        input_pdf_dir: Optional custom input directory for PDFs
        
    Returns:
        Dictionary containing pipeline status, results, and summary metrics
        
    Raises:
        Exception: If critical pipeline steps fail
    """
    import time
    start_time = time.time()
    
    try:
        dirs = setup_directories(base_path, input_pdf_dir=input_pdf_dir)
        input_path = Path(dirs['input_pdfs'])
        pdf_files = [f for f in input_path.iterdir() if f.suffix.lower() == '.pdf']

        if not pdf_files:
            msg = f"No PDF files found in {dirs['input_pdfs']}"
            logger.warning(msg)
            return {
                'status': 'no_input',
                'message': msg,
                'dirs': dirs,
                'output_files': [],
            }

        logger.info(f"Found {len(pdf_files)} PDF files")

        # Step 1: PDF to Image conversion with timing
        step_start = time.time()
        pdf_to_images = batch_convert_pdfs(dirs['input_pdfs'], dirs['images'])
        step_time = time.time() - step_start
        logger.info(f"PDF to images: {len(pdf_to_images)} conversions in {step_time:.2f}s")
        
        if not pdf_to_images:
            msg = 'No PDFs were successfully converted.'
            logger.error(msg)
            return {
                'status': 'error',
                'message': msg,
                'dirs': dirs,
                'output_files': [],
            }
        
        # Step 2: Image preprocessing with timing
        step_start = time.time()
        preprocessed_images = batch_preprocess_images(dirs['images'], dirs['preprocessed'])
        step_time = time.time() - step_start
        logger.info(f"Preprocessed images: {len(preprocessed_images)} images in {step_time:.2f}s")
        
        if not preprocessed_images:
            msg = 'No images were successfully preprocessed.'
            logger.error(msg)
            return {
                'status': 'error',
                'message': msg,
                'dirs': dirs,
                'output_files': [],
            }
        
        # Step 3: OCR with timing
        step_start = time.time()
        ocr_results = batch_ocr_images(dirs['preprocessed'], dirs['extracted_text'])
        step_time = time.time() - step_start
        logger.info(f"OCR results: {len(ocr_results)} documents in {step_time:.2f}s")
        
        if not ocr_results:
            msg = 'OCR extraction failed.'
            logger.error(msg)
            return {
                'status': 'error',
                'message': msg,
                'dirs': dirs,
                'output_files': [],
            }
        
        # Step 4: Classification and extraction with timing
        step_start = time.time()
        classifications = classify_documents(ocr_results)
        extracted_fields = extract_fields_from_documents(ocr_results)
        step_time = time.time() - step_start
        logger.info(f"Classifications: {len(classifications)} documents in {step_time:.2f}s")
        logger.info(f"Field extraction: {len(extracted_fields)} documents")

        # Step 5: Matching with timing
        step_start = time.time()
        matching_input = {doc_name: fields for doc_name, fields in extracted_fields.items()}
        matching_results: Dict[str, Any] = {}
        if len(matching_input) >= 2:
            matching_results = perform_multi_document_matching(matching_input)
            step_time = time.time() - step_start
            logger.info(f"Document matching: {len(matching_results.get('details', {}))} pairs found in {step_time:.2f}s")

        # Step 6: Export results with timing
        step_start = time.time()
        exporter = ExcelExporter()

        output_files: List[str] = []
        extraction_output = str(Path(dirs['output']) / 'Extracted_Fields.xlsx')
        exporter.export_extraction_results(extracted_fields, extraction_output)
        output_files.append(extraction_output)
        logger.info(f"Exported extraction results to {extraction_output}")

        classification_output = str(Path(dirs['output']) / 'Document_Classification.xlsx')
        exporter.export_classification_results(classifications, classification_output)
        output_files.append(classification_output)
        logger.info(f"Exported classification results to {classification_output}")

        matching_output = None
        if matching_results and 'details' in matching_results:
            matching_output = str(Path(dirs['output']) / 'Hybrid_Matching_Results.xlsx')
            exporter.export_hybrid_matching_results(matching_results, matching_output)
            output_files.append(matching_output)
            logger.info(f"Exported matching results to {matching_output}")
        
        step_time = time.time() - step_start
        logger.info(f"Export completed in {step_time:.2f}s")

        # Calculate metrics
        num_documents = len(classifications)
        
        # Count unique document types (with confidence > 0)
        unique_types = set()
        for c in classifications.values():
            if isinstance(c, dict) and c.get('confidence', 0) > 0:
                unique_types.add(c.get('document_type', 'Unknown'))
        
        # Count fields that were actually extracted with confidence > 0
        fields_with_values = 0
        for doc_fields in extracted_fields.values():
            if isinstance(doc_fields, dict):
                for field_data in doc_fields.values():
                    if isinstance(field_data, dict) and field_data.get('confidence', 0) > 0:
                        fields_with_values += 1
        
        # Count matched pairs
        pairs_matched = len(matching_results.get('details', {}))
        
        logger.info(f"Pipeline complete: {num_documents} docs, {len(unique_types)} types, {fields_with_values} fields, {pairs_matched} pairs matched")
        
        total_time = time.time() - start_time
        logger.info(f"Total pipeline execution time: {total_time:.2f}s")
        
        return {
            'status': 'ok',
            'message': 'Processing complete',
            'dirs': dirs,
            'output_files': output_files,
            'pdf_to_images': pdf_to_images,
            'preprocessed_images': preprocessed_images,
            'ocr_results': ocr_results,
            'classifications': classifications,
            'extracted_fields': extracted_fields,
            'matching_results': matching_results,
            'matching_output': matching_output,
            'summary': {
                'documents_processed': num_documents,
                'document_types_identified': len(unique_types),
                'fields_extracted': fields_with_values,
                'document_pairs_matched': pairs_matched,
                'total_execution_time_seconds': round(total_time, 2),
            },
        }
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        return {
            'status': 'error',
            'message': f'Pipeline execution failed: {str(e)}',
            'output_files': [],
        }
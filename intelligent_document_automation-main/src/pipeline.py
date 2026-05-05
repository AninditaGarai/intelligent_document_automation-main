"""
Reusable document-processing pipeline.

This module centralizes the backend workflow so it can be used both by the
command-line entry point and the web frontend.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

from src.document_classifier import classify_documents
from src.export_excel import ExcelExporter
from src.field_extractor import extract_fields_from_documents
from src.ocr import batch_ocr_images
from src.pdf_to_image import batch_convert_pdfs
from src.preprocess import batch_preprocess_images
from src.semantic_matcher import perform_multi_document_matching


def setup_directories(base_path: str, input_pdf_dir: Optional[str] = None) -> Dict[str, str]:
    """Create and return the working directories used by the pipeline."""

    dirs = {
        'input_pdfs': input_pdf_dir or os.path.join(base_path, 'input_pdfs'),
        'images': os.path.join(base_path, 'images'),
        'extracted_text': os.path.join(base_path, 'extracted_text'),
        'output': os.path.join(base_path, 'output'),
        'preprocessed': os.path.join(base_path, 'images', 'preprocessed'),
    }

    for dir_path in dirs.values():
        os.makedirs(dir_path, exist_ok=True)

    return dirs


def run_pipeline(base_path: str, input_pdf_dir: Optional[str] = None) -> Dict[str, Any]:
    """Run the full document-processing pipeline and return a structured summary."""

    dirs = setup_directories(base_path, input_pdf_dir=input_pdf_dir)
    pdf_files = [f for f in os.listdir(dirs['input_pdfs']) if f.lower().endswith('.pdf')]

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

    pdf_to_images = batch_convert_pdfs(dirs['input_pdfs'], dirs['images'])
    if not pdf_to_images:
        msg = 'No PDFs were successfully converted.'
        logger.error(msg)
        return {
            'status': 'error',
            'message': msg,
            'dirs': dirs,
            'output_files': [],
        }
    
    logger.info(f"PDF to images: {len(pdf_to_images)} conversions")

    preprocessed_images = batch_preprocess_images(dirs['images'], dirs['preprocessed'])
    if not preprocessed_images:
        msg = 'No images were successfully preprocessed.'
        logger.error(msg)
        return {
            'status': 'error',
            'message': msg,
            'dirs': dirs,
            'output_files': [],
        }
    
    logger.info(f"Preprocessed images: {len(preprocessed_images)} images")

    ocr_results = batch_ocr_images(dirs['preprocessed'], dirs['extracted_text'])
    if not ocr_results:
        msg = 'OCR extraction failed.'
        logger.error(msg)
        return {
            'status': 'error',
            'message': msg,
            'dirs': dirs,
            'output_files': [],
        }
    
    logger.info(f"OCR results: {len(ocr_results)} documents")

    classifications = classify_documents(ocr_results)
    extracted_fields = extract_fields_from_documents(ocr_results)
    
    logger.info(f"Classifications: {len(classifications)} documents")
    logger.info(f"Field extraction: {len(extracted_fields)} documents")

    matching_input = {doc_name: fields for doc_name, fields in extracted_fields.items()}
    matching_results: Dict[str, Any] = {}
    if len(matching_input) >= 2:
        matching_results = perform_multi_document_matching(matching_input)
        logger.info(f"Document matching: {len(matching_results.get('details', {}))} pairs found")

    exporter = ExcelExporter()

    output_files = []
    extraction_output = os.path.join(dirs['output'], 'Extracted_Fields.xlsx')
    exporter.export_extraction_results(extracted_fields, extraction_output)
    output_files.append(extraction_output)
    logger.info(f"Exported extraction results to {extraction_output}")

    classification_output = os.path.join(dirs['output'], 'Document_Classification.xlsx')
    exporter.export_classification_results(classifications, classification_output)
    output_files.append(classification_output)
    logger.info(f"Exported classification results to {classification_output}")

    matching_output = None
    if matching_results and 'details' in matching_results:
        matching_output = os.path.join(dirs['output'], 'Hybrid_Matching_Results.xlsx')
        exporter.export_hybrid_matching_results(matching_results, matching_output)
        output_files.append(matching_output)
        logger.info(f"Exported matching results to {matching_output}")

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
        },
    }
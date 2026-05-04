"""
Reusable document-processing pipeline.

This module centralizes the backend workflow so it can be used both by the
command-line entry point and the web frontend.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

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
        return {
            'status': 'no_input',
            'message': f"No PDF files found in {dirs['input_pdfs']}",
            'dirs': dirs,
            'output_files': [],
        }

    pdf_to_images = batch_convert_pdfs(dirs['input_pdfs'], dirs['images'])
    if not pdf_to_images:
        return {
            'status': 'error',
            'message': 'No PDFs were successfully converted.',
            'dirs': dirs,
            'output_files': [],
        }

    preprocessed_images = batch_preprocess_images(dirs['images'], dirs['preprocessed'])
    if not preprocessed_images:
        return {
            'status': 'error',
            'message': 'No images were successfully preprocessed.',
            'dirs': dirs,
            'output_files': [],
        }

    ocr_results = batch_ocr_images(dirs['preprocessed'], dirs['extracted_text'])
    if not ocr_results:
        return {
            'status': 'error',
            'message': 'OCR extraction failed.',
            'dirs': dirs,
            'output_files': [],
        }

    classifications = classify_documents(ocr_results)
    extracted_fields = extract_fields_from_documents(ocr_results)

    matching_input = {doc_name: fields for doc_name, fields in extracted_fields.items()}
    matching_results: Dict[str, Any] = {}
    if len(matching_input) >= 2:
        matching_results = perform_multi_document_matching(matching_input)

    exporter = ExcelExporter()

    output_files = []
    extraction_output = os.path.join(dirs['output'], 'Extracted_Fields.xlsx')
    exporter.export_extraction_results(extracted_fields, extraction_output)
    output_files.append(extraction_output)

    classification_output = os.path.join(dirs['output'], 'Document_Classification.xlsx')
    exporter.export_classification_results(classifications, classification_output)
    output_files.append(classification_output)

    matching_output = None
    if matching_results and 'details' in matching_results:
        matching_output = os.path.join(dirs['output'], 'Hybrid_Matching_Results.xlsx')
        exporter.export_hybrid_matching_results(matching_results, matching_output)
        output_files.append(matching_output)

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
            'documents_processed': len(classifications),
            'document_types_identified': len({
                c.get('document_type', 'Unknown') for c in classifications.values() if isinstance(c, dict)
            }),
            'fields_extracted': sum(len(fields) for fields in extracted_fields.values() if isinstance(fields, dict)),
            'document_pairs_matched': len(matching_results.get('details', {})),
        },
    }
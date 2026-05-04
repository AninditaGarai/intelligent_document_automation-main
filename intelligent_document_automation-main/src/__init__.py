"""
Intelligent Document Automation with Explainable Semantic Matching.

The package exposes the document-processing modules without importing them
eagerly so that optional dependencies do not break simple imports.
"""

__version__ = "1.0.0"
__title__ = "Intelligent Document Automation"
__description__ = "End-to-end document processing with explainable semantic matching"

__all__ = [
    'pdf_to_image',
    'preprocess',
    'ocr',
    'document_classifier',
    'field_extractor',
    'semantic_matcher',
    'export_excel',
    'main',
    'pipeline',
]

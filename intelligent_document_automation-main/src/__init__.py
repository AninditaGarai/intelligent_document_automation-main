"""
Intelligent Document Automation with Explainable Semantic Matching

An academic final-year project that processes scanned financial/legal PDFs.

Key Features:
- PDF to image conversion with OCR
- Document classification (rule-based)
- Field extraction (pattern matching)
- Semantic matching with explainability (XAI)
- Excel report generation

Version: 1.0
Author: Academic Project
"""

__version__ = "1.0.0"
__title__ = "Intelligent Document Automation"
__description__ = "End-to-end document processing with explainable semantic matching"

from . import pdf_to_image
from . import preprocess
from . import ocr
from . import document_classifier
from . import field_extractor
from . import semantic_matcher
from . import export_excel
from . import main

__all__ = [
    'pdf_to_image',
    'preprocess',
    'ocr',
    'document_classifier',
    'field_extractor',
    'semantic_matcher',
    'export_excel',
    'main'
]

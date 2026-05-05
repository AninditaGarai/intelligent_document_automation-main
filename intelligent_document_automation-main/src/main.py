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

import sys
import argparse
import logging
from pathlib import Path

from src.pipeline import run_pipeline
from src.logger_config import setup_logging

logger = logging.getLogger("document_automation")


def main():
    """Main execution function for document processing pipeline."""
    parser = argparse.ArgumentParser(
        description="Intelligent Document Automation with Explainable Semantic Matching"
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Custom input PDF directory (default: ./input_pdfs)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        default="logs",
        help="Directory for log files (default: ./logs)"
    )
    
    args = parser.parse_args()
    setup_logging(log_dir=args.log_dir, log_level=args.log_level)
    
    print("="*80)
    print("INTELLIGENT DOCUMENT AUTOMATION WITH EXPLAINABLE SEMANTIC MATCHING")
    print("="*80)
    print()
    logger.info(f"Starting pipeline with log level {args.log_level}")
    
    # Get base project path (go up one level from src directory)
    base_path = Path(__file__).resolve().parents[1]
    logger.info(f"Base path: {base_path}")
    
    # Setup directories
    print("Step 0: Setting up directories...")
    summary = run_pipeline(str(base_path), input_pdf_dir=args.input)
    print(f"  Input PDFs: {summary['dirs']['input_pdfs']}")
    print(f"  Output: {summary['dirs']['output']}")
    print()

    if summary['status'] == 'no_input':
        print(f"WARNING: {summary['message']}")
        print("Please add PDF files to the input_pdfs directory and run again.")
        print()
        logger.warning(summary['message'])
        return

    if summary['status'] != 'ok':
        print(f"ERROR: {summary['message']}")
        logger.error(summary['message'])
        return
    
    logger.info("Pipeline completed successfully")

    print("="*80)
    print("PROCESSING COMPLETE ✓")
    print("="*80)
    print()
    print("Summary of Results:")
    print(f"  Documents Processed: {summary['summary']['documents_processed']}")
    print(f"  Document Types Identified: {summary['summary']['document_types_identified']}")
    print(f"  Fields Extracted: {summary['summary']['fields_extracted']}")
    print(f"  Document Pairs Matched: {summary['summary']['document_pairs_matched']}")
    print()
    print("Output Files Generated:")
    for output_file in summary['output_files']:
        print(f"  - {output_file}")
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

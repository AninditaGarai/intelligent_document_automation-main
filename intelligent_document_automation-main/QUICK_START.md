# Quick Start Guide

Get the Intelligent Document Automation system running in 5 minutes!

---

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] pip package manager available
- [ ] Tesseract OCR installed
- [ ] Poppler installed
- [ ] Project files extracted/cloned

---

## Installation (Windows)

### 1. Install Tesseract OCR (One-time)

```powershell
# Option A: Using Chocolatey
choco install tesseract

# Option B: Manual download
# Visit: https://github.com/UB-Mannheim/tesseract/wiki
# Download and run installer
# Default install path: C:\Program Files\Tesseract-OCR
```

### 2. Install Poppler (One-time)

```powershell
# Using Chocolatey
choco install poppler

# OR using Python package
pip install python-poppler-qt5
```

### 3. Install Python Dependencies

```powershell
# Navigate to project directory
cd "c:\Users\ruchi\OneDrive\Desktop\Intelligent_Document_Automation"

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**Installation Time**: ~2-3 minutes (first time)

---

## Running the System

### Step 1: Add PDF Files
Place your PDF files in the `input_pdfs/` folder:
```
input_pdfs/
├── quotation.pdf
├── sow_document.pdf
└── contract.pdf
```

### Step 2: Run the Pipeline
```powershell
# Make sure virtual environment is activated
venv\Scripts\activate

# Run the main script
python -m src.main
```

**Processing Time**: ~30 seconds per page (depends on page quality)

### Step 3: Check Results
Results are in the `output/` folder:
- `Complete_Report.xlsx` ← **Start here** (recommended)
- `Extracted_Fields.xlsx`
- `Document_Classification.xlsx`
- `Semantic_Matching.xlsx`

---

## Example Run

### Input
Place 2 sample PDFs in `input_pdfs/`:
- `quotation.pdf` - A quotation document
- `contract.pdf` - A contract document

### Run Command
```powershell
python -m src.main
```

### Expected Output
```
================================================================================
INTELLIGENT DOCUMENT AUTOMATION WITH EXPLAINABLE SEMANTIC MATCHING
================================================================================

Step 0: Setting up directories...
Step 1: Converting PDFs to Images...
  Converted 2 PDF(s) to images

Step 2: Preprocessing Images for OCR...
  Preprocessed 2 image(s)

Step 3: Extracting Text via OCR...
  Extracted text from 2 image(s)

Step 4: Classifying Documents...
  Quotation: Confidence 95%
  Contract: Confidence 92%

Step 5: Extracting Key Fields...
  Client Name: ABC Corporation (Confidence 85%)
  Currency: USD (Confidence 95%)
  ...

Step 6: Performing Semantic Matching...
  Overall Match Score: 85.3/100

Step 7: Exporting Results to Excel...
  ✓ Extracted_Fields.xlsx
  ✓ Document_Classification.xlsx
  ✓ Semantic_Matching.xlsx
  ✓ Complete_Report.xlsx

✅ PROCESSING COMPLETE
```

---

## Understanding the Output

### Complete_Report.xlsx (Main Report)

**Sheet 1: Summary**
- Total documents processed
- Average match score
- Quick overview

**Sheet 2: Document Classification**
- Document type (Quotation/SOW/Contract)
- Confidence score
- Keywords found

**Sheet 3: Extracted Fields**
- Client Name, Organization, Currency, Address
- Extraction confidence for each field
- Why it was extracted that way

**Sheet 4: Semantic Matching**
- Field-by-field comparison
- Match scores with explanations
- Value pairs being compared

---

## Troubleshooting

### "pytesseract.TesseractNotFoundError"
**Solution**:
1. Verify Tesseract is installed: `tesseract --version`
2. If not found, install from: https://github.com/UB-Mannheim/tesseract/wiki
3. Edit `src/ocr.py` line 22 to your install path:
   ```python
   pytesseract.pytesseract.pytesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### "ModuleNotFoundError" for pdf2image
**Solution**:
```powershell
# Install missing package
pip install pdf2image

# May need poppler
pip install python-poppler-qt5
```

### Poor OCR Quality
**Solutions**:
1. Ensure PDFs are well-scanned (≥150 DPI)
2. Check output in `images/preprocessed/` folder
3. Adjust preprocessing parameters in `src/preprocess.py`

### No results generated
**Checklist**:
1. Verify PDFs are in `input_pdfs/` folder
2. Check file extensions are `.pdf` (case-sensitive on Linux)
3. Run with:
   ```powershell
   python -m src.main 2>&1 | Tee output.log
   ```
   This saves errors to `output.log` for debugging

---

## File Structure Reference

```
Intelligent_Document_Automation/
├── input_pdfs/          ← Add your PDFs here
│   ├── document1.pdf
│   └── document2.pdf
│
├── images/
│   ├── (raw converted images)
│   └── preprocessed/    ← Preprocessed images (check quality)
│
├── extracted_text/      ← Raw OCR output
│   ├── document1_page_001.txt
│   └── document2_page_001.txt
│
├── output/              ← YOUR RESULTS
│   ├── Complete_Report.xlsx         ← Open this first!
│   ├── Extracted_Fields.xlsx
│   ├── Document_Classification.xlsx
│   └── Semantic_Matching.xlsx
│
├── src/
│   ├── pdf_to_image.py        (Step 1)
│   ├── preprocess.py          (Step 2)
│   ├── ocr.py                 (Step 3)
│   ├── document_classifier.py (Step 4)
│   ├── field_extractor.py     (Step 5)
│   ├── semantic_matcher.py    (Step 6) ⭐ XAI Magic Here
│   ├── export_excel.py        (Step 7)
│   └── main.py                (Orchestrator)
│
├── docs/
│   ├── SEMANTIC_MATCHING_EXAMPLES.md
│   └── EXPLAINABLE_AI_GUIDE.md
│
├── requirements.txt           ← Dependencies
├── README.md                  ← Full documentation
└── QUICK_START.md             ← This file
```

---

## Common Customizations

### Change Input/Output Folder
Edit `src/main.py`:
```python
base_path = "C:\\your\\custom\\path"  # Line ~140
```

### Add Custom Document Type
Edit `src/document_classifier.py`:
```python
self.custom_keywords = [
    'custom_keyword_1', 'custom_keyword_2'
]
```

### Adjust OCR Settings
Edit `src/ocr.py`:
```python
custom_config = r'--psm 6 --oem 2'  # Change PSM mode (default: 11)
# PSM modes:
# 6 = Uniform block of text
# 11 = Sparse text
```

### Improve Field Extraction
Edit `src/field_extractor.py`:
```python
self.name_prefixes = [
    'client:', 'to:', 'customer:', 'for:', # Add more prefixes
]
```

---

## Performance Tips

### Process Multiple Documents
The system automatically handles all PDFs in `input_pdfs/`:
- Just add more files
- All are processed in sequence
- Results are combined in Excel

### Optimize for Speed
1. Use well-scanned PDFs (clearer = faster OCR)
2. Reduce image preprocessing if already clean
3. Use lighter compression if modifying images

### Optimize for Accuracy
1. Ensure high-quality scans (≥200 DPI)
2. Check preprocessed images: `images/preprocessed/`
3. Verify OCR text: `extracted_text/`
4. Adjust preprocessing in `preprocess.py` if needed

---

## Testing with Sample Data

### Create Sample PDF
If you don't have test PDFs, create one using any text editor:
1. Create a document with:
   ```
   QUOTATION
   
   To: ABC Corporation Limited
   From: XYZ Services Pvt Ltd
   
   Services: Software Development
   Total Price: $50,000
   Currency: USD
   
   Date: 2025-02-09
   ```
2. Save as PDF (print to PDF from Word/browser)
3. Place in `input_pdfs/` folder
4. Run the system

---

## Next Steps

1. **Read Full Documentation**: `README.md`
2. **Understand Semantic Matching**: `docs/SEMANTIC_MATCHING_EXAMPLES.md`
3. **Learn XAI Approach**: `docs/EXPLAINABLE_AI_GUIDE.md`
4. **Customize for Your Documents**: Edit field patterns
5. **Scale to Production**: Integrate with your workflow

---

## Viva Tips

**Be ready to explain:**
- ✅ Why rule-based matching is better than LLMs for this task
- ✅ How confidence scores are calculated
- ✅ Why normalization is important
- ✅ How you handle missing fields
- ✅ The difference between extraction and matching confidence

**Demonstrate:**
- ✅ Run live demo with sample PDFs
- ✅ Show Excel output with explanations
- ✅ Trace code for a matching decision
- ✅ Explain normalized text transformations

---

## Getting Help

1. **Installation Issues**: Check `README.md` Troubleshooting section
2. **Understanding Output**: Read Excel sheet explanations carefully
3. **Code Questions**: Check comments in source files
4. **Semantic Matching**: Review `SEMANTIC_MATCHING_EXAMPLES.md`
5. **XAI Concepts**: Read `EXPLAINABLE_AI_GUIDE.md`

---

## Summary

**Installation**: 5 minutes (one-time)  
**First Run**: 1 minute (with 2 sample PDFs)  
**Understanding Results**: 5 minutes  
**Total Time to First Results**: ~11 minutes ⚡

**You're all set! Start with Sample Data → Check Results → Customize as needed** 🚀


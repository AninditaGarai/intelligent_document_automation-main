# VISUALIZATION GRAPHS - QUICK START GUIDE

## Overview
Your results now include 6 comprehensive, publication-ready visualization graphs generated automatically after each analysis run.

## Generated Visualizations

### 1. **Confusion Matrix Heatmap** (`confusion_matrix.png`)
- **What it shows**: True Positives, True Negatives, False Positives, and False Negatives
- **Use case**: Visualize classification performance of field matching
- **Format**: Color-coded heatmap with numerical values
- **Research application**: Essential for academic papers on classification accuracy

### 2. **Evaluation Metrics Bar Chart** (`evaluation_metrics.png`)
- **What it shows**: Four key metrics in one visualization
  - Accuracy: Overall correctness of predictions
  - Precision: Accuracy of positive predictions
  - Recall: Coverage of actual positives
  - F1 Score: Harmonic mean of Precision and Recall
- **Use case**: Compare model performance across all metrics
- **Color coding**: Different colors for each metric for clarity
- **Research application**: Main performance summary for papers

### 3. **Document Classification Distribution** (`document_classification.png`)
- **What it shows**: Pie chart of document types found
  - Percentage of Quotations
  - Percentage of Statements of Work
  - Percentage of Contracts
  - Other document types
- **Use case**: Understand the composition of your document corpus
- **Format**: Pie chart with percentage labels
- **Research application**: Dataset composition overview

### 4. **Field Extraction Success Rate** (`field_extraction_success.png`)
- **What it shows**: Success rate for each field extracted
  - Name extraction success %
  - Organization extraction success %
  - Currency detection success %
  - Address extraction success %
- **Use case**: Identify which fields are most reliably extracted
- **Color coding**:
  - Green (≥80%): Excellent extraction
  - Yellow (50-79%): Good extraction
  - Red (<50%): Needs improvement
- **Research application**: Field-level performance analysis

### 5. **Confidence Score Distribution** (`confidence_distribution.png`)
- **What it shows**: Histogram of all confidence scores
  - Frequency distribution of scores 0.0-1.0
  - Mean confidence score marked
  - Color coded by confidence ranges
- **Use case**: Understand the reliability distribution of matches
- **Color coding**:
  - Green (≥0.8): High confidence matches
  - Yellow (0.5-0.8): Medium confidence
  - Red (<0.5): Low confidence matches
- **Research application**: Confidence calibration analysis

### 6. **Document-wise Performance Comparison** (`document_performance.png`)
- **What it shows**: Extraction success rate for each document
  - Comparison across all processed documents
  - Extraction success percentage per document
- **Use case**: Identify documents that were processed well or poorly
- **Format**: Bar chart with document names
- **Research application**: Per-document performance metrics

## Where to Find Graphs

All graphs are automatically saved in: `output/`

```
output/
├── confusion_matrix.png
├── evaluation_metrics.png
├── document_classification.png
├── field_extraction_success.png
├── confidence_distribution.png
├── document_performance.png
├── Extracted_Fields.xlsx
├── Currency_Normalization.xlsx
├── Document_Classification.xlsx
├── Hybrid_Matching_Results.xlsx
└── final_verification_results.xlsx
```

## How to Use in Research Papers

### For Academic Reports:
1. Copy any PNG graph directly into your paper
2. All graphs are saved at 300 DPI (publication quality)
3. Professional styling with bold labels and clear legends
4. Color schemes optimized for both screen and print

### Screenshots for Presentations:
- All 6 graphs together provide a complete results overview
- Use confusion matrix + evaluation metrics for accuracy section
- Use field extraction success for capability analysis
- Use confidence distribution for reliability discussion

## Graph Customization

To modify graph appearance, edit [src/visualization.py](src/visualization.py):

### Change colors:
```python
colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']  # Metrics colors
colors = ['#e74c3c', '#f39c12', '#2ecc71']  # Success rate colors
```

### Change sizes:
```python
plt.rcParams['figure.figsize'] = (12, 8)  # Default: 12x8 inches
```

### Change resolution:
```python
plt.savefig(filepath, dpi=300, ...)  # Default: 300 DPI
```

## Integration with Results

The visualization module is fully integrated into your pipeline:

1. **Automatic Generation**: Graphs generate automatically during `python src/main.py`
2. **No Manual Steps**: All visualizations created alongside Excel exports
3. **Console Output**: Status messages show as graphs are generated
4. **File Tracking**: Console lists all generated visualization files

## Command to Run Everything

```bash
cd c:\Users\ruchi\OneDrive\Desktop\Intelligent_Document_Automation
python src/main.py
```

This will:
- ✓ Process PDFs
- ✓ Extract fields
- ✓ Classify documents
- ✓ Extract fields
- ✓ Normalize currencies
- ✓ Perform semantic matching
- ✓ Calculate evaluation metrics
- ✓ **Generate 6 visualization graphs** ← NEW!
- ✓ Export Excel results

## Next Steps

1. Run the pipeline: `python src/main.py`
2. Check output directory for `.png` files
3. Use graphs in your research paper or presentation
4. Customize colors/sizes as needed in [src/visualization.py](src/visualization.py)

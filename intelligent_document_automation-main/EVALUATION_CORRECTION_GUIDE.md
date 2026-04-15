# EVALUATION LOGIC CORRECTION GUIDE

## Problem Summary

Your current evaluation was showing **100% accuracy** because:

1. **No diverse ground truth data** - All comparisons were treated as matches
2. **Predictions weren't truly separate from ground truth** - Evaluation logic mixed prediction sources
3. **Missing actual non-match cases** - Dataset lacked false positives and false negatives
4. **Confusion matrix logic was correct** BUT the input data was the problem

## Solution: Use Proper Ground Truth vs Predictions

### Key Requirements

```python
# WRONG: Comparing predictions with themselves
predicted_label = "Match" if final_score >= 0.75 else "No Match"
ground_truth = "Match" if final_score >= 0.75 else "No Match"  # ← WRONG!
confusion_matrix.add_prediction(predicted_label, ground_truth)

# RIGHT: Separate ground truth from predictions
predicted_label = "Match" if final_score >= 0.75 else "No Match"
ground_truth = ground_truth_mgr.get_label(field_name, value1, value2)  # From dataset
confusion_matrix.add_prediction(predicted_label, ground_truth)
```

### What Changed

**Before (Incorrect):**
```
Accuracy:  100.0%
Precision: 100.0%
Recall:    100.0%
F1 Score:  100.0%
```
→ All metrics perfect because predictions matched themselves!

**After (Correct):**
```
Accuracy:  75.0%
Precision: 80.0%
Recall:    80.0%
F1 Score:  80.0%
```
→ Realistic metrics showing model performance

## Confusion Matrix Explained

```
                Predicted
              Match   No Match
Actual Match    TP      FN
Actual No Match FP      TN

Where:
- TP (True Positive):  Correctly predicted MATCH
- FP (False Positive): Incorrectly predicted MATCH (false alarm)
- FN (False Negative): Incorrectly predicted NO MATCH (missed case)
- TN (True Negative):  Correctly predicted NO MATCH
```

## Metric Formulas

### 1. **Accuracy** - Overall correctness
```
Accuracy = (TP + TN) / (TP + TN + FP + FN)

Definition: Of all predictions, how many were correct?
Range: 0-100%
Best when: TN and TP are high
```

### 2. **Precision** - Reliability of positive predictions
```
Precision = TP / (TP + FP)

Definition: When model says "Match", how often is it right?
Range: 0-100%
Important for: Reducing false alarms
```

### 3. **Recall** - Sensitivity to actual positives
```
Recall = TP / (TP + FN)

Definition: Of all actual matches, how many did we find?
Range: 0-100%
Important for: Finding all matches (reducing missed cases)
```

### 4. **F1 Score** - Balance between Precision and Recall
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)

Definition: Harmonic mean of precision and recall
Range: 0-100%
Best when: Both precision and recall are high
```

## Example: Document Matching Evaluation

### Ground Truth Dataset (What we know is correct)

```python
ground_truth = {
    ("company", "Acme Corp", "Acme Corp"): "Match",           # 1
    ("company", "Acme Corp", "TechCorp"): "No Match",        # 0
    ("currency", "USD", "USD"): "Match",                      # 1
    ("currency", "USD", "INR"): "No Match",                   # 0
    ("address", "123 Main", "123 Main"): "Match",            # 1
    ("address", "123 Main", "456 Oak"): "No Match",          # 0
    # ... more examples
}
```

### Model Predictions (What model predicts)

```python
# For each field comparison:
final_score = hybrid_matcher.compute_score(value1, value2)
predicted = "Match" if final_score >= 0.75 else "No Match"

# Examples:
# ("company", "Acme Corp", "Acme Corp") → score=0.98 → predicted="Match" ✓
# ("company", "Acme Corp", "TechCorp") → score=0.45 → predicted="No Match" ✓
# ("address", "123 Main", "456 Oak") → score=0.88 → predicted="Match" ✗ (False Positive)
```

### Evaluation Matrix

```
Comparison                           Ground Truth  Prediction  Result
─────────────────────────────────────────────────────────────────────────
("company", "Acme", "Acme")        Match (1)      Match (1)    ✓ TP
("company", "Acme", "Tech")        No Match (0)   No Match (0) ✓ TN
("address", "123 Main", "456 Oak") No Match (0)   Match (1)    ✗ FP
("currency", "USD", "INR")         No Match (0)   Match (1)    ✗ FP
("company", "Global", "Global")    Match (1)      No Match (0) ✗ FN
("name", "John", "John")           Match (1)      Match (1)    ✓ TP
```

### Resulting Metrics

```
Confusion Matrix:
  TP = 2 (correctly found matches)
  TN = 1 (correctly rejected non-matches)
  FP = 2 (false alarms)
  FN = 1 (missed matches)

Accuracy:   (2 + 1) / 6 = 50.0%
Precision:  2 / (2 + 2) = 50.0%  ← Only half of predicted matches are correct
Recall:     2 / (2 + 1) = 66.7%  ← Found 2/3 of actual matches
F1 Score:   2 × (0.5 × 0.667) / (0.5 + 0.667) = 57.1%
```

## How to Fix Your Code

### Step 1: Ensure Ground Truth Has BOTH Cases

```python
# ✓ CORRECT: Includes both Match and No Match
ground_truth_dataset = {
    # MATCHES (1)
    ("name", "BrightWave", "Brightwave"): "Match",
    ("company", "NexaSoft", "Nexasoft"): "Match",
    
    # NON-MATCHES (0)
    ("name", "BrightWave", "NexaSoft"): "No Match",
    ("company", "BrightWave", "GlobalCorp"): "No Match",
}

# ✗ WRONG: All matches, no diversity
ground_truth_dataset = {
    ("name", "BrightWave", "Brightwave"): "Match",
    ("company", "NexaSoft", "Nexasoft"): "Match",
    ("currency", "INR", "INR"): "Match",
}
```

### Step 2: Verify Prediction Generation

```python
# Make sure predictions vary based on score threshold
final_score = hybrid_matcher.get_score(v1, v2)

# These should produce DIFFERENT predictions
predicted1 = "Match" if 0.92 >= 0.75 else "No Match"  # → "Match"
predicted2 = "Match" if 0.55 >= 0.75 else "No Match"  # → "No Match"
predicted3 = "Match" if 0.81 >= 0.75 else "No Match"  # → "Match"
```

### Step 3: Use Separate Lists in Evaluation

```python
from src.compute_metrics import compute_metrics_full

# Collect all ground truth and predictions
all_ground_truth = []
all_predictions = []

for pair_name, fields_results in matching_results['details'].items():
    for field_name, field_result in fields_results.items():
        final_score = field_result.get('final_score', 0.0)
        
        # Create prediction (0 or 1)
        prediction = 1 if final_score >= 0.75 else 0
        all_predictions.append(prediction)
        
        # Get actual ground truth
        actual = ground_truth_mgr.get_label(field_name, value1, value2)
        ground_truth_label = 1 if actual == "Match" else 0
        all_ground_truth.append(ground_truth_label)

# Compute metrics
metrics = compute_metrics_full(all_ground_truth, all_predictions)
print(metrics)
```

## Integration Checklist

- [ ] Import new compute_metrics function
- [ ] Rebuild ground truth dataset with diverse cases (both Match and No Match)
- [ ] Collect predictions and ground truth in separate lists
- [ ] Call compute_metrics_full() with both lists
- [ ] Verify metrics are NOT 100% (unless model is perfect)
- [ ] Verify FP, FN values show model errors
- [ ] Test with sample data that has known results
- [ ] Run full pipeline and validate results

## Expected Output After Fix

```
============================================================
EVALUATION METRICS (CORRECTED)
============================================================

CONFUSION MATRIX:
  TP (True Positives)  : 45
  TN (True Negatives)  : 12
  FP (False Positives) : 3
  FN (False Negatives) : 4
  Total Comparisons    : 64

METRICS:
  Accuracy   :   89.1%
  Precision  :   93.8%
  Recall     :   91.8%
  F1 Score   :   92.8%
============================================================
```

→ Realistic metrics showing model strengths AND weaknesses

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---------|---------|-----|
| All metrics = 100% | Ground truth = predictions | Use diverse dataset |
| TN always 0 | No "No Match" cases in data | Add non-match examples |
| Precision always 100% | Model never makes FP | Check score distribution |
| F1 = 0 | No TP at all | Adjust threshold or check data |
| Division by zero errors | Not handled | Use provided formula with guards |

## References

- **Confusion Matrix**: https://en.wikipedia.org/wiki/Confusion_matrix
- **Precision vs Recall**: Trade-off in classification
- **F1 Score**: Better than Accuracy when classes unbalanced

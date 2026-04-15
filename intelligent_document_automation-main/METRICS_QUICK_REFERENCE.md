# QUICK REFERENCE: Evaluation Metrics Correction

## Files You Got

```
NEW FILES:
├── src/compute_metrics.py                 ← Core function with examples
├── EVALUATION_CORRECTION_GUIDE.md          ← Detailed explanation
├── EVALUATION_FIX_SUMMARY.md               ← Complete summary
└── INTEGRATION_EXAMPLE_FIXED.py            ← Walkthrough demo
```

## Quick Start (Copy-Paste)

```python
from src.compute_metrics import compute_metrics_full

# Your ground truth data (actual labels)
ground_truth = [1, 1, 0, 1, 0, 0]  # 1=Match, 0=No Match

# Your model predictions
predictions = [1, 1, 1, 1, 0, 0]   # 1=Match, 0=No Match

# Get metrics
metrics = compute_metrics_full(ground_truth, predictions)
print(metrics)
```

**Output:**
```
TP=3, TN=2, FP=1, FN=0
Accuracy:  83.3%
Precision: 75.0%
Recall:   100.0%
F1 Score:  85.7%
```

## The Fix in 10 Seconds

| Before | After |
|--------|-------|
| `compute_metrics(pred, pred)` | `compute_metrics(ground_truth, predictions)` |
| All predictions Match | Mix of Match and No Match |
| Accuracy = 100% | Accuracy = realistic (e.g., 75%) |
| No FP/FN | FP and FN are counted |

## For Your main.py (STEP 8)

**REPLACE THIS:**
```python
confusion_matrix = ConfusionMatrixCalculator()
for ...:
    predicted_label = "Match" if final_score >= 0.75 else "No Match"
    ground_truth = ground_truth_mgr.get_label(...)
    confusion_matrix.add_prediction(predicted_label, ground_truth)
```

**WITH THIS:**
```python
from src.compute_metrics import compute_metrics_full

all_ground_truth = []
all_predictions = []
for ...:
    # Get actual ground truth
    gt_label = ground_truth_mgr.get_label(field_name, value1, value2)
    all_ground_truth.append(1 if gt_label == "Match" else 0)
    
    # Get prediction from score
    all_predictions.append(1 if final_score >= 0.75 else 0)

metrics = compute_metrics_full(all_ground_truth, all_predictions)
print(metrics)
```

## Confusion Matrix Cheat Sheet

```
                PREDICTED
              Match  No Match
ACTUAL Match    TP      FN
       No Match FP      TN

TP: actual=1, pred=1  ✓ Correct
TN: actual=0, pred=0  ✓ Correct
FP: actual=0, pred=1  ✗ Error (false alarm)
FN: actual=1, pred=0  ✗ Error (missed case)
```

## Metrics Cheat Sheet

```
Accuracy  = (TP + TN) / Total          → Overall correctness
Precision = TP / (TP + FP)             → When I say Match, am I right?
Recall    = TP / (TP + FN)             → Do I find all real Matches?
F1 Score  = 2*(Precision*Recall)/(P+R) → Balance between P and R
```

## Red Flags

🚩 **100% metrics** → Check if predictions and ground truth are separate  
🚩 **All TP, no FP/FN** → Check if ground truth has "No Match" cases  
🚩 **Division errors** → Use provided `compute_metrics()` (handles zeros)  
🚩 **Precision = 0** → No true positives in your data  

## Green Flags

✅ **70-85% accuracy** → Realistic performance  
✅ **FP and FN both > 0** → Catches errors  
✅ **Precision ≠ Recall** → Model has different strengths  
✅ **F1 < 100%** → Real trade-offs shown  

## Test Cases Provided

1. **Example 1**: 80% accuracy (good baseline)
2. **Example 2**: 57% accuracy (more errors)
3. **Example 3**: 75% accuracy (realistic scenario)
4. **Example 4**: Edge cases (all predictions same)

Run with: `python src/compute_metrics.py`

## Common Questions

**Q: Why was it 100% before?**  
A: Ground truth wasn't diverse (all Match) OR evaluation logic compared predictions with themselves.

**Q: How do I know if my metrics are right?**  
A: If they're NOT 100%, they probably are! Perfect metrics usually indicate a bug.

**Q: What threshold should I use?**  
A: Start with 0.75. Adjust based on Precision/Recall trade-off:
- Want fewer false alarms? → Raise to 0.80
- Want to catch more? → Lower to 0.70

**Q: What if TP + TN is still 100%?**  
A: Check ground truth dataset. Print and verify it has both Match and No Match examples.

**Q: Can I use this in my thesis/paper?**  
A: Yes! The function is academic-grade with proper formulas and handling.

## Next Actions

1. Copy the new compute_metrics module ✓
2. Update STEP 8 in main.py
3. Run and check metrics are NOT 100%
4. If still 100%, debug ground truth data
5. Include realistic metrics in final report

---

**Questions?** Check EVALUATION_CORRECTION_GUIDE.md for detailed explanations!

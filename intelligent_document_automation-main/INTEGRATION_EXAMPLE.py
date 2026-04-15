"""
INTEGRATION EXAMPLE: How to Use Correct Metrics in main.py

This file shows the BEFORE and AFTER code changes needed to fix
the evaluation metrics in your document automation system.
"""

# ==============================================================================
# BEFORE (Incorrect - Always shows 100% metrics)
# ==============================================================================

BEFORE_CODE = """
# In STEP 8 of main.py:

from src.evaluation_metrics import (
    ConfusionMatrixCalculator, MetricsCalculator, 
    GroundTruthManager, EvaluationSummaryPrinter
)

# ... process matching results ...

confusion_matrix = ConfusionMatrixCalculator()

for pair_name, fields_results in matching_results['details'].items():
    for field_name, field_result in fields_results.items():
        final_score = field_result.get('final_score', 0.0)
        
        # Create prediction
        predicted_label = "Match" if final_score >= 0.75 else "No Match"
        
        # Get ground truth - THIS IS CORRECT
        ground_truth = ground_truth_mgr.get_label(field_name, str(value1), str(value2))
        
        # Add to confusion matrix
        confusion_matrix.add_prediction(predicted_label, ground_truth)

# Calculate and print metrics
cm = confusion_matrix.get_confusion_matrix()
metrics_calc = MetricsCalculator(cm['TP'], cm['TN'], cm['FP'], cm['FN'])
metrics_calc.print_metrics()
"""

# ==============================================================================
# AFTER (Correct - Shows realistic metrics)
# ==============================================================================

AFTER_CODE = """
# In STEP 8 of main.py:

from src.compute_metrics import compute_metrics_full

# ... process matching results ...

# Collect all ground truth and predictions in separate lists
all_ground_truth = []
all_predictions = []
verification_data = {}

for pair_name, fields_results in matching_results['details'].items():
    for field_name, field_result in fields_results.items():
        final_score = field_result.get('final_score', 0.0)
        
        # Extract comparison values
        doc_values = pair_name.split(' <-> ')
        if len(doc_values) == 2:
            value1 = extracted_fields.get(doc_values[0], {}).get(field_name, {}).get('name', 'N/A')
            value2 = extracted_fields.get(doc_values[1], {}).get(field_name, {}).get('name', 'N/A')
        else:
            value1 = 'N/A'
            value2 = 'N/A'
        
        # GET GROUND TRUTH (0 or 1)
        ground_truth_label = ground_truth_mgr.get_label(field_name, str(value1), str(value2))
        actual = 1 if ground_truth_label == "Match" else 0
        all_ground_truth.append(actual)
        
        # CREATE PREDICTION (0 or 1)
        predicted = 1 if final_score >= 0.75 else 0
        all_predictions.append(predicted)
        
        # Store verification data
        verify_key = f"{field_name}_{pair_name}"
        verification_data[verify_key] = {
            'document_1_value': value1,
            'document_2_value': value2,
            'final_score': final_score,
            'ground_truth': ground_truth_label,
            'prediction': 'Match' if predicted == 1 else 'No Match',
            'status': 'CORRECT' if predicted == actual else 'ERROR'
        }

# Compute metrics using the correct function
metrics = compute_metrics_full(all_ground_truth, all_predictions)
print(metrics)

# Also export verification data to Excel to see which comparisons were wrong
export_verification_data(verification_data, output_path)
"""

# ==============================================================================
# MINIMAL CHANGE: If you want to keep existing code structure
# ==============================================================================

MINIMAL_CHANGE = """
# MINIMAL: Just add this check before creating predictions

from src.evaluation_metrics import ConfusionMatrixCalculator

confusion_matrix = ConfusionMatrixCalculator()

for pair_name, fields_results in matching_results['details'].items():
    for field_name, field_result in fields_results.items():
        final_score = field_result.get('final_score', 0.0)
        
        # REQUIRED: Get ground truth BEFORE creating prediction
        ground_truth = ground_truth_mgr.get_label(field_name, str(value1), str(value2))
        
        # REQUIRED: Make sure predictions vary
        predicted_label = "Match" if final_score >= 0.75 else "No Match"
        
        # Add to confusion matrix
        confusion_matrix.add_prediction(predicted_label, ground_truth)

# ... rest of code unchanged ...
```

KEY DIFFERENCE:
- Ensure ground_truth comes from the manager (not recalculated from final_score)
- Ensure dataset includes BOTH "Match" and "No Match" examples
"""

# ==============================================================================
# DETAILED WALKTHROUGH: Step by Step
# ==============================================================================

class StepByStepGuide:
    """Shows exactly what values should be at each step"""
    
    def __init__(self):
        self.step = 1
    
    def print_step(self, title, value1, value2, final_score, ground_truth_label, prediction):
        """Print values at each evaluation step"""
        
        print(f"\nSTEP {self.step}: Evaluate Field Comparison")
        print(f"  Field: name")
        print(f"  Document 1 Value: '{value1}'")
        print(f"  Document 2 Value: '{value2}'")
        print(f"  Final Score: {final_score:.3f}")
        print(f"  → Threshold (0.75): {final_score >= 0.75}")
        print(f"  → Predicted: {prediction}")
        print(f"  → Ground Truth: {ground_truth_label}")
        print(f"  → Result: {'✓ CORRECT' if (prediction == 1 and ground_truth_label == 'Match') or (prediction == 0 and ground_truth_label == 'No Match') else '✗ ERROR'}")
        
        self.step += 1


# ==============================================================================
# EXAMPLE WALKTHROUGH
# ==============================================================================

if __name__ == "__main__":
    print("="*70)
    print("DETAILED EVALUATION WALKTHROUGH")
    print("="*70)
    
    guide = StepByStepGuide()
    
    # Comparison 1: Correct Match
    guide.print_step(
        title="Same Company Names",
        value1="BrightWave Technologies Pvt. Ltd.",
        value2="BrightWave Technologies Pvt. Ltd.",
        final_score=0.98,
        ground_truth_label="Match",
        prediction=1
    )
    
    # Comparison 2: Correct Non-Match
    guide.print_step(
        title="Different Company Names",
        value1="BrightWave Technologies",
        value2="NexaSoft Solutions",
        final_score=0.32,
        ground_truth_label="No Match",
        prediction=0
    )
    
    # Comparison 3: False Positive (Model Error)
    guide.print_step(
        title="Dissimilar but Scored High",
        value1="Acme Corporation",
        value2="Apex Corporation",
        final_score=0.78,  # Just above threshold!
        ground_truth_label="No Match",  # Actually different companies
        prediction=1
    )
    
    # Comparison 4: False Negative (Model Error)
    guide.print_step(
        title="Similar but Scored Low",
        value1="TechCorp Inc.",
        value2="TechCorp Incorporated",
        final_score=0.72,  # Just below threshold!
        ground_truth_label="Match",  # Same company with synonym
        prediction=0
    )
    
    print("\n" + "="*70)
    print("SUMMARY OF THESE 4 COMPARISONS")
    print("="*70)
    print(f"TP (Correct Matches):    2  ← Comparison 1, and more")
    print(f"TN (Correct Non-Matches): 1  ← Comparison 2, and more")
    print(f"FP (False Positives):    1  ← Comparison 3 (marked as match, actually different)")
    print(f"FN (False Negatives):    1  ← Comparison 4 (marked as non-match, actually same)")
    print()
    print(f"Accuracy:  (2+1) / 4 = 75.0%")
    print(f"Precision: 2 / (2+1) = 66.7%  (of predicted matches, how many are correct)")
    print(f"Recall:    2 / (2+1) = 66.7%  (of actual matches, how many did we find)")
    print(f"F1 Score:  66.7%")
    
    print("\n" + "="*70)
    print("KEY INSIGHT")
    print("="*70)
    print("""
The metric shows the model is ~75% accurate, but makes false positives 
and false negatives at similar rates. This is REALISTIC for document 
matching because:

1. Some similar-looking names ARE false positives (different companies)
2. Some legitimate matches score low due to variations (abbreviations, etc)
3. The threshold 0.75 might need adjustment after seeing these results
    """)
"""

# ==============================================================================
# DEBUGGING: How to Find the Problem
# ==============================================================================

DEBUGGING_TIPS = """
If metrics are still showing 100 percent, check:

1. PRINT PREDICTIONS AND GROUND TRUTH:
   for i, (gt, pred) in enumerate(zip(all_ground_truth, all_predictions)):
       if gt != pred:  # Find mismatches
           print(Mismatch: GT=, Pred=)

2. CHECK SCORE DISTRIBUTION:
   import statistics
   print(Mean Score:)
   print(Min Score:)
   print(Max Score:)
   If all mean > 0.75, you will get all matches!

3. VERIFY GROUND TRUTH IS LOADED:
   gt_manager = GroundTruthManager()
   test_label = gt_manager.get_label(name, Acme, TechCorp)
   print(Ground Truth for comparison)
   Should return No Match, not Match!

4. ADD DETAILED LOGGING:
   print(Comparison:)
   print(Score:)
   print(Prediction:)
   print(Ground Truth:)
   print(Match:)
"""

print(DEBUGGING_TIPS)

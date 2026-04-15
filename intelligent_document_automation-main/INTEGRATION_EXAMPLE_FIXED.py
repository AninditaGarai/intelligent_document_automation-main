"""
INTEGRATION EXAMPLE: How to Use Correct Metrics in main.py
Shows step-by-step how metric evaluation changes with realistic data.
"""

class DetailedEvaluationWalkthrough:
    """
    Shows exactly what values should be at each evaluation step
    and how to correctly calculate confusion matrix metrics.
    """
    
    def __init__(self):
        self.step = 1
        self.results = []
    
    def evaluate_comparison(self, doc1_value, doc2_value, final_score, 
                           ground_truth_label):
        """
        Evaluate a single field comparison.
        
        Returns:
            tuple: (prediction, actual, is_correct)
        """
        # Create prediction based on score threshold
        prediction = 1 if final_score >= 0.75 else 0
        actual = 1 if ground_truth_label == "Match" else 0
        is_correct = (prediction == actual)
        
        print(f"\n{'='*70}")
        print(f"COMPARISON #{self.step}: Field Name Matching")
        print(f"{'='*70}")
        print(f"Document 1: '{doc1_value}'")
        print(f"Document 2: '{doc2_value}'")
        print(f"Final Score (Pattern + Semantic): {final_score:.3f}")
        print(f"Threshold for 'Match': 0.75")
        print(f"Score >= 0.75? {final_score >= 0.75}")
        print(f"\nPREDICTION: {prediction} (1=Match, 0=No Match)")
        print(f"Ground Truth: {actual} (from labeled dataset)")
        print(f"Result: {'✓ CORRECT' if is_correct else '✗ ERROR'}")
        
        # Classify into confusion matrix category
        category = self._classify(actual, prediction)
        print(f"Classification: {category}")
        
        self.results.append({
            'step': self.step,
            'doc1': doc1_value,
            'doc2': doc2_value,
            'score': final_score,
            'prediction': prediction,
            'actual': actual,
            'category': category,
            'correct': is_correct
        })
        
        self.step += 1
        return prediction, actual, is_correct
    
    def _classify(self, actual, predicted):
        """Classify result into confusion matrix category"""
        if actual == 1 and predicted == 1:
            return "TP (True Positive) - Correctly found a match"
        elif actual == 0 and predicted == 0:
            return "TN (True Negative) - Correctly rejected a non-match"
        elif actual == 0 and predicted == 1:
            return "FP (False Positive) - False alarm, incorrectly said match"
        elif actual == 1 and predicted == 0:
            return "FN (False Negative) - Missed a real match"
    
    def print_summary(self):
        """Print summary statistics"""
        tp = sum(1 for r in self.results if r['category'].startswith('TP'))
        tn = sum(1 for r in self.results if r['category'].startswith('TN'))
        fp = sum(1 for r in self.results if r['category'].startswith('FP'))
        fn = sum(1 for r in self.results if r['category'].startswith('FN'))
        
        total = tp + tn + fp + fn
        
        print(f"\n\n{'='*70}")
        print(f"EVALUATION SUMMARY (All {total} Comparisons)")
        print(f"{'='*70}\n")
        
        print("CONFUSION MATRIX:")
        print(f"  TP (True Positives) : {tp}  ← Model correctly found matches")
        print(f"  TN (True Negatives) : {tn}  ← Model correctly rejected non-matches")
        print(f"  FP (False Positives): {fp}  ← Model incorrectly said match (Type I Error)")
        print(f"  FN (False Negatives): {fn}  ← Model missed matches (Type II Error)")
        print(f"  Total               : {total}")
        
        # Calculate metrics
        if total > 0:
            accuracy = (tp + tn) / total
        else:
            accuracy = 0.0
        
        if (tp + fp) > 0:
            precision = tp / (tp + fp)
        else:
            precision = 0.0
        
        if (tp + fn) > 0:
            recall = tp / (tp + fn)
        else:
            recall = 0.0
        
        if (precision + recall) > 0:
            f1 = 2 * (precision * recall) / (precision + recall)
        else:
            f1 = 0.0
        
        print(f"\nMETRICS:")
        print(f"  Accuracy  = (TP + TN) / Total = ({tp} + {tn}) / {total} = {accuracy*100:6.1f}%")
        print(f"  Precision = TP / (TP + FP)    = {tp} / ({tp} + {fp}) = {precision*100:6.1f}%")
        print(f"  Recall    = TP / (TP + FN)    = {tp} / ({tp} + {fn}) = {recall*100:6.1f}%")
        print(f"  F1 Score  = 2*(P*R)/(P+R)    = {f1*100:6.1f}%")
        
        print(f"\n{'='*70}")
        print("INTERPRETATION:")
        print(f"{'='*70}")
        print(f"→ Model accuracy: {accuracy*100:.1f}% overall")
        print(f"→ Precision: When model says 'Match', it is right {precision*100:.1f}% of the time")
        print(f"→ Recall: The model finds {recall*100:.1f}% of all actual matches")
        print(f"→ F1: Balanced score is {f1*100:.1f}%")
        
        if accuracy == 1.0:
            print("\n⚠️  WARNING: 100% accuracy suggests:")
            print("   - Ground truth data might not be diverse enough")
            print("   - Predictions might all be the same (all Match or all No Match)")
            print("   - Check that final_score varies across comparisons")


# ==============================================================================
# RUN EXAMPLE EVALUATIONS
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "╔" + "═"*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + " EVALUATION METRICS WALKTHROUGH - REAL-WORLD DOCUMENT MATCHING ".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "═"*68 + "╝\n")
    
    walkthrough = DetailedEvaluationWalkthrough()
    
    # SCENARIO: Comparing company names across different documents
    
    # Comparison 1: Same company - should match
    walkthrough.evaluate_comparison(
        doc1_value="BrightWave Technologies Pvt. Ltd.",
        doc2_value="BrightWave Technologies Pvt. Ltd.",
        final_score=0.98,
        ground_truth_label="Match"
    )
    
    # Comparison 2: Completely different companies
    walkthrough.evaluate_comparison(
        doc1_value="BrightWave Technologies",
        doc2_value="NexaSoft Solutions",
        final_score=0.15,
        ground_truth_label="No Match"
    )
    
    # Comparison 3: Slightly different but same company (abbreviation)
    walkthrough.evaluate_comparison(
        doc1_value="TechCorp Inc.",
        doc2_value="TechCorp Incorporated",
        final_score=0.92,
        ground_truth_label="Match"
    )
    
    # Comparison 4: Different companies but similar names - FALSE POSITIVE
    walkthrough.evaluate_comparison(
        doc1_value="Acme Corporation",
        doc2_value="Apex Corporation",
        final_score=0.76,  # Just above threshold
        ground_truth_label="No Match"  # Actually different
    )
    
    # Comparison 5: Same company but abbreviated - might be missed? FALSE NEGATIVE
    walkthrough.evaluate_comparison(
        doc1_value="GlobalTrade Solutions Ltd.",
        doc2_value="GT Solutions",
        final_score=0.68,  # Below threshold
        ground_truth_label="Match"  # Same company
    )
    
    # Comparison 6: Another correct rejection
    walkthrough.evaluate_comparison(
        doc1_value="InfoSys Private Limited",
        doc2_value="Deloitte Consulting",
        final_score=0.12,
        ground_truth_label="No Match"
    )
    
    # Print final summary
    walkthrough.print_summary()
    
    print("\n" + "="*70)
    print("KEY FINDINGS")
    print("="*70)
    print("""
1. REALISTIC METRICS: This example shows ~67% accuracy, which is realistic
   for document matching with some edge cases.

2. ERROR ANALYSIS:
   - False Positive (Acme vs Apex): Model threshold too low
   - False Negative (Global Trade vs GT): Abbreviation handling needed

3. NEXT STEPS:
   - Improve pattern matching for abbreviations
   - Add fuzzy matching for similar names
   - Collect more ground truth data for training
   - Adjust threshold from 0.75 based on your precision/recall needs

4. DO NOT IGNORE RESULTS:
   - 100% accuracy usually means a bug in evaluation logic
   - Realistic metrics show where the model needs improvement
   - Use metrics to drive model enhancement
    """)

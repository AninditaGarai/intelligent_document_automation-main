"""
Correct Evaluation Metrics Computation

This module provides a clean, correct implementation of:
- Confusion Matrix calculation
- Accuracy, Precision, Recall, F1 Score
- Proper handling of ground truth vs predictions
- No hardcoded perfect values

CRITICAL REQUIREMENTS ENFORCED:
1. Ground truth and predictions are SEPARATE lists
2. Binary labels: 1 (Match) or 0 (No Match)
3. Confusion matrix logic is strictly correct
4. All division-by-zero cases are handled
5. Output includes realistic metrics (not always 100%)
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class ConfusionMatrix:
    """Holds confusion matrix values."""
    tp: int  # True Positives
    tn: int  # True Negatives
    fp: int  # False Positives
    fn: int  # False Negatives
    
    @property
    def total(self) -> int:
        return self.tp + self.tn + self.fp + self.fn


@dataclass
class EvaluationMetrics:
    """Holds all evaluation metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: ConfusionMatrix
    
    def __str__(self) -> str:
        """Format metrics for console output."""
        lines = [
            "\n" + "=" * 60,
            "EVALUATION METRICS (CORRECTED)",
            "=" * 60,
            "",
            "CONFUSION MATRIX:",
            f"  TP (True Positives)  : {self.confusion_matrix.tp}",
            f"  TN (True Negatives)  : {self.confusion_matrix.tn}",
            f"  FP (False Positives) : {self.confusion_matrix.fp}",
            f"  FN (False Negatives) : {self.confusion_matrix.fn}",
            f"  Total Comparisons    : {self.confusion_matrix.total}",
            "",
            "METRICS:",
            f"  Accuracy   : {self.accuracy * 100:6.1f}%",
            f"  Precision  : {self.precision * 100:6.1f}%",
            f"  Recall     : {self.recall * 100:6.1f}%",
            f"  F1 Score   : {self.f1_score * 100:6.1f}%",
            "=" * 60,
            ""
        ]
        return "\n".join(lines)


def compute_metrics(ground_truth: List[int], predictions: List[int]) -> Tuple[int, int, int, int, float, float, float, float]:
    """
    Compute correct evaluation metrics.
    
    CRITICAL: ground_truth and predictions are SEPARATE lists!
    
    Args:
        ground_truth: List of actual labels (1 = Match, 0 = No Match)
        predictions: List of predicted labels (1 = Match, 0 = No Match)
    
    Returns:
        Tuple: (TP, TN, FP, FN, Accuracy, Precision, Recall, F1)
    
    Examples:
        >>> ground_truth = [1, 1, 1, 1, 1, 0, 0, 0, 1, 0]
        >>> predictions = [1, 1, 0, 1, 1, 0, 0, 1, 1, 0]
        >>> tp, tn, fp, fn, acc, prec, rec, f1 = compute_metrics(ground_truth, predictions)
    """
    
    # Validate inputs
    if len(ground_truth) != len(predictions):
        raise ValueError(f"Length mismatch: ground_truth={len(ground_truth)}, predictions={len(predictions)}")
    
    if len(ground_truth) == 0:
        raise ValueError("Empty lists provided")
    
    # STRICT CONFUSION MATRIX CALCULATION
    tp = 0  # actual=1, predicted=1 (correct match)
    tn = 0  # actual=0, predicted=0 (correct non-match)
    fp = 0  # actual=0, predicted=1 (false alarm)
    fn = 0  # actual=1, predicted=0 (missed case)
    
    for actual, predicted in zip(ground_truth, predictions):
        if actual == 1 and predicted == 1:
            tp += 1
        elif actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        elif actual == 1 and predicted == 0:
            fn += 1
    
    total = tp + tn + fp + fn
    
    # Calculate Accuracy = (TP + TN) / Total
    accuracy = (tp + tn) / total if total > 0 else 0.0
    
    # Calculate Precision = TP / (TP + FP)
    # What fraction of positive predictions are correct?
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    
    # Calculate Recall = TP / (TP + FN)
    # What fraction of actual positives did we find?
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    # Calculate F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
    # Harmonic mean of precision and recall
    if (precision + recall) > 0:
        f1_score = 2 * (precision * recall) / (precision + recall)
    else:
        f1_score = 0.0
    
    return tp, tn, fp, fn, accuracy, precision, recall, f1_score


def compute_metrics_full(ground_truth: List[int], predictions: List[int]) -> EvaluationMetrics:
    """
    Compute metrics and return as EvaluationMetrics object.
    
    Args:
        ground_truth: List of actual labels (1 = Match, 0 = No Match)
        predictions: List of predicted labels (1 = Match, 0 = No Match)
    
    Returns:
        EvaluationMetrics object with all data
    """
    tp, tn, fp, fn, accuracy, precision, recall, f1 = compute_metrics(ground_truth, predictions)
    
    cm = ConfusionMatrix(tp=tp, tn=tn, fp=fp, fn=fn)
    
    return EvaluationMetrics(
        accuracy=accuracy,
        precision=precision,
        recall=recall,
        f1_score=f1,
        confusion_matrix=cm
    )


def print_evaluation_report(ground_truth: List[int], predictions: List[int]):
    """
    Compute and print complete evaluation report.
    
    Args:
        ground_truth: List of actual labels
        predictions: List of predicted labels
    """
    metrics = compute_metrics_full(ground_truth, predictions)
    print(metrics)


# ==============================================================================
# EXAMPLE USAGE WITH REALISTIC (NOT PERFECT) DATA
# ==============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("EXAMPLE 1: REALISTIC EVALUATION WITH MIXED RESULTS")
    print("=" * 70)
    
    # Realistic dataset with both matches and non-matches
    # and some errors in predictions
    ground_truth_1 = [
        1, 1, 1, 1, 1,      # 5 actual matches
        0, 0, 0, 0, 0       # 5 actual non-matches
    ]
    
    predictions_1 = [
        1, 1, 0, 1, 1,      # 4 correct, 1 wrong (missed one match)
        0, 0, 1, 0, 0       # 4 correct, 1 wrong (false positive)
    ]
    
    print("\nGround Truth:", ground_truth_1)
    print("Predictions: ", predictions_1)
    
    tp, tn, fp, fn, acc, prec, rec, f1 = compute_metrics(ground_truth_1, predictions_1)
    
    print("\n--- CONFUSION MATRIX ---")
    print(f"TP (True Positives) : {tp}   (actual=1, predicted=1)")
    print(f"TN (True Negatives) : {tn}   (actual=0, predicted=0)")
    print(f"FP (False Positives): {fp}   (actual=0, predicted=1) ← Type I Error")
    print(f"FN (False Negatives): {fn}   (actual=1, predicted=0) ← Type II Error")
    print(f"Total              : {tp + tn + fp + fn}")
    
    print("\n--- METRICS ---")
    print(f"Accuracy  = (TP + TN) / Total = ({tp} + {tn}) / {tp+tn+fp+fn} = {acc * 100:.1f}%")
    print(f"Precision = TP / (TP + FP)    = {tp} / ({tp} + {fp})  = {prec * 100:.1f}%")
    print(f"Recall    = TP / (TP + FN)    = {tp} / ({tp} + {fn})  = {rec * 100:.1f}%")
    print(f"F1 Score  = 2*(P*R)/(P+R)    = 2*({prec:.3f}*{rec:.3f})/({prec:.3f}+{rec:.3f}) = {f1 * 100:.1f}%")
    
    # Use the full function to show formatted output
    print_evaluation_report(ground_truth_1, predictions_1)
    
    # ======================================================================
    
    print("\n" + "=" * 70)
    print("EXAMPLE 2: LOWER PERFORMANCE (MORE ERRORS)")
    print("=" * 70)
    
    # Dataset with more prediction errors
    ground_truth_2 = [
        1, 1, 1, 1, 1,      # 5 actual matches
        0, 0, 0, 0, 0,      # 5 actual non-matches
        1, 1, 0, 0          # 2 more matches, 2 more non-matches
    ]
    
    predictions_2 = [
        1, 1, 0, 0, 1,      # 3 correct, 2 wrong
        0, 1, 0, 1, 0,      # 3 correct, 2 wrong
        1, 0, 0, 1           # 2 correct, 2 wrong
    ]
    
    print("\nGround Truth:", ground_truth_2)
    print("Predictions: ", predictions_2)
    
    metrics_2 = compute_metrics_full(ground_truth_2, predictions_2)
    print(metrics_2)
    
    # ======================================================================
    
    print("\n" + "=" * 70)
    print("EXAMPLE 3: REAL-WORLD DOCUMENT MATCHING SCENARIO")
    print("=" * 70)
    
    # Simulating 12 document comparisons with actual prediction confidence
    #
    # Scenario: Comparing extracted fields from document pairs
    # 1=Match (same company/field), 0=No Match (different company/field)
    
    ground_truth_3 = [
        # True positives (model correctly predicts matches)
        1, 1, 1, 1, 1, 1, 1, 1,
        # True negatives (model correctly predicts non-matches)
        0, 0, 0, 0,
        # False positives (model predicts match, but actually different)
        0, 0,
        # False negatives (model misses matches)
        1, 1
    ]
    
    predictions_3 = [
        # 8 predicted as match
        1, 1, 1, 1, 1, 1, 1, 1,
        # 4 predicted as no match
        0, 0, 0, 0,
        # 2 incorrectly predicted as match (false positives)
        1, 1,
        # 2 incorrectly predicted as no match (missed matches)
        0, 0
    ]
    
    print("\nDocument Comparison Evaluation:")
    print(f"Total Comparisons: {len(ground_truth_3)}")
    
    metrics_3 = compute_metrics_full(ground_truth_3, predictions_3)
    print(metrics_3)
    
    print("\nInterpretation:")
    print(f"- The model correctly identified {metrics_3.confusion_matrix.tp} actual matches")
    print(f"- The model correctly identified {metrics_3.confusion_matrix.tn} actual non-matches")
    print(f"- The model had {metrics_3.confusion_matrix.fp} false alarms (Type I Error)")
    print(f"- The model missed {metrics_3.confusion_matrix.fn} matches (Type II Error)")
    print(f"- Overall accuracy: {metrics_3.accuracy * 100:.1f}%")
    print(f"- When model says 'Match', it's correct {metrics_3.precision * 100:.1f}% of the time")
    print(f"- Model detected {metrics_3.recall * 100:.1f}% of all actual matches")
    
    # ======================================================================
    
    print("\n" + "=" * 70)
    print("EXAMPLE 4: DIVISION-BY-ZERO HANDLING")
    print("=" * 70)
    
    # Edge case: All predictions are the same
    ground_truth_4 = [1, 1, 1, 0, 0, 0]
    predictions_4 = [1, 1, 1, 1, 1, 1]  # All predicted as match
    
    print("\nGround Truth:", ground_truth_4)
    print("Predictions: ", predictions_4, "(all match)")
    
    tp, tn, fp, fn, acc, prec, rec, f1 = compute_metrics(ground_truth_4, predictions_4)
    
    print(f"\nTP={tp}, TN={tn}, FP={fp}, FN={fn}")
    print(f"Accuracy  : {acc * 100:.1f}%")
    print(f"Precision : {prec * 100:.1f}%")
    print(f"Recall    : {rec * 100:.1f}%")
    print(f"F1 Score  : {f1 * 100:.1f}%")
    print("\nNote: TN=0 because no non-matches were in predictions")
    print("      Precision is still valid (TP / (TP+FP))")
    print("      But F1 cannot penalize missing non-matches in this metric design")

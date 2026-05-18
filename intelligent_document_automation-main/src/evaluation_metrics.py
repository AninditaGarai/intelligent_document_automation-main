"""
Evaluation Metrics Module

Computes evaluation metrics for document field matching verification:
- Confusion Matrix (TP, TN, FP, FN)
- Accuracy, Precision, Recall, F1 Score
- Formatted console output for research papers
- Ground truth management with deterministic fallback

This module provides clean, reproducible evaluation results.
"""

from typing import Dict, List, Tuple
import json
from datetime import datetime


class ConfusionMatrixCalculator:
    """
    Computes confusion matrix for binary classification:
    - Predicted_Label vs Ground_Truth
    
    Explanation of terms:
    - TP (True Positive): Field correctly identified as match (both predict and actual: match)
    - TN (True Negative): Field correctly identified as non-match (both predict and actual: no match)
    - FP (False Positive): Field incorrectly identified as match (predict: match, actual: no match)
    - FN (False Negative): Field incorrectly identified as non-match (predict: no match, actual: match)
    """
    
    def __init__(self):
        """Initialize confusion matrix counts."""
        self.tp = 0  # True Positives
        self.tn = 0  # True Negatives
        self.fp = 0  # False Positives
        self.fn = 0  # False Negatives
    
    def add_prediction(self, predicted_label: str, ground_truth: str):
        """
        Add a single prediction to the confusion matrix.
        
        Args:
            predicted_label (str): "Match" or "No Match" (from final_score >= 0.75)
            ground_truth (str): "Match" or "No Match"
        """
        # Normalize labels
        pred = "Match" if "Match" in predicted_label else "No Match"
        truth = "Match" if "Match" in ground_truth else "No Match"
        
        if pred == "Match" and truth == "Match":
            self.tp += 1
        elif pred == "No Match" and truth == "No Match":
            self.tn += 1
        elif pred == "Match" and truth == "No Match":
            self.fp += 1
        elif pred == "No Match" and truth == "Match":
            self.fn += 1
    
    def get_confusion_matrix(self) -> Dict[str, int]:
        """Return confusion matrix as dictionary."""
        return {
            "TP": self.tp,
            "TN": self.tn,
            "FP": self.fp,
            "FN": self.fn
        }
    
    def print_confusion_matrix(self):
        """Print formatted confusion matrix for console output."""
        print()
        print("=" * 50)
        print("CONFUSION MATRIX")
        print("=" * 50)
        print()
        print("                Predicted")
        print("              Match   No Match")
        print(f"Actual Match     {self.tp:2d}        {self.fn:2d}")
        print(f"Actual No Match  {self.fp:2d}        {self.tn:2d}")
        print()
        print("=" * 50)
        print()


class MetricsCalculator:
    """
    Computes evaluation metrics from confusion matrix.
    
    Formulas:
    - Accuracy = (TP + TN) / (TP + TN + FP + FN)
    - Precision = TP / (TP + FP)    [Of predicted positives, how many are correct?]
    - Recall = TP / (TP + FN)       [Of actual positives, how many are detected?]
    - F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
    """
    
    def __init__(self, tp: int, tn: int, fp: int, fn: int):
        """
        Initialize calculator with confusion matrix values.
        
        Args:
            tp (int): True Positives
            tn (int): True Negatives
            fp (int): False Positives
            fn (int): False Negatives
        """
        self.tp = tp
        self.tn = tn
        self.fp = fp
        self.fn = fn
        
        self.total = tp + tn + fp + fn
    
    def accuracy(self) -> float:
        """
        Accuracy = (TP + TN) / Total
        Overall correctness of predictions.
        """
        if self.total == 0:
            return 0.0
        return (self.tp + self.tn) / self.total
    
    def precision(self) -> float:
        """
        Precision = TP / (TP + FP)
        Of all positive predictions, how many were correct?
        """
        denominator = self.tp + self.fp
        if denominator == 0:
            return 0.0
        return self.tp / denominator
    
    def recall(self) -> float:
        """
        Recall = TP / (TP + FN)
        Of all actual positives, how many did we detect?
        Also called Sensitivity or True Positive Rate.
        """
        denominator = self.tp + self.fn
        if denominator == 0:
            return 0.0
        return self.tp / denominator
    
    def f1_score(self) -> float:
        """
        F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
        Harmonic mean of Precision and Recall.
        Useful when you need balance between precision and recall.
        """
        precision = self.precision()
        recall = self.recall()
        
        denominator = precision + recall
        if denominator == 0:
            return 0.0
        
        return 2 * (precision * recall) / denominator
    
    def print_metrics(self):
        """Print formatted metrics for console output."""
        accuracy_pct = self.accuracy() * 100
        precision_pct = self.precision() * 100
        recall_pct = self.recall() * 100
        f1_pct = self.f1_score() * 100
        
        print("\n" + "=" * 50)
        print("EVALUATION METRICS")
        print("=" * 50)
        print()
        print(f"Accuracy  : {accuracy_pct:6.1f}%")
        print(f"Precision : {precision_pct:6.1f}%")
        print(f"Recall    : {recall_pct:6.1f}%")
        print(f"F1 Score  : {f1_pct:6.1f}%")
        print()
        print("=" * 50)
        print()
    
    def get_metrics_dict(self) -> Dict[str, float]:
        """Return metrics as dictionary."""
        return {
            "accuracy": self.accuracy(),
            "precision": self.precision(),
            "recall": self.recall(),
            "f1_score": self.f1_score()
        }


class GroundTruthManager:
    """
    Manages ground truth labels for evaluation.
    
    Strategy:
    1. Try to load from ground_truth.json file
    2. If not available, use deterministic internal dataset
    3. Allow manual labeling for custom data
    """
    
    def __init__(self, workspace_path: str = None):
        """
        Initialize ground truth manager.
        
        Args:
            workspace_path (str): Path to workspace for loading/saving ground truth
        """
        self.workspace_path = workspace_path
        self.ground_truth = {}
        self.load_ground_truth()
    
    def load_ground_truth(self):
        """
        Try to load ground truth from file.
        If not found, use internal sample dataset.
        """
        import os
        
        if self.workspace_path:
            gt_file = os.path.join(self.workspace_path, 'ground_truth.json')
            if os.path.exists(gt_file):
                try:
                    with open(gt_file, 'r') as f:
                        self.ground_truth = json.load(f)
                    return
                except Exception as e:
                    logger.warning(f"Failed to load ground truth file {gt_file}: {str(e)}")
                    pass
        
        # Use internal sample evaluation dataset (deterministic)
        self.ground_truth = self._get_sample_ground_truth()
    
    def _get_sample_ground_truth(self) -> Dict[str, str]:
        """
        Internal deterministic ground truth dataset for testing.
        Maps field comparisons to expected match status.
        
        This is used when no external ground truth file exists.
        """
        # Sample ground truth: (field, doc1_value, doc2_value) -> expected_match
        sample_gt = {
            # Example: Same company names -> Match
            ("name", "Acme Corporation", "Acme Corporation"): "Match",
            ("name", "TechCorp Inc", "TechCorp Inc"): "Match",
            ("name", "GlobalTrade Limited", "GlobalTrade Limited"): "Match",
            
            # Example: Same company with different suffixes -> Match (after normalization)
            ("name", "TechCorp Inc", "TechCorp Incorporated"): "Match",
            ("name", "GlobalTrade Ltd", "GlobalTrade Limited"): "Match",
            ("name", "InfoSys Pvt Ltd", "InfoSys Private Limited"): "Match",
            
            # Example: Different company names -> No Match
            ("name", "Acme Corporation", "TechCorp Inc"): "No Match",
            ("name", "GlobalTrade Limited", "InfoSys Pvt Ltd"): "No Match",
            
            # Example: Currency fields
            ("currency", "USD", "USD"): "Match",
            ("currency", "INR", "INR"): "Match",
            ("currency", "USD", "INR"): "No Match",
            
            # Example: Address fields
            ("address", "123 Main St, New York", "123 Main St, New York"): "Match",
            ("address", "456 Oak Ave, Boston", "789 Oak Ave, Boston"): "No Match",
            
            # Fall-through default
            "default": "No Match"
        }
        
        return sample_gt
    
    def get_label(self, field_name: str, value1: str, value2: str) -> str:
        """
        Get ground truth label for a field comparison.
        
        Args:
            field_name (str): Name of field (e.g., "name", "currency")
            value1 (str): Value from document 1
            value2 (str): Value from document 2
        
        Returns:
            str: "Match" or "No Match"
        """
        key = (field_name, value1, value2)
        
        if key in self.ground_truth:
            return self.ground_truth[key]
        
        # Try reverse order
        reverse_key = (field_name, value2, value1)
        if reverse_key in self.ground_truth:
            return self.ground_truth[reverse_key]
        
        # Return default
        return self.ground_truth.get("default", "No Match")
    
    def save_ground_truth(self, output_path: str):
        """
        Save ground truth to JSON file for future use.
        
        Args:
            output_path (str): Path to save JSON file
        """
        # Convert keys to strings for JSON serialization
        serializable_gt = {}
        for key, value in self.ground_truth.items():
            if isinstance(key, tuple):
                str_key = "|".join(str(k) for k in key)
            else:
                str_key = str(key)
            serializable_gt[str_key] = value
        
        with open(output_path, 'w') as f:
            json.dump(serializable_gt, f, indent=2)


class EvaluationSummaryPrinter:
    """
    Generates formatted evaluation summary for research paper screenshots.
    Clean, centered output suitable for academic documentation.
    """
    
    @staticmethod
    def print_final_summary(total_comparisons: int, tp: int, tn: int, fp: int, fn: int,
                           accuracy: float, precision: float, recall: float, f1: float):
        """
        Print final evaluation summary in clean format.
        
        Args:
            total_comparisons (int): Total number of field comparisons
            tp (int): True Positives
            tn (int): True Negatives
            fp (int): False Positives
            fn (int): False Negatives
            accuracy (float): Accuracy (0-1)
            precision (float): Precision (0-1)
            recall (float): Recall (0-1)
            f1 (float): F1 Score (0-1)
        """
        
        # Convert to percentages
        acc_pct = accuracy * 100
        prec_pct = precision * 100
        rec_pct = recall * 100
        f1_pct = f1 * 100
        
        # Print summary block
        print("\n")
        print("=" * 55)
        print("FINAL EVALUATION SUMMARY")
        print("=" * 55)
        print()
        print(f"Total Comparisons  : {total_comparisons}")
        print(f"True Positives     : {tp}")
        print(f"True Negatives     : {tn}")
        print(f"False Positives    : {fp}")
        print(f"False Negatives    : {fn}")
        print()
        print(f"Accuracy           : {acc_pct:6.1f}%")
        print(f"Precision          : {prec_pct:6.1f}%")
        print(f"Recall             : {rec_pct:6.1f}%")
        print(f"F1 Score           : {f1_pct:6.1f}%")
        print()
        print("=" * 55)
        print()

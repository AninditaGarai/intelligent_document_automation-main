"""
Visualization Module

Generates comprehensive visualizations for document automation results:
- Confusion Matrix heatmap
- Evaluation Metrics bar chart
- Document Classification distribution
- Field Extraction success rates
- Confidence Score distribution
- Document-wise Performance comparison

All graphs are saved as PNG and embedded in Excel results.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime


class ResultsVisualizer:
    """
    Generates publication-ready visualizations for research paper results.
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize visualizer.
        
        Args:
            output_dir (str): Directory to save visualization PNG files
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style for professional-looking plots
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['axes.titlesize'] = 13
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
    
    def visualize_confusion_matrix(self, confusion_matrix: Dict[str, int], 
                                   filename: str = "confusion_matrix.png") -> str:
        """
        Create confusion matrix heatmap visualization.
        
        Args:
            confusion_matrix (dict): {"TP": int, "TN": int, "FP": int, "FN": int}
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create confusion matrix as 2D array
        cm_array = np.array([
            [confusion_matrix['TP'], confusion_matrix['FN']],
            [confusion_matrix['FP'], confusion_matrix['TN']]
        ])
        
        # Create heatmap
        sns.heatmap(cm_array, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Match', 'No Match'],
                   yticklabels=['Match', 'No Match'],
                   cbar_kws={'label': 'Count'},
                   annot_kws={'size': 14, 'weight': 'bold'},
                   ax=ax)
        
        ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
        ax.set_ylabel('Actual Label', fontsize=12, fontweight='bold')
        ax.set_title('Confusion Matrix - Field Matching Results', 
                    fontsize=14, fontweight='bold', pad=20)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_metrics(self, metrics: Dict[str, float], 
                         filename: str = "evaluation_metrics.png") -> str:
        """
        Create evaluation metrics bar chart.
        
        Args:
            metrics (dict): {"Accuracy": float, "Precision": float, "Recall": float, "F1 Score": float}
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D']
        
        bars = ax.bar(metric_names, metric_values, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        ax.set_ylim(0, 1.0)
        ax.set_ylabel('Score', fontsize=12, fontweight='bold')
        ax.set_title('Evaluation Metrics - Field Matching Performance', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_document_classification(self, classifications: Dict[str, str],
                                         filename: str = "document_classification.png") -> str:
        """
        Create document classification distribution pie chart.
        
        Args:
            classifications (dict): {doc_name: document_type}
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Count document types
        doc_types = {}
        for doc_name, classification in classifications.items():
            doc_type = classification if isinstance(classification, str) else classification.get('document_type', 'Unknown')
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        if not doc_types:
            doc_types = {'No Data': 1}
        
        colors = plt.cm.Set3(range(len(doc_types)))
        wedges, texts, autotexts = ax.pie(doc_types.values(), labels=doc_types.keys(),
                                           autopct='%1.1f%%', colors=colors,
                                           startangle=90, textprops={'fontsize': 11})
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('black')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        # Make labels bold
        for text in texts:
            text.set_fontweight('bold')
        
        ax.set_title('Document Classification Distribution', 
                    fontsize=14, fontweight='bold', pad=20)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_field_extraction_success(self, extraction_results: Dict[str, Dict],
                                          filename: str = "field_extraction_success.png") -> str:
        """
        Create field extraction success rate visualization.
        
        Args:
            extraction_results (dict): {doc_name: {field_name: {values...}}}
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Count successful extractions per field
        field_success = {}
        field_total = {}
        
        for doc_name, fields in extraction_results.items():
            for field_name, field_data in fields.items():
                field_success[field_name] = field_success.get(field_name, 0) + (1 if field_data.get('name') or field_data.get('value') else 0)
                field_total[field_name] = field_total.get(field_name, 0) + 1
        
        if not field_total:
            field_total = {'No Fields': 1}
            field_success = {'No Fields': 0}
        
        field_names = list(field_total.keys())
        success_rates = [field_success.get(f, 0) / field_total[f] * 100 if field_total[f] > 0 else 0 
                        for f in field_names]
        
        colors = ['#2ecc71' if rate >= 80 else '#f39c12' if rate >= 50 else '#e74c3c' 
                 for rate in success_rates]
        
        bars = ax.barh(field_names, success_rates, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add percentage labels
        for i, (bar, rate) in enumerate(zip(bars, success_rates)):
            ax.text(rate, bar.get_y() + bar.get_height()/2,
                   f' {rate:.1f}%', va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlim(0, 105)
        ax.set_xlabel('Success Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Field Extraction Success Rate', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_confidence_distribution(self, confidence_scores: List[float],
                                         filename: str = "confidence_distribution.png") -> str:
        """
        Create confidence score distribution histogram.
        
        Args:
            confidence_scores (list): List of confidence scores [0-1]
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if not confidence_scores:
            confidence_scores = [0]
        
        # Create histogram
        n, bins, patches = ax.hist(confidence_scores, bins=20, edgecolor='black', 
                                   color='#3498db', alpha=0.7)
        
        # Color bins based on confidence level
        for i, patch in enumerate(patches):
            if bins[i] >= 0.8:
                patch.set_facecolor('#2ecc71')  # Green for high confidence
            elif bins[i] >= 0.5:
                patch.set_facecolor('#f39c12')  # Yellow for medium confidence
            else:
                patch.set_facecolor('#e74c3c')  # Red for low confidence
        
        ax.set_xlabel('Confidence Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Confidence Score Distribution', fontsize=14, fontweight='bold', pad=20)
        ax.axvline(np.mean(confidence_scores), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(confidence_scores):.3f}')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def visualize_document_performance(self, documents_results: Dict[str, Dict],
                                      filename: str = "document_performance.png") -> str:
        """
        Create document-wise performance comparison.
        
        Args:
            documents_results (dict): {doc_name: {metrics_info}}
            filename (str): Output filename
            
        Returns:
            str: Path to saved image
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        doc_names = []
        extraction_success = []
        
        for doc_name, result in documents_results.items():
            doc_names.append(doc_name.replace('_', ' '))
            
            if isinstance(result, dict):
                fields = result.get('fields', {})
                if fields:
                    success = sum(1 for f in fields.values() if f.get('name') or f.get('value')) / len(fields) * 100
                else:
                    success = 0
            else:
                success = 0
            
            extraction_success.append(success)
        
        if not doc_names:
            doc_names = ['No Data']
            extraction_success = [0]
        
        colors = ['#2ecc71' if s >= 80 else '#f39c12' if s >= 50 else '#e74c3c' 
                 for s in extraction_success]
        
        bars = ax.bar(range(len(doc_names)), extraction_success, color=colors, 
                     edgecolor='black', linewidth=1.5)
        
        ax.set_xticks(range(len(doc_names)))
        ax.set_xticklabels(doc_names, rotation=45, ha='right')
        ax.set_ylabel('Extraction Success (%)', fontsize=12, fontweight='bold')
        ax.set_title('Document-wise Extraction Performance', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, value in zip(bars, extraction_success):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'{value:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        filepath = os.path.join(self.output_dir, filename)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath
    
    def generate_all_visualizations(self, results_data: Dict) -> Dict[str, str]:
        """
        Generate all visualizations from results data.
        
        Args:
            results_data (dict): Complete results containing:
                - confusion_matrix
                - metrics
                - classifications
                - extracted_data
                - confidence_scores
                
        Returns:
            dict: {graph_name: filepath}
        """
        graph_paths = {}
        
        try:
            if 'confusion_matrix' in results_data:
                graph_paths['confusion_matrix'] = self.visualize_confusion_matrix(
                    results_data['confusion_matrix']
                )
                print("✓ Generated: Confusion Matrix visualization")
            
            if 'metrics' in results_data:
                graph_paths['metrics'] = self.visualize_metrics(results_data['metrics'])
                print("✓ Generated: Evaluation Metrics visualization")
            
            if 'classifications' in results_data:
                graph_paths['classification'] = self.visualize_document_classification(
                    results_data['classifications']
                )
                print("✓ Generated: Document Classification visualization")
            
            if 'extracted_data' in results_data:
                graph_paths['extraction'] = self.visualize_field_extraction_success(
                    results_data['extracted_data']
                )
                print("✓ Generated: Field Extraction Success visualization")
            
            if 'confidence_scores' in results_data:
                graph_paths['confidence'] = self.visualize_confidence_distribution(
                    results_data['confidence_scores']
                )
                print("✓ Generated: Confidence Distribution visualization")
            
            if 'extracted_data' in results_data:
                graph_paths['performance'] = self.visualize_document_performance(
                    results_data['extracted_data']
                )
                print("✓ Generated: Document Performance visualization")
        
        except Exception as e:
            print(f"Warning: Could not generate some visualizations: {e}")
        
        return graph_paths

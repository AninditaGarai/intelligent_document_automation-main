"""
Document Classifier Module

Classifies document type using rule-based keyword detection.
Supports: Quotation, Statement of Work (SOW), and Contract documents.
"""

import re


class DocumentClassifier:
    """
    Rule-based document classifier that identifies document types
    using keyword patterns and heuristics.
    """
    
    def __init__(self):
        """Initialize classifier with keyword patterns for each document type."""
        
        # Keywords for each document type
        self.quotation_keywords = [
            'quotation', 'quote', 'proposal', 'estimate', 'bid',
            'pricing', 'cost estimate', 'tender', 'qtn', 'rate card'
        ]
        
        self.sow_keywords = [
            'statement of work', 'sow', 'scope of work', 'project charter',
            'deliverables', 'milestones', 'timeline'
        ]
        
        self.contract_keywords = [
            'contract', 'agreement', 'terms and conditions', 't&c', 'service agreement',
            'master agreement', 'msa', 'terms of service', 'license agreement',
            'nda', 'non-disclosure'
        ]
    
    def classify(self, text: str) -> dict:
        """
        Classify document based on extracted text.
        
        Args:
            text (str): Extracted text from document
            
        Returns:
            dict: Contains:
                - 'document_type': Classified type (Quotation/SOW/Contract/Unknown)
                - 'confidence': Confidence score (0-100)
                - 'explanation': Reason for classification
                - 'found_keywords': Keywords that matched
        """
        
        # Convert text to lowercase for matching
        text_lower = text.lower()
        
        # Count keyword matches for each type
        quotation_matches = sum(1 for kw in self.quotation_keywords if kw in text_lower)
        sow_matches = sum(1 for kw in self.sow_keywords if kw in text_lower)
        contract_matches = sum(1 for kw in self.contract_keywords if kw in text_lower)
        
        # Find which keywords actually matched
        found_quotation = [kw for kw in self.quotation_keywords if kw in text_lower]
        found_sow = [kw for kw in self.sow_keywords if kw in text_lower]
        found_contract = [kw for kw in self.contract_keywords if kw in text_lower]
        
        # Determine document type based on keyword matches
        max_matches = max(quotation_matches, sow_matches, contract_matches)
        
        if max_matches == 0:
            # Try alternative heuristics
            classification = self._classify_by_heuristics(text_lower)
            return classification
        
        # Determine primary type
        if quotation_matches > sow_matches and quotation_matches > contract_matches:
            doc_type = "Quotation"
            found_keywords = found_quotation
        elif sow_matches > quotation_matches and sow_matches > contract_matches:
            doc_type = "Statement of Work"
            found_keywords = found_sow
        elif contract_matches > quotation_matches and contract_matches > sow_matches:
            doc_type = "Contract"
            found_keywords = found_contract
        else:
            # Tie-breaker: use first prominent match
            if quotation_matches > 0:
                doc_type = "Quotation"
                found_keywords = found_quotation
            elif sow_matches > 0:
                doc_type = "Statement of Work"
                found_keywords = found_sow
            else:
                doc_type = "Contract"
                found_keywords = found_contract
        
        # Calculate confidence based on keyword density
        total_keywords = quotation_matches + sow_matches + contract_matches
        confidence = min(100, int((max_matches / total_keywords * 100) if total_keywords > 0 else 0))
        
        result = {
            'document_type': doc_type,
            'confidence': confidence,
            'explanation': f"Classified as {doc_type} based on keyword matches: {', '.join(found_keywords)}",
            'found_keywords': found_keywords,
            'match_counts': {
                'quotation': quotation_matches,
                'sow': sow_matches,
                'contract': contract_matches
            }
        }
        
        return result
    
    def _classify_by_heuristics(self, text: str) -> dict:
        """
        Alternative classification using content heuristics.
        
        Args:
            text (str): Lowercased text
            
        Returns:
            dict: Classification result
        """
        
        # Check for quotation indicators
        if any(phrase in text for phrase in ['total price', 'unit price', 'rate per', 'pricing']):
            return {
                'document_type': 'Quotation',
                'confidence': 50,
                'explanation': 'Classified as Quotation based on pricing-related terms',
                'found_keywords': ['pricing-related content'],
                'match_counts': {'quotation': 1, 'sow': 0, 'contract': 0}
            }
        
        # Check for SOW indicators
        if any(phrase in text for phrase in ['deliverable', 'timeline', 'milestone', 'phase']):
            return {
                'document_type': 'Statement of Work',
                'confidence': 50,
                'explanation': 'Classified as Statement of Work based on project-related terms',
                'found_keywords': ['project-related content'],
                'match_counts': {'quotation': 0, 'sow': 1, 'contract': 0}
            }
        
        # Default to Contract if nothing else matches
        return {
            'document_type': 'Unknown',
            'confidence': 0,
            'explanation': 'Could not classify document with confidence. Manual review recommended.',
            'found_keywords': [],
            'match_counts': {'quotation': 0, 'sow': 0, 'contract': 0}
        }
    
    def get_supported_types(self) -> list:
        """
        Get list of supported document types.
        
        Returns:
            list: Supported document type names
        """
        return ["Quotation", "Statement of Work", "Contract"]


def classify_documents(text_dict: dict) -> dict:
    """
    Classify multiple documents.
    
    Args:
        text_dict (dict): Dictionary mapping document names to extracted text
        
    Returns:
        dict: Mapping of document names to classification results
    """
    
    classifier = DocumentClassifier()
    classifications = {}
    
    for doc_name, text in text_dict.items():
        try:
            classification = classifier.classify(text)
            classifications[doc_name] = classification
            
            print(f"{doc_name}:")
            print(f"  Type: {classification['document_type']}")
            print(f"  Confidence: {classification['confidence']}%")
            print(f"  Keywords found: {', '.join(classification['found_keywords'])}\n")
            
        except Exception as e:
            print(f"Error classifying {doc_name}: {str(e)}\n")
            classifications[doc_name] = {
                'document_type': 'Error',
                'confidence': 0,
                'explanation': f"Classification failed: {str(e)}",
                'found_keywords': []
            }
    
    return classifications

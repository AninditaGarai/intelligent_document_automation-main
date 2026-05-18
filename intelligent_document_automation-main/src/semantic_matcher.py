"""
Semantic Matcher Module with Hybrid Pattern-Semantic Verification Framework

Implements a sophisticated multi-layer verification system:

1. PATTERN MATCHING LAYER
   - String similarity using difflib.SequenceMatcher
   - Company suffix normalization (Pvt Ltd, Limited, Ltd, etc.)
   - Case and whitespace normalization
   - Returns pattern similarity score (0 to 1)

2. RULE-BASED VALIDATION LAYER
   - Currency mapping: INR → ₹ → Indian Rupees
   - Currency codes: USD → $ → US Dollars
   - Exact match overrides with rule-based explanations
   - Deterministic matching rules

3. LIGHTWEIGHT SEMANTIC SIMILARITY LAYER (LLM-inspired)
   - Token-based Jaccard similarity (no ML models)
   - Normalized token set comparison
   - Conceptually inspired by transformer similarity
   - Returns semantic similarity score (0 to 1)

4. DECISION FUSION ENGINE
   - Hybrid scoring: Final Score = (0.6 × Pattern Score) + (0.4 × Semantic Score)
   - Threshold-based decision: Score ≥ 0.75 → Match Found
   - Clear numeric breakdown with reasoning

5. EXPLAINABLE OUTPUT
   - Every match includes numeric scores
   - Clear reasoning for accept/reject decisions
   - Transparency in score calculation
   - Human-readable explanations

This system is fully deterministic and does NOT use any trained ML models or cloud APIs.
All similarity calculations are rule-based and repeatable.
"""

import difflib
import re
from typing import Tuple, Dict, List


class HybridMatchingEngine:
    """
    Hybrid Pattern-Semantic Matching with Explainability (XAI).
    Combines deterministic pattern matching with semantic similarity scoring.
    
    Core Philosophy:
    - No trained models required
    - Fully deterministic behavior
    - Explainable at every step
    - Transparent numeric scoring
    """
    
    # Decision thresholds
    PATTERN_SCORE_WEIGHT = 0.6      # Pattern matching contributes 60%
    SEMANTIC_SCORE_WEIGHT = 0.4     # Semantic similarity contributes 40%
    MATCH_DECISION_THRESHOLD = 0.75  # Score ≥ 0.75 = Match Found
    
    def __init__(self):
        """Initialize matcher with normalization rules and validation mappings."""
        
        # COMPANY SUFFIX NORMALIZATION (Pattern Matching Layer)
        # Standard company suffixes that should be normalized
        self.company_suffixes = [
            'private limited', 'pvt ltd', 'pvtltd', 'pvt. ltd.',
            'private', 'limited', 'ltd', 'ltd.',
            'inc', 'inc.', 'incorporated',
            'llc', 'limited liability company',
            'llp', 'limited liability partnership',
            'co', 'co.', 'company',
            'corp', 'corp.', 'corporation',
            'gmbh',  # German
            'ag',    # German
            'sa',    # Spanish/Portuguese
            'pte',   # Singapore
        ]
        
        # RULE-BASED VALIDATION MAPPINGS (Rule-Based Validation Layer)
        # Currency normalization: symbol → code → full name
        self.currency_rules = {
            # USD
            '$': 'USD',
            'usd': 'USD',
            'us dollar': 'USD',
            'us dollars': 'USD',
            'dollar': 'USD',
            'dollars': 'USD',
            
            # INR
            '₹': 'INR',
            'inr': 'INR',
            'indian rupee': 'INR',
            'indian rupees': 'INR',
            'rupee': 'INR',
            'rupees': 'INR',
            
            # EUR
            '€': 'EUR',
            'eur': 'EUR',
            'euro': 'EUR',
            'euros': 'EUR',
            
            # GBP
            '£': 'GBP',
            'gbp': 'GBP',
            'pound': 'GBP',
            'pounds': 'GBP',
            'british pound': 'GBP',
        }
        
        # ABBREVIATION MAPPINGS (for token normalization)
        self.abbreviation_map = {
            'pvt': 'private',
            'ltd': 'limited',
            'inc': 'incorporated',
            'corp': 'corporation',
            'llc': 'limited liability company',
            'llp': 'limited liability partnership',
            'co': 'company',
            'org': 'organization',
        }
    
    # ========== LAYER 1: PATTERN MATCHING ==========
    
    def normalize_company_name(self, text: str) -> str:
        """
        Normalize company names for pattern matching.
        Removes company suffixes and extra punctuation.
        
        Args:
            text (str): Company name
            
        Returns:
            str: Normalized company name
        """
        if not text:
            return ""
        
        # Convert to lowercase and strip
        text = text.lower().strip()
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        # Remove company suffixes
        for suffix in sorted(self.company_suffixes, key=len, reverse=True):
            suffix_pattern = r'\b' + re.escape(suffix) + r'\b'
            text = re.sub(suffix_pattern, '', text)
        
        # Remove periods and special chars except spaces
        text = re.sub(r'[^\w\s]', '', text)
        
        # Remove extra spaces again after cleanup
        text = ' '.join(text.split())
        
        return text
    
    def calculate_pattern_score(self, text1: str, text2: str) -> Tuple[float, str]:
        """
        PATTERN MATCHING LAYER
        Calculate string similarity using difflib.SequenceMatcher.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            Tuple[float, str]: (similarity_score 0-1, explanation)
        """
        if not text1 or not text2:
            return 0.0, "One or both values missing"
        
        # Normalize both texts
        norm1 = self.normalize_company_name(str(text1))
        norm2 = self.normalize_company_name(str(text2))
        
        if not norm1 or not norm2:
            return 0.0, "Normalization resulted in empty strings"
        
        # Exact match after normalization
        if norm1 == norm2:
            return 1.0, f"Exact match after normalization: '{norm1}'"
        
        # Calculate sequence matcher ratio
        matcher = difflib.SequenceMatcher(None, norm1, norm2)
        ratio = matcher.ratio()
        
        return ratio, f"Pattern similarity (normalized): '{norm1}' vs '{norm2}' = {ratio:.2f}"
    
    # ========== LAYER 2: RULE-BASED VALIDATION ==========
    
    def apply_rule_based_matching(self, value1: str, value2: str, field_type: str) -> Tuple[bool, str]:
        """
        RULE-BASED VALIDATION LAYER
        Apply deterministic rules for specific field types.
        
        Args:
            value1 (str): First value
            value2 (str): Second value
            field_type (str): Type of field (currency, client_name, etc.)
            
        Returns:
            Tuple[bool, str]: (rule_matched, explanation)
        """
        
        if field_type == 'currency':
            return self._match_currency_rule(value1, value2)
        
        # No specific rules for other field types
        return False, "No rule-based validation for this field type"
    
    def _match_currency_rule(self, curr1: str, curr2: str) -> Tuple[bool, str]:
        """
        Rule-based currency matching using normalization rules.
        
        Args:
            curr1 (str): First currency representation
            curr2 (str): Second currency representation
            
        Returns:
            Tuple[bool, str]: (match, explanation)
        """
        if not curr1 or not curr2:
            return False, "One or both currency values missing"
        
        # Normalize currencies using rule mappings
        norm1 = self.currency_rules.get(str(curr1).lower(), str(curr1).upper()) if curr1 else None
        norm2 = self.currency_rules.get(str(curr2).lower(), str(curr2).upper()) if curr2 else None
        
        if not norm1 or not norm2:
            return False, "Currency normalization failed - None values"
        
        match = norm1.upper() == norm2.upper()
        explanation = f"Currency rule match: '{curr1}' → {norm1} vs '{curr2}' → {norm2} = {match}"
        
        return match, explanation
    
    # ========== LAYER 3: LIGHTWEIGHT SEMANTIC SIMILARITY ==========
    
    def normalize_text_for_semantic(self, text: str) -> str:
        """
        Normalize text for semantic similarity calculation.
        Expands abbreviations and removes noise.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove extra spaces
        text = ' '.join(text.split())
        
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        
        # Expand abbreviations
        for abbrev, full in self.abbreviation_map.items():
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            text = re.sub(pattern, full, text)
        
        return text
    
    def calculate_semantic_similarity(self, text1: str, text2: str) -> Tuple[float, Dict]:
        """
        LIGHTWEIGHT SEMANTIC SIMILARITY LAYER (LLM-inspired)
        Uses token-based Jaccard similarity.
        
        IMPORTANT: This is conceptually inspired by transformer-based semantic similarity
        but uses simplistic token overlap, NOT a trained LLM model.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            Tuple[float, dict]: (semantic_score 0-1, analysis_dict)
        """
        if not text1 or not text2:
            return 0.0, {'method': 'empty_input', 'tokens1': [], 'tokens2': []}
        
        # Normalize both texts
        norm1 = self.normalize_text_for_semantic(str(text1))
        norm2 = self.normalize_text_for_semantic(str(text2))
        
        # Tokenize (simple whitespace split)
        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())
        
        if not tokens1 or not tokens2:
            return 0.0, {'method': 'empty_after_norm', 'tokens1': list(tokens1), 'tokens2': list(tokens2)}
        
        # Jaccard Similarity = Intersection / Union
        intersection = len(tokens1 & tokens2)
        union = len(tokens1 | tokens2)
        
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        analysis = {
            'method': 'token_jaccard_similarity',
            'tokens1': sorted(list(tokens1)),
            'tokens2': sorted(list(tokens2)),
            'intersection': intersection,
            'union': union,
            'jaccard_score': jaccard_similarity,
            'normalized_text1': norm1,
            'normalized_text2': norm2
        }
        
        return jaccard_similarity, analysis
    
    # ========== LAYER 4: DECISION FUSION ENGINE ==========
    
    def fuse_scores(self, pattern_score: float, semantic_score: float) -> Tuple[float, str]:
        """
        DECISION FUSION ENGINE
        Combine pattern and semantic scores using weighted fusion.
        
        Formula: Final Score = (0.6 × Pattern Score) + (0.4 × Semantic Score)
        Decision: Score ≥ 0.75 → Match Found, Else → Not Found
        
        Args:
            pattern_score (float): Pattern similarity score (0-1)
            semantic_score (float): Semantic similarity score (0-1)
            
        Returns:
            Tuple[float, str]: (final_score 0-1, reasoning)
        """
        
        # Weighted combination
        final_score = (self.PATTERN_SCORE_WEIGHT * pattern_score) + (self.SEMANTIC_SCORE_WEIGHT * semantic_score)
        
        # Decision reasoning
        if final_score >= self.MATCH_DECISION_THRESHOLD:
            decision = "MATCH FOUND ✓"
            reason = f"Final score {final_score:.2f} ≥ {self.MATCH_DECISION_THRESHOLD} (Match threshold)"
        else:
            decision = "NO MATCH ✗"
            reason = f"Final score {final_score:.2f} < {self.MATCH_DECISION_THRESHOLD} (Match threshold)"
        
        reasoning = f"{decision} | {reason}"
        
        return final_score, reasoning
    
    # ========== LAYER 5: EXPLAINABLE OUTPUT ==========
    
    def match_field_values(self, value1: str, value2: str, field_name: str, field_type: str = 'text') -> Dict:
        """
        Perform complete hybrid matching on two field values with full explanation.
        
        Orchestrates all layers:
        1. Pattern Matching → pattern_score
        2. Rule-Based Validation → rule_match
        3. Semantic Similarity → semantic_score
        4. Decision Fusion → final_score + decision
        
        Args:
            value1 (str): First value
            value2 (str): Second value
            field_name (str): Name of field (for reporting)
            field_type (str): Type of field (currency, client_name, etc.)
            
        Returns:
            Dict: Complete match result with explainability
        """
        
        # Handle missing values
        if not value1 and not value2:
            return {
                'field': field_name,
                'status': 'NOT FOUND',
                'final_score': 0.0,
                'pattern_score': 0.0,
                'semantic_score': 0.0,
                'rule_matched': False,
                'explanation': [
                    f"Field: {field_name}",
                    f"Status: NOT FOUND",
                    f"Reason: Both values are missing. Manual verification required."
                ]
            }
        
        if not value1 or not value2:
            found_in = "Document 1" if value1 else "Document 2"
            return {
                'field': field_name,
                'status': 'INCOMPLETE',
                'final_score': 0.0,
                'pattern_score': 0.0,
                'semantic_score': 0.0,
                'rule_matched': False,
                'explanation': [
                    f"Field: {field_name}",
                    f"Status: INCOMPLETE",
                    f"Value 1: {value1 if value1 else 'MISSING'}",
                    f"Value 2: {value2 if value2 else 'MISSING'}",
                    f"Reason: Field missing in one document. Found in {found_in} only."
                ]
            }
        
        # LAYER 1: Pattern Matching
        pattern_score, pattern_explanation = self.calculate_pattern_score(value1, value2)
        
        # LAYER 2: Rule-Based Validation
        rule_matched, rule_explanation = self.apply_rule_based_matching(value1, value2, field_type)
        
        # If rule matches, return early with high confidence
        if rule_matched:
            return {
                'field': field_name,
                'status': 'FOUND (Rule-Based)',
                'final_score': 1.0,
                'pattern_score': pattern_score,
                'semantic_score': 1.0,
                'rule_matched': True,
                'explanation': [
                    f"Field: {field_name}",
                    f"Status: FOUND (Rule-Based Match) ✓",
                    f"Value 1: {value1}",
                    f"Value 2: {value2}",
                    f"Rule Explanation: {rule_explanation}",
                    f"Decision: Rule-based match OVERRIDES other scores. This is a definitive match."
                ]
            }
        
        # LAYER 3: Semantic Similarity
        semantic_score, semantic_analysis = self.calculate_semantic_similarity(value1, value2)
        
        # LAYER 4: Decision Fusion
        final_score, fusion_reasoning = self.fuse_scores(pattern_score, semantic_score)
        
        # Determine status
        if final_score >= self.MATCH_DECISION_THRESHOLD:
            status = "FOUND"
        else:
            status = "NOT FOUND"
        
        # LAYER 5: Explainable Output
        explanation = [
            f"Field: {field_name}",
            f"Status: {status}",
            f"Value 1: {value1}",
            f"Value 2: {value2}",
            "",
            f"--- HYBRID MATCHING FRAMEWORK ANALYSIS ---",
            "",
            f"LAYER 1: Pattern Matching",
            f"  Score: {pattern_score:.2f} (0-1)",
            f"  Explanation: {pattern_explanation}",
            "",
            f"LAYER 3: Lightweight Semantic Similarity (LLM-inspired)",
            f"  Score: {semantic_score:.2f} (0-1)",
            f"  Method: Token-based Jaccard similarity (conceptually inspired by transformers, no ML models used)",
            f"  Token 1: {semantic_analysis.get('tokens1', [])}",
            f"  Token 2: {semantic_analysis.get('tokens2', [])}",
            "",
            f"LAYER 4: Decision Fusion Engine",
            f"  Formula: (0.6 × {pattern_score:.2f}) + (0.4 × {semantic_score:.2f})",
            f"  Final Score: {final_score:.2f}",
            f"  Decision: {fusion_reasoning}",
            ""
        ]
        
        return {
            'field': field_name,
            'status': status,
            'final_score': round(final_score, 2),
            'pattern_score': round(pattern_score, 2),
            'semantic_score': round(semantic_score, 2),
            'rule_matched': rule_matched,
            'explanation': explanation
        }


def perform_multi_document_matching(documents: Dict[str, Dict]) -> Dict:
    """
    Perform hybrid matching across multiple documents.
    
    Args:
        documents (dict): Dictionary of {doc_name: extracted_fields}
                         Each field dict should have: name, organization, currency, address
    
    Returns:
        dict: Comprehensive matching results for all document pairs
    """
    
    engine = HybridMatchingEngine()
    
    # Get list of document names
    doc_names = list(documents.keys())
    
    # Results dictionary
    matching_results = {
        'summary': {},
        'details': {}
    }
    
    # Perform pairwise matching for all document combinations
    for i, doc1_name in enumerate(doc_names):
        for j, doc2_name in enumerate(doc_names[i+1:], start=i+1):
            
            doc1_fields = documents[doc1_name]
            doc2_fields = documents[doc2_name]
            
            pair_key = f"{doc1_name} ↔ {doc2_name}"
            matching_results['details'][pair_key] = {}
            
            # Match key fields
            fields_to_match = [
                ('client_name', 'text'),
                ('organization_name', 'text'),
                ('currency', 'currency'),
                ('billing_address', 'text')
            ]
            
            for field_name, field_type in fields_to_match:
                value1 = doc1_fields.get(field_name, {}).get('name') or \
                        doc1_fields.get(field_name, {}).get('currency') or \
                        doc1_fields.get(field_name, {}).get('organization') or \
                        doc1_fields.get(field_name, {}).get('address')
                
                value2 = doc2_fields.get(field_name, {}).get('name') or \
                        doc2_fields.get(field_name, {}).get('currency') or \
                        doc2_fields.get(field_name, {}).get('organization') or \
                        doc2_fields.get(field_name, {}).get('address')
                
                # Perform matching
                match_result = engine.match_field_values(value1, value2, field_name, field_type)
                matching_results['details'][pair_key][field_name] = match_result
    
    return matching_results

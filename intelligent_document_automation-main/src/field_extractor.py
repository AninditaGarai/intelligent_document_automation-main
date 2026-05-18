"""
Field Extraction Module

Extracts key business fields from documents using pattern matching and heuristics.
Fields: Client Name, Billing Address, Organization Name, Currency
"""

import re
from logger_config import get_logger

logger = get_logger(__name__)


class FieldExtractor:
    """
    Extracts structured fields from unstructured document text.
    Uses regex patterns and heuristics for reliable extraction.
    """
    
    def __init__(self):
        """Initialize field extractor with patterns."""
        
        # Currency patterns: symbols and codes
        self.currency_pattern = r'\$|€|£|¥|INR|USD|EUR|GBP|JPY|AUD|CAD|CHF|\bDollar\b|\bEuro\b|\bPound\b|\bRupee\b'
        
        # Common address indicators
        self.address_indicators = [
            'address:', 'billing address:', 'address of', 'located at',
            'street:', 'city:', 'postal', 'zip code', 'pin code'
        ]
        
        # Common name prefixes in documents
        self.name_prefixes = [
            'client:', 'client name:', 'to:', 'company:', 'organization:',
            'vendor:', 'supplier:', 'from:', 'attention:'
        ]
    
    def extract_currency(self, text: str) -> dict:
        """
        Extract currency information from text.
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Contains:
                - 'currency': Detected currency (code or symbol)
                - 'confidence': Confidence score (0-100)
                - 'explanation': Reason for finding/not finding currency
        """
        
        text_lower = text.lower()
        
        # Search for currency patterns
        matches = re.findall(self.currency_pattern, text)
        
        if matches:
            # Found currency
            currency = matches[0]  # Take first match
            
            # Map common currencies to codes
            currency_mapping = {
                '$': 'USD',
                'dollar': 'USD',
                'usd': 'USD',
                '€': 'EUR',
                'euro': 'EUR',
                'eur': 'EUR',
                '£': 'GBP',
                'pound': 'GBP',
                'gbp': 'GBP',
                '¥': 'JPY',
                'inr': 'INR',
                'rupee': 'INR'
            }
            
            # Get standardized currency code
            currency_code = currency_mapping.get(currency.lower(), currency.upper())
            
            return {
                'currency': currency_code,
                'confidence': 90,
                'explanation': f'Found currency: {currency_code}',
                'raw_match': currency
            }
        else:
            return {
                'currency': None,
                'confidence': 0,
                'explanation': 'No currency information found in document',
                'raw_match': None
            }
    
    def extract_client_name(self, text: str) -> dict:
        """
        Extract client/customer name from text.
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Contains:
                - 'name': Extracted client name (or None)
                - 'confidence': Confidence score (0-100)
                - 'explanation': How name was extracted
        """
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Strategy 1: Look for explicit "Client:" or "To:" labels
        for line in lines:
            line_lower = line.lower()
            for prefix in ['client:', 'client name:', 'to:', 'attention:']:
                if prefix in line_lower:
                    # Extract text after the prefix
                    match = re.search(prefix + r'\s*([A-Za-z\s&.,\-]+)', line_lower)
                    if match:
                        name = match.group(1).strip()
                        if len(name) < 100:  # Sanity check
                            return {
                                'name': name.title(),
                                'confidence': 85,
                                'explanation': f'Found explicit client label: "{prefix}"',
                                'method': 'explicit_label'
                            }
        
        # Strategy 2: Look for company-like patterns (Pvt Ltd, Inc, Ltd, etc.)
        company_pattern = r'([A-Z][A-Za-z\s&.,\-]+?(?:Pvt\.?\s+Ltd|Inc\.|Limited|Ltd|LLC|LLP|Corporation|Corp\.))'
        matches = re.findall(company_pattern, text)
        
        if matches:
            name = matches[0].strip()
            return {
                'name': name,
                'confidence': 75,
                'explanation': f'Found organization pattern: {name}',
                'method': 'company_pattern'
            }
        
        # Strategy 3: Look at first meaningful line (common in formal letters)
        first_meaningful = None
        for line in lines:
            line = line.strip()
            if len(line) > 5 and not line[0].isspace():
                # Check if it looks like a name (mostly letters, spaces, special chars)
                if re.match(r'^[A-Z][A-Za-z\s&.,\-]{3,50}$', line):
                    first_meaningful = line
                    break
        
        if first_meaningful:
            return {
                'name': first_meaningful,
                'confidence': 50,
                'explanation': 'Assumed first formal line is client name (low confidence)',
                'method': 'first_line_heuristic'
            }
        
        # No client name found
        return {
            'name': None,
            'confidence': 0,
            'explanation': 'Could not identify client name. Document may lack this information.',
            'method': 'not_found'
        }
    
    def extract_organization_name(self, text: str) -> dict:
        """
        Extract our organization/vendor name from document.
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Contains:
                - 'organization': Name (or None)
                - 'confidence': Confidence score (0-100)
                - 'explanation': How it was extracted
        """
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Strategy 1: Look for "From:", "Vendor:", "Supplier:" labels
        for line in lines:
            line_lower = line.lower()
            for prefix in ['from:', 'vendor:', 'vendor name:', 'supplier:', 'company:', 'our company:']:
                if prefix in line_lower:
                    match = re.search(prefix + r'\s*([A-Za-z\s&.,\-]+)', line_lower)
                    if match:
                        org_name = match.group(1).strip()
                        if len(org_name) < 100:
                            return {
                                'organization': org_name.title(),
                                'confidence': 80,
                                'explanation': f'Found explicit label: "{prefix}"',
                                'method': 'explicit_label'
                            }
        
        # Strategy 2: Look for letterhead-like content at the top
        # Usually first 20% of document
        doc_start = '\n'.join(lines[:min(5, len(lines))])
        
        # Look for company patterns in first few lines
        company_pattern = r'([A-Z][A-Za-z\s&.,\-]+?(?:Pvt\.?\s+Ltd|Inc\.|Limited|Ltd|LLC|LLP|Corporation|Corp\.))'
        matches = re.findall(company_pattern, doc_start)
        
        if matches:
            org_name = matches[0].strip()
            return {
                'organization': org_name,
                'confidence': 70,
                'explanation': f'Found organization in document header: {org_name}',
                'method': 'header_pattern'
            }
        
        # No organization found
        return {
            'organization': None,
            'confidence': 0,
            'explanation': 'Could not identify organization name.',
            'method': 'not_found'
        }
    
    def extract_billing_address(self, text: str) -> dict:
        """
        Extract billing address (complex field, often optional).
        
        Args:
            text (str): Document text
            
        Returns:
            dict: Contains:
                - 'address': Address text (or None)
                - 'confidence': Confidence score (0-100)
                - 'explanation': Why address was/wasn't found
        """
        
        text_lower = text.lower()
        lines = text.split('\n')
        
        # Strategy 1: Look for explicit "Address:" label
        for i, line in enumerate(lines):
            if 'billing address' in line.lower() or 'address:' in line.lower():
                # Get next 2-3 lines as address
                address_lines = []
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and len(next_line) < 100:
                        address_lines.append(next_line)
                    else:
                        break
                
                if address_lines:
                    address = ' | '.join(address_lines)
                    return {
                        'address': address,
                        'confidence': 85,
                        'explanation': f'Found explicit address label',
                        'method': 'explicit_label'
                    }
        
        # Strategy 2: Look for postal code patterns (indicates address)
        postal_pattern = r'\b\d{5,6}\b|\bpin\s*code:?\s*\d+\b'
        if re.search(postal_pattern, text_lower):
            return {
                'address': 'Found postal code pattern but full address extraction too complex',
                'confidence': 30,
                'explanation': 'Postal code found but complete address requires advanced extraction',
                'method': 'partial_match'
            }
        
        # No address found
        return {
            'address': None,
            'confidence': 0,
            'explanation': 'Address information not clearly marked in document',
            'method': 'not_found'
        }
    
    def extract_all_fields(self, text: str) -> dict:
        """
        Extract all key fields from document.
        
        Args:
            text (str): Document text
            
        Returns:
            dict: All extracted fields
        """
        
        return {
            'client_name': self.extract_client_name(text),
            'organization_name': self.extract_organization_name(text),
            'currency': self.extract_currency(text),
            'billing_address': self.extract_billing_address(text)
        }


def extract_fields_from_documents(text_dict: dict) -> dict:
    """
    Extract fields from multiple documents.
    
    Args:
        text_dict (dict): Map of document names to extracted text
        
    Returns:
        dict: All extracted fields for each document
    """
    
    extractor = FieldExtractor()
    results = {}
    
    for doc_name, text in text_dict.items():
        # Validate input: must be string and non-empty
        if not isinstance(text, str) or not text.strip():
            logger.warning(f"Skipping {doc_name}: text is not a valid string or is empty")
            results[doc_name] = {
                'client_name': {'name': None, 'confidence': 0, 'explanation': 'Invalid or empty text'},
                'organization_name': {'organization': None, 'confidence': 0, 'explanation': 'Invalid or empty text'},
                'currency': {'currency': None, 'confidence': 0, 'explanation': 'Invalid or empty text'},
                'billing_address': {'address': None, 'confidence': 0, 'explanation': 'Invalid or empty text'}
            }
            continue
        
        try:
            fields = extractor.extract_all_fields(text)
            results[doc_name] = fields
            
            logger.info(f"Extracted fields from {doc_name}")
            for field_name, field_data in fields.items():
                # Safe dict access: check if field_data is dict and has keys
                if field_data and isinstance(field_data, dict) and len(field_data) > 0:
                    first_key = list(field_data.keys())[0]
                    if field_data[first_key]:
                        logger.debug(f"  {field_name}: {field_data[first_key]}")
                    else:
                        logger.debug(f"  {field_name}: Not found")
                else:
                    logger.debug(f"  {field_name}: Invalid field data")
            
        except Exception as e:
            logger.error(f"Error extracting fields from {doc_name}: {str(e)}", exc_info=True)
            results[doc_name] = {
                'client_name': {'name': None, 'confidence': 0, 'explanation': str(e)},
                'organization_name': {'organization': None, 'confidence': 0, 'explanation': str(e)},
                'currency': {'currency': None, 'confidence': 0, 'explanation': str(e)},
                'billing_address': {'address': None, 'confidence': 0, 'explanation': str(e)}
            }
    
    return results

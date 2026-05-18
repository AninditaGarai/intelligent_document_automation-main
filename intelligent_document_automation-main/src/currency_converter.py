"""
Currency Normalization Module

Real-time currency detection and conversion to INR (Indian Rupee).
Implements deterministic conversion with API fallback and logging.

Features:
- Detects currency type from extracted fields (USD, EUR, GBP, etc.)
- Extracts numerical amounts using regex patterns
- Fetches real-time exchange rates from exchangerate-api.com
- Falls back to hardcoded exchange rates if API fails
- Logs all conversions with timestamps
- Provides explainable conversion details
- Handles INR-denominated amounts (no conversion needed)

Conversion Formula:
    Converted Amount (INR) = Original Amount × Exchange Rate to INR

This module is purely deterministic and performs NO financial forecasting.
All conversions are logged with timestamps for audit trail.
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import urllib.request
import urllib.error


class CurrencyConverter:
    """
    Handles currency detection, amount extraction, and real-time conversion to INR.
    Provides explainable output for currency transformations.
    """
    
    def __init__(self):
        """
        Initialize currency converter with:
        - Currency detection patterns
        - Hardcoded fallback exchange rates
        - Configuration parameters
        """
        
        # Supported currency codes with symbols
        self.currency_patterns = {
            'USD': [r'\$', r'\bUSD\b', r'\bDollars?\b'],
            'EUR': [r'€', r'\bEUR\b', r'\bEuros?\b'],
            'GBP': [r'£', r'\bGBP\b', r'\bPounds?\b'],
            'JPY': [r'¥', r'\bJPY\b', r'\bYen\b'],
            'AUD': [r'\bAUD\b', r'\bAustralian Dollars?\b'],
            'CAD': [r'\bCAD\b', r'\bCanadian Dollars?\b'],
            'CHF': [r'\bCHF\b', r'\bSwiss Francs?\b'],
            'INR': [r'\bINR\b', r'₹', r'\bRupees?\b'],
        }
        
        # Hardcoded fallback exchange rates to INR
        # These are reference rates and updated periodically
        self.fallback_rates = {
            'USD': 83.25,  # 1 USD = 83.25 INR
            'EUR': 90.50,  # 1 EUR = 90.50 INR
            'GBP': 105.30, # 1 GBP = 105.30 INR
            'JPY': 0.56,   # 1 JPY = 0.56 INR
            'AUD': 54.75,  # 1 AUD = 54.75 INR
            'CAD': 61.20,  # 1 CAD = 61.20 INR
            'CHF': 93.80,  # 1 CHF = 93.80 INR
            'INR': 1.00,   # 1 INR = 1 INR
        }
        
        # API configuration
        self.api_url = "https://api.exchangerate-api.com/v4/latest/"
        self.timeout_seconds = 5
    
    
    def detect_currency(self, text: str, currency_field: Optional[Dict] = None) -> Tuple[Optional[str], str]:
        """
        Detect currency code from text or from extracted currency field.
        
        Args:
            text (str): Document text to search
            currency_field (dict, optional): Pre-extracted currency field from field_extractor
        
        Returns:
            Tuple[Optional[str], str]: (currency_code, explanation)
                - currency_code: 3-letter code (e.g., 'USD', 'INR') or None
                - explanation: Human-readable explanation of detection
        """
        
        if not text:
            return None, "Empty text provided"
        
        # Priority 1: Use pre-extracted currency field if available
        if currency_field and currency_field.get('currency'):
            code = currency_field['currency'].upper()
            if code in self.fallback_rates:
                return code, f"Currency from pre-extraction field: {code}"
        
        # Priority 2: Search text for currency patterns
        text_upper = text.upper()
        text_lower = text.lower()
        
        for currency_code, patterns in self.currency_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return currency_code, f"Detected by regex pattern: {currency_code}"
        
        # No currency detected
        return None, "No currency detected in text"
    
    
    def extract_amount(self, text: str) -> Tuple[Optional[float], str]:
        """
        Extract numerical amount from text.
        Recognizes various formats: 1000, 1,000, 1000.50, $1000, etc.
        
        Args:
            text (str): Text containing the amount
        
        Returns:
            Tuple[Optional[float], str]: (amount, explanation)
                - amount: Numerical value or None
                - explanation: How amount was extracted
        """
        
        if not text:
            return None, "Empty text provided"
        
        # Remove common currency symbols and text
        cleaned = re.sub(r'[\$€£¥₹]', '', text)
        cleaned = re.sub(r'\b(USD|EUR|GBP|JPY|AUD|CAD|CHF|INR|Dollars?|Rupees?|Euros?|Pounds?)\b', '', cleaned, flags=re.IGNORECASE)
        
        # Extract numbers with optional decimals, commas
        # Pattern matches: 1000, 1,000, 1000.50, 1,000.50 etc.
        amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)'
        
        matches = re.findall(amount_pattern, cleaned)
        
        if not matches:
            return None, "No numerical amount found"
        
        # Take the largest amount (usually the main financial value)
        amounts = []
        for match in matches:
            try:
                amount = float(match.replace(',', ''))
                if amount > 0:
                    amounts.append(amount)
            except ValueError:
                continue
        
        if amounts:
            largest = max(amounts)
            return largest, f"Extracted amount: {largest} (largest value found)"
        
        return None, "Could not parse extracted numbers"
    
    
    def fetch_exchange_rate(self, currency_code: str) -> Tuple[float, str, bool]:
        """
        Fetch real-time exchange rate from API.
        Falls back to hardcoded rates if API fails.
        
        Args:
            currency_code (str): 3-letter currency code (e.g., 'USD')
        
        Returns:
            Tuple[float, str, bool]: (rate, source, is_live)
                - rate: Exchange rate to INR
                - source: Description of rate source (API or fallback)
                - is_live: True if from API, False if fallback
        """
        
        if currency_code == 'INR':
            return 1.0, "INR (no conversion needed)", True
        
        if currency_code not in self.fallback_rates:
            fallback_rate = self.fallback_rates.get('USD', 83.25)
            return fallback_rate, f"Unknown currency {currency_code}, using fallback", False
        
        try:
            # Construct API URL
            url = f"{self.api_url}{currency_code}"
            
            # Create request with timeout
            request = urllib.request.Request(url)
            request.add_header('User-Agent', 'IntelligentDocumentAutomation/1.0')
            
            # Fetch data with timeout
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                # Extract INR rate
                if 'rates' in data and 'INR' in data['rates']:
                    rate = data['rates']['INR']
                    source = f"Live API (exchangerate-api.com) - {currency_code} to INR"
                    return rate, source, True
        
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, 
                timeout, Exception) as e:
            # API failed, use fallback
            logger.warning(f"Currency conversion API failed for {currency_code}: {str(e)}. Using fallback rate.")
            pass
        
        # Fallback to hardcoded rate
        fallback_rate = self.fallback_rates[currency_code]
        source = f"Fallback static rate (API unavailable) - {currency_code} to INR"
        return fallback_rate, source, False
    
    
    def convert_amount(self, amount: float, currency_code: str, rate: float) -> float:
        """
        Convert amount to INR using provided exchange rate.
        
        Args:
            amount (float): Original amount
            currency_code (str): Currency code
            rate (float): Exchange rate to INR
        
        Returns:
            float: Converted amount in INR
        """
        
        if currency_code == 'INR':
            return amount
        
        return round(amount * rate, 2)
    
    
    def process_document_currencies(self, doc_name: str, extracted_fields: Dict) -> Dict:
        """
        Process all currencies in a single document's extracted fields.
        
        Args:
            doc_name (str): Document name
            extracted_fields (dict): Fields extracted from field_extractor.py
        
        Returns:
            dict: Currency conversion results containing:
                - document_name
                - conversions: List of conversion details
                - timestamp
                - explanation: Human-readable summary
                - raw_results: Raw conversion data
        """
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversions = []
        explanations = []
        
        # Get currency field if available
        currency_field = extracted_fields.get('currency', {})
        
        # Get text source (from any field that might contain amount)
        text_sources = {}
        for field_name, field_data in extracted_fields.items():
            if isinstance(field_data, dict):
                # Extract any text that might contain amount
                for key, value in field_data.items():
                    if isinstance(value, str) and len(value) > 0:
                        text_sources[field_name] = value
        
        # Combine all text for detection
        combined_text = ' '.join(text_sources.values())
        
        # Detect currency
        currency_code, currency_explanation = self.detect_currency(combined_text, currency_field)
        
        if not currency_code:
            return {
                'document_name': doc_name,
                'conversions': [],
                'timestamp': timestamp,
                'explanation': "No currency detected in document. No conversion performed.",
                'raw_results': {
                    'currency_detected': False,
                    'currency_code': None
                }
            }
        
        explanations.append(f"Currency Detected: {currency_code}")
        explanations.append(currency_explanation)
        
        # If INR, no conversion needed
        if currency_code == 'INR':
            return {
                'document_name': doc_name,
                'conversions': [],
                'timestamp': timestamp,
                'explanation': "Currency detected as INR. No conversion required.",
                'raw_results': {
                    'currency_detected': True,
                    'currency_code': 'INR',
                    'requires_conversion': False
                }
            }
        
        # Extract amount
        amount, amount_explanation = self.extract_amount(combined_text)
        
        if not amount:
            return {
                'document_name': doc_name,
                'conversions': [],
                'timestamp': timestamp,
                'explanation': f"Currency {currency_code} detected but no amount found.",
                'raw_results': {
                    'currency_detected': True,
                    'currency_code': currency_code,
                    'amount_found': False
                }
            }
        
        explanations.append(amount_explanation)
        
        # Fetch exchange rate
        rate, rate_source, is_live = self.fetch_exchange_rate(currency_code)
        
        explanations.append(f"Exchange Rate Source: {rate_source}")
        explanations.append(f"Exchange Rate: 1 {currency_code} = {rate} INR")
        
        # Perform conversion
        converted_amount = self.convert_amount(amount, currency_code, rate)
        
        explanations.append(f"Conversion Calculation: {amount} × {rate} = {converted_amount} INR")
        
        # Store conversion result
        conversion_result = {
            'document_name': doc_name,
            'original_amount': amount,
            'original_currency': currency_code,
            'conversion_rate': rate,
            'converted_amount_inr': converted_amount,
            'rate_source': rate_source,
            'is_live_rate': is_live,
            'timestamp': timestamp
        }
        
        conversions.append(conversion_result)
        
        explanations.append(f"Final Converted Amount: {converted_amount:,.2f} INR")
        explanations.append(f"Timestamp: {timestamp}")
        
        return {
            'document_name': doc_name,
            'conversions': conversions,
            'timestamp': timestamp,
            'explanation': '\n'.join(explanations),
            'raw_results': {
                'currency_detected': True,
                'currency_code': currency_code,
                'amount_found': True,
                'amount': amount,
                'rate': rate,
                'is_live_rate': is_live,
                'converted_amount': converted_amount
            }
        }
    
    
    def process_all_documents(self, extracted_fields_by_doc: Dict[str, Dict]) -> Dict[str, Dict]:
        """
        Process currencies across all documents.
        
        Args:
            extracted_fields_by_doc (dict): Fields by document name from field_extractor
        
        Returns:
            dict: Conversion results for all documents with structure:
                {
                    'doc_name': {
                        'document_name': str,
                        'conversions': list,
                        'timestamp': str,
                        'explanation': str,
                        'raw_results': dict
                    }
                }
        """
        
        results = {}
        
        for doc_name, fields in extracted_fields_by_doc.items():
            results[doc_name] = self.process_document_currencies(doc_name, fields)
        
        return results


def normalize_currencies(extracted_fields_by_doc: Dict[str, Dict]) -> Dict[str, Dict]:
    """
    Convenience function to normalize currencies in all documents.
    
    Args:
        extracted_fields_by_doc (dict): Output from field_extractor module
    
    Returns:
        dict: Currency normalization results from CurrencyConverter
    """
    
    converter = CurrencyConverter()
    return converter.process_all_documents(extracted_fields_by_doc)


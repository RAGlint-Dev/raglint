"""
PII (Personally Identifiable Information) Detector Plugin.

Warns if RAG responses contain sensitive personal information.
"""
from typing import Dict, Any, List
import re
from raglint.plugins.interface import PluginInterface


class PIIDetectorPlugin(PluginInterface):
    """
    Detects PII in responses (emails, phone numbers, SSNs, etc.).
    """
    
    name = "pii_detector"
    version = "2.0.0"
    description = "Detects personally identifiable information in responses"
    
    def evaluate(self, query: str, context: list, response: str) -> float:
        """
        Real implementation: Detect PII in the response using regex patterns.
        
        Detects: emails, phone numbers, SSNs, credit cards, IP addresses.
        Returns 1.0 if no PII found, 0.0 if PII detected.
        """
        import re
        
        # PII patterns
        patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b(\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            'credit_card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            'ip_address': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
            'zip_code': r'\b\d{5}(-\d{4})?\b',
        }
        
        pii_found = {}
        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, response)
            if matches:
                pii_found[pii_type] = len(matches)
        
        if not pii_found:
            return 1.0  # No PII found - good
        
        # PII detected - score based on severity
        # Email/phone less severe than SSN/credit card
        severe_types = {'ssn', 'credit_card'}
        if any(pii_type in severe_types for pii_type in pii_found):
            return 0.0  # Critical PII found
        
        return 0.3  # Less severe PII found

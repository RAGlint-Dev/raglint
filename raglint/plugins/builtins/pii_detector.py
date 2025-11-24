"""
PII (Personally Identifiable Information) Detector Plugin.

Warns if RAG responses contain sensitive personal information.
"""

import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class PIIDetectorPlugin(PluginInterface):
    """
    Detects PII in responses (emails, phone numbers, SSNs, etc.).
    """

    name = "pii_detector"
    version = "2.0.0"
    description = "Detects personally identifiable information in responses"

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """
        Detect PII in the response using regex patterns.
        """
        # PII patterns
        patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "phone": r"\b(\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b",
            "ssn": r"\b\d{3}[-]?\d{2}[-]?\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            "zip_code": r"\b\d{5}(-\d{4})?\b",
        }

        pii_found = {}
        pii_types = []
        total_matches = 0
        
        for pii_type, pattern in patterns.items():
            matches = re.findall(pattern, response)
            if matches:
                count = len(matches)
                pii_found[pii_type] = count
                pii_types.append(pii_type)
                total_matches += count

        if not pii_found:
            return {
                "score": 1.0,
                "pii_found": False,
                "pii_count": 0,
                "pii_types": []
            }

        # PII detected - score based on severity
        # Email/phone less severe than SSN/credit card
        severe_types = {"ssn", "credit_card"}
        is_severe = any(pii_type in severe_types for pii_type in pii_found)
        
        score = 0.0 if is_severe else 0.3

        return {
            "score": score,
            "pii_found": True,
            "pii_count": total_matches,
            "pii_types": pii_types,
            "details": pii_found
        }

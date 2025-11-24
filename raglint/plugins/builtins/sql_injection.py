"""
SQL Injection Detector Plugin - Identifies potential SQL injection patterns.

Important for applications that might use RAG responses in database queries.
"""

import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class SQLInjectionDetectorPlugin(PluginInterface):
    """
    Detects potential SQL injection patterns in responses.

    Warning: This is heuristic-based. Always use parameterized queries!
    """

    name = "sql_injection_detector"
    version = "2.0.0"
    description = "Detects potential SQL injection patterns for security"

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Detect SQL injection patterns async."""
        from typing import Any

        score = self.evaluate(query, contexts, response)

        # Count patterns for reporting
        dangerous_patterns = [
            r"\bSELECT\b.*\bFROM\b",
            r"\bINSERT\s+INTO\b",
            r"\bDELETE\s+FROM\b",
            r"\bDROP\s+TABLE\b",
            r"\bUNION\s+SELECT\b",
        ]

        response_upper = response.upper()
        pattern_count = sum(
            1 for pattern in dangerous_patterns if re.search(pattern, response_upper, re.IGNORECASE)
        )

        return {
            "score": score,
            "sql_patterns_found": pattern_count > 0,
            "pattern_count": pattern_count,
            "risk_level": "critical" if score == 0.0 else "low" if score == 1.0 else "medium",
        }

    def evaluate(self, query: str, context: list, response: str) -> float:
        """
        Real implementation: Detect SQL injection patterns in response.

        Checks for dangerous SQL keywords and patterns that could indicate
        SQL injection vulnerabilities or leaked SQL code.

        Returns 1.0 if safe, 0.0 if injections detected.
        """

        # SQL injection patterns
        dangerous_patterns = [
            r"\bSELECT\b.*\bFROM\b",  # SELECT ... FROM
            r"\bINSERT\s+INTO\b",  # INSERT INTO
            r"\bDELETE\s+FROM\b",  # DELETE FROM
            r"\bDROP\s+TABLE\b",  # DROP TABLE
            r"\bUNION\s+SELECT\b",  # UNION SELECT
            r"\b--\s",  # SQL comments
            r";\s*DROP",  # ; DROP (Bobby Tables)
            r"'\s*OR\s*'1'\s*=\s*'1",  # ' OR '1'='1
            r"'\s*OR\s*1\s*=\s*1",  # ' OR 1=1
            r"\bEXEC\s*\(",  # EXEC(
            r"\bxp_cmdshell\b",  # xp_cmdshell
        ]

        # Check response for SQL injection patterns
        response_upper = response.upper()
        detected_patterns = []

        for pattern in dangerous_patterns:
            if re.search(pattern, response_upper, re.IGNORECASE):
                detected_patterns.append(pattern)

        if not detected_patterns:
            return 1.0  # No SQL injection patterns found

        # Calculate severity
        critical_patterns = ["DROP TABLE", "xp_cmdshell", "DELETE FROM"]
        has_critical = any(p in response_upper for p in critical_patterns)

        if has_critical:
            return 0.0  # Critical SQL injection attempt

        # Non-critical patterns (might be legitimate SQL discussion)
        return 0.5  # Suspicious but not critical

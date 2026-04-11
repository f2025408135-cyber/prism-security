"""Common Weakness Enumeration (CWE) mapping."""

import structlog

logger = structlog.get_logger(__name__)


class CWEMapper:
    """Maps vulnerability classifications to official CWE IDs."""

    def map_cwe(self, classification: str) -> str:
        """Return the most appropriate CWE ID for the classification.

        Args:
            classification: The vulnerability classification string.

        Returns:
            The CWE string (e.g., 'CWE-284').
        """
        logger.debug("mapping_cwe", classification=classification)
        
        class_upper = classification.upper()

        if "BOLA" in class_upper or "IDOR" in class_upper:
            # CWE-284: Improper Access Control
            # CWE-639: Authorization Bypass Through User-Controlled Key
            return "CWE-639"
            
        if "BFLA" in class_upper:
            # CWE-285: Improper Authorization
            return "CWE-285"
            
        if "RACE" in class_upper or "TOCTOU" in class_upper:
            # CWE-362: Concurrent Execution using Shared Resource with Improper Synchronization
            return "CWE-362"
            
        if "SCOPE" in class_upper:
            # CWE-200: Exposure of Sensitive Information to an Unauthorized Actor
            return "CWE-200"

        # Default fallback for access control issues
        return "CWE-284"

"""CVSS 3.1 Vector calculation."""

import structlog

logger = structlog.get_logger(__name__)


class CVSSCalculator:
    """Calculates CVSS 3.1 vectors based on finding heuristics."""

    def calculate_vector(self, finding_title: str, method: str = "GET") -> str:
        """Determine an appropriate CVSS vector for the vulnerability.

        Args:
            finding_title: The classification (e.g., BOLA_CANDIDATE).
            method: The HTTP method used in the exploit (determines Integrity/Availability impacts).

        Returns:
            A standard CVSS 3.1 vector string.
        """
        logger.debug("calculating_cvss", title=finding_title, method=method)

        # Baseline network attack, low complexity, no user interaction
        base_vector = "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U"
        
        # Confidentiality Impact
        confidentiality = "C:H" if "BOLA" in finding_title.upper() or "SCOPE" in finding_title.upper() else "C:N"
        
        # Integrity Impact (Destructive actions affect integrity)
        integrity = "I:H" if method.upper() in ("POST", "PUT", "PATCH", "DELETE") else "I:N"
        
        # Availability Impact (Deletes or Race Deadlocks affect availability)
        availability = "A:H" if method.upper() == "DELETE" or "RACE" in finding_title.upper() else "A:N"

        # If it's BFLA and they could POST/PUT, it's a huge integrity issue
        if "BFLA" in finding_title.upper() and method.upper() in ("POST", "PUT", "DELETE"):
            confidentiality = "C:H"
            integrity = "I:H"

        vector = f"{base_vector}/{confidentiality}/{integrity}/{availability}"
        
        logger.info("cvss_calculated", vector=vector)
        return vector

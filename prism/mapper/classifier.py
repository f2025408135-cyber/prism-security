"""Classification of authorization inconsistencies."""

import structlog
from pydantic import BaseModel, ConfigDict

from prism.mapper.inconsistency import AuthzInconsistency

logger = structlog.get_logger(__name__)

class ClassifiedInconsistency(BaseModel):
    """An inconsistency mapped to a vulnerability class.
    
    Attributes:
        inconsistency: The base inconsistency found.
        vuln_class: The classification (e.g., 'BOLA_CANDIDATE').
        confidence: Confidence score between 0.0 and 1.0.
    """
    model_config = ConfigDict(frozen=True)

    inconsistency: AuthzInconsistency
    vuln_class: str
    confidence: float


class InconsistencyClassifier:
    """Classifies raw AuthzInconsistencies into distinct vulnerability categories."""

    def classify(self, inconsistencies: tuple[AuthzInconsistency, ...]) -> tuple[ClassifiedInconsistency, ...]:
        """Classify a list of inconsistencies.

        Args:
            inconsistencies: The raw inconsistencies from the detector.

        Returns:
            A tuple of ClassifiedInconsistency models.
        """
        logger.info("classification_started", count=len(inconsistencies))
        results: list[ClassifiedInconsistency] = []

        for inc in inconsistencies:
            vuln_class = "UNKNOWN"
            confidence = 0.5
            
            reason = inc.reason.lower()
            acc_method = inc.accessible_endpoint.split(" ")[0].upper()
            denied_method = inc.denied_endpoint.split(" ")[0].upper()

            # BOLA (Broken Object Level Authorization)
            # Typically occurs when someone accesses an object directly (GET /obj/id) 
            # without having list/source rights.
            if "bola" in reason or "forbidden at source" in reason:
                vuln_class = "BOLA_CANDIDATE"
                confidence = 0.8
                if acc_method in ("PUT", "PATCH", "DELETE", "POST"):
                    # Destructive BOLA is higher confidence
                    confidence = 0.95

            # BFLA (Broken Function Level Authorization)
            # Typically happens when a user can read (GET) but inexplicably can also write (POST/DELETE)
            # Or is blocked from reading but allowed to write.
            elif acc_method in ("POST", "PUT", "DELETE") and denied_method == "GET":
                vuln_class = "BFLA_CANDIDATE"
                confidence = 0.85

            # SCOPE GAP
            # Usually when user has access to source collection but is blocked from specific items,
            # which might represent internal multi-tenant leaks (they can list it, but can't fetch it, meaning it leaked in list).
            elif "authorized at source" in reason:
                vuln_class = "SCOPE_GAP_CANDIDATE"
                confidence = 0.7

            results.append(
                ClassifiedInconsistency(
                    inconsistency=inc,
                    vuln_class=vuln_class,
                    confidence=confidence
                )
            )

        logger.info("classification_completed", classified=len(results))
        return tuple(results)

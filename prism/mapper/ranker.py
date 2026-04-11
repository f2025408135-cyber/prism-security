"""Ranking of classified inconsistencies by risk impact."""

import structlog

from prism.mapper.classifier import ClassifiedInconsistency

logger = structlog.get_logger(__name__)


class InconsistencyRanker:
    """Sorts classified inconsistencies by potential impact and confidence."""

    # Weights for different vulnerability classes
    CLASS_WEIGHTS = {
        "BOLA_CANDIDATE": 10.0,
        "BFLA_CANDIDATE": 9.0,
        "SCOPE_GAP_CANDIDATE": 6.0,
        "UNKNOWN": 3.0
    }

    # Weights for the HTTP method where access was allowed
    METHOD_WEIGHTS = {
        "DELETE": 10.0,
        "POST": 8.0,
        "PUT": 8.0,
        "PATCH": 8.0,
        "GET": 4.0,
        "HEAD": 2.0,
        "OPTIONS": 1.0
    }

    def rank(self, classified: tuple[ClassifiedInconsistency, ...]) -> tuple[ClassifiedInconsistency, ...]:
        """Rank classified inconsistencies from most critical to least.

        Args:
            classified: A tuple of classified inconsistencies.

        Returns:
            A tuple of the same inconsistencies, sorted by calculated severity score.
        """
        logger.info("ranking_started", count=len(classified))
        
        def calculate_score(item: ClassifiedInconsistency) -> float:
            base_score = self.CLASS_WEIGHTS.get(item.vuln_class, 3.0)
            
            # The method that the attacker *successfully* accessed gives the impact
            acc_method = item.inconsistency.accessible_endpoint.split(" ")[0].upper()
            method_multiplier = self.METHOD_WEIGHTS.get(acc_method, 3.0)
            
            raw_score = base_score * method_multiplier
            
            # Final score is weighted by the classifier's confidence
            return raw_score * item.confidence

        sorted_results = sorted(classified, key=calculate_score, reverse=True)
        
        logger.info("ranking_completed")
        return tuple(sorted_results)

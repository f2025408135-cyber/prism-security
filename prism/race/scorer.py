"""Scorer for race vulnerability probability."""

import structlog

logger = structlog.get_logger(__name__)


class RaceProbabilityScorer:
    """Scores an endpoint's likelihood of being vulnerable to a race condition.

    Heuristics:
    - Financial operations (pay, withdraw, buy): Extremely high probability
    - State transitions (activate, cancel): High probability
    - Single-use operations (redeem, claim): High probability
    - Read-only endpoints (GET): Zero probability
    """

    FINANCIAL_KEYWORDS = frozenset({"pay", "withdraw", "deposit", "transfer", "buy", "checkout", "redeem"})
    STATE_KEYWORDS = frozenset({"activate", "cancel", "suspend", "approve", "reject"})

    def score_endpoint(self, method: str, url: str, is_single_use: bool) -> float:
        """Calculate the race vulnerability score for a given endpoint.

        Args:
            method: The HTTP method.
            url: The endpoint URL.
            is_single_use: Whether the operation is known to be single-use.

        Returns:
            A float score from 0.0 (no risk) to 1.0 (highest risk).
        """
        logger.debug("scoring_endpoint_for_race", method=method, url=url)

        if method.upper() in ("GET", "HEAD", "OPTIONS"):
            return 0.0

        score = 0.1  # Baseline for any mutation

        url_lower = url.lower()

        # Check for financial keywords
        if any(kw in url_lower for kw in self.FINANCIAL_KEYWORDS):
            score += 0.6

        # Check for state transitions
        if any(kw in url_lower for kw in self.STATE_KEYWORDS):
            score += 0.4

        # Check for single-use (inherently a check-then-act)
        if is_single_use:
            score += 0.5

        # Cap score at 1.0
        final_score = min(score, 1.0)
        
        logger.debug("endpoint_scored", url=url, score=final_score)
        return final_score

"""Attacker agent implementation."""

import structlog

from prism.dialectic.models import DialecticModelRouter

logger = structlog.get_logger(__name__)


class AttackerAgent:
    """The adversarial agent motivated to prove a finding is a TRUE POSITIVE.

    Its goal is to find edge cases, misconfigurations, or combinations of HTTP
    behaviors in the evidence that confirm the vulnerability's impact.
    """

    SYSTEM_PROMPT = (
        "You are an elite offensive security researcher. Your goal is to prove "
        "that the provided vulnerability finding is a TRUE POSITIVE. Analyze the "
        "HTTP evidence, identify exploitation vectors, and counter the defender's arguments. "
        "If you concede the finding is invalid, state 'CONCEDE: FALSE POSITIVE'. "
        "Otherwise, argue for its validity."
    )

    def __init__(self, router: DialecticModelRouter):
        """Initialize the attacker.

        Args:
            router: The LLM routing engine.
        """
        self.router = router

    async def argue(self, evidence: str, debate_history: str) -> str:
        """Generate the next argument in the debate.

        Args:
            evidence: The raw HTTP evidence and finding details.
            debate_history: The transcript of previous rounds.

        Returns:
            The LLM's adversarial response.
        """
        context = f"EVIDENCE:\n{evidence}\n\nDEBATE HISTORY:\n{debate_history}"
        logger.debug("attacker_generating_argument")
        
        response = await self.router.get_attacker_response(self.SYSTEM_PROMPT, context)
        return response

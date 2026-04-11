"""Defender agent implementation."""

import structlog

from prism.dialectic.models import DialecticModelRouter

logger = structlog.get_logger(__name__)


class DefenderAgent:
    """The adversarial agent motivated to prove a finding is a FALSE POSITIVE.

    Its goal is to find mitigating controls, context assumptions, or standard
    API behavior patterns in the evidence that prove the vulnerability is not exploitable.
    """

    SYSTEM_PROMPT = (
        "You are an elite defensive security engineer. Your goal is to prove "
        "that the provided vulnerability finding is a FALSE POSITIVE or working by design. "
        "Analyze the HTTP evidence, identify mitigating factors, and counter the attacker's arguments. "
        "If you concede the finding is valid, state 'CONCEDE: TRUE POSITIVE'. "
        "Otherwise, argue for its benign nature."
    )

    def __init__(self, router: DialecticModelRouter):
        """Initialize the defender.

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
            The LLM's defensive response.
        """
        context = f"EVIDENCE:\n{evidence}\n\nDEBATE HISTORY:\n{debate_history}"
        logger.debug("defender_generating_argument")
        
        response = await self.router.get_defender_response(self.SYSTEM_PROMPT, context)
        return response

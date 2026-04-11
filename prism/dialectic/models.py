"""LiteLLM model routing and configurations."""

import structlog
from litellm import completion # type: ignore
from typing import Any

logger = structlog.get_logger(__name__)


class DialecticModelRouter:
    """Routes prompts to the appropriate LLM via LiteLLM.

    Allows the attacker and defender agents to utilize different models
    (e.g. GPT-4 for attacker, Claude 3 for defender) for robust debate.
    """

    def __init__(self, attacker_model: str = "gpt-3.5-turbo", defender_model: str = "gpt-3.5-turbo"):
        """Initialize the router.

        Args:
            attacker_model: LiteLLM compatible model string.
            defender_model: LiteLLM compatible model string.
        """
        self.attacker_model = attacker_model
        self.defender_model = defender_model

    async def get_attacker_response(self, system_prompt: str, context: str) -> str:
        """Route to the attacker model."""
        return await self._call_llm(self.attacker_model, system_prompt, context)

    async def get_defender_response(self, system_prompt: str, context: str) -> str:
        """Route to the defender model."""
        return await self._call_llm(self.defender_model, system_prompt, context)

    async def _call_llm(self, model: str, system: str, user: str) -> str:
        """Execute the async completion call."""
        logger.debug("llm_call_started", model=model)
        try:
            # LiteLLM abstract wrapper
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ]
            )
            # The type system of litellm is heavily generic, so we access attributes safely
            return str(response.choices[0].message.content) # type: ignore
        except Exception as e:
            logger.error("llm_call_failed", model=model, error=str(e))
            return f"ERROR: LLM failed to respond ({e})"

"""Round management and debate loop."""

import structlog
from pydantic import BaseModel, ConfigDict

from prism.dialectic.attacker import AttackerAgent
from prism.dialectic.defender import DefenderAgent

logger = structlog.get_logger(__name__)


class DebateTranscript(BaseModel):
    """Stores the complete record of an adversarial debate."""
    model_config = ConfigDict(frozen=True)

    finding_id: str
    rounds: tuple[dict[str, str], ...]
    final_verdict: str


class DebateManager:
    """Orchestrates the debate between Attacker and Defender."""

    MAX_ROUNDS = 5

    def __init__(self, attacker: AttackerAgent, defender: DefenderAgent):
        """Initialize the manager.

        Args:
            attacker: The offensive agent.
            defender: The defensive agent.
        """
        self.attacker = attacker
        self.defender = defender

    async def conduct_debate(self, finding_id: str, evidence: str) -> DebateTranscript:
        """Run the dialectic loop up to MAX_ROUNDS or until concession.

        Args:
            finding_id: The ID of the finding being debated.
            evidence: The raw evidence string.

        Returns:
            A frozen DebateTranscript containing the full dialogue and verdict.
        """
        logger.info("debate_started", finding_id=finding_id)
        
        history: list[str] = []
        rounds: list[dict[str, str]] = []
        final_verdict = "STALEMATE"

        for i in range(self.MAX_ROUNDS):
            history_text = "\n\n".join(history)
            
            # 1. Attacker turn
            att_resp = await self.attacker.argue(evidence, history_text)
            history.append(f"ATTACKER:\n{att_resp}")
            
            if "CONCEDE: FALSE POSITIVE" in att_resp:
                final_verdict = "DEFENDER_WINS_FALSE_POSITIVE"
                rounds.append({"attacker": att_resp, "defender": ""})
                logger.info("debate_concluded_attacker_concedes", round=i+1)
                break

            # 2. Defender turn
            history_text = "\n\n".join(history)
            def_resp = await self.defender.argue(evidence, history_text)
            history.append(f"DEFENDER:\n{def_resp}")
            
            rounds.append({"attacker": att_resp, "defender": def_resp})

            if "CONCEDE: TRUE POSITIVE" in def_resp:
                final_verdict = "ATTACKER_WINS_TRUE_POSITIVE"
                logger.info("debate_concluded_defender_concedes", round=i+1)
                break

        logger.info("debate_finished", finding_id=finding_id, verdict=final_verdict)
        
        return DebateTranscript(
            finding_id=finding_id,
            rounds=tuple(rounds),
            final_verdict=final_verdict
        )

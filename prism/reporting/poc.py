"""Automatic Proof of Concept (PoC) generation."""

import structlog

from prism.models.finding import PoC, Evidence

logger = structlog.get_logger(__name__)


class PoCGenerator:
    """Generates reproducible curl command chains for confirmed vulnerabilities."""

    def generate_poc(self, finding_title: str, evidence: tuple[Evidence, ...]) -> PoC | None:
        """Create a PoC object containing sequential steps to reproduce the attack.

        Args:
            finding_title: The title or category of the finding (e.g. BOLA_CANDIDATE).
            evidence: The tuple of HTTP evidence associated with the finding.

        Returns:
            A frozen PoC model, or None if insufficient evidence exists.
        """
        logger.info("generating_poc", title=finding_title, evidence_count=len(evidence))

        if not evidence:
            return None

        steps: list[str] = []

        if "BOLA" in finding_title.upper() or "BFLA" in finding_title.upper() or "SCOPE" in finding_title.upper():
            # Standard authorization bypass PoC chain
            # We assume the last piece of evidence is the actual successful bypass
            bypass_ev = evidence[-1]
            
            # For a true PoC we need to know the baseline (what should happen) vs the bypass (what did happen)
            # In this simplistic generator, we convert the evidence request excerpts into basic curl commands
            
            # Step A: The Attack
            req = bypass_ev.request_excerpt
            
            # Simple heuristic to extract METHOD and URL from something like "GET /api/users"
            parts = req.split(" ", 1)
            method = parts[0] if len(parts) > 0 else "GET"
            url = parts[1] if len(parts) > 1 else ""
            
            # (A real implementation would reconstruct headers from raw TrafficStorage)
            curl_cmd = f"curl -X {method} '{url}' -H 'Authorization: Bearer <ATTACKER_TOKEN>'"
            
            steps.append(f"Step A (Attack): Execute the following request using the attacker's context:\n{curl_cmd}")
            
            # Step B: Verification
            steps.append(f"Step B (Verify): Observe the response matches the unauthorized data:\n{bypass_ev.response_excerpt}")

        elif "RACE" in finding_title.upper():
            # Race condition PoC
            ev = evidence[0]
            req = ev.request_excerpt
            parts = req.split(" ", 1)
            method = parts[0] if len(parts) > 0 else "POST"
            url = parts[1] if len(parts) > 1 else ""
            
            curl_cmd = f"curl -X {method} '{url}' -H 'Authorization: Bearer <TOKEN>'"
            
            steps.append(f"Step A (Setup): Prepare {len(evidence)} concurrent terminal sessions.")
            steps.append(f"Step B (Attack): Execute the following command simultaneously in all sessions:\n{curl_cmd}")
            steps.append(f"Step C (Verify): Observe multiple 200 OK responses or state corruption.")
            
        else:
            # Generic fallback
            for i, ev in enumerate(evidence, 1):
                steps.append(f"Step {i}: Execute request -> {ev.request_excerpt}")

        logger.info("poc_generated", steps=len(steps))
        return PoC(steps=tuple(steps))

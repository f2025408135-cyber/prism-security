"""Vulnerability finding and evidence models."""

from pydantic import BaseModel, ConfigDict


class Evidence(BaseModel):
    """Represents raw evidence supporting a finding (e.g., HTTP request/response).

    Attributes:
        id: Unique identifier for the evidence.
        description: Context about what the evidence shows.
        request_excerpt: The HTTP request excerpt.
        response_excerpt: The HTTP response excerpt.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    request_excerpt: str
    response_excerpt: str


class PoC(BaseModel):
    """Represents a Proof of Concept chain to reproduce a finding.

    Attributes:
        steps: A tuple of curl commands or descriptions to execute the attack.
    """
    model_config = ConfigDict(frozen=True)

    steps: tuple[str, ...] = ()


class Finding(BaseModel):
    """Represents a confirmed vulnerability report.

    Attributes:
        id: Unique identifier for the finding.
        title: Short title of the vulnerability.
        description: Detailed explanation of the vulnerability.
        cwe_id: The Common Weakness Enumeration ID.
        cvss_vector: The CVSS 3.1 vector string.
        evidence: Tuple of evidence objects supporting the finding.
        poc: The Proof of Concept to reproduce it.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    description: str
    cwe_id: str
    cvss_vector: str
    evidence: tuple[Evidence, ...] = ()
    poc: PoC | None = None

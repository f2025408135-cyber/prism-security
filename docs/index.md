# PRISM Security Research Framework

Welcome to the **PRISM** documentation. PRISM is a production-grade, open-source Python security research framework designed for mapping API authorization topology, inferring business logic state machines, and automatically discovering complex vulnerabilities like BOLA/IDOR, BFLA, and Race Conditions.

## Why PRISM?

Traditional DAST (Dynamic Application Security Testing) tools fire payloads indiscriminately. They are noisy, they struggle with multi-tenant authorization contexts, and they cannot understand the underlying business logic of an application.

PRISM solves this by:
1. **Mapping** the exact authorization rules of every endpoint across multiple users concurrently.
2. **Inferring** the state machines (e.g. `CREATED` -> `ACTIVE` -> `DELETED`) by observing traffic.
3. **Graphing** the flow of object identifiers (UUIDs, integers) between endpoints.
4. **Debating** findings using an adversarial dual-LLM dialectic engine to virtually eliminate False Positives.

Navigate through this documentation to learn how to install, configure, and operate PRISM against your authorized bug bounty targets.

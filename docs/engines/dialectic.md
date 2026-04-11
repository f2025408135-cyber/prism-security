# Dialectic Engine

The Adversarial Dialectic Engine (`prism/dialectic/`) pits two Large Language Models against each other:

1. **Attacker Agent**: Motivated to prove the finding is exploitable.
2. **Defender Agent**: Motivated to prove the finding is benign or working as intended.

It routes evidence via `litellm` through up to 5 rounds of debate. If the Defender forces the Attacker to concede the finding is unexploitable, the finding is discarded with high confidence as a False Positive.

"""Authorization Matrix construction and aggregation."""

import structlog

from prism.models.authz import AuthzDecision, AuthzMatrix
from prism.mapper.prober import EndpointAuthzProfile

logger = structlog.get_logger(__name__)


class MatrixBuilder:
    """Aggregates individual endpoint profiles into a global AuthzMatrix."""

    def __init__(self) -> None:
        self.profiles: list[EndpointAuthzProfile] = []

    def add_profile(self, profile: EndpointAuthzProfile) -> None:
        """Add an endpoint's authorization profile to the matrix builder.

        Args:
            profile: The profile containing decisions for a single endpoint.
        """
        self.profiles.append(profile)
        logger.debug("profile_added_to_matrix", decisions_in_profile=len(profile))

    def build_matrix(self) -> AuthzMatrix:
        """Build the final AuthzMatrix from all added profiles.

        Returns:
            A frozen AuthzMatrix model containing all decisions.
        """
        all_decisions: list[AuthzDecision] = []
        for profile in self.profiles:
            all_decisions.extend(profile)

        matrix = AuthzMatrix(decisions=tuple(all_decisions))
        logger.info("authz_matrix_built", total_decisions=len(matrix.decisions))
        return matrix

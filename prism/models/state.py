"""State machine data models."""

from pydantic import BaseModel, ConfigDict


class State(BaseModel):
    """Represents a discrete state in a business logic state machine.

    Attributes:
        name: The name of the state (e.g., 'created', 'active', 'deleted').
        description: A human-readable description of what this state represents.
    """
    model_config = ConfigDict(frozen=True)

    name: str
    description: str = ""


class StateTransition(BaseModel):
    """Represents a valid transition between two states.

    Attributes:
        from_state: The name of the starting state.
        to_state: The name of the resulting state.
        endpoint_method: The HTTP method that triggered the transition.
        endpoint_url: The URL that triggered the transition.
    """
    model_config = ConfigDict(frozen=True)

    from_state: str
    to_state: str
    endpoint_method: str
    endpoint_url: str


class StateMachine(BaseModel):
    """Represents the inferred state machine for a resource lifecycle.

    Attributes:
        resource_name: The name of the resource (e.g., 'user', 'invoice').
        states: A tuple of all identified states.
        transitions: A tuple of all valid transitions between states.
    """
    model_config = ConfigDict(frozen=True)

    resource_name: str
    states: tuple[State, ...] = ()
    transitions: tuple[StateTransition, ...] = ()

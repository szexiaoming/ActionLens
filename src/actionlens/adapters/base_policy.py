"""Policy boundary for mock and future SmolVLA implementations."""

from __future__ import annotations

from typing import Protocol, Sequence

from .base_environment import Observation


class Policy(Protocol):
    """A model that converts one observation into an environment action."""

    @property
    def model_id(self) -> str:
        """Return the model identifier stored in every run record."""

    def reset(self) -> None:
        """Clear any per-episode policy state."""

    def predict(self, observation: Observation) -> Sequence[float]:
        """Predict one normalized action."""

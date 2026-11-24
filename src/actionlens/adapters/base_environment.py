"""Environment boundary used by both mock and future LIBERO implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence


@dataclass(frozen=True)
class Observation:
    """A policy-ready observation without a dependency on a simulator package."""

    state: Sequence[float]
    images: Mapping[str, Any]
    instruction: str


@dataclass(frozen=True)
class StepResult:
    """Normalized result returned after one environment step."""

    observation: Observation
    reward: float
    terminated: bool
    truncated: bool
    success: bool
    info: Mapping[str, Any]


class Environment(Protocol):
    """Minimal simulator contract required by the evaluation loop."""

    def reset(self, *, seed: int) -> Observation:
        """Reset the task and return the first observation."""

    def step(self, action: Sequence[float]) -> StepResult:
        """Apply one normalized action to the simulator."""

    def close(self) -> None:
        """Release simulator resources."""

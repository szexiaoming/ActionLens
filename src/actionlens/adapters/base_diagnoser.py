"""Visual diagnosis boundary for mock and future VLM implementations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, Sequence


@dataclass(frozen=True)
class Diagnosis:
    """Structured visual observations produced from selected frames."""

    target_visible: bool | None
    target_position: str | None
    task_stage: str
    suspected_failure_stage: str | None
    observations: Sequence[str]
    needs_human_review: bool


class Diagnoser(Protocol):
    """Analyze keyframes without deciding simulator success."""

    @property
    def model_id(self) -> str:
        """Return the visual model identifier."""

    def analyze(self, frame_paths: Sequence[Path], instruction: str) -> Diagnosis:
        """Return structured observations for the supplied frames."""

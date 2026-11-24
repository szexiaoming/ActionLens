"""Stable enum values shared by data generation and result processing."""

from enum import Enum


class DataSource(str, Enum):
    MOCK = "mock"
    REAL = "real"


class RunStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ERROR = "error"
    INTERRUPTED = "interrupted"


class FailureCategory(str, Enum):
    TARGET_RECOGNITION = "target_recognition"
    LOCALIZATION = "localization"
    GRASP = "grasp"
    PLACEMENT = "placement"
    CONTROL = "control"
    TERMINATION = "termination"
    PERTURBATION = "perturbation"
    SYSTEM_ERROR = "system_error"
    UNKNOWN = "unknown"

"""Generation, validation, and aggregation for ActionLens run records."""

from .mock_data import generate_mock_runs
from .models import DataSource, FailureCategory, RunStatus
from .importing import import_real_results
from .summary import build_summary
from .validation import ResultValidationError, validate_runs

__all__ = [
    "DataSource",
    "FailureCategory",
    "ResultValidationError",
    "RunStatus",
    "build_summary",
    "generate_mock_runs",
    "import_real_results",
    "validate_runs",
]

"""JSON Schema and semantic validation for evaluation results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource


class ResultValidationError(ValueError):
    """Raised when one or more run records violate the data contract."""


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _format_path(parts: Sequence[Any]) -> str:
    path = "$"
    for part in parts:
        if isinstance(part, int):
            path += f"[{part}]"
        else:
            path += f".{part}"
    return path


def _create_validator(schema_directory: Path) -> Draft202012Validator:
    run_schema = _load_json(schema_directory / "run.schema.json")
    diagnosis_schema = _load_json(schema_directory / "diagnosis.schema.json")
    registry = Registry().with_resources(
        [
            (run_schema["$id"], Resource.from_contents(run_schema)),
            (diagnosis_schema["$id"], Resource.from_contents(diagnosis_schema)),
        ]
    )
    return Draft202012Validator(
        run_schema,
        registry=registry,
        format_checker=FormatChecker(),
    )


def _semantic_errors(run: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    result = run["result"]
    status = result["status"]

    if result["success"] != (status == "success"):
        errors.append("$.result.success: must be true only when status is 'success'")

    if result["executedSteps"] > result["maxSteps"]:
        errors.append("$.result.executedSteps: cannot exceed maxSteps")

    condition = run["condition"]
    if condition["type"] == "normal" and condition["perturbation"] is not None:
        errors.append("$.condition.perturbation: must be null for the normal condition")
    if condition["type"] == "disturbed" and condition["perturbation"] is None:
        errors.append("$.condition.perturbation: is required for the disturbed condition")

    failure_category = run["humanReview"]["failureCategory"]
    if status == "success" and failure_category is not None:
        errors.append("$.humanReview.failureCategory: must be null for successful runs")
    if status != "success" and run["humanReview"]["reviewed"] and failure_category is None:
        errors.append("$.humanReview.failureCategory: is required for reviewed non-success runs")

    return errors


def validate_runs(runs: Sequence[Mapping[str, Any]], schema_directory: Path) -> None:
    """Validate a complete result set and raise one readable combined error."""

    if not isinstance(runs, list):
        raise ResultValidationError("$: expected an array of run records")

    validator = _create_validator(schema_directory)
    errors: list[str] = []
    run_ids: set[str] = set()

    for index, run in enumerate(runs):
        schema_errors = sorted(
            validator.iter_errors(run),
            key=lambda error: tuple(str(part) for part in error.absolute_path),
        )
        for error in schema_errors:
            errors.append(f"$[{index}]{_format_path(list(error.absolute_path))[1:]}: {error.message}")

        if schema_errors:
            continue

        for semantic_error in _semantic_errors(run):
            errors.append(f"$[{index}]{semantic_error[1:]}")

        run_id = run["runId"]
        if run_id in run_ids:
            errors.append(f"$[{index}].runId: duplicate value '{run_id}'")
        run_ids.add(run_id)

    if errors:
        raise ResultValidationError("\n".join(errors))


def load_and_validate_results(path: Path, schema_directory: Path) -> list[dict[str, Any]]:
    """Load one JSON array and validate it against the current contract."""

    runs = _load_json(path)
    validate_runs(runs, schema_directory)
    return runs

"""Import validated real evaluation records and their local media artifacts."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from typing import Any

from .mock_data import write_json
from .summary import build_summary
from .validation import ResultValidationError, validate_runs


ARTIFACT_NAMES = {
    "videoUrl": "video",
    "startFrameUrl": "start",
    "middleFrameUrl": "middle",
    "endFrameUrl": "end",
}


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _load_source(source: Path) -> tuple[list[tuple[dict[str, Any], Path]], Path]:
    source = source.resolve()
    if source.is_file():
        value = _load_json(source)
        records = value if isinstance(value, list) else [value]
        return [(record, source.parent) for record in records], source.parent

    if not source.is_dir():
        raise FileNotFoundError(f"Import source does not exist: {source}")

    runs_file = source / "runs.json"
    if runs_file.is_file():
        value = _load_json(runs_file)
        if not isinstance(value, list):
            raise ResultValidationError("runs.json must contain an array")
        return [(record, source) for record in value], source

    metadata_files = sorted(source.rglob("metadata.json"))
    if not metadata_files:
        raise FileNotFoundError("No runs.json or metadata.json files were found")
    return [(_load_json(path), path.parent) for path in metadata_files], source


def _resolve_artifact(raw_value: str, base: Path, source_root: Path) -> Path:
    candidate = Path(raw_value)
    if candidate.is_absolute() or "://" in raw_value or raw_value.startswith("/"):
        raise ResultValidationError(f"Artifact path must be relative: {raw_value}")
    resolved = (base / candidate).resolve()
    if not resolved.is_relative_to(source_root.resolve()):
        raise ResultValidationError(f"Artifact path leaves the import directory: {raw_value}")
    if not resolved.is_file():
        raise FileNotFoundError(f"Artifact file does not exist: {resolved}")
    return resolved


def import_real_results(
    source: Path,
    data_directory: Path,
    public_directory: Path,
    schema_directory: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Normalize real records, copy media, validate, and build frontend data."""

    loaded, source_root = _load_source(source)
    normalized: list[dict[str, Any]] = []
    pending_copies: list[tuple[Path, Path]] = []

    for raw_record, base in loaded:
        record = copy.deepcopy(raw_record)
        if not isinstance(record, dict):
            raise ResultValidationError("Every imported run must be a JSON object")
        if record.get("dataSource") != "real":
            raise ResultValidationError(
                f"{record.get('runId', '<unknown>')}: dataSource must be 'real'"
            )

        run_id = record.get("runId", "unknown")
        artifacts = record.get("artifacts", {})
        for field, output_stem in ARTIFACT_NAMES.items():
            raw_value = artifacts.get(field)
            if raw_value is None:
                continue
            source_file = _resolve_artifact(raw_value, base, source_root)
            destination = public_directory / "media" / run_id / f"{output_stem}{source_file.suffix.lower()}"
            pending_copies.append((source_file, destination))
            artifacts[field] = f"/media/{run_id}/{destination.name}"
        normalized.append(record)

    validate_runs(normalized, schema_directory)
    summary = build_summary(normalized)

    for source_file, destination in pending_copies:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, destination)

    write_json(data_directory / "runs.json", normalized)
    write_json(data_directory / "summary.json", summary)
    write_json(public_directory / "data" / "runs.json", normalized)
    write_json(public_directory / "data" / "summary.json", summary)
    write_json(
        public_directory / "data" / "manifest.json",
        {
            "schemaVersion": "1.0",
            "activeSource": "real",
            "runsPath": "/data/runs.json",
            "summaryPath": "/data/summary.json",
            "updatedAt": summary["generatedAt"],
        },
    )
    return normalized, summary

"""Deterministic aggregation of ActionLens run records."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any, Callable, Hashable, Mapping, Sequence


Run = Mapping[str, Any]


def _round(value: float) -> float:
    return round(value, 2)


def _group_summary(runs: Sequence[Run], key: Callable[[Run], Hashable]) -> list[dict[str, Any]]:
    groups: dict[Hashable, list[Run]] = {}
    for run in runs:
        groups.setdefault(key(run), []).append(run)

    items: list[dict[str, Any]] = []
    for group_key, group_runs in groups.items():
        success_count = sum(run["result"]["status"] == "success" for run in group_runs)
        item: dict[str, Any] = {
            "key": group_key,
            "totalRuns": len(group_runs),
            "successCount": success_count,
            "successRate": _round(success_count / len(group_runs)),
            "statusCounts": dict(
                sorted(Counter(run["result"]["status"] for run in group_runs).items())
            ),
        }
        if isinstance(group_key, tuple):
            item["key"] = list(group_key)
        items.append(item)

    return items


def build_summary(runs: Sequence[Run]) -> dict[str, Any]:
    """Build the frontend summary without merging errors into ordinary failures."""

    sources = {run["dataSource"] for run in runs}
    if len(sources) > 1:
        raise ValueError("A summary cannot mix mock and real run records")

    status_counts = Counter(run["result"]["status"] for run in runs)
    successful_runs = [run for run in runs if run["result"]["status"] == "success"]
    failure_categories = Counter(
        run["humanReview"]["failureCategory"]
        for run in runs
        if run["humanReview"]["failureCategory"] is not None
    )

    by_task = _group_summary(runs, lambda run: run["task"]["id"])
    task_names = {run["task"]["id"]: run["task"]["name"] for run in runs}
    for item in by_task:
        item["name"] = task_names[item["key"]]

    return {
        "schemaVersion": "1.0",
        "dataSource": next(iter(sources), "mock"),
        "generatedAt": max((run["createdAt"] for run in runs), default="2026-11-24T10:00:00Z"),
        "totalRuns": len(runs),
        "statusCounts": {
            status: status_counts.get(status, 0)
            for status in ("success", "failed", "error", "interrupted")
        },
        "success": {
            "count": len(successful_runs),
            "total": len(runs),
            "rate": _round(len(successful_runs) / len(runs)) if runs else 0,
        },
        "metrics": {
            "averageDurationSeconds": _round(
                mean(run["result"]["durationSeconds"] for run in runs)
            )
            if runs
            else 0,
            "averageSuccessfulSteps": _round(
                mean(run["result"]["executedSteps"] for run in successful_runs)
            )
            if successful_runs
            else 0,
        },
        "byTask": by_task,
        "byCondition": _group_summary(runs, lambda run: run["condition"]["type"]),
        "byTaskAndCondition": _group_summary(
            runs,
            lambda run: (run["task"]["id"], run["condition"]["type"]),
        ),
        "failureCategories": dict(sorted(failure_categories.items())),
        "dataQuality": {
            "withDiagnosis": sum(run["diagnosis"] is not None for run in runs),
            "needsHumanReview": sum(
                run["diagnosis"] is not None and run["diagnosis"]["needsHumanReview"]
                for run in runs
            ),
            "missingVideo": sum(run["artifacts"]["videoUrl"] is None for run in runs),
        },
    }

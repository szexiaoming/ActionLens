from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation import build_summary, generate_mock_runs, validate_runs  # noqa: E402
from actionlens.evaluation.mock_data import write_json  # noqa: E402


def main() -> None:
    runs = generate_mock_runs(PROJECT_ROOT / "configs")
    validate_runs(runs, PROJECT_ROOT / "schemas")
    summary = build_summary(runs)

    destinations = (
        PROJECT_ROOT / "data" / "mock",
        PROJECT_ROOT / "web" / "public" / "data",
    )
    for destination in destinations:
        write_json(destination / "runs.json", runs)
        write_json(destination / "summary.json", summary)
    write_json(
        PROJECT_ROOT / "web" / "public" / "data" / "manifest.json",
        {
            "schemaVersion": "1.0",
            "activeSource": "mock",
            "runsPath": "/data/runs.json",
            "summaryPath": "/data/summary.json",
            "updatedAt": summary["generatedAt"],
        },
    )

    print(
        "Generated 40 deterministic mock runs: "
        f"{summary['statusCounts']['success']} success, "
        f"{summary['statusCounts']['failed']} failed, "
        f"{summary['statusCounts']['error']} error, "
        f"{summary['statusCounts']['interrupted']} interrupted."
    )


if __name__ == "__main__":
    main()

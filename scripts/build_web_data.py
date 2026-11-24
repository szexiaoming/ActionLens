from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation import build_summary  # noqa: E402
from actionlens.evaluation.mock_data import write_json  # noqa: E402
from actionlens.evaluation.validation import load_and_validate_results  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Select ActionLens data for the React application.")
    parser.add_argument("--source", choices=("mock", "real"), default="mock")
    args = parser.parse_args()

    source = PROJECT_ROOT / "data" / args.source / "runs.json"
    destination = PROJECT_ROOT / "web" / "public" / "data"
    if not source.is_file():
        raise FileNotFoundError(f"No {args.source} result file exists at {source}")
    runs = load_and_validate_results(source, PROJECT_ROOT / "schemas")
    summary = build_summary(runs)
    write_json(destination / "runs.json", runs)
    write_json(destination / "summary.json", summary)
    write_json(
        destination / "manifest.json",
        {
            "schemaVersion": "1.0",
            "activeSource": args.source,
            "runsPath": "/data/runs.json",
            "summaryPath": "/data/summary.json",
            "updatedAt": summary["generatedAt"],
        },
    )
    print(f"Prepared {len(runs)} {args.source} records for the React application.")


if __name__ == "__main__":
    main()

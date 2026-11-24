from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation.validation import load_and_validate_results  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate ActionLens run records.")
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=PROJECT_ROOT / "data" / "mock" / "runs.json",
    )
    args = parser.parse_args()
    path = args.path.resolve()
    runs = load_and_validate_results(path, PROJECT_ROOT / "schemas")
    print(f"Validated {len(runs)} run records from {path}")


if __name__ == "__main__":
    main()

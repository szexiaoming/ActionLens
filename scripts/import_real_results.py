from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation import import_real_results  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import real ActionLens records and copy their media for the React application."
    )
    parser.add_argument("source", type=Path, help="A runs.json file or evaluation output directory")
    args = parser.parse_args()
    runs, summary = import_real_results(
        args.source,
        PROJECT_ROOT / "data" / "real",
        PROJECT_ROOT / "web" / "public",
        PROJECT_ROOT / "schemas",
    )
    print(
        f"Imported {len(runs)} real runs: "
        f"{summary['statusCounts']['success']} success, "
        f"{summary['statusCounts']['failed']} failed, "
        f"{summary['statusCounts']['error']} error, "
        f"{summary['statusCounts']['interrupted']} interrupted."
    )


if __name__ == "__main__":
    main()

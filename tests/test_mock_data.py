from __future__ import annotations

import copy
import sys
import unittest
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation import (  # noqa: E402
    ResultValidationError,
    build_summary,
    generate_mock_runs,
    validate_runs,
)


class MockDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runs = generate_mock_runs(PROJECT_ROOT / "configs")

    def test_generator_is_deterministic(self) -> None:
        regenerated = generate_mock_runs(PROJECT_ROOT / "configs")
        self.assertEqual(self.runs, regenerated)

    def test_generator_builds_complete_evaluation_matrix(self) -> None:
        self.assertEqual(len(self.runs), 40)
        self.assertEqual(len({run["runId"] for run in self.runs}), 40)

        matrix = Counter((run["task"]["id"], run["condition"]["type"]) for run in self.runs)
        self.assertEqual(set(matrix.values()), {10})
        self.assertEqual(len(matrix), 4)

    def test_status_distribution_is_fixed(self) -> None:
        counts = Counter(run["result"]["status"] for run in self.runs)
        self.assertEqual(
            counts,
            {"success": 24, "failed": 13, "error": 2, "interrupted": 1},
        )

    def test_records_cover_edge_cases(self) -> None:
        categories = {
            run["humanReview"]["failureCategory"]
            for run in self.runs
            if run["humanReview"]["failureCategory"] is not None
        }
        self.assertGreaterEqual(len(categories), 8)
        self.assertTrue(any(run["diagnosis"] is None for run in self.runs))
        self.assertTrue(all(run["artifacts"]["videoUrl"] is None for run in self.runs))

    def test_generated_records_pass_schema_validation(self) -> None:
        validate_runs(self.runs, PROJECT_ROOT / "schemas")

    def test_invalid_status_reports_the_exact_field(self) -> None:
        invalid_runs = copy.deepcopy(self.runs)
        invalid_runs[0]["result"]["status"] = "unknown-status"

        with self.assertRaisesRegex(
            ResultValidationError,
            r"\$\[0\]\.result\.status",
        ):
            validate_runs(invalid_runs, PROJECT_ROOT / "schemas")

    def test_summary_keeps_failures_and_errors_separate(self) -> None:
        summary = build_summary(self.runs)
        self.assertEqual(summary["totalRuns"], 40)
        self.assertEqual(summary["success"], {"count": 24, "total": 40, "rate": 0.6})
        self.assertEqual(summary["statusCounts"]["failed"], 13)
        self.assertEqual(summary["statusCounts"]["error"], 2)
        self.assertEqual(sum(item["totalRuns"] for item in summary["byTask"]), 40)


if __name__ == "__main__":
    unittest.main()

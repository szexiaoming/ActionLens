from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from actionlens.evaluation import DataSource, RunStatus  # noqa: E402


class ProjectStructureTests(unittest.TestCase):
    def test_configuration_files_are_valid_json(self) -> None:
        for relative_path in ("configs/tasks.json", "configs/evaluation.json"):
            with (PROJECT_ROOT / relative_path).open(encoding="utf-8") as file:
                value = json.load(file)
            self.assertEqual(value["schemaVersion"], "1.0")

    def test_schema_files_are_valid_json(self) -> None:
        for schema_path in (PROJECT_ROOT / "schemas").glob("*.schema.json"):
            with schema_path.open(encoding="utf-8") as file:
                schema = json.load(file)
            self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")

    def test_evaluation_matrix_contains_40_runs(self) -> None:
        with (PROJECT_ROOT / "configs/tasks.json").open(encoding="utf-8") as file:
            tasks = json.load(file)["tasks"]
        with (PROJECT_ROOT / "configs/evaluation.json").open(encoding="utf-8") as file:
            evaluation = json.load(file)

        total_runs = len(tasks) * len(evaluation["conditions"]) * evaluation["episodesPerCondition"]
        self.assertEqual(total_runs, 40)

    def test_shared_enum_values_are_stable(self) -> None:
        self.assertEqual(DataSource.MOCK.value, "mock")
        self.assertEqual(RunStatus.SUCCESS.value, "success")


if __name__ == "__main__":
    unittest.main()

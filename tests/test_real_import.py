from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from actionlens.evaluation import ResultValidationError, generate_mock_runs, import_real_results  # noqa: E402


class RealResultImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.source = self.root / "incoming"
        self.episode = self.source / "real-run-0001"
        self.episode.mkdir(parents=True)

        self.record = copy.deepcopy(generate_mock_runs(PROJECT_ROOT / "configs")[0])
        self.record["runId"] = "real-run-0001"
        self.record["dataSource"] = "real"
        self.record["models"]["policy"] = "lerobot/smolvla_libero"
        self.record["artifacts"] = {
            "videoUrl": "episode.mp4",
            "startFrameUrl": "frames/start.png",
            "middleFrameUrl": None,
            "endFrameUrl": None,
        }
        (self.episode / "frames").mkdir()
        (self.episode / "episode.mp4").write_bytes(b"mock-video")
        (self.episode / "frames" / "start.png").write_bytes(b"mock-image")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def _write_metadata(self, record: dict) -> None:
        with (self.episode / "metadata.json").open("w", encoding="utf-8") as file:
            json.dump(record, file, ensure_ascii=False)

    def test_imports_records_and_copies_media(self) -> None:
        self._write_metadata(self.record)
        data_directory = self.root / "data" / "real"
        public_directory = self.root / "public"

        runs, summary = import_real_results(
            self.source,
            data_directory,
            public_directory,
            PROJECT_ROOT / "schemas",
        )

        self.assertEqual(len(runs), 1)
        self.assertEqual(summary["dataSource"], "real")
        self.assertEqual(runs[0]["artifacts"]["videoUrl"], "/media/real-run-0001/video.mp4")
        self.assertEqual(runs[0]["artifacts"]["startFrameUrl"], "/media/real-run-0001/start.png")
        self.assertEqual(
            (public_directory / "media" / "real-run-0001" / "video.mp4").read_bytes(),
            b"mock-video",
        )
        with (public_directory / "data" / "manifest.json").open(encoding="utf-8") as file:
            manifest = json.load(file)
        self.assertEqual(manifest["activeSource"], "real")

    def test_rejects_artifact_paths_outside_import_directory(self) -> None:
        invalid = copy.deepcopy(self.record)
        invalid["artifacts"]["videoUrl"] = "../../outside.mp4"
        self._write_metadata(invalid)

        with self.assertRaisesRegex(ResultValidationError, "leaves the import directory"):
            import_real_results(
                self.source,
                self.root / "data" / "real",
                self.root / "public",
                PROJECT_ROOT / "schemas",
            )

    def test_rejects_records_not_marked_as_real(self) -> None:
        invalid = copy.deepcopy(self.record)
        invalid["dataSource"] = "mock"
        self._write_metadata(invalid)

        with self.assertRaisesRegex(ResultValidationError, "dataSource must be 'real'"):
            import_real_results(
                self.source,
                self.root / "data" / "real",
                self.root / "public",
                PROJECT_ROOT / "schemas",
            )


if __name__ == "__main__":
    unittest.main()

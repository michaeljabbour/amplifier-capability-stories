"""Real filesystem boundaries for development replay output; no model calls."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stories_evaluate", ROOT / "scripts/evaluate_dev.py")
evaluator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluator)


class EvaluationOutputTests(unittest.TestCase):
    def test_existing_directory_and_record_are_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary).resolve() / "existing"
            folder.mkdir()
            record = folder / "RESULT.json"
            record.write_bytes(b"frozen evidence")
            with self.assertRaises(FileExistsError):
                evaluator.new_report_directory(folder)
            self.assertEqual(record.read_bytes(), b"frozen evidence")

    def test_symlinked_parent_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            real = base / "real"
            real.mkdir()
            link = base / "link"
            link.symlink_to(real, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"):
                evaluator.new_report_directory(link / "new")
            self.assertFalse((real / "new").exists())

    def test_distinct_new_directories_remain_independent(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            first = evaluator.new_report_directory(base / "first")
            (first / "RESULT.json").write_bytes(b"first replay")
            second = evaluator.new_report_directory(base / "second")
            self.assertNotEqual(first, second)
            self.assertEqual((first / "RESULT.json").read_bytes(), b"first replay")
            self.assertEqual(list(second.iterdir()), [])

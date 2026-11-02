import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/stories/scripts/check.py"
spec = importlib.util.spec_from_file_location("stories_check", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class StructuralBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.pack = json.loads((ROOT / "evals/dev/repair-club.json").read_text())
        self.ledger = json.loads((ROOT / "evals/dev/final/claims.json").read_text())
        self.tmp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.folder = Path(self.tmp.name).resolve()
        for name in ["case-study.md", "adaptation.md", "review.md"]:
            (self.folder / name).write_bytes((ROOT / "evals/dev/final" / name).read_bytes())

    def tearDown(self):
        self.tmp.cleanup()

    def run_output(self):
        return checker.output(self.ledger, self.pack, checker.packet(self.pack), self.folder)

    def test_valid_supplied_contract(self):
        self.assertEqual(self.run_output()["status"], "pass")

    def test_unknown_source_rejected(self):
        self.pack["requested_claims"][0]["source_ids"] = ["S404"]
        with self.assertRaisesRegex(ValueError, "Unknown source"):
            checker.packet(self.pack)

    def test_source_withheld_for_output_rejected(self):
        self.ledger["claims"][0]["source_ids"] = ["S5"]
        with self.assertRaisesRegex(ValueError, "not approved"):
            self.run_output()

    def test_unsupported_claim_cannot_be_used(self):
        self.ledger["claims"][0]["status"] = "unsupported"
        with self.assertRaisesRegex(ValueError, "unsupported claim"):
            self.run_output()

    def test_used_claim_needs_source(self):
        self.ledger["claims"][0]["source_ids"] = []
        with self.assertRaisesRegex(ValueError, "lacks a source"):
            self.run_output()

    def test_undeclared_reference_rejected(self):
        with (self.folder / "adaptation.md").open("a") as f:
            f.write("\n[C404]\n")
        with self.assertRaisesRegex(ValueError, "references differ"):
            self.run_output()

    def test_missing_reference_rejected(self):
        p = self.folder / "case-study.md"
        p.write_text(p.read_text().replace("[C2]", ""))
        with self.assertRaisesRegex(ValueError, "references differ"):
            self.run_output()

    def test_duplicate_claim_id_rejected(self):
        self.ledger["claims"].append(copy.deepcopy(self.ledger["claims"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate claim"):
            self.run_output()

    def test_changed_audience_rejected(self):
        self.ledger["adaptation_audience"] = "community"
        with self.assertRaisesRegex(ValueError, "audience differs"):
            self.run_output()

    def test_cancellation_rejects_draft_review(self):
        self.pack["stop"] = True
        with self.assertRaisesRegex(ValueError, "Cancelled"):
            self.run_output()

    def test_cancelled_cli_is_readonly_and_reports_cancelled(self):
        self.pack["stop"] = True
        p = self.folder / "input.json"
        p.write_text(json.dumps(self.pack))
        before = {x.name: x.read_bytes() for x in self.folder.iterdir()}
        result = subprocess.run([sys.executable, str(SCRIPT), "packet", "--input", str(p)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "cancelled")
        self.assertEqual(before, {x.name: x.read_bytes() for x in self.folder.iterdir()})

    def test_source_locator_is_not_traversed(self):
        self.pack["sources"][0]["locator"] = "file:///nonexistent/private/location; $(not-a-command)"
        self.assertIn("S1", checker.packet(self.pack))

    def test_symlink_refused(self):
        link = self.folder / "link.json"
        link.symlink_to(ROOT / "evals/dev/repair-club.json")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            checker.load(link)

    def test_malformed_json_refused(self):
        p = self.folder / "input.json"
        p.write_text("{")
        with self.assertRaises(ValueError):
            checker.load(p)

    def test_duplicate_json_keys_refused(self):
        p = self.folder / "input.json"
        p.write_text('{"stop":true,"stop":false}')
        with self.assertRaisesRegex(ValueError, "Duplicate JSON key"):
            checker.load(p)

    def test_size_bound_refused(self):
        p = self.folder / "huge.json"
        p.write_bytes(b" " * (checker.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "exceeds"):
            checker.load(p)

    def test_checker_does_not_claim_semantic_entailment(self):
        self.ledger["claims"][0]["text"] = "This deliberately unrelated claim still has a structurally valid source ID."
        result = self.run_output()
        self.assertEqual(result["scope"], "structural-only")
        self.assertTrue(result["semantic_review_required"])

    def test_claim_free_maintenance_is_preserved_and_disclosed(self):
        for name in checker.DRAFTS:
            self.ledger["used_claim_ids"][name] = []
            (self.folder / name).write_text("Maintenance note: more evidence is needed before a project account.\n")
        result = self.run_output()
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["referenced_claims_per_draft"], {name: 0 for name in checker.DRAFTS})
        self.assertEqual(len(result["warnings"]), 2)
        self.assertTrue(result["semantic_review_required"])

    def test_coverage_is_reported_separately_for_each_draft(self):
        self.ledger["used_claim_ids"]["adaptation.md"] = []
        (self.folder / "adaptation.md").write_text("Adaptation withheld pending author review.\n")
        result = self.run_output()
        self.assertGreater(result["referenced_claims_per_draft"]["case-study.md"], 0)
        self.assertEqual(result["referenced_claims_per_draft"]["adaptation.md"], 0)
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("adaptation.md", result["warnings"][0])


if __name__ == "__main__":
    unittest.main()

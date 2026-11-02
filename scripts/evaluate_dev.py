#!/usr/bin/env python3
"""Offline development diagnostics; does not execute an LLM or upstream workflow."""
import argparse
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "skills/stories/scripts/check.py"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def new_report_directory(output=None):
    """Use a fresh selected directory; never rewrite a historical result."""
    if output is None:
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        output = ROOT / ".eval-output" / stamp
    output = Path(output).absolute()
    if any(path.is_symlink() for path in [output, *output.parents]):
        raise ValueError("Report output may not use a symlink")
    output.mkdir(parents=True, exist_ok=False)
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New output directory; existing paths are refused")
    args = parser.parse_args(argv)
    try:
        report_dir = new_report_directory(args.output)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    spec = importlib.util.spec_from_file_location("stories_check", CHECKER)
    check = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(check)
    pack = check.load(ROOT / "evals/dev/repair-club.json")
    sources = check.packet(pack)
    folder = ROOT / "evals/dev/final"
    ledger = check.load(folder / "claims.json")
    checks = []
    try:
        checks.append({"id": "draft-ledger-source-contract", **check.output(ledger, pack, sources, folder)})
    except (ValueError, OSError) as error:
        checks.append({"id": "draft-ledger-source-contract", "status": "fail", "error": str(error)})
    drafts = [(folder / name).read_text() for name in check.DRAFTS]
    checks.append({"id": "fictional-private-marker-excluded", "status": "pass" if all("PRIVATE_FIXTURE_NAME" not in x and "ada@example.invalid" not in x for x in drafts) else "fail", "scope": "literal planted marker only; not a general privacy guarantee"})
    usage = ledger["used_claim_ids"]
    checks.append({"id": "same-core-claim-ids-across-adaptation", "status": "pass" if set(usage[check.DRAFTS[0]]) == set(usage[check.DRAFTS[1]]) else "fail", "scope": "selected fixture continuity, not semantic equivalence"})
    claim_map = {x["id"]: x for x in ledger["claims"]}
    checks.append({"id": "unsupported-roi-excluded-from-usage", "status": "pass" if claim_map["C4"]["status"] == "unsupported" and all("C4" not in ids for ids in usage.values()) else "fail"})
    checks.append({"id": "proposed-next-check-not-an-outcome", "status": "pass" if claim_map["C5"]["status"] == "proposed" and all("[C5]" in x and "proposed" in x for x in drafts) else "fail", "scope": "fixture labels and literal text; human reading still required"})
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT, capture_output=True, text=True)
    (report_dir / "final-boundary-tests.log").write_text(result.stdout + result.stderr)
    checks.append({"id": "read-only-checker-boundaries", "status": "pass" if result.returncode == 0 else "fail", "returncode": result.returncode, "log": "final-boundary-tests.log"})
    report = {"schema_version": "stories-development-result/v1", "at": datetime.datetime.now(datetime.timezone.utc).isoformat(), "status": "pass" if all(x["status"] == "pass" for x in checks) else "fail", "checks": checks, "source_hashes": {str(p.relative_to(ROOT)): digest(p) for p in [CHECKER, ROOT / "skills/stories/SKILL.md", ROOT / "evals/dev/repair-club.json", folder / "claims.json", folder / "case-study.md", folder / "adaptation.md"]}, "baseline": {"output": "evals/baseline/repair-club-output.md", "diagnostic": "Evidence/privacy constraints were already respected; no demonstrated semantic improvement", "same_agent": True}, "final_authoring": {"output": "evals/dev/final", "execution": "Normal authoring-agent application of the packaged method; no external provider experiment", "independent_or_blind": False}, "hill_climb": {"initial_boundary_tests": "16 passed, 1 failed duplicate-key rejection", "correction": "Reject duplicate JSON object keys so ambiguity cannot change a stop/approval value", "iterations": 1, "regression_result": "See exact final boundary log"}, "held_out": "not read or run by this package author; parent-controlled", "L1_blind_different_family": "not measured", "L3_outside_user": "not measured", "external_provider_calls": 0, "new_dependencies": [], "new_service_cost_usd": 0}
    (report_dir / "RESULT.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "development_checks": len(checks), "report": str(report_dir / "RESULT.json")}, indent=2))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

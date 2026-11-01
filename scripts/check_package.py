#!/usr/bin/env python3
"""Validate local package structure, references and metadata; optionally build its guide."""
import argparse
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def check():
    manifest = json.loads((ROOT / "capability.json").read_text())
    required = ("contract_version", "id", "name", "legacy_names", "version", "kind", "engine", "engine_components", "promise", "surfaces", "portable_method", "interfaces", "permissions", "dataflow", "source_policy")
    assert all(x in manifest for x in required)
    assert manifest["contract_version"] == "amplifier-capability/v1"
    assert manifest["name"] == "amplifier-capability-stories"
    assert manifest["kind"] == "skill" and manifest["engine"] == "LLM"
    assert manifest["surfaces"] == ["agent-skills"]
    assert len(list(ROOT.rglob("SKILL.md"))) == 1
    skill = ROOT / manifest["portable_method"]["path"]
    assert (skill / "LICENSE").read_bytes() == (ROOT / "LICENSE").read_bytes()
    assert "name: stories\n" in (skill / "SKILL.md").read_text()
    project = json.loads((ROOT / "project.json").read_text())
    assert all(project[key] == manifest[key] for key in ("name", "version", "kind", "engine", "surfaces"))
    for name in ("input", "output"):
        schema = json.loads((skill / "references" / (name + ".schema.json")).read_text())
        assert schema["$schema"].endswith("2020-12/schema")
    for path in ROOT.rglob("*.md"):
        if ".research" in path.parts:
            continue
        if "baseline" in path.parts:
            continue  # Frozen upstream references describe the old bundle, not this package.
        for target in re.findall(r"\]\(([^)\s]+)\)", path.read_text()):
            if target.startswith(("http:", "https:", "#", "mailto:")):
                continue
            assert (path.parent / target.split("#")[0]).exists(), (path, target)
    assert ".research/" in (ROOT / ".gitignore").read_text()
    return {"status": "pass", "scope": "package-structure-and-local-links", "canonical_skill_entries": 1}


def build():
    (ROOT / "site").mkdir(exist_ok=True)
    svg = (ROOT / "skills/stories/assets/workflow.svg").read_text()
    body = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:"><title>Stories guide</title><style>body{font:17px/1.6 system-ui,sans-serif;color:#233d4b;background:#f0f5f5;margin:0}main{max-width:1040px;margin:auto;padding:clamp(20px,5vw,64px)}h1{font-size:clamp(40px,7vw,72px);line-height:1.1}p{max-width:760px}svg{width:100%;height:auto}a{color:#216e67}section{background:white;padding:24px;border-radius:16px;margin:24px 0}code{overflow-wrap:anywhere}</style><main><p>MIT · 0.1.0</p><h1>Stories</h1><p>Turn selected evidence about documented project work into one sourced case study and one audience adaptation with a shared claim map.</p>'''
    body += svg
    body += '''<section><h2>One account, adapted carefully</h2><p>Choose explicit evidence, audiences and visibility. Keep supported, proposed and unsupported claims separate. Draft the case study, adapt it once, and review the same facts and limits in both.</p><p>Outputs: <code>case-study.md</code>, <code>adaptation.md</code>, <code>claims.json</code> and <code>review.md</code>.</p></section><section><h2>A method, not a publishing service</h2><p>No session mining, automatic research, document renderer, model loop or distribution route is included. The read-only checker validates structure; it does not establish narrative quality or source truth.</p></section><section><h2>Evidence and verification limits</h2><p>The frozen original-method development sample already respected the fixture’s evidence limits. Packaging and checker results do not establish better writing. Held-out behavior, independent-family comparison and outside-user outcomes remain separately assessed.</p><p><a href="../README.md">Read the guide</a> · <a href="../docs/BENCHMARK.md">Benchmark protocol</a> · <a href="../docs/RIGHT-SHAPE.md">Right Shape</a> · <a href="../skills/stories/SKILL.md">Portable method</a></p></section></main></html>'''
    (ROOT / "site/index.html").write_text(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    result = check()
    if args.build:
        build()
        result["guide"] = "site/index.html"
    print(json.dumps(result, sort_keys=True))

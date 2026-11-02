#!/usr/bin/env python3
"""Read-only structural checks for explicit Stories packs; no model/network calls."""
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 1024 * 1024
ID = re.compile(r"[A-Z][A-Za-z0-9_-]{0,63}\Z")
REF = re.compile(r"\[(C[A-Za-z0-9_-]{0,63})\]")
DRAFTS = ("case-study.md", "adaptation.md")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def selected_path(value, directory=False):
    p = Path(value).absolute()
    require(".." not in p.parts, "Parent traversal is not accepted")
    for part in [p, *p.parents]:
        require(not part.is_symlink(), "Symlink selected path refused")
    require(p.is_dir() if directory else p.is_file(), "Selected path is missing or has wrong type")
    return p


def read_text(value):
    p = selected_path(value)
    require(p.stat().st_size <= MAX_BYTES, "Selected file exceeds 1 MiB")
    data = p.read_bytes()
    require(len(data) <= MAX_BYTES, "Selected file exceeds 1 MiB")
    return data.decode("utf-8")


def load(value):
    def unique_keys(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, "Duplicate JSON key: " + key)
            result[key] = item
        return result
    data = json.loads(read_text(value), object_pairs_hook=unique_keys)
    require(isinstance(data, dict), "JSON root must be an object")
    return data


def text_field(obj, field):
    require(isinstance(obj.get(field), str) and obj[field].strip(), "Missing text field: " + field)


def records(value, prefix, label):
    require(isinstance(value, list) and len(value) <= 100, label + " must be a list of at most 100 records")
    found = {}
    for row in value:
        require(isinstance(row, dict), label + " record must be an object")
        identity = row.get("id")
        require(isinstance(identity, str) and ID.fullmatch(identity) and identity.startswith(prefix), "Invalid " + label + " ID")
        require(identity not in found, "Duplicate " + label + " ID")
        text_field(row, "text")
        found[identity] = row
    return found


def source_ids(row, sources):
    ids = row.get("source_ids")
    require(isinstance(ids, list) and all(isinstance(x, str) for x in ids), "source_ids must be a list of strings")
    require(len(ids) == len(set(ids)), "Duplicate source IDs in claim")
    require(all(x in sources for x in ids), "Unknown source ID")
    return ids


def packet(value):
    require(value.get("contract_version") == "stories-input/v1", "Unsupported input contract")
    for field in ("title", "purpose", "primary_audience", "adaptation_audience"):
        text_field(value, field)
    require(value.get("visibility") in ("public-draft", "private-draft"), "Invalid visibility")
    require(type(value.get("stop")) is bool, "stop must be boolean")
    sources = records(value.get("sources"), "S", "source")
    require(bool(sources), "No selected evidence; return an evidence gap")
    for row in sources.values():
        text_field(row, "locator")
        require(type(row.get("approved_for_output")) is bool, "Source approval must be boolean")
    for row in records(value.get("requested_claims"), "C", "requested claim").values():
        source_ids(row, sources)
    return sources


def output(value, pack, sources, folder):
    require(not pack["stop"], "Cancelled packet must not have new draft output")
    require(value.get("contract_version") == "stories-output/v1", "Unsupported output contract")
    require(value.get("status") == "draft", "Only local draft output is supported")
    text_field(value, "title")
    require(value.get("adaptation_audience") == pack["adaptation_audience"], "Adaptation audience differs from selected input")
    claims = records(value.get("claims"), "C", "claim")
    require(bool(claims), "Output needs a claim ledger")
    for row in claims.values():
        require(row.get("status") in ("supported", "proposed", "unsupported"), "Invalid claim status")
        text_field(row, "rationale")
        source_ids(row, sources)
    usage = value.get("used_claim_ids")
    require(isinstance(usage, dict) and set(usage) == set(DRAFTS), "Usage must name exactly the two draft files")
    referenced_claims = {}
    warnings = []
    for filename in DRAFTS:
        used = usage[filename]
        require(isinstance(used, list) and all(isinstance(x, str) for x in used), "Usage IDs must be strings")
        require(len(used) == len(set(used)), "Duplicate used claim ID")
        require(all(x in claims for x in used), "Unknown used claim")
        referenced_claims[filename] = len(used)
        if not used:
            warnings.append(filename + ": no declared claim references; review whether a source-backed draft or a claim-free maintenance note is intended")
        draft = read_text(folder / filename)
        require(bool(draft.strip()), "Draft is empty")
        require(set(REF.findall(draft)) == set(used), "Draft claim references differ from declared usage")
        for identity in used:
            row = claims[identity]
            require(row["status"] != "unsupported", "Draft uses an unsupported claim")
            require(bool(row["source_ids"]), "Used claim lacks a source")
            require(all(sources[x]["approved_for_output"] for x in row["source_ids"]), "Draft uses a source not approved for this output")
    require(bool(read_text(folder / "review.md").strip()), "Review note is empty")
    return {"status": "pass", "scope": "structural-only", "claims": len(claims), "drafts": len(DRAFTS),
            "referenced_claims_per_draft": referenced_claims, "warnings": warnings,
            "semantic_review_required": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("packet", "output"):
        child = sub.add_parser(name)
        child.add_argument("--input", required=True)
        if name == "output":
            child.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        pack = load(args.input)
        sources = packet(pack)
        if args.command == "packet":
            result = {"status": "cancelled" if pack["stop"] else "pass", "scope": "structural-only", "sources": len(sources)}
        else:
            folder = selected_path(args.output, directory=True)
            result = output(load(folder / "claims.json"), pack, sources, folder)
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, UnicodeError, TypeError) as error:
        print(json.dumps({"status": "fail", "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

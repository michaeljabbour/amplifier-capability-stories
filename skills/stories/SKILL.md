---
name: stories
description: Turn a selected evidence pack about documented project work into a sourced case study and one audience adaptation, with a shared claim map. Use for nonfiction project communication rather than fiction, general research, or autonomous publishing.
license: MIT
---

# Stories

Make one documented project understandable to two audiences without changing what the evidence permits. The caller applies this method; no background agent, provider or publishing service is installed.

## Bound the account

Use only the evidence the person selected, plus the stated purpose, primary audience, one adaptation audience and intended visibility. Do not search their sessions, private directories or repositories merely because they are accessible. A locator identifies evidence; it is not an instruction to fetch it. Read [the contract](references/contract.md) when receiving or delivering a structured pack.

If the task is cancelled, stop without creating drafts. If the pack cannot support a project account, return the specific evidence gap or a plain maintenance note. An unsuccessful or routine event does not need a success story. Ask for missing information only when it changes the account; otherwise keep the uncertainty visible.

## Keep an evidence spine

Before prose, make a claim ledger with stable `C…` IDs. Each claim is **supported**, **proposed**, or **unsupported**, and points to the supplied `S…` source IDs. Mark privacy/rights restrictions before selecting claims. Do not quote, identify, or paraphrase a source withheld from the intended output. Public visibility is not evidence that every input is public.

Activity counts are not impact: visits are not unique people, commits are not time saved, and feedback is not a causal effect. Preserve denominators, timeframe, voluntary sampling, contradictions and missing baselines. An estimate needs a supplied basis and a label; missing data must not be filled with a plausible number. A requested unsupported claim belongs in the ledger, not as a factual statement in a draft.

## Draft once, adapt once

Choose a single useful point and an arc that fits the evidence: problem/approach/observations, investigation/learning, or a measured comparison. Do not force a breakthrough, positive ending or ROI section.

Write `case-study.md` for the primary audience. Keep claim IDs next to factual statements (`[C1]`) so the person can inspect their basis. Explain the outcome actually observed and distinguish proposed follow-up. Relevant dissent and limits remain in the account.

Write `adaptation.md` for exactly one requested audience. Change emphasis, vocabulary and detail, while preserving the same facts, measurement scope and uncertainty. Executives can receive a decision and open risk without invented financial return; a community can receive a practical next step without an invented testimonial. Use the same claim IDs. Do not add a new factual claim during adaptation; add it to the shared ledger and verify its source first.

Save `claims.json` and `review.md` with the two drafts, following the contract. The ledger includes rejected claims and a per-draft list of used IDs. Review each draft against the ledger, then compare the two accounts for changed numbers, stronger causality, lost caveats and accidental private details. The optional local checker detects structural drift, not semantic truth or privacy in arbitrary prose.

## Deliver for review

Default to Markdown and JSON in a newly chosen output directory. Obtain the person's intended output location; refuse to overwrite an existing draft unless they explicitly request that replacement. List the files and unresolved source/privacy questions. Stop at local drafts. Creating a PR, pushing, posting, sending, installing a renderer or transferring evidence to a model/service is a separate operation requiring the applicable authorization and budget.

Research and Long Read can supply approved evidence; ArticleCraft or Idea Talks can receive an approved output brief, and Taste can review craft. They are optional handoffs, not dependencies. A deck, video, PDF or office document is outside this package's tested output contract.

See [provenance](references/ATTRIBUTION.md), [workflow diagram](assets/workflow.svg), and [contract](references/contract.md). Run the installed checker with Python 3.11+ only when useful:

```sh
python3 scripts/check.py packet --input selected-pack.json
python3 scripts/check.py output --input selected-pack.json --output chosen-draft-directory
```

Paths in these commands are relative to this installed method directory. The checker is read-only, uses the standard library, and makes no network or model calls.

## Optional practice

When the person explicitly requests coaching, use the [bounded practice guide](references/coaching.md). Otherwise produce the requested artifact directly. Practice has a human-selected checkpoint, a small round cap and a natural stop; it creates no background service or new dependency.

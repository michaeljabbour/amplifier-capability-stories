# Stories working instructions

Keep one promise: a sourced nonfiction project case study plus one audience adaptation, using the same claim map. The distributed package is MIT licensed. Repository publication is an owner action; installation or evaluation never authorizes posting the supplied project evidence.

## Local market research

At session start check `.research/market/last_updated`. If missing, seed the local store from this package's cited primary provenance and record retrieval dates. If older than 30 days, or before positioning, launch or naming work, refresh it from cited primary sources (URL plus retrieval date). Log changes in `.research/market/CHANGELOG.md`. The directory is gitignored; never commit it, and never put private research or source corpora into public examples. A metadata refresh is not comparative effectiveness evidence.

## Development and evaluation

Use `make check` for the package and read-only checker. Keep baseline freezes and raw failures. Development fixtures may guide changes; parent-controlled held-out examples may not. Do not tune a failed held-out result or relabel it as a development case. Match claims in public docs to dated scoped results. L0 conformance is separate from L1 blinded behavior and L3 outside-user outcomes.

Keep all generic runtime resources inside `skills/stories/`. There is exactly one canonical SKILL.md. Root contracts and docs link to the canonical resources rather than keeping divergent schema copies. Use the existing shared installer; no new dependency installs or credentials.

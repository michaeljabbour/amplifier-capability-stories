# Stories input and output contract v1

The machine-readable shapes are [input.schema.json](input.schema.json) and [output.schema.json](output.schema.json). The read-only checker implements the package's bounded validation rules without needing a JSON Schema library.

## Selected input

`stories-input/v1` has a title, purpose, primary audience, one adaptation audience, visibility (`public-draft` or `private-draft`), a boolean stop flag, and explicit source records. Each source has a unique `S…` ID, a locator, text, and `approved_for_output`. That approval refers to this output/visibility; it does not authorize posting, broad research, or sending to an external provider.

The caller supplies `requested_claims` as candidate `C…` records, each with text and source IDs; the method may add claims to its output ledger after source review. A source locator remains inert text. Empty evidence or cancelled work produces a gap/cancellation response instead of prose files. The checker accepts at most 1 MiB of JSON per file, 100 sources, 100 requested claims and 100 output claims; larger work must be deliberately divided.

## Reviewable output

Choose an explicit new directory. The method produces:

- `case-study.md`: primary-audience account with `[C…]` references.
- `adaptation.md`: exactly one named audience adaptation, using the same ledger.
- `claims.json`: `stories-output/v1`, `status: draft`, `title`, `adaptation_audience`, and `claims` containing unique IDs, text, status (`supported`, `proposed`, `unsupported`), source IDs and rationale. `used_claim_ids` maps each draft filename to its used IDs.
- `review.md`: evidence gaps, contradictory findings, privacy/rights decisions, structural-check result when run, and the person's remaining review.

Supported and proposed claims used by a draft must cite at least one supplied source approved for that output. A proposal's source supports that it was proposed, not that it happened. Unsupported claims may remain in the ledger with no source, but neither draft may reference them. An unused supported claim may be omitted for focus. Every declared used ID must occur in its draft, and every bracketed claim reference must be declared for that draft. The checker verifies this membership, source eligibility, audience consistency and known-file bounds. It cannot establish entailment, spot every factual claim without an ID, classify arbitrary prose, guarantee absence of sensitive text, or evaluate narrative quality.

The checker reports `referenced_claims_per_draft` and warns when a draft declares no references. Claim-free maintenance notes remain structurally valid; the warning asks the reviewer to distinguish those notes from an untraced project account. A structural `pass`, a nonzero count or an empty warning list never establishes complete factual coverage. `semantic_review_required` remains true for every successful output check. These additive report fields do not change the draft exchange or the checker's read-only behavior.

## Failure and stop

Invalid input is reported before output review. Missing evidence, incompatible visibility or irreconcilable accounts need an explicit gap, not fabricated content. `stop: true` yields cancellation and no new drafts. The checker never creates, deletes, changes or publishes files; write safety is a caller obligation. It rejects symlinked selected files/directories and malformed/oversized inputs rather than following them. It reads only the selected pack and the four named files in the selected directory, never a source locator.

Installation copies method files and does not grant runtime permissions. No native model loop, bundle namespace, shell interpolation, renderer, account, credential or standing network access is required by this contract.

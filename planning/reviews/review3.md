My reviewer left this File: planning/reviews/review3.md

Title: forcen review 3 — stateless rebuilds landed; verification and next steps

Date: 2025-10-06

Executive summary

Good news: the agent’s changes land the core architectural promise from the spec: stateless builds. Raw data now lives in observations_raw.csv and DSL is serialized per transaction; every lint/submit/build reassembles the full dataset (assemble_dataset) and rewrites all derived artifacts. Growth validation runs on true tree identities, SPLIT reassigns past/future consistently, PRIMARY timelines propagate to implied/future rows, and the stale survey_meta config + old assembler were removed.
This aligns very closely with the spec. The main focus now should be on validating retroactive correctness, determinism of artifacts (especially Parquet), and closing remaining CLI and validator gaps.
What looks correct and on-spec

Stateless pipeline:
Storage: raw measurements only + DSL per transaction. Derived artifacts are rewritten on lint/submit/build. Good.
Lint previews: can pull cumulative raw + cumulative DSL via --workspace for realistic “as-of” previews. Good.
Assembly completeness in assemble_dataset:
Alias resolution “as-of” with deterministic tree_uid assignment (uuid5 by tag) and back-dated ALIAS supported across history.
UPDATE timelines for genus/species/code/site/plot applied as-of to all rows.
PRIMARY timelines applied to all rows including implied ones; public_tag computed per date.
SPLIT selectors reassign matching historical rows and future rows (forward) deterministically; idempotency claimed. Good.
Implied-dead insertion/removal computed on full tree histories, not per-tx subsets. Good.
Validation
Growth validator now per tree_uid (max dbh per tree per survey) with the configured percent thresholds and absolute floors. Good.
Manifests and artifacts
Full rewrite of observations_long.{csv,parquet}, trees_view.csv, retag_suggestions.csv, updates_log.tdl, validation_report.json on submit/build; checksums in manifests; row-count logging by origin; DSL command counts per tx. Good.
Hygiene
Old survey_meta config removed from planning fixtures; assembler cleanup. Good.
Things to double-check or tighten

Parquet determinism:
Parquet can embed non-deterministic metadata (e.g., created_by). Ensure writer options are deterministic or rely on CSV for checksums in manifests. If Parquet checksums vary across runs/pyarrow versions, keep checksums for CSV authoritative and list Parquet without checksum (or normalize metadata).
DSL serialization fidelity:
Ensure the concatenated updates_log.tdl exactly appends the original per-tx bytes (including newline at EOF) so tx_id hashes remain meaningful and audits are exact. Avoid reformatting or TOML/AST round-trips of DSL text.
If you also store per-tx DSL files (e.g., updates/<tx_id>.tdl), ensure manifest references them (optional).
Idempotency of SPLIT:
Confirm re-running assemble_dataset does not continue to “move” rows after the first application. Unit test: apply the same SPLIT twice; resulting assembled outputs identical.
UPDATE field constraints:
Enforce code == upper(genus[:3] + species[:3]) after UPDATE; reject mismatched UPDATEs or auto-correct with a clear warning. Add tests.
For UPDATE that moves site/plot, confirm this does not implicitly retag historical rows; tag-to-tree binding is governed by ALIAS only, which is correct per spec.
Implied-dead semantics:
Verify edge cases: multiple disjoint ≥2-survey gaps; ensure implied is inserted at the first missing survey of each gap and removed on rediscovery. Add tests for two gaps in one history.
Confirm implied rows never count for datasheet inclusion (when you add datasheets).
Retag suggestions:
Deduplicate suggestions when multiple “new” candidates are within threshold for a single “lost” tree; prefer the closest dbh, then earliest public_tag numeric. Add tests.
Make sure suggestions don’t reference tags already aliased as-of the target survey (avoid suggesting work already done).
Lint with and without workspace:
If --workspace is omitted, lint should use only tx rows + tx DSL; if provided, it should merge cumulative raw + cumulative DSL. Document the behavior and add tests for both.
Deterministic ordering:
Reconfirm stable sort keys before writing all artifacts. For observations_long: (survey_id, site, plot, public_tag, date, dbh desc, obs_id) or your chosen canonical order; for trees_view: (survey_id, site, plot, public_tag); for retag_suggestions: (survey_id, plot, new_public_tag).
Error surfaces:
Back-dated ALIAS/UPDATE that produce conflicting PRIMARY or alias overlaps across cumulative DSL should fail closed with precise line locations (tx file + line number). Validate by parsing cumulative updates_log + new tx.
Gaps to close (high impact, quick wins)

Trees index (optional but useful):
Write trees_index.jsonl entries when a tree_uid first appears (tree_uid, first_seen_tx, site/plot/tag at that time). Not needed for assembly but good for audit/provenance.
Growth validator details:
Ensure NA handling is clear: skip comparisons when either side is NA; no issue emitted. Already looks that way; add explicit tests.
Manifest enrichment:
Include sizes (bytes) for artifacts; include list of DSL files (or command counts per type) in the manifest for quick auditing.
CLI coverage:
versions show/diff
tx new (scaffold)
datasheets generate (scaffold)
ai prepare (scaffold)
Recommended tests to add now

Retroactive ALIAS end-to-end:
tx1 introduces tag A; tx2 introduces tag B later; tx3 adds back-dated ALIAS B→A at a date before B appeared. After submit tx3, assembled observations_long should have a single tree_uid across all rows for A and B as-of their dates; trees_view reflects PRIMARY as-of.
Retroactive UPDATE and SPLIT:
UPDATE species/code back-dated to before some rows; assembled outputs show corrected species/code for all affected rows.
SPLIT with SELECT RANKS 2,3 BETWEEN dates moves only those rows; re-running assemble_dataset yields identical outputs (idempotency).
Multiple implied gaps:
Build a history with appearances at t0 and t5 and nothing in between with drop_after=2; implied rows at first missing surveys t1 and t? only when gaps meet rule; rediscovery at t5 removes earlier implieds as required.
Retag suggestions robustness:
Cases with two new candidates within 10% for one lost tree; ensure de-duplication and closest-dbh wins.
New tree below 60 mm threshold does not create a suggestion.
Parquet checksum stability:
If you keep Parquet checksums in manifest, assert identical across two identical runs on same platform. If flaky, drop Parquet checksum from manifest and keep CSV checksums authoritative.
Housekeeping

Remove planning/fixtures/configs/survey_meta.toml (it’s not a global config).
Add a tiny root README pointing to planning/ and the CLI.
Best-effort code_version: read git describe or HEAD; fall back to "unknown".
Next-step roadmap (target order)

Tests for retroactive correctness and SPLIT idempotency (as above).
Deterministic artifact ordering and Parquet checksum policy.
CLI additions: versions show/diff; tx new; datasheets generate (context-only); ai prepare (stub).
Trees index (optional) and manifest enrichment (artifact sizes, DSL per-tx list).
Documentation updates: planning/spec.md update to reflect finalized behaviors (especially lint --workspace semantics and Parquet checksum policy).
Acceptance criteria for the next PR

Retroactive ALIAS/UPDATE/SPLIT change prior rows in assembled outputs; rebuild after deleting artifacts reproduces identical outputs.
Growth validator operates per tree_uid; tests cover NA and threshold floors.
Parquet checksum policy decided and deterministic; manifests stable across two runs.
versions show/diff works; tx new scaffolds; datasheets generate outputs context JSON.
Lint with and without workspace behaves as documented; tests cover both.
Overall assessment

The agent delivered the critical architectural pivot and most of the tricky per-tree logic. With the verification items and small feature gaps closed, you’ll have the exact pipeline you envisioned: stateless, deterministic, auditable, and ready for datasheets + AI scaffolds.
File: planning/handbook/backlog.md

Title: forcen backlog (prioritized with acceptance criteria)

High priority (ship next)

CLI: versions show/diff
Why: Inspect specific manifests; compare versions.
Implement:
forcen versions show <seq> → print manifest.json for that version to stdout.
forcen versions diff <seqA> <seqB> → show differences in:
tx_ids (added/removed)
artifact_checksums (CSV authoritative; Parquet informational)
artifact_sizes
row_counts (by origin)
validation_summary
Acceptance:
Unit tests on a synthetic workspace with two versions; verify JSON structure and key diffs.
Exit 0 on success; 4 if version not found.
2. CLI: tx new (scaffold)

Why: Faster onboarding for field/ops.
Implement:
forcen tx new --out DIR → creates:
measurements.csv header only
updates.tdl empty file
No survey_meta by default (single source of truth is config/surveys.toml).
Acceptance:
Creates files with correct headers; re-running should fail with exit 4 unless --force is added.
3. Datasheets scaffold (context only)

Why: Datasheet generation is core but template-dependent.
Implement:
forcen datasheets generate --survey <id> --site <site> --plot <plot> --out DIR
Build context JSON using assembled observations (include DHS1/DHS2 strings, zombie marker, “tags used” list).
No Typst invocation required; write JSON per plot.
Acceptance:
Unit/golden test on fixtures: JSON contains expected keys and respects inclusion rules (seen in S-1 or S-2; implied rows don’t count for presence).
Sorting by numeric public_tag asc; stems display-ranked by dbh desc.
4. Manifest/output polish (determinism and policy)

Why: Ensure stable CI and documentation parity.
Implement:
CSV checksums authoritative, Parquet checksums informational; document and keep current behavior.
Ensure explicit stable sort keys are used before writing all artifacts (observations_long, trees_view, retag_suggestions).
Acceptance:
Golden tests: assemble twice; CSV checksums match. Parquet checksum either matches or is ignored in diff tests.
Explicit sort keys verified by reading back and asserting ordering on keys.
5. Validators/enforcement

UPDATE constraints:
Enforce code == upper(genus[:3]+species[:3]) for UPDATE assignments; reject mismatched assignment with clear error pointing at updates.tdl line number.
Tag concurrency guard (cumulative):
After loading cumulative DSL (ledger + tx), detect overlapping bindings at the same instant for a tag (additional safety net beyond same-date checks).
Acceptance:
Negative tests that submit lint reports E_UPDATE_CODE_MISMATCH with updates.tdl:line N.
Negative tests that a back-dated ALIAS causing overlap over an interval triggers E_ALIAS_OVERLAP_CUMULATIVE (line reference for tx file).
6. Retag suggestions finalization

Why: Reduce noise; align with spec.
Implement:
Deduplicate suggestions per lost tree: choose closest dbh; tie-break by earliest numeric public_tag.
Skip suggestions where lost and new already resolve to the same tree_uid or share public_tag as-of target survey.
Acceptance:
Unit tests: two new candidates; only the closest remains. Pre-aliased case produces no suggestion.
Medium priority

7. Trees index (optional, audit trail)

Implement:
trees_index.jsonl: append on first appearance of a new tree_uid (tree_uid, first_seen_tx, site, plot, tag, date).
Use assembled rows to determine first_seen (by date, real rows only).
Acceptance:
Unit test: after two submits creating two tree_uids, index contains two entries with first_seen_tx equal to their source tx_ids.
8. Parquet checksum policy in code

Implement:
Keep Parquet checksums in manifest but mark them informational in docs and review tools; versions diff should not fail on Parquet mismatch (warn only).
Acceptance:
versions diff test: if only Parquet checksum changes, diff shows warning section; overall exit remains 0.
9. Documentation polish

Update planning/spec.md sections to include:
Lint --workspace semantics.
CSV checksum policy vs Parquet.
Deterministic sort keys for artifacts.
Acceptance:
Docs updated; cross-links from handbook.
Test additions (targeted)

A) Retroactive ALIAS/UPDATE/SPLIT E2E

Add tx-3-retro with back-dated ALIAS and UPDATE:
After submit tx3, reassemble and assert prior rows’ tree_uid/properties reflect retro changes.
Acceptance: tests/test_retroactive.py asserts pass (similar to existing but broader).
B) Multiple implied gaps

Synthetic config with 5 consecutive surveys; data at t0 and t4 only.
drop_after=2 → implied at t1 only; rediscovery at t4 removes earlier implied.
Acceptance: assemble_dataset produces exactly one implied at t1; none after adding a t3 row.
C) Growth NA handling

Adjacent surveys where one side dbh is NA; ensure no warn/error.
Acceptance: validators emit no growth issues.
D) Lint behavior with/without workspace

Same tx; lint with and without --workspace; verify tree_view/retag_suggestions differences are expected and documented.
Acceptance: unit tests compare report payloads.
Low priority / nice-to-haves

versions diff pretty-print table mode.
code_version from git HEAD where available (fallback to “unknown”).
Datasheet template integration (Typst subprocess) behind a flag.
Done definition for backlog

All high-priority items implemented with unit/golden tests.
Docs updated (spec.md + handbook).
CI can run lint/submit/build on fixtures; versions show/diff passes; datasheets generate produces context JSON.
Patch: planning/spec.md (additions/update)

Add this under “9. CLI contract” after tx lint:

Lint with --workspace:
When provided, lint merges the current ledger’s cumulative raw observations and DSL with the transaction prior to assembly, producing a preview that reflects history “as-of” now plus the tx. Without --workspace, lint previews the tx in isolation. Both modes set default EFFECTIVE dates for commands if omitted.
Add this under “10. Outputs and manifest”:

Checksum policy:
CSV checksums in manifests are authoritative for determinism and CI. Parquet checksums are provided for convenience and may vary across platforms or pyarrow versions. Tools should consider Parquet checksum differences as warnings, not failures.
Add this at the end of “8. Assembly (per-tree algorithm; pure and deterministic)”:

Deterministic ordering:
Before writing artifacts, rows are sorted by explicit keys:
observations_long: (survey_id, site, plot, tag, obs_id)
trees_view: (survey_id, site, plot, public_tag)
retag_suggestions: (survey_id, plot, new_public_tag)
Add this in “5. Transactions” (Survey metadata note):

Survey metadata:
The single source of truth for survey windows is the configuration (surveys.toml). Transactions should not include survey metadata by default. Only include a survey_meta file in a transaction when introducing a new survey ad-hoc; otherwise update surveys.toml via a configuration change.
File: planning/reviews/review4.md

Title: forcen review 4 — new-agent documentation and remaining work

Date: 2025-10-07

What’s new since review 3

Documentation to reset context for a new agent:
planning/handbook/orientation.md — brief intro, invariants, current status, glossary.
planning/handbook/dev-quickstart.md — local run instructions, commands, determinism checks, troubleshooting.
planning/handbook/architecture.md — components map, data flow, key invariants, behaviors.
planning/handbook/cli-reference.md — concise command guide with exit codes and behavior notes.
planning/handbook/backlog.md — prioritized backlog with acceptance criteria and test notes.
Spec patch prepared:
Lint --workspace semantics recorded.
CSV checksums authoritative; Parquet informational.
Deterministic sort keys documented.
Survey metadata policy clarified (surveys.toml is source of truth; tx-level survey_meta only for ad-hoc new surveys).
Current state (brief)

Stateless rebuild architecture is implemented and tested.
Cumulative DSL is serialized per-transaction and applied across history at assemble time.
Growth validation runs per tree_uid; SPLIT is idempotent; implied-dead logic is history-aware.
CLI supports tx lint/submit, build, versions list. Manifests include checksums and sizes; validation reports are persisted.
Remaining work (from backlog, high priority first)

CLI additions:
versions show/diff (manifest inspection and differences).
tx new (scaffold measurements.csv and updates.tdl only).
datasheets generate (context-only; no Typst invocation).
Validators/enforcement:
UPDATE assignment constraints (code must equal upper(gen[:3]+spp[:3])).
Cumulative tag concurrency guard (detect overlapping bindings at the same instant).
Retag suggestions:
Finalize dedupe/tie-break; skip pre-aliased cases consistently with unit tests.
Determinism/outputs:
Confirm explicit sort keys before writes (observations_long, trees_view, retag_suggestions).
Keep CSV checksums authoritative; Parquet checksum differences treated as warnings in diff tooling.
Optional audit:
trees_index.jsonl recording first appearances of tree_uids (tree_uid, first_seen_tx, site/plot/tag, date).
Acceptance criteria to close this phase

End-to-end:
Submit tx-1, tx-2; build; versions show/diff produce expected JSON and stable results; re-running build yields identical CSV checksums.
Retroactivity and idempotency:
New retroactive fixture shows ALIAS/UPDATE/SPLIT alter prior rows in assembled outputs; running assemble twice yields identical outputs.
Validators:
UPDATE mismatch produces an error with updates.tdl line reference.
Cumulative alias overlap across intervals is reported and prevents submit.
Retag:
When two new candidates are within delta, only the closest is suggested; pre-aliased cases suggest nothing.
Datasheets:
datasheets generate outputs context JSON per spec; trees included only if present in S-1 or S-2 (real rows), sorted by numeric public tag.
Open decisions (not blockers)

versions diff UX: plain JSON vs human-readable table output (both okay; JSON first).
code_version: best-effort from git HEAD (add later if useful).
trees_index audit scope (optional; implement if audit trails become important).
Next steps for the new agent

Start with backlog high-priority items in order:
versions show/diff + tests
tx new + tests
datasheets generate (context) + golden test
UPDATE constraint + cumulative alias overlap guard + tests
Retag dedupe/skip + tests
Update planning/spec.md with the provided patch content.
Ensure all tests pass: PYTHONPATH=src uv run --group test pytest
With these done, forcen will be feature-complete for your stated goals: stateless, deterministic, small CLI, with clear docs for future contributors.
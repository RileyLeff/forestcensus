File: planning/reviews/review2.md

Title: forcen review 2 — progress, gaps, and implementation plan

Date: 2025-10-06

Executive summary

Excellent progress since review 1. The codebase now has time-aware alias resolution, per-tree timelines (PRIMARY and UPDATE), SPLIT selectors with retroactive reassignment (on the transaction’s working set), implied-dead generation, retag suggestions, a richer manifest, and validation reports. The CLI and tests exercise lint/submit/build flows end-to-end.
The largest remaining gap versus the spec is statelessness and retroactive consistency: derived fields (tree_uid, genus/species/code, public_tag) are persisted in the ledger’s observations CSV and are not recomputed for prior rows when new DSL lines arrive. This makes certain back-dated ALIAS/UPDATE/SPLIT effects incomplete across prior transactions and can let derived columns drift from “as-of” truth.
Recommended next step: pivot the ledger to store raw canonical observations only and reassemble the entire dataset (across all accepted transactions + cumulative DSL) on every submit and build. This brings the implementation back in line with the spec’s “stateless builds” and guarantees retroactive correctness.
What’s improved since review 1

Time semantics and defaults
Default EFFECTIVE date is now derived deterministically from survey_meta or inferred survey (engine/utils.determine_default_effective_date + with_default_effective). Tests added.
Identity and timelines
Deterministic base tree_uid per tag via uuid5 and an AliasResolver timeline (assembly/treebuilder.py).
PRIMARY timelines from ALIAS (assembly/primary.py) with apply_primary_tags over measurements and existing rows.
Property timelines from UPDATE (assembly/properties.py), applied to current measurements.
SPLIT with selectors (ALL/LARGEST/SMALLEST/RANKS + date windows) implemented and tested; selection ties resolved deterministically (dbh desc, health desc, then input order).
Implied-dead and tree-level outputs
generate_implied_rows implements the “insert at first missing after two consecutive absences” rule (assembly/trees.py). Unit tests cover trailing gap and rediscovery removal (on the per-tx working set).
build_tree_view and build_retag_suggestions produce trees_view.csv and retag_suggestions.csv, used in lint and submit paths. Retag suggestions include ready-to-paste ALIAS lines; unit tests added.
Lint + submit UX
Lint now shows tree_uid/public_tag on normalized measurement rows, a tree_view preview, and retag suggestions for the tx working set.
Submit writes observations_long (CSV/Parquet), trees_view, retag_suggestions, updates_log, and a validation_report.json; manifest includes checksums for all artifacts and row_counts by origin.
Build + versions
build writes a validation report aggregated over transactions and snapshots artifacts into versions/<seq>/ with checksums. versions list works.
Tests
Coverage extended across utils, timelines, splits, implied dead, manifest checks, and CLI behavior.
Where it still diverges from the spec (and why it matters)

Stateful persistence of derived columns (highest-priority)
Current ledger.append_observations writes measurements with derived fields (tree_uid, genus/species/code) that reflect only the DSL present in the current tx. If a later tx adds a back-dated ALIAS/UPDATE/SPLIT, prior rows in observations_long.csv are not recomputed and can become stale.
Side effects:
Back-dated ALIAS does not merge historical rows’ tree_uids in the ledger; only current tx rows get the new identity.
Back-dated UPDATEs do not revise genus/species/code for prior rows (properties applied only to current tx rows).
SPLIT retro selection is applied to current tx’s working set, but not to historical rows in the ledger.
Implied-dead is computed from current tx rows rather than entire tree histories in the ledger, leading to incorrect implied insertion/removal over time.
Cumulative DSL scope
Lint/submit build alias/primary/property timelines from tx.commands rather than “cumulative” updates_log.tdl. That means previews and applications do not reflect earlier accepted DSL operations unless they were already encoded into prior rows’ derived fields.
Growth validator identity
validate_growth still keys by (site, plot, tag). After aliases/splits, it should key by tree_uid with max dbh per tree per survey.
Minor spec gaps
No trees_index.jsonl for explicit “existence” records (optional if uuids are deterministic, but useful for audit).
versions show/diff, tx new, datasheets generate (scaffold), ai prepare (scaffold) are not implemented yet.
planning/fixtures/configs/survey_meta.toml is still present (misleading; survey_meta belongs in per-tx folders only).
Correctness and determinism risks if unaddressed

Retroactive corrections (ALIAS/UPDATE/SPLIT) won’t fully reflect in earlier data; public artifacts may disagree with intended “as-of” semantics.
Derived columns can drift from configuration and DSL truth over time; rebuild will not fix them because build currently snapshots existing CSVs instead of reassembling.
Recommended refactor to restore statelessness (design-level)

Storage contract
Keep the ledger as a write-optimized, raw store:
raw_observations.csv/parquet: append-only canonical rows with only raw fields: survey_id, date, site, plot, tag, dbh_mm, health, standing, notes, origin, source_tx; no tree_uid/genus/species/code/public_tag.
updates_log.tdl: append-only DSL.
transactions.jsonl: ledger entries (already present).
Treat observations_long.csv in the workspace as an ephemeral assembled artifact, overwritten at every submit/build.
Assembly contract (submit and build)
Reassemble “full dataset” every time:
Read raw_observations (all rows) + parse cumulative updates_log.tdl + add current tx rows (prior to acceptance if submit).
Build alias/property/primary timelines from cumulative DSL.
Assign tree_uids for all rows, apply SPLIT retro selection across all history, apply properties and primary tags as-of each row date.
Compute implied-dead from complete tree histories (not per-tx rows).
Emit assembled observations_long, trees_view, retag_suggestions (for latest adjacent pair), and validation_report.
On accept:
Append current tx raw rows to raw_observations.
Append current tx DSL to updates_log.tdl.
Reassemble and overwrite observations_long.csv, trees_view.csv, retag_suggestions.csv, validation_report.json.
Snapshot a new version.
On build:
Reassemble from raw_observations + updates_log only; overwrite workspace artifacts; snapshot a new version.
Implementation notes
You already have most of the components; the key change is replacing incremental, per-tx application with a full reassembly step driven by “all rows” + “all DSL”.
Priority bug/behavior fixes (surgical, short-term)

Apply timelines cumulatively:
Parse and include existing updates_log.tdl (if present) along with tx.commands to build alias/property/primary timelines for lint and submit. This makes previews accurate in presence of prior DSL.
Recompute derived fields on existing rows at submit:
As an interim step before the full refactor, in submit:
Load existing observations CSV into MeasurementRows (you already do).
Build cumulative timelines (updates_log + tx.commands).
Re-assign tree_uid to existing rows, apply SPLIT selectors (retro) to historical rows, apply properties and primary to all existing rows.
Then add tx rows and implied rows, re-derive tree_view and retag suggestions, and overwrite observations_long.csv.
This gives retroactive correctness now, and you can later switch to a raw store without changing downstream artifacts.
Move growth validator to tree identity:
After tree assignment, compute max dbh per tree_uid per survey and apply 8%/16% + floors; deprecate tag-based validator.
Implied-dead correctness:
Change generate_implied_rows signature to accept “all rows” for a tree across all surveys and return implied rows; call it after merging existing + current rows, not only on the tx measurement subset.
Cleanup
Remove planning/fixtures/configs/survey_meta.toml (it belongs in per-tx folders).
Ensure submit/lint pass rounding from config (already done).
Consider reading git HEAD for code_version (best-effort).
Roadmap (target order and acceptance criteria)

Phase 1 — Cumulative timelines and retroactive application (submit + lint)

Parse cumulative DSL:
Add a small loader to read Ledger.updates_log (if exists) and DSL-parse it; merge with tx.commands (tx last).
Lint should use cumulative commands for previews.
Retro apply to existing rows (pre-refactor):
In submit, load existing observations CSV → to MeasurementRows; build cumulative timelines; re-assign tree_uid, apply SPLIT (retro), properties, and PRIMARY to these existing rows.
Compute implied rows from the full set (existing-after-reassign + tx rows).
Overwrite observations_long.csv with the newly assembled dataset.
Tests:
Start with tx-1 (H4/112); submit tx-2 with ALIAS back-dated to 2020-06-15 mapping H4/508 → H4/112; assert prior rows for 508 (if any) are reassigned to the same tree_uid as 112 in observations_long.csv.
Add a synthetic SPLIT retro test that moves older rows into a new tag; verify reassignments in observations_long.csv (not just in tx working set).
Phase 2 — Growth validator on tree identity

Implement validate_growth_tree using tree_uid; retire tag-based growth check in the pipeline.
Tests:
Synthetic tree histories that trigger W/E thresholds, including no-ops when dbh is missing.
Phase 3 — Full stateless refactor (move to raw store)

Ledger changes:
Introduce raw_observations.csv/parquet (canonical raw fields only).
In submit: append tx rows to raw_observations; append DSL; reassemble full artifacts and overwrite workspace outputs; snapshot version.
In build: reassemble from raw_observations + DSL; overwrite outputs; snapshot version.
Observations_long.csv becomes an assembled product only (not the canonical store).
Tests:
Golden test: submit tx1, tx2; then delete observations_long.csv and rebuild — artifacts identical to pre-delete.
Ensure implied rows and properties/PRIMARY are identical between submit and build.
Phase 4 — CLI and UX

tx new: scaffold a tx folder with measurements.csv header and empty updates.tdl; optional survey_meta.toml.
versions show/diff: show prints a manifest; diff shows tx_ids, checksums, row_counts deltas, and warnings deltas.
datasheets generate (scaffold): produce context JSON per spec; Typst call optional.
ai prepare (scaffold): generate draft CSV/TDL files; never auto-submit.
Phase 5 — Safety and performance

Alias concurrency guard across ledger:
When loading cumulative DSL, detect two bindings for the same tag with the same EFFECTIVE date (already), and optionally warn if a tag’s binding flips frequently; enforce “no overlapping at same instant.”
Trees index (optional):
Append trees_index.jsonl lines when a brand-new (site, plot, tag) first appears (tree_uid + tx_id). Provides provenance without affecting behavior.
Additional code-level notes

assembly/properties.apply_properties currently writes properties onto tx rows only. After the cumulative pass, ensure it applies to all rows.
engine/submit: when building tree_view and retag_suggestions, use the reassembled full rows, not existing_rows + tx rows with only primary applied. You already pipe through output_rows; keep that pointing at the fully reassembled list.
validators/rows._date_within_surveys compares ISO strings; switching to date comparisons is safer. Not urgent.
DSL parser: the elif item == "PRIMARY" branches in parser transformer are redundant given primary() returns True; safe to remove for clarity.
Quick wins you can ask the agent to land immediately

Load cumulative DSL from updates_log in lint/submit and merge with tx.commands.
In submit, reassign tree_uid/apply SPLIT + properties + PRIMARY to existing rows before writing outputs (uses cumulative timelines).
Run implied-dead on full rows instead of tx rows.
Port growth validator to tree identity.
Remove planning/fixtures/configs/survey_meta.toml.
Acceptance criteria for next PR

Submitting a tx with back-dated ALIAS/UPDATE/SPLIT modifies prior rows in observations_long.csv appropriately (prove with a new fixture).
Rebuilding after deleting workspace artifacts reproduces identical outputs (once Phase 3 is done).
Growth warnings/errors are computed per tree_uid.
Implied-dead rows appear/disappear correctly against the full history.
Retag suggestions and trees_view are generated from the full reassembled dataset.
Manifest includes all expected checksums; versions list/show remains stable.
This plan brings the implementation back to the spec’s guarantees: stateless, retroactive, deterministic builds with a minimal, auditable ledger.
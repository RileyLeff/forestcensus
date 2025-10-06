File: planning/plan.md
Scope

Deliver a working forcen CLI and library that:
Loads config TOML files and validates them.
Parses and applies the minimal DSL (ALIAS, UPDATE, SPLIT) with effective dates and idempotency.
Implements a transaction engine (lint and submit) with atomic accept/reject, a simple ledger, and deterministic manifests.
Normalizes inputs (health rounding/clamp, legacy alive override, standing coercion, taxonomy enforcement, date-in-survey).
Validates at row, alias, per-tree (across surveys), and dataset levels (including tight growth checks, implied-dead logic, retag suggestions).
Assembles the dataset using per-tree processing (as-of alias/update, SPLIT retro selection, implied dead insert/remove, zombie detection).
Provides CLI commands for tx new/lint/submit, build, datasheets generate (scaffold), and ai prepare (scaffold).
Emits versioned artifacts and a manifest.
Milestones and exit criteria

Config and schemas
Implement loaders and validators for taxonomy.toml, sites.toml, surveys.toml, validation.toml, datasheets.toml.
Exit: invalid or overlapping surveys are rejected; missing plots or species are detected with clear errors.
1. DSL parser and applier

Implement ALIAS, UPDATE, SPLIT with EFFECTIVE dates, PRIMARY, tree_ref resolution, and SPLIT selectors (ALL, LARGEST, SMALLEST, RANKS with BEFORE/AFTER/BETWEEN).
Enforce: no overlapping alias bindings for the same (site, plot, tag); at most one PRIMARY per tree at any date; idempotency of repeated lines.
Exit: tx-2-ops/updates.tdl parses and dry-applies without side effects on a second run.
3. Transaction engine

Commands: tx new (scaffold), tx lint (parse, normalize, dry-assemble, validate), tx submit (atomic accept).
Ledger: append-only transactions.jsonl; trees_index.jsonl for new tree_uids; updates_log.tdl concatenation; hashing of tx contents for tx_id.
Exit: tx-1-initial lints and submits cleanly; resubmitting is a no-op; manifest contains code/config hashes and input checksums.
4. Normalization and validators

Normalization: health rounding/clamp; legacy alive override (alive TRUE with health 0 → health 1); standing coercion.
Validators:
Row: dbh ≥ 0 (or NA only for origin="implied"), health in 0..10 or NA, standing in {true,false,NA}, date in survey.
Alias: no overlapping bindings; tag reuse allowed only over non-overlapping intervals; PRIMARY uniqueness.
Per-tree across surveys: max dbh growth warn at 8% (and ≥3 mm) and error at 16% (and ≥6 mm); species changes only via UPDATE.
Implied-dead logic: insert after two consecutive absences; remove on rediscovery; implied rows don’t count as presence.
Retag candidates: within plot, lost vs new with dbh ≥ 60 mm and within 10%; output suggestions (do not auto-apply).
Exit: clear error codes and pinpointed messages on failing fixtures; warnings summarized.
5. Assembly (per-tree engine)

As-of resolution for ALIAS and UPDATE by date.
SPLIT retro row reassignment per survey using computed ranks during selection; forward-only if no SELECT.
Compute alive per survey, implied dead insert/remove, and zombie_ever; never store ranks.
Exit: assembled outputs for fixtures contain expected rows and derived fields; implied rows appear/disappear correctly.
6. CLI wiring

Implement: ai prepare (scaffold only), tx new, tx lint, tx submit, build, datasheets generate (scaffold), versions list/show/diff.
Exit: help text and exit codes are correct; commands operate on fixtures end-to-end; rebuild reproduces prior artifacts byte-identically.
7. Datasheets scaffold

Provide context builder that selects trees (seen in S-1 or S-2), sorts by public tag, derives DHS1/DHS2 strings, and appends zombie asterisk where needed.
Call typst as a subprocess if present; otherwise write the context JSON to disk.
Exit: context JSON matches spec for fixtures; command succeeds even without Typst installed.
8. AI prepare scaffold

Given PDFs, write draft measurements.csv and updates.tdl side-by-side; never auto-submit.
Exit: command runs and produces files with correct headers; actual model invocation can be mocked or skipped.
Acceptance criteria

Deterministic rebuild: running build twice yields identical manifests and artifacts.
Idempotent submit: re-submitting an identical tx produces no changes.
DSL idempotency: re-applying the same DSL lines is a no-op; alias overlap is rejected with clear, line-referenced errors.
Validation strictness: any failing check causes tx reject with precise row/field or DSL line references; no partial commits.
Growth checks: warn and error thresholds enforced on max dbh across adjacent surveys.
Implied dead: inserted after 2-miss gaps and removed on rediscovery; implied rows excluded from datasheet inclusion logic.
Retag suggestions: produced for tx-2-ops with expected columns and suggested ALIAS lines.
CLI: all commands present; help text informative; correct exit codes (0 success; 2 validation error; 3 DSL parse error; 4 IO error).
Testing strategy

Unit tests for config loaders, DSL parsing, normalization, validators, per-tree assembly steps.
Property tests:
Idempotency of DSL application and tx submit.
SPLIT selectors across synthetic rank ties and date windows.
Golden tests:
Run lint and submit on fixtures; compare artifacts and manifest hashes.
Rebuild from ledger; compare to prior version artifacts.
Risks and mitigations

Alias overlap complexity → strict validation with interval checks; fail closed.
SPLIT retro selection correctness → property tests over synthetic datasets with varying rank distributions.
Implied dead edge cases → per-tree tests over multiple gap/rediscovery patterns.
Determinism regressions → golden tests with byte-identical manifests; pinned sort orders and tie-breaks.
Delivery checklist (short)

CLI commands implemented with help text and exit codes.
Config loading and validation.
DSL parser and applier with idempotency and overlap checks.
Transaction engine with ledger, manifest, hashing, atomic writes.
Normalization and validators.
Assembly with implied dead and zombie detection.
Datasheets and AI prepare scaffolds.
Tests (unit, property, golden) passing on fixtures.
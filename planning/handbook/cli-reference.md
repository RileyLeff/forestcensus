File: planning/handbook/cli-reference.md

Title: forcen CLI reference

Conventions

Paths default to:
--config: planning/fixtures/configs (for tests)
--workspace: .forcen (local ledger)
Exit codes:
0 success
2 validation error (row/growth/submit rejection)
3 DSL parse error
4 IO/runtime error
5 config error
Commands

forcen tx lint
Synopsis:
forcen tx lint TX_DIR [--config DIR] [--report FILE] [--workspace DIR]
What it does:
Loads and normalizes the tx in TX_DIR (measurements.csv, updates.tdl).
Attaches default EFFECTIVE dates for commands if missing (survey start).
If --workspace is provided, merges ledger history (raw + DSL) with the tx; otherwise, uses tx-only.
Reassembles full dataset in-memory, runs validators, and prints JSON report to stdout.
Writes the same JSON to --report (default: TX_DIR/lint-report.json).
Output (JSON fields):
tx_id, issues[], summary{errors,warnings,rows}, measurement_rows[] (assembled rows sourced from this tx), tree_view[], retag_suggestions[].
Exit:
0 if no errors (warnings allowed), 2 if any validation error, 3 for DSL parse errors, 5 for config errors.
2. forcen tx submit

Synopsis:
forcen tx submit TX_DIR [--config DIR] [--workspace DIR]
What it does:
Computes tx_id; if already accepted, returns accepted=false (idempotent).
Loads existing raw rows + serialized DSL from ledger; loads and normalizes tx; applies default EFFECTIVE dates.
Adds tx raw rows to observations_raw.csv (with source_tx set), appends DSL to updates_log.tdl/transactions.jsonl.
Reassembles full dataset and rewrites artifacts:
observations_long.csv/parquet, trees_view.csv, retag_suggestions.csv, validation_report.json.
Snapshots a new version in versions/000N/ with manifest.json (includes CSV checksums and sizes).
Exit:
0 on accept; 2 if validation rejects; 3 DSL parse; 4 IO; 5 config.
Notes:
CSV checksums are authoritative in manifest; Parquet checksums may differ across platforms.
3. forcen build

Synopsis:
forcen build [--config DIR] [--workspace DIR]
What it does:
Reassembles full dataset solely from observations_raw.csv and cumulative DSL in ledger.
Rewrites artifacts, emits aggregate validation_report.json, and snapshots a new version with a manifest.
Exit:
0 on success; 4/5 on errors.
4. forcen versions list

Synopsis:
forcen versions list [--workspace DIR]
What it does:
Lists numeric version sequences available under versions/.
Exit:
0 on success.
Behavior notes

Default EFFECTIVE:
Derived from the survey window that covers the tx’s measurement dates; if the tx has only DSL and no measurements, explicit EFFECTIVE is recommended; otherwise the earliest survey is used when unambiguous.
Lint with/without workspace:
Without: preview only the tx’s effect in isolation.
With: preview the tx applied to the current ledger history (recommended in practice).
Idempotent submit:
Re-submitting the same tx dir produces accepted=false and does not create a new version.
Planned/Upcoming commands (backlog)

forcen versions show <seq>:
Print manifest.json for a specific version.
forcen versions diff <seqA> <seqB>:
Show differences in tx_ids, artifact checksums/sizes, row_counts, and validation summaries.
forcen tx new --out DIR:
Scaffold a tx directory (measurements.csv header + empty updates.tdl). No survey_meta by default; surveys.toml is the source of truth.
forcen datasheets generate --survey <id> --site <site> --plot <plot> --out DIR:
Produce JSON context per spec for Typst templates; do not require Typst installed to run.
forcen ai prepare <pdf|dir> --out DIR:
Produce draft measurements.csv and updates.tdl from scanned sheets (stub/mockable), never auto-submit.
Examples (with fixtures)

Lint, tx-only:
uv run forcen tx lint planning/fixtures/transactions/tx-1-initial --config planning/fixtures/configs
Lint, with history:
uv run forcen tx lint planning/fixtures/transactions/tx-2-ops --config planning/fixtures/configs --workspace .forcen
Submit, then build:
uv run forcen tx submit planning/fixtures/transactions/tx-1-initial --config planning/fixtures/configs --workspace .forcen
uv run forcen build --config planning/fixtures/configs --workspace .forcen
Notes on CSV vs Parquet

CSV checksums in manifests are authoritative for determinism and CI.
Parquet is provided for analytics; its checksum may vary by platform/pyarrow and is informational only.
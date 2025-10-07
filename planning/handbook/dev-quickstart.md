File: planning/handbook/dev-quickstart.md

Title: forcen developer quickstart

Prerequisites

Python 3.11+ and uv (recommended). If you use pip/venv instead of uv, adapt commands accordingly.
Install

uv sync
Run tests: PYTHONPATH=src uv run --group test pytest
Core commands (using fixtures)

Lint a transaction (preview assembled rows and suggestions; standalone)
uv run forcen tx lint planning/fixtures/transactions/tx-1-initial --config planning/fixtures/configs --report planning/fixtures/transactions/tx-1-initial/lint-report.json
Lint using cumulative history (pass a workspace to include prior DSL/raw)
uv run forcen tx lint planning/fixtures/transactions/tx-2-ops --config planning/fixtures/configs --workspace .forcen --report /tmp/report.json
Submit (accepts the tx, appends raw rows and DSL, reassembles all artifacts, snapshots a version)
uv run forcen tx submit planning/fixtures/transactions/tx-1-initial --config planning/fixtures/configs --workspace .forcen
uv run forcen tx submit planning/fixtures/transactions/tx-2-ops --config planning/fixtures/configs --workspace .forcen
Rebuild from ledger (reassembles artifacts from observations_raw.csv + cumulative DSL)
uv run forcen build --config planning/fixtures/configs --workspace .forcen
List versions
uv run forcen versions list --workspace .forcen
What lint does

Parses and normalizes the tx; resolves a default EFFECTIVE date (survey start) if omitted.
If you pass --workspace, it merges the ledger’s raw rows + DSL with the tx; otherwise it uses tx-only.
Reassembles full dataset in-memory to preview:
measurement rows (for just this tx), tree views, and retag suggestions.
Runs validators over these assembled rows and DSL.
What submit does

Computes tx_id; rejects if already accepted (idempotent).
Loads existing raw + DSL from the workspace; adds this tx’s raw rows and DSL.
Reassembles entire dataset and rewrites:
observations_long.csv/parquet, trees_view.csv, retag_suggestions.csv, updates_log.tdl, validation_report.json.
Writes a new version with a manifest (checksums + sizes).
CSV checksums are authoritative; Parquet checksums may vary across platforms.
Where artifacts land (default workspace: .forcen/)

observations_raw.csv: canonical raw inputs (append-only).
observations_long.csv/parquet: assembled dataset (rewritten each build/submit).
trees_view.csv: per tree_uid, per survey view (public_tag + properties).
retag_suggestions.csv: latest adjacent survey pair suggestions.
updates_log.tdl: concatenated DSL lines (exactly as submitted, newline-terminated).
validation_report.json: summary of warnings/errors for the last operation.
versions/000N/: snapshot of current artifacts + manifest.json.
Determinism checks (manual)

Submit tx-1-initial and tx-2-ops; then run build. The new version’s manifest should differ only by version_seq and aggregated stats; artifacts should match the workspace copies.
Delete observations_long.csv/parquet and run build again; artifacts and manifest checksums should match the previous build (CSV checksums authoritative).
Re-run submit on the same tx; CLI should report accepted: false and not create a new version.
Survey metadata policy

The single source of truth for survey windows is config/surveys.toml.
Transactions generally do not include survey metadata. Only include a survey_meta file in a tx if you must introduce a new survey id/window ad-hoc; otherwise prefer updating surveys.toml in a config change.
Lint/submit infer default EFFECTIVE from the survey window covering the tx’s measurement dates.
Troubleshooting

ConfigError: verify planning/fixtures/configs/*.toml exist and validate; pay attention to survey overlaps.
DSLParseError: check updates.tdl line/column; ensure ALIAS/UPDATE/SPLIT syntax and EFFECTIVE dates are correct.
TransactionDataError: measurements.csv has a malformed field (date, boolean, etc.). The error includes row/column.
Submit error (idempotency): submitting the same tx twice returns accepted=false; this is expected.
Growth warnings/errors: validate dbh changes by tree_uid across adjacent surveys; adjust thresholds in validation.toml if needed (warn=8%, error=16% with 3/6 mm floors).
Developer notes

CSV checksums are authoritative in manifests; Parquet checksums are best-effort and may vary by platform/pyarrow.
Deterministic ordering before writes:
observations_long: sorted by (survey_id, site, plot, tag, obs_id).
trees_view: (survey_id, site, plot, public_tag).
retag_suggestions: (survey_id, plot, new_public_tag).
Next docs to read

architecture.md for how the pieces fit.
cli-reference.md for a concise command guide.
backlog.md for the remaining work items and acceptance criteria
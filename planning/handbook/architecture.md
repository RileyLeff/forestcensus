File: planning/handbook/architecture.md

Title: forcen architecture overview

Purpose

Give a concise mental model of how forcen works so you can find the right place to change things and keep invariants intact.
System goals (restate)

Stateless rebuilds: every lint/submit/build reassembles the full dataset from raw observations + cumulative DSL + config + code.
Minimal, auditable metadata language (DSL) with ALIAS/UPDATE/SPLIT and EFFECTIVE dates; idempotent and time-aware.
Deterministic artifacts and manifests; CSV checksums are authoritative.
High-level data flow

Input (per transaction)
measurements.csv → normalized to MeasurementRow (types, rounding, alive→health override, booleans).
updates.tdl → parsed into commands (ALIAS/UPDATE/SPLIT), with default EFFECTIVE set to the survey start if omitted.
2. Ledger (workspace)

Stores:
observations_raw.csv: canonical raw rows only (no derived fields).
transactions.jsonl: one JSON line per accepted tx with serialized DSL commands, counts, and summaries.
updates_log.tdl: concatenated DSL text for audit (newline-terminated).
Derived artifacts rewritten on every submit/build: observations_long.csv/parquet, trees_view.csv, retag_suggestions.csv, validation_report.json. Versions/000N/ contain snapshots and a manifest.
3. Assembly (assemble_dataset)

Inputs: all raw rows + cumulative commands + config.
Steps:
Build alias resolver timelines; assign tree_uid to every row as-of row.date (uuid5 base per tag timeline).
Apply SPLIT selectors: retroactively reassign selected rows to the target tree_uid; also reassign forward rows consistent with the selector (idempotent on re-run).
Build UPDATE property timelines (genus/species/code/site/plot) and apply as-of row.date to all rows.
Build PRIMARY timelines from ALIAS primary flags; compute public_tag as-of row.date (fallback to row.tag).
Generate implied-dead rows per tree when two consecutive survey absences occur, inserting at the first missing survey and removing on rediscovery (implied rows never count as presence).
Sort rows deterministically (see below) and return the assembled dataset.
4. Outputs

observations_long: assembled rows with derived fields (tree_uid, public_tag, properties), plus origin/source_tx.
trees_view: per tree_uid per survey “best” row (prefer real over implied, then most recent date).
retag_suggestions: “lost vs new” matching within the same plot (first-seen ≥ threshold dbh, within delta%) with deduped, closest match and suggested ALIAS lines.
validation_report.json: summary (errors/warnings) plus per-tx validation summaries for build; per-submit report for submit.
Components map (by module)

config/
models.py: Pydantic schemas and constraints (taxonomy, sites, surveys non-overlapping, validation thresholds, datasheets).
loader.py: TOML reading and error reporting (ConfigError).
dsl/
parser.py: Lark grammar → typed commands.
types.py: TagRef, TreeRef, commands, selectors.
state.py: semantic checks for alias overlap and PRIMARY conflicts (same EFFECTIVE).
serialization.py: serialize/deserialize commands for transactions.jsonl.
exceptions.py: DSLParseError and semantic errors.
transactions/
normalization.py: CSV normalization to MeasurementRow (rounding, clamping, booleans).
loader.py: assemble a TransactionData (rows + commands).
txid.py: deterministic tx hash of normalized files.
models.py: dataclasses for rows and tx.
assembly/
treebuilder.py: deterministic tree_uid per tag (uuid5); TagTimeline alias resolver; bind ALIAS and SPLIT target tags into the resolver.
split.py: evaluate SPLIT selectors per survey; move selected historical rows; reassign future rows consistently; idempotent selection.
properties.py: build/apply UPDATE property timelines (as-of).
primary.py: build/apply PRIMARY tag timelines (as-of public_tag).
trees.py: implied-dead row generation over full histories.
tree_outputs.py: trees_view selection and retag_suggestions algorithm.
reassemble.py: assemble_dataset orchestration (source of truth).
survey.py: SurveyCatalog (mapping dates ↔ survey_id; ordered windows).
validators/
rows.py: row-level checks (dbh, health range, standing tokens, dates within survey, taxonomy).
trees.py: growth validation per tree_uid (max dbh between adjacent surveys; warn/error thresholds with absolute floors; skip implied).
updates.py: apply DSLState to catch alias overlap and PRIMARY conflicts.
ledger/
storage.py: read/write raw rows; load cumulative commands; write derived artifacts; write versions and manifests (CSV checksums authoritative; sizes tracked).
engine/
lint.py: normalize current tx, merge with cumulative history if --workspace, assemble full dataset, run validators, emit report.
submit.py: idempotency check, merge raw + DSL, assemble, write artifacts, append logs, snapshot version.
build.py: reassemble from ledger, rewrite artifacts, snapshot version.
utils.py: determine default EFFECTIVE and attach defaults.
Key invariants and where enforced

Surveys non-overlapping and ordered: config.models.SurveysConfig.
Row validity (dbh/health/standing/date/taxonomy): validators.rows.
Growth sanity (per tree_uid, max dbh across adjacent surveys): validators.trees.
DSL conflicts (same EFFECTIVE): dsl.state via validators.updates.
Deterministic ordering before writes:
observations_long: (survey_id, site, plot, tag, obs_id).
trees_view: (survey_id, site, plot, public_tag).
retag_suggestions: (survey_id, plot, new_public_tag).
Important behaviors

Default EFFECTIVE date: inferred from the survey covering the tx’s measurement dates; if the tx has commands only, picks the earliest survey in config unless explicit dates are present.
Public tag resolution: PRIMARY timeline as-of date; fallback to current row tag if no PRIMARY is active.
SPLIT evaluation:
Retro: apply selector to historical rows (by per-survey ranks or size).
Forward: apply selector to future surveys so identity remains consistent.
Idempotent: applying the same SPLIT again yields no change.
Retag suggestions:
Lost = present in S-1, not present in S.
New = first seen in S with max dbh ≥ threshold.
Same plot; choose closest dbh (tie-break by public_tag); skip cases where lost/new already share the same tree_uid or public_tag.
Error model and exit codes

ConfigError → exit 5 (config issue).
DSLParseError → exit 3 (syntax/grammar).
TransactionDataError → exit 2 (row-level normalization/validation).
SubmitError/BuildError → exit 2 or 4 (validation fail or IO).
Generic ForcenError → exit 4.
Determinism notes

All artifacts written with stable sort keys.
CSV checksums in manifests are authoritative; Parquet checksums can vary by platform and are informational only.
obs_id derived from (source_tx, row_number, site, plot, tag, date) to be stable across rebuilds.
Survey metadata location

surveys.toml in config is the single source of truth for survey windows. Do not duplicate in tx by default. Only introduce a survey ad-hoc in a tx if there is no prior config entry (rare).
Performance and extensibility

Current reassembly is in-memory Pandas; datasets expected to be modest. Polars can be swapped in assembly if needed.
Multiple sites supported by config; alias and assembly are site/plot-aware by design.
A tree identity index (trees_index.jsonl) can be added later for audit without changing assembly semantics.
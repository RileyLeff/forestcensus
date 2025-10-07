File: planning/handbook/orientation.md

Title: forcen orientation

What this is

forcen is a stateless, deterministic pipeline and CLI for forest census data.
You submit “transactions” (raw measurements + optional DSL updates). The system normalizes, validates, and rebuilds the entire dataset from scratch on every lint/submit/build using cumulative raw data and DSL.
Core invariants (must stay true)

Stateless builds: outputs are a pure function of (raw observations + cumulative DSL + config + code).
No persistent stem identity: stems are unranked in storage; ranks are computed on demand by dbh descending (ties: health desc, then input order).
Tree-level alive: any stem with health > 0 in a survey.
Zombie is tree-level only: dead in a survey and later alive in a later survey.
Implied dead: if absent for two consecutive surveys, insert one synthetic row at the first missing survey (health=0, standing=false, dbh=NA, origin="implied"); remove it if the tree is later observed again.
Minimal DSL, time-aware, idempotent: ALIAS, UPDATE, SPLIT with EFFECTIVE dating and PRIMARY public-name selection; no overlapping tag bindings at the same instant.
Determinism and idempotency: re-running the same command sequences yields identical artifacts and manifests; re-submitting the same tx is a no-op.
Current status (what’s already built)

Raw store + rebuilds:
Ledger stores only raw rows (observations_raw.csv) and serialized DSL commands in transactions.jsonl. Every lint/submit/build reassembles the full dataset.
Assembly (assemble_dataset):
Alias resolution with deterministic tree_uid per tag (uuid5) and back-dated ALIAS across history.
UPDATE timelines (genus/species/code/site/plot) and PRIMARY timelines applied as-of for all rows (including implied).
SPLIT selectors (ALL/LARGEST/SMALLEST/RANKS) reassign past rows and the forward timeline; idempotent.
Implied-dead generation over full history; public_tag computed per survey.
Validators:
Row-level checks; growth checks per tree_uid using percent thresholds + absolute floors.
DSL overlap and PRIMARY conflict checks.
CLI:
forcen tx lint/submit, forcen build, forcen versions list.
Artifacts + manifests:
observations_long.{csv,parquet}, trees_view.csv, retag_suggestions.csv, updates_log.tdl, validation_report.json, versioned manifests with checksums and sizes.
CSV checksums are authoritative (see policy below).
Read these next

dev-quickstart.md: how to run locally, lint/submit/build, determinism checks.
architecture.md: components map and data flow.
cli-reference.md: commands, options, and exit codes.
backlog.md: what’s left to implement (with acceptance criteria and test notes).
planning/spec.md remains the single source of truth for domain rules.
Where things live

planning/fixtures: minimal configs and two example transactions.
src/forcen: code organized by config, dsl, transactions, assembly, validators, ledger, engine, cli.
Workspace (default .forcen/): raw and assembled artifacts + versions folder with manifests.
Success criteria (at a glance)

Lint/submit/build run clean on fixtures; manifests deterministic across runs.
Re-submitting the same tx produces no changes; rebuild reproduces current artifacts exactly.
Back-dated ALIAS/UPDATE/SPLIT affect all history; implied rows appear/disappear correctly.
Growth validator operates on tree_uid histories, not tag strings.
Quick glossary

Transaction (tx): a directory with measurements.csv and optional updates.tdl.
DSL: the metadata update language (ALIAS, UPDATE, SPLIT).
Effective date: date from which a DSL change applies forward.
PRIMARY: which tag is the public display name for a tree as-of a date.
tree_uid: deterministic internal identity per tag timeline (merges via ALIAS).
Implied row: synthetic dead record inserted after two-miss gaps; removed on rediscovery.
Retag suggestion: a flagged potential ALIAS based on dbh similarity and first-seen rules.
Policies to note

Checksums: CSV checksums are authoritative in manifests; Parquet checksums are best-effort and may vary by platform/pyarrow (safe to ignore for determinism).
Survey metadata: lives in config (surveys.toml). Do not duplicate. Only include survey_meta inside a tx if you must introduce a new survey window ad-hoc; otherwise, update surveys.toml in a config change.

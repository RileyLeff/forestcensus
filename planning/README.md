File: planning/README.md
Title: forcen planning folder

Purpose

This folder contains the minimal but complete specification and fixtures an implementation agent needs to build forcen (forest census pipeline).
It is designed for stateless, deterministic builds with a small, unified CLI and a strict, minimal metadata DSL.
Core invariants (read first)

Stateless builds: outputs are a pure function of accepted transactions + config + code.
Stems unranked in storage: ranks are computed on demand by dbh (descending) with deterministic tie-breaks.
Tree-level alive: any stem health > 0 in that survey.
Tree-level zombie: a survey with alive=false followed by a later survey with alive=true.
Implied dead insertion and removal:
If a tree is absent in two consecutive surveys Sk and Sk+1, insert one synthetic record at Sk (health=0, standing=false, dbh=NA, origin="implied").
If later rediscovered, remove that implied record on rebuild.
Implied rows do not count as presence for datasheet inclusion.
Datasheets include only trees seen in S-1 or S-2 (the prior two surveys), sorted by public tag; stems shown in dbh-desc order.
Minimal metadata DSL: ALIAS, UPDATE, SPLIT. Time-aware, non-overlapping alias bindings. Idempotent by design.
Transactions are atomic: apply updates.tdl, then normalize/validate measurements, assemble entire dataset; accept or reject as a whole.
New, never-seen tags implicitly create new trees (with a suggested ALIAS PRIMARY line in the tx report). You can later correct/merge via ALIAS.
Tight growth sanity on max dbh between adjacent surveys: warn at 8% (and ≥3 mm), error at 16% (and ≥6 mm).
Retag candidates flagged (never auto-applied): lost vs new trees within the same plot with dbh within 10% and new tree dbh ≥ 60 mm.
Read order

spec.md — single source of truth for rules, schemas, DSL, assembly, validators, CLI, and outputs.
fixtures/ — minimal configs and transactions used as golden tests and examples.
plan.md — milestones, acceptance criteria, and testing strategy for delivery.
How to use the fixtures

configs/ contains TOML examples for taxonomy, sites/plots, surveys, validation thresholds, and datasheet preferences.
transactions/ contains two transaction directories:
tx-1-initial: new tree via a never-seen tag, no DSL lines.
tx-2-ops: a retag (ALIAS) and a retroactive SPLIT example.
During development:
Implement loaders, DSL, and tx engine.
Run “lint” and “submit” on tx-1-initial, then tx-2-ops.
Verify manifests and artifacts are deterministic and match expected shapes.
Implementation guidelines (short)

Python 3.11+, uv for dependency management.
Libraries: pydantic v2, typer, pandas or polars, pyarrow, toml, lark (or similar) for DSL, rich for reports, pytest.
Determinism and idempotency are required: repeated tx submit must not change outputs; rebuild from ledger must reproduce identical artifacts and manifest.
Fail closed: any validation error rejects the transaction with a precise, actionable report.
Non-goals (for this phase)

No web UI, no DB server, no GIS, no smoothing/filling beyond rules above, no persistent stem IDs, no external salinity integration.
Support

If anything is ambiguous, the agent should restate the requirement and propose a test in fixtures/ before coding.

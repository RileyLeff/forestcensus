File: planning/checklist.md

forcen delivery checklist

Use this as a PR-by-PR tracker. Each item should have tests and clear docs in spec.md referenced in commit messages.

Milestone 1 — Config loaders and schemas

 Load taxonomy.toml; validate species triplets and code=UPPER(gen[0:3]+spp[0:3])
 Load sites.toml; validate plots array and zone_order; parse girdling dates
 Load surveys.toml; validate non-overlapping, ordered windows
 Load validation.toml; apply defaults; bounds check thresholds
 Load datasheets.toml
 Error messages include file and key path; exit code 5 on config errors
 Unit tests for each loader (good and bad cases)
Milestone 2 — DSL parser and applier (no writes yet)

 Parse ALIAS, UPDATE, SPLIT with EFFECTIVE, PRIMARY, NOTE
 tree_ref resolution (tree_uid or site/plot/tag@date)
 SPLIT selector grammar: ALL | LARGEST | SMALLEST | RANKS n[,m…] + BEFORE/AFTER/BETWEEN
 Detect alias overlap for same tag across time (E_ALIAS_OVERLAP)
 Enforce one PRIMARY per tree at any date (E_PRIMARY_DUPLICATE_AT_DATE)
 Idempotency: re-parsing/re-applying the same lines is a no-op
 Tests cover happy paths, overlap errors, selector edge cases, idempotency
Milestone 3 — Transaction engine (lint/submit)

 tx new scaffolds directory with headers
 tx_id = SHA256 over normalized contents
 tx lint: parse DSL, normalize CSV, dry-assemble, validate; write lint-report.json; exit 0/2/3/4/5
 tx submit: atomic accept or reject; on accept append to updates_log.tdl, observations, trees_index.jsonl, transactions.jsonl; write new version
 Idempotent resubmit (same tx_id) is a no-op with clear message
 Unit tests (mocks) + golden tests on fixtures tx-1-initial and tx-2-ops
Milestone 4 — Normalization and validators

 Health rounding half-up, clamp to [0..10]
 Legacy alive override: alive TRUE with health 0 → health 1 (reported)
 Standing coercion to {true,false,NA}
 Taxonomy enforcement; species changes only via UPDATE
 Row-level errors (codes per spec.md §7)
 Dataset-level: surveys overlap detection
 Tests for normalization and each validator with precise locations
Milestone 5 — Assembly (per-tree engine)

 As-of alias resolution and public-name resolution (PRIMARY)
 As-of UPDATE for genus/species/code/site/plot
 SPLIT retro reassignment using on-demand ranks
 Implied-dead insertion after two-miss gaps at the first missing survey; removal on rediscovery
 Alive per survey and zombie_ever computation (ignoring removed implied rows)
 Max dbh growth checks (warn 8% ≥3 mm; error 16% ≥6 mm)
 Deterministic sort/tie-breaks
 Unit + golden tests over synthetic trees with gaps/splits/retags
Milestone 6 — CLI wiring and outputs

 ai prepare (scaffold): write draft measurements.csv + updates.tdl; never auto-submit
 datasheets generate (scaffold): build context JSON; optional Typst subprocess
 versions list/show/diff
 Write artifacts and manifest.json with checksums; deterministic write (temp dir → atomic rename)
 Help text and exit codes per spec.md §9
 Golden tests: rebuild reproduces identical artifacts and manifest
Retag suggestions

 Algorithm: within plot, Lost (S-1 not in S) × New (first-seen in S with max dbh ≥ 60 mm) within 10% delta
 Emit suggested ALIAS lines with rationale in lint/submit reports and retag_suggestions.csv
 Tests for positive/negative matches
Acceptance criteria (final)

 Deterministic rebuild: identical artifacts and manifest across runs
 Idempotent submit: re-submitting the same tx produces no changes
 DSL idempotency and overlap protections proven by tests
 Implied-dead behavior verified (insert/remove) and excluded from datasheet inclusion
 Fixtures pass end-to-end; outputs present with expected shapes
 Clear error/warn reports with exact locations and codes
# Decision layer

Date: 2026-05-11

Historical design snapshot: the counts below describe May 11, not today's
dataset. The October 26 handoff has 214 configured decisions. See
[the current handoff](researcher_handoff.md) and
[open implementation gaps](handoff_open_questions.md) before treating an old
proposal as implemented or an old review count as current.

The pipeline now separates raw detection from accepted manual decisions.

## Flow

```text
raw source files
  -> adapt into normalized raw observations
  -> raw diagnostics (`forestcensus diagnose-raw`)
  -> apply accepted configured decisions (`forestcensus decisions` documents these)
  -> assemble canonical dataset
  -> post-decision validation/invariants
  -> canonical review UI artifacts
```

The important design point is that accepted manual calls are applied in one explicit phase through `apply_decisions()`. The old `corrections.toml` sections are still the source config for now, but they are represented as configured decisions rather than being conceptually separate pre-diagnostic cleanup.

## Configured decisions

Current configured decision ledger:

| Operation | Count |
|---|---:|
| `set_field` | 29 |
| `suppress_field` | 12 |
| `set_status` | 7 |
| `set_row_taxon` | 2 |
| `interpret_as_not_found` | 1 |
| `suppress_observation` | 5 |
| `set_taxon` | 35 |
| `reassign_identity_row` | 11 |
| `split_identity` | 5 |

Total configured decisions: 107.

Outputs:

- `output/decisions/configured_decisions.csv`
- `output/decisions/configured_decisions.parquet`
- `output/decisions/summary.json`

## Raw vs post-decision diagnostics

Raw diagnostics are materialized with:

```sh
uv run forestcensus diagnose-raw
```

Post-decision diagnostics are materialized with the normal build:

```sh
uv run forestcensus build
uv run forestcensus validate
uv run forestcensus invariants
uv run forestcensus canonical-review
```

Current comparison:

| Diagnostic | Raw | Post-decision | Delta |
|---|---:|---:|---:|
| Validation issues | 1,765 | 1,987 | +222 |
| Invariant findings | 2,227 | 2,043 | -184 |
| Trees with invariant findings | 714 | 688 | -26 |
| `W_TAXON_CONFLICT` | 39 | 2 | -37 |
| `W_ALIVE_HEALTH_CONFLICT` | 12 | 0 | -12 |
| `W_BELOW_THRESHOLD_DBH` | 172 | 149 | -23 |
| `W_DBH_JUMP` | 288 | 234 | -54 |
| `W_TREE_RANKED_DBH_JUMP` | 258 | 234 | -24 |
| `I_ZOMBIE_TREE` | 103 | 96 | -7 |
| `I_CORRECTED_ROW` | 0 | 394 | +394 |

The `I_CORRECTED_ROW` increase is expected: it is the audit signal that accepted decisions touched canonical rows. It is not an unresolved problem by itself.

Selected invariant movement:

| Invariant | Raw | Post-decision | Delta |
|---|---:|---:|---:|
| `taxon_conflict` | 39 | 2 | -37 |
| `mortality_contradiction` | 126 | 106 | -20 |
| `single_survey_dbh_outlier` | 138 | 124 | -14 |
| `stable_incompatible_dbh_era` | 91 | 78 | -13 |
| `max_dbh_jump` | 33 | 13 | -20 |
| `ranked_dbh_jump` | 15 | 11 | -4 |
| `subthreshold_dbh_present` | 172 | 149 | -23 |
| `new_persistent_large_stem` | 44 | 39 | -5 |
| `tag_scope_note_review` | 13 | 12 | -1 |
| `source_note_dbh_conflict` | 21 | 18 | -3 |
| `persistent_dbh_regime_shift` | 16 | 10 | -6 |

## Next step

The next useful move is to make the UI decision-writing path emit the same operation vocabulary:

- `set_field`
- `suppress_field`
- `suppress_observation`
- `set_taxon`
- `set_status`
- `interpret_as_not_found`
- `reassign_identity_row`
- `split_identity`
- later: `accept_no_change`, `accept_link`, `reject_link`

Then remaining review cases can be resolved by adding decisions to the same ledger and re-running the raw -> decisions -> post-decision verification loop.

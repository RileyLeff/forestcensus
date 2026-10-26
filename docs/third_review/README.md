# Third review

Date: 2026-05-11

Purpose: parallel investigation of the current flagged tag surface after the pipeline was split into raw diagnostics, configured decisions, and post-decision diagnostics.

Agents should write one shard report each under `docs/third_review/agent_shards/`. Reports are investigation notes only: do not edit config, source data, generated outputs, or decision files from a shard.

## Case schema

Each assigned tag should be reported with:

| Field | Meaning |
|---|---|
| `selection` | Bare tag plus relevant plot/UUID scope found during review. |
| `related_uids` | Canonical UUIDs touched by the tag and any linked UUIDs worth considering. |
| `raw_flags` | Important pre-decision diagnostics/invariants. |
| `configured_decisions_applied` | Existing configured decisions matched to the selection. |
| `current_flags` | Important post-decision diagnostics/invariants. |
| `evidence_summary` | Compact description of the observation history and any source notes. |
| `interpretation` | Best explanation of what is going on. |
| `recommended_action` | Suggested action: human call, source check, rule candidate, already handled, or no change. |
| `decision_scope` | Suggested scope if a decision is needed: source row, UUID, tag-plot, candidate link, taxon, mortality/status, DBH field, or stem profile. |
| `confidence` | `high`, `medium`, or `low`. |
| `needs_riley_call` | `yes` if field/source judgment is needed. |
| `candidate_auto_rule` | Repeated pattern that might become a rule-generated decision. |
| `source_rows_to_check` | Specific source rows/files if applicable. |

## Synthesis targets

After shard reports come back, synthesize into:

- human/source attention queue updates
- candidate auto-rule/decision-generator list
- already-handled or diagnostic-noise list
- cases that challenge the current review criteria

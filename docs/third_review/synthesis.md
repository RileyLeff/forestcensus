# Third review synthesis

Date: 2026-05-11

Status: all ten agent shards completed.

This pass reviewed the current flagged bare-tag surface after the pipeline split into:

1. raw diagnostics
2. configured decisions
3. post-decision/current diagnostics

The shard reports are in `docs/third_review/agent_shards/shard_*.md`.

## Intake status

| Shard | Tags | Status | Main signal |
|---|---:|---|---|
| 01 | 22 | complete | rule candidates, source-era DBH blocks, bracketed death labels |
| 02 | 22 | complete | source checks, mortality rules, multi-stem Morella context |
| 03 | 22 | complete | source-era DBH blocks, row outliers, note-only taxon artifacts |
| 04 | 22 | complete | source-row corrections, single death rows, early-source DBH regimes |
| 05 | 22 | complete | clean identity links, source-row corrections, mortality/status calls |
| 06 | 22 | complete | DBH suppression candidates, blank stem backfills, source-era blocks |
| 07 | 22 | complete | old-tag links, mortality rule candidates, diagnostic downgrades |
| 08 | 21 | complete | human/source calls, bracketed death rows, source-era clusters |
| 09 | 21 | complete | safe dead-only links, source endpoints blocking links, DBH strikes |
| 10 | 21 | complete | DBH correction candidates, endpoint-specific link review, stem backfills |

## Overall read

The agents converged strongly. Most raw and current flags are identical, which means the remaining cases are not mostly failures of the new configured-decision phase. They are unresolved post-decision cases.

The review surface now splits into four useful workflows:

1. **Rule-generated decision candidates**
   These are repeated enough, scoped enough, and biologically plausible enough to generate candidate decisions automatically, then verify post-decision.

2. **Source-row correction candidates**
   These are likely fixes, but the exact value/action often depends on whether the source sheet supports correction versus suppression.

3. **Human/source calls**
   These need Riley/Juan/source-sheet judgment because they involve tag identity, field plausibility, marginal live tissue, or source-era alignment.

4. **Diagnostic tuning/watch**
   These are useful context but should not keep cases in urgent review.

## Candidate decision generators

These patterns are strong enough to implement as generated candidate decisions, ideally written to the unified decision vocabulary but still reviewable before acceptance.

| Pattern | Candidate operation | Guardrails | Example cases |
|---|---|---|---|
| One observed-dead/health-0 row bracketed by observed-alive rows | `set_status` to uncertain/missing or alive-consistent interpretation | Do not apply if there is explicit true-death context, a long dead run, tag identity ambiguity, or later persistent death that may be a separate event. | L7/5032, L7/14, M5/2500, L0/477, L1/131, M0/514, M4/2451, L5/425, H4/113, H1/221 |
| Explicit note contradicts prior death, e.g. `marked dead last year`, `not dead` | `set_status` for the earlier death row | Keep source evidence; apply only to the referenced prior-row window. | M7/325, H7/459, H7/460, M1/843 |
| Clean dead-only old-tag link | `accept_link` / identity alias candidate | Same plot, compatible taxon/status, no conflicting DBH, target lacks contradictory live history. | L0/157, M7/5832 -> M7/914, L5/413 -> L5/985, likely L7/506 -> L7/974 |
| Bounded missing secondary stem in otherwise stable multistem profile | blank/not-reported stem backfill | Stem rank is survey-local; only add blank rows as profile scaffolding, not persistent stem identity. | R2/626, R4/5213, R3/684, R4/5224, H6/529 |
| Single isolated DBH outlier bracketed by stable neighboring values | `suppress_field` for DBH, or source-check correction candidate | Prefer suppression unless the source gives a clear intended value. Do not apply to stable era shifts. | M7/326, R4/5206, H3/160, R4/5236, L5/414, L1/5060, M6/362 |
| Probable duplicate/near-duplicate extra stem appearing once | `suppress_observation` or `suppress_field` candidate | Do not apply when later surveys support a real second stem or notes say added/new/noticed. | H0/286, H2/208 needs review before applying, R1/961, selected May 2024 duplicate cases |

## Human/source calls

These should remain in a human attention queue, not become automatic rules yet.

| Category | Why not automatic | Examples |
|---|---|---|
| Stable incompatible DBH eras | Looks like source-era/tag alignment, missing-leading-digit carry-forward, or historical source integration error. Needs grouped source review, not per-row blind edits. | H4/136-152 block, H1/233/235/239/241, L6/61/69/70/77/83, M1/831/860, H5/550, L4/247/248 |
| Candidate links with noisy endpoints | Explicit old-tag evidence may be real, but endpoint mortality/DBH/taxon conflicts must be resolved first. | L7/5029 -> L7/982, H5/559 -> H5/912, H4/136 -> H4/992, M2/5863 -> M2/5883, L4/243 -> L4/925 |
| Marginal live tissue / true zombie ambiguity | Low-health alive after dead labels may be real field biology, not a typo. | M3/356, M3/5189, L1/5050, L6/101, L7/498, M7/336, M7/5835 |
| Tag/stem scope notes | Notes like `new tag`, `tag on trunk`, `to 5051`, `NO second stem`, or `could be one of the new tags` imply identity/stem-scope uncertainty. | M7/5274, L6/87, L6/91, L1/5052 |
| Note-only taxon/stem artifacts | Some conflicts come from notes rows rather than true measured observations. | R2/631, M4/2444 |
| Multistem Morella/cluster mortality | Rank is emergent, stems are not individually tagged, and live/dead stems can coexist. | M5/487, L5/704, H0/274, R1/963 |

## Source-row correction queue

These look like high-value row-level checks. The likely decision is often DBH suppression if the original sheet does not support an exact correction.

| Pattern | Examples |
|---|---|
| Isolated high/low DBH spike between stable values | H3/160, M4/2453, R4/5236, M7/326, L1/5060, M6/362 |
| Dead-tree DBH rebound/increase after stable lower dead values | L5/418, L7/6, H1/199, L2/198, M7/319, L7/12 |
| Source-note conflict around DBH | M7/320, H4/992, L4/615, L1/107 |
| Early low DBH likely missing leading digit or source-era issue | H4/147, H4/148, H4/150, L6/70, H7/887 |
| One row mixing mortality and DBH implausibility | M0/585, M5/2496, M0/816, L3/5886 |

## Diagnostic tuning / watch

These should stay visible but should not necessarily count as urgent review.

| Tuning target | Suggested behavior |
|---|---|
| Dead-tree DBH loss | Preserve as context. Only escalate isolated increases/rebounds or source-note contradictions. |
| Knot/split/measurement-point notes | Some DBH jumps should downgrade to watch/context rather than source-row correction. |
| Morella/cluster rank churn | Treat ranked jumps as context unless there is whole-tree contradiction or duplicate rows. |
| Threshold-edge secondary stems | Sub-50 mm stems should remain evidence but not qualifying canonical stems. Exact 50 mm qualifies; 48-49 should not inflate stem-profile review. |
| Post-decision residual flags | A current flag after an existing configured decision can mean the original correction worked but a biological/status question remains. Do not treat this as decision failure. |

## Recommended next implementation order

1. Add a machine-readable decision-candidate output for **generated but not yet accepted** decisions.
   This should be separate from accepted `configured_decisions.csv`, but use the same operation vocabulary.

2. Implement candidate generators for:
   - bracketed single-survey death labels
   - explicit death-correction notes
   - clean dead-only old-tag links
   - blank missing-stem backfills
   - isolated DBH outlier suppression candidates

3. Add a review/acceptance path in the UI:
   - show generated candidate decisions beside raw/current flags
   - allow accept/reject/defer
   - accepted decisions flow into the same unified decision layer

4. Keep the following as human queues:
   - source-era DBH blocks
   - noisy candidate links
   - marginal-live zombie cases
   - tag/stem scope notes
   - note-only taxon artifacts

5. After candidate generation, rebuild and compare:
   - raw diagnostics
   - accepted decisions
   - generated candidate decisions
   - post-decision diagnostics

## Open design question

Generated candidate decisions should probably not be silently applied. The clean architecture is:

```text
raw observations
  -> raw diagnostics
  -> accepted manual decisions
  -> generated candidate decisions
  -> reviewer accepts/rejects candidates
  -> accepted decision ledger
  -> canonical build
  -> post-decision diagnostics
```

This preserves the user's concern that there should be one accepted decision phase, while still letting the system propose high-confidence repeated fixes.

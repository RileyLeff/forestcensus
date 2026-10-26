# Canonical review synthesis

Date: 2026-05-10

Scope: synthesis from the first five `Tags -> needs_review` review passes, covering the first 125 bare tags in the current UI ordering. This document is not a correction log and does not apply changes. It is the current rule/doctrine proposal before pipeline changes.

## Operating assumptions

### Decision scope

Bare tag review is a useful way to surface noise, but decisions should apply at UUID/tag-plot scope. Bare tags collide across plots and often group unrelated cases.

Evidence should not be deleted when canonical values are corrected. The right model is usually: preserve the observation row and source evidence, but suppress, strike, or reinterpret the specific canonical field that is not trusted.

### October 2025 DBH protocol

October 2025 is the transition survey where DBH collection stopped partway through. From October 2025 onward:

- Missing DBH is protocol-valid.
- Missing DBH must not trigger stem disappearance, missing-measurement suspicion, or mortality inference by itself.
- Health/status/alive/standing observations remain valid evidence even when DBH is absent.
- If an October 2025 row does contain DBH, preserve it as valid evidence rather than discarding it because the protocol changed.

### Dead trees and DBH loss

Dead trees can genuinely lose DBH. Decay, falling, snapping, bark loss, chunk loss, and measurement-access changes are all real forest processes. DBH loss on dead trees should be treated as potentially meaningful ecological/structural signal, not automatically as error.

Dead-tree DBH jumps should be downgraded when the only issue is intermittent measurement or gradual/moderate loss. They should still be reviewed when the shape looks like a one-off typo, a digit loss, a rebound, a source contradiction, or possible tag confusion.

### Mortality and missingness

Missing/not-found rows alone should not create zombie events. A zombie/mortality contradiction requires observed dead/health 0 or observed dead status followed by observed alive/nonzero-health evidence.

One-survey or short-run missingness should usually remain missing/unknown if later alive evidence returns. If absence crosses the configured missing threshold, posthoc inferred death can apply, but those inferred dead rows should be convertible back to missing/unknown if later observed alive evidence appears.

## Common failure modes

### May 2024 duplicate-stem artifact

Pattern: a stable one-stem tree gains an extra stem in May 2024 with exactly the same DBH as an existing stem, then returns to one stem in the next survey. This appears across H2 and H0 and recurs outside those dense runs.

Examples include H2/175-180, H2/181-191, H2/193-196, H2/201-207, H0/255-289, H2/195, H2/205, and H4/149 in June 2023 as a related duplicate-slot case.

Proposed rule: classify as probable duplicate-entry stem when all are true:

- stem count increases by one in a survey,
- the new stem has exact duplicate DBH relative to another stem on the same tree/survey,
- no note supports a true new stem,
- the extra duplicate stem disappears in the adjacent later survey.

Action: suppress the duplicate stem from canonical DBH profile and stem count, while preserving the evidence row. If duplicate rows disagree on health/status, require manual field-survival choice.

Guardrails:

- Do not suppress all evidence for a second stem if a plausible second stem appears later, as in H2/208.
- Cluster notes such as "same tree" or "likely one multistem tree" should escalate to identity/plant-boundary review, not blind duplicate cleanup.

### Subthreshold and threshold-edge DBH

The survey threshold is DBH >= 50 mm. Treat 50 as qualifying. DBH below 50 should not contribute to canonical DBH/stem profiles.

If a tree has ever qualified, preserve its identity and health/status evidence even when later measured DBH falls below 50. If a tree never convincingly qualifies, exclude it from canonical survey evidence.

Examples: H1/198, H1/224, H1/230, H1/231, L2/233, H0/278, L3/289, H4/149 side stems.

Action: strike subthreshold DBH values from canonical DBH fields, preserve observation/status evidence where the tree identity remains relevant.

### Persistent DBH regime shifts

Pattern: early values are very different from later values, and the later values remain internally stable for years. This is not normal growth and not a one-row typo.

Examples:

- H4/138: 270 -> stable ~105.
- H4/145: 372 -> stable ~100.
- H4/150: 67 -> stable ~380.
- H4/147: 65 -> stable ~130.
- H1/233: 353 -> stable ~70.
- H1/235: 194 -> stable ~310.
- L1/116: 260 -> stable ~170.

Likely causes: old-source integration errors, tag confusion, measuring a different stem/tree, measurement location changes, or source-column/entry problems.

Action: source/identity review, not automatic correction. Search original sheets and complementary nearby tags before deciding whether to strike early values, move rows to another identity, or preserve with notes.

### Single-survey or short-run DBH outliers

Pattern: one value or a short run diverges sharply, then later observations return to the previous level.

Examples:

- H0/286: 315 -> 155 -> 307.
- L1/110: 332 -> 132 -> 330.
- H3/160: ~500 -> 407 -> ~491.
- H4/152: 99 -> 61/64 -> 96.
- L2/219: 155 -> 55, likely digit loss or bad measurement.

Action: create a `single_survey_dbh_outlier` or `short_run_dbh_outlier` diagnostic. These are candidates for per-case correction, especially when the shape is rebound-like.

Dead-tree caveat: dead trees can lose DBH legitimately. Only keep high severity when the pattern is rebound-shaped, digit-loss-shaped, contradicted by trusted later observations, or unsupported by notes.

### Dead-tree DBH gaps and structural change

Pattern: dead tree has DBH, then missing rows, then DBH again, or dead tree gradually loses DBH.

Examples recur throughout L0/L1/L2/L3/L4: L2/227, L3/274, L1/140, L2/208, L0/194, L2/201, L2/206, L2/207, L4/264, L6/103, H4/132, L1/143, L0/168.

Action: downgrade DBH-gap-only findings on dead trees. Preserve DBH loss as signal where plausible. Surface notes like broken, snapped, fallen, no bark, tag hidden, lost tag, poison ivy, vine, or knot.

### Mortality/zombie contradictions

Pattern: observed dead/health 0 followed by observed alive/nonzero health, or alive label with death-like health conflicts.

Examples: L0/181, L0/186, H4/113, L1/129, H1/221, L2/224, H1/230, L1/108.

Action: route to mortality/zombie review. Do not solve these through DBH cleanup. Dead status with low health that never recovers can often become health 0; dead status followed by later strong alive evidence often means the death label was wrong or should become missing/uncertain.

### Missing/not-found alive trees

Pattern: a living tree is missing for one survey or a short period, then reappears alive.

Examples: L1/149, H4/127, L1/124, L0/158, L0/167, H1/229, L0/169.

Action: downgrade to missing/not found. Do not infer death unless the missing-threshold rule is met, and reverse inferred death if later alive evidence returns.

### Cluster and identity boundary notes

Pattern: notes indicate multiple tags may be one plant, a tag is scratched/lost/hidden, or field workers were uncertain about plant boundaries.

Examples: H2/185-191 cluster, H0/274/H0/275, H4/149, lost-tag dead cases.

Action: escalate to identity/plant-boundary review. Duplicate-stem cleanup may still apply inside the cluster, but do not merge or split UUIDs automatically.

### New persistent stems above threshold

Pattern: a new stem above 60 mm appears and persists. It was probably previously missed or was already above threshold before the first recorded measurement.

Examples: H3/153, H1/242, H4/119.

Action: consider blank back-history for earlier surveys, especially when the tree identity is otherwise stable. Do not pretend the stem began existing only when first recorded.

## Correction categories

### High-confidence batch/rule corrections

These can likely be implemented as rule-assisted corrections with review/audit output:

- Probable May 2024 exact duplicate-stem suppression.
- Subthreshold DBH suppression for canonical DBH/stem profile.
- October 2025+ missing DBH ignored for stem-disappearance diagnostics.
- Dead-tree DBH-gap downgrades when no other contradiction exists.
- Missing blank rows not counted as measured stems.

### High-confidence per-case corrections already identified

These should be represented explicitly in correction config with notes:

- L2/223: strike DBH for June 2022, June 2023, and May 2024; preserve observation/status evidence. Trust October 2024 and October 2025 field context more strongly.
- H4/149 June 2023: duplicate-slot/duplicate-stem candidate; strike duplicate DBH/stem contribution unless original sheet proves four distinct stems.
- Previously discussed manual corrections in `config/corrections.toml` should be displayed as prior decisions so they are not relitigated.

### Review-only categories

These should remain human review until we inspect original sources or complementary tags:

- Persistent DBH regime shifts.
- Cluster/plant-boundary notes.
- Tag-change or wrong-tag candidates.
- Duplicate DBH rows with conflicting health/status fields.
- New large stems that persist and need blank back-history.
- Mortality/zombie contradictions.

## Proposed diagnostic changes

Implemented reclassification replaces or supplements generic `max_dbh_jump`/`qualifying_rank_gap` with more specific labels:

- `probable_duplicate_stem_artifact`
- `duplicate_stem_conflicting_fields`
- `subthreshold_dbh_present`
- `oct_2025_protocol_missing_dbh`
- `dead_tree_dbh_gap`
- `dead_tree_dbh_loss`
- `single_survey_dbh_outlier`
- `short_run_dbh_outlier`
- `persistent_dbh_regime_shift`
- `cluster_identity_note`
- `mortality_contradiction`
- `sharp_health_drop_to_observed_dead`
- `sharp_health_rebound`
- `source_note_dbh_conflict`
- `measurement_note_dbh_context`
- `dead_low_health_to_zero_candidate`
- `dead_label_low_health_later_alive`
- `missing_then_refound_alive`
- `new_persistent_large_stem`
- `blank_missing_stem_backfill_candidate`

Review severity should be computed from these labels rather than from raw `max_dbh_jump` and `qualifying_rank_gap` alone.

Candidate tag-change links now carry their own `review_status` and `review_reason`. Benign-looking tag-change assertions are routed as `rule_assisted_link`; links with taxon conflicts, mortality/DBH review findings, no comparable DBH profile, or large whole-tree DBH mismatch remain `candidate_identity_link` for human review.

Current status buckets after reclassification are:

- Needs review: taxon/identity conflicts, mortality contradictions, isolated or persistent DBH outliers, unresolved raw DBH jumps, new persistent stems, blank-gap stem backfill candidates, and first-qualifying-after-prior-observation cases.
- Watch: probable duplicate-stem artifacts, subthreshold DBH values, dead-tree DBH gaps/loss, October 2025 protocol DBH omissions, nonqualifying excluded trees, note context, and recent-missing context.
- Quiet: cases without review/watch status after the current rules.

Current rebuilt counts after the second-pass implementation:

- UI status: 360 `needs_review`, 493 `watch`, 28 `quiet`.
- Review buckets: 35 `candidate_identity_link`, 7 `rule_assisted_link`, 130 `mortality_review`, 102 `dbh_review`, 148 `stem_profile_review`, 198 `watch_context`.
- Candidate links: 18 `needs_human`, 9 `watch`.

The stricter mortality/health rules intentionally surface more human-review cases than the first pass, especially zombie and sharp health rebound/drop cases. The link-specific routing reduces ordinary tag-change noise, but it does not hide mortality contradictions.

## Proposed next work

1. Encode the operating assumptions in code comments/config docs where diagnostics are defined.
2. Implement rule-assisted diagnostic reclassification without changing canonical data yet.
3. Add correction-config entries for the per-case decisions we already made, starting with L2/223.
4. Regenerate `output/canonical_review` and `output/diagnostics`.
5. Compare counts before/after for `needs_review`, `watch`, and `quiet`.
6. Resume human review on the reduced set, sorted by the new diagnostic subtype rather than raw tag order.

The guiding principle: common failure modes should become rules; weird one-offs should become explicit per-case corrections; all original evidence stays available.

# Rule consolidation

Date: 2026-05-10

This note summarizes the second-review lessons that have now been incorporated into the pipeline diagnostics.

## Implemented routing

These are still human-review cases because a person may need to change a row, split/merge an identity, or inspect a source sheet:

| Diagnostic code | Meaning |
|---|---|
| `taxon_conflict` | Canonical rows for a UUID disagree on taxon. |
| `mortality_contradiction` | Alive/dead/health evidence still genuinely conflicts after context rules are applied. |
| `single_survey_death_label_outlier` | One observed-dead row is bracketed by observed-alive surveys. |
| `single_survey_dbh_outlier` | A DBH value is isolated and neighboring surveys return to the previous baseline. |
| `persistent_dbh_regime_shift` | DBH changes into a new stable regime, suggesting identity/source/measurement-regime confusion. |
| `dead_tree_dbh_increase` | Dead-tree DBH increases sharply; dead-tree DBH losses are allowed, increases are suspicious. |
| `source_note_dbh_conflict` | Source notes directly question the DBH or make the measurement uncertain. |
| `new_persistent_large_stem` | A qualifying stem appears without enough context to call it threshold-edge, added, dead-stem, or duplicate-like. |
| `blank_missing_stem_backfill_candidate` | A qualifying stem disappears without enough context to call it dead-stem, October 2025 protocol, or bounded-rank context. |

These are watch/context or rule-assisted cases. They should stay visible, but should not automatically keep the case in the urgent human-review stream:

| Diagnostic code | Meaning |
|---|---|
| `observed_mortality_event` | High health drops to observed dead with no later observed-alive evidence. |
| `health_rebound_alive_context` | Health rebounds, but adjacent surveys are both observed alive. |
| `health_rebound_new_stem_context` | Tree-level max health rebounds because a different/new stem enters the profile. |
| `stem_mortality_context` | Notes or mixed stem health suggest stem-level mortality rather than whole-tree zombie behavior. |
| `dead_tree_dbh_loss` | Dead-tree DBH decreases; this can be real decay/breakage signal. |
| `dead_tree_dbh_gap` | Dead-tree DBH profile has a bounded gap. |
| `dead_tree_stem_context` | Stem-count/profile change occurs while the tree is deadish. |
| `bounded_stem_rank_gap` | A non-primary ranked stem disappears and reappears; use blank-stem rows rather than treating rank as persistent identity. |
| `measurement_note_dbh_context` | Poison ivy, vines, knots, split stems, or non-circular trunks plausibly explain measurement variation. |
| `threshold_edge_dbh_context` | DBH/stem behavior occurs around the 50 mm inclusion threshold. |
| `prior_dead_first_qualifying_dbh` | First qualifying DBH appears after prior observed-dead evidence. |
| `prior_live_blank_dbh_history` | Prior observed live evidence exists before first qualifying DBH; candidate for blank history, but not necessarily an error. |
| `new_noticed_stem_context` | Notes say a stem/trunk was added or newly noticed. |
| `merge_note_context` | Notes explicitly mention merge/combine behavior. |
| `near_duplicate_stem_artifact` | A May 2024 one-stem count change has near-identical DBH values and likely reflects duplicate entry. |
| `oct_2025_protocol_missing_dbh` | October 2025 and later surveys may omit DBH by protocol. |
| `subthreshold_dbh_present` | DBH below 50 mm is preserved as evidence but excluded from qualifying profiles. |

## Rebuild counts

After applying the consolidated classifier and rebuilding `output/diagnostics/invariants.csv`:

| Metric | Count |
|---|---:|
| Invariant findings | 2,016 |
| Trees with findings | 688 |
| `stem_mortality_context` | 122 |
| `measurement_note_dbh_context` | 98 |
| `observed_mortality_event` | 34 |
| `single_survey_death_label_outlier` | 19 |
| `dead_tree_dbh_increase` | 28 |
| `near_duplicate_stem_artifact` | 20 |
| `bounded_stem_rank_gap` | 32 |

After rebuilding `output/canonical_review/tree_cases.csv`, the UI-facing status split is:

| Status | Count |
|---|---:|
| Needs review | 233 |
| Watch/context | 648 |

Remaining needs-review codes are mostly `mortality_contradiction`, `persistent_dbh_regime_shift`, `single_survey_dbh_outlier`, `new_persistent_large_stem`, `single_survey_death_label_outlier`, DBH jumps, and dead-tree DBH increases.

## Policy reminders

- DBH is no longer collected as of October 2025 onward; missing October 2025 DBH is not inherently suspicious.
- Dead trees can legitimately lose DBH through decay, breakage, or fallen chunks.
- Stem rank is survey-local, not persistent identity. Use rank profiles for diagnostics, but do not infer hard stem identity from rank alone.
- Alive/dead can be row/stem-level evidence in old sources. A multi-stem tree can have live and dead stems at the same survey.
- Subthreshold DBH evidence should not qualify a tree/stem for the census, but the source row can still matter for field-history context.

## Second consolidation

The later 25-case review passes surfaced a few repeated patterns that are now routed more explicitly.

| Diagnostic code | Stream | Meaning |
|---|---|---|
| `stable_incompatible_dbh_era` | Human review | Adjacent multi-survey DBH eras are internally stable but mutually incompatible, suggesting source-era/tag alignment or identity confusion rather than ordinary growth. |
| `structural_measurement_dbh_context` | Watch/context | Notes such as horizontal, falling, bent, broken, snapped, or girdled plausibly explain inconsistent DBH measurement position. |
| `cluster_measurement_dbh_context` | Watch/context | Cluster/clump notes explain why DBH/stem profiles may be unstable without implying a simple typo. |
| `single_survey_low_health_death_label_outlier` | Rule-assisted cleanup | A low-health alive sequence has one observed-dead row bracketed by observed-alive evidence. |
| `explicit_note_mortality_correction_candidate` | Rule-assisted cleanup | Notes such as `marked dead last year` or `not dead` explicitly contradict an earlier observed-dead label. |

This pass also keeps `persistent_dbh_regime_shift` as a fallback, but most stable-era cases now get the more precise `stable_incompatible_dbh_era` code.

## Rebuild counts after second consolidation

After rebuilding `output/diagnostics/invariants.csv` and `output/canonical_review/tree_cases.csv`:

| Metric | Count |
|---|---:|
| Invariant findings | 2,043 |
| Trees with findings | 688 |
| `stable_incompatible_dbh_era` | 104 |
| `persistent_dbh_regime_shift` | 8 |
| `structural_measurement_dbh_context` | 75 |
| `single_survey_low_health_death_label_outlier` | 27 |
| `explicit_note_mortality_correction_candidate` | 15 |
| `mortality_contradiction` | 108 |
| `single_survey_dbh_outlier` | 96 |
| `new_persistent_large_stem` | 51 |

UI-facing case status after this rebuild:

| Status | Count |
|---|---:|
| Needs review | 226 |
| Watch/context | 627 |
| Quiet | 28 |

The queue is still large, but the remaining needs-review set is now better partitioned: source-era/tag-alignment cases are named directly, low-health one-survey death labels are no longer mixed with high-confidence mortality contradictions, and structural/cluster measurement contexts are visible without automatically demanding urgent correction.

## Fourteenth-batch consolidation

The final unseen needs-review batch added three routing refinements.

| Diagnostic code | Stream | Meaning |
|---|---|---|
| `dead_tree_stable_dbh_loss_context` | Watch/context | All compared observations are deadish and the later stable DBH era is lower; this is usually decay, breakage, or changed measurability rather than identity chaos. |
| `early_low_dbh_source_era_candidate` | Human review | 2019-2020 have repeated low DBHs followed by a much larger stable modern era; this may be a missing-leading-digit carry-forward or source/tag alignment issue. |
| `morella_cluster_rank_jump_context` | Watch/context | Ranked DBH jumps in multistem Morella/cluster profiles are likely survey-local rank instability rather than persistent stem identity errors. |

After rebuilding:

| Metric | Count |
|---|---:|
| Invariant findings | 2,043 |
| Trees with findings | 688 |
| `dead_tree_stable_dbh_loss_context` | 12 |
| `early_low_dbh_source_era_candidate` | 14 |
| `morella_cluster_rank_jump_context` | 3 |
| `stable_incompatible_dbh_era` | 78 |
| `ranked_dbh_jump` | 15 |

UI-facing case status after this rebuild:

| Status | Count |
|---|---:|
| Needs review | 220 |
| Watch/context | 633 |
| Quiet | 28 |

## Random QA consolidation

The three random QA passes found that the broad routing is working, but a few context rules needed tighter scope.

| Diagnostic code | Stream | Meaning |
|---|---|---|
| `tag_scope_note_review` | Human review | Notes such as `to 5051`, `NO second stem`, `new tags`, or similar tag/stem-scope comments are identity/stem-scope ambiguity and should not be hidden by general measurement context. |
| `dead_tree_threshold_dbh_context` | Watch/context | Small dead or failing stems near the 50 mm threshold can lose measurable DBH without implying source or identity confusion. |
| `threshold_multistem_gap_context` | Watch/context | Small multistem profiles with one bounded threshold-ish stem gap are usually stem-accounting context rather than urgent identity review. |

Implementation details from this pass:

- Structural DBH notes now have to be temporally local to the offending survey pair. Later `girdling`, `falling`, `leaning`, or similar notes no longer explain older unrelated DBH jumps.
- Exact 50 mm threshold cases are treated as threshold-edge context, not only values strictly below 50 mm.
- Missing-from-October priority is limited to trees whose last pre-October status is alive. Long-dead or already inferred-dead trees are no longer elevated just because they lack an October 2025 row.
- Probable duplicate stem routing now respects explicit multistem notes such as `two trunks`.
- Near-duplicate stem cleanup no longer triggers when notes say the stem was `Added` or newly noticed.

After rebuilding:

| Metric | Count |
|---|---:|
| Invariant findings | 2,043 |
| Trees with findings | 688 |
| `tag_scope_note_review` | 12 |
| `dead_tree_threshold_dbh_context` | 27 |
| `threshold_multistem_gap_context` | 26 |
| `threshold_edge_dbh_context` | 18 |
| `structural_measurement_dbh_context` | 6 |
| `near_duplicate_stem_artifact` | 58 |
| `probable_duplicate_stem_artifact` | 401 |

UI-facing case status after this rebuild:

| Status | Count |
|---|---:|
| Needs review | 225 |
| Watch/context | 625 |
| Quiet | 28 |

Verification:

- `uv run python -m compileall src/forestcensus`
- `uv run forestcensus build && uv run forestcensus validate && uv run forestcensus invariants && uv run forestcensus canonical-review`
- `uv run pytest`
- `npm run check` in `canonical-ui`

## Targeted QA follow-up

The targeted post-consolidation QA pass made two additional routing fixes.

| Diagnostic/bucket | Stream | Meaning |
|---|---|---|
| `tag_or_stem_scope_review` | Human review bucket | `tag_scope_note_review` now has user-facing language for tag/stem-scope ambiguity instead of being bundled under taxon conflict. |
| `threshold_new_stem_context` | Watch/context | A newly recorded secondary stem around 50-60 mm in a clustered taxon, currently Morella, is treated as threshold/newly-noticed-stem context rather than urgent stem-profile review. |

After rebuilding:

| Metric | Count |
|---|---:|
| `threshold_new_stem_context` | 4 |
| `new_persistent_large_stem` | 39 |
| `tag_or_stem_scope_review` cases | 4 |
| `taxon_or_identity_conflict` cases | 2 |

UI-facing case status after this rebuild:

| Status | Count |
|---|---:|
| Needs review | 223 |
| Watch/context | 627 |
| Quiet | 28 |

Verification:

- `uv run python -m compileall src/forestcensus`
- `uv run forestcensus build && uv run forestcensus validate && uv run forestcensus invariants && uv run forestcensus canonical-review`
- `uv run pytest`
- `npm run check` in `canonical-ui`

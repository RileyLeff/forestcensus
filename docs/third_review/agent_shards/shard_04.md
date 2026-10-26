# Third review shard 04

Assigned cases reviewed: 22 tags.

Configured decisions matched to these selections: none found in `output/decisions/configured_decisions.csv`.

## Action summary

| recommended_action | count | Cases |
|---|---:|---|
| `source check / human call` | 9 | M3/359, H5/912, M5/2477, M3/911, L7/25, L6/54, H6/523, H4/141, L7/18 |
| `source-row correction candidate` | 5 | L6/49, L3/300, M5/2496, M7/331, L2/224 |
| `rule-generated decision candidate` | 5 | R2/634, H0/274, R2/622, M1/872, M1/843 |
| `source check, possible rule candidate` | 2 | L4/248, M6/400 |
| `no immediate change / watch context` | 1 | H5/567 |

## Recurring patterns

- Single-survey death labels bracketed by alive evidence are common and often high-confidence row corrections, especially when there is no DBH measured on the dead row or an explicit note contradicts it.
- Dead-tree DBH gaps are mostly context, not problems. The issue is mortality/status inconsistency, not the bounded missing DBH.
- Explicit tag-change assertions need endpoint review before aliasing: several link endpoints are dead-only or have incompatible DBH profiles.
- Early-source DBH regimes are still surfacing. Some look like missing-leading-digit errors; others may be old source/tag alignment issues and should not be auto-fixed without a source check.
- Subthreshold stems nested under a qualifying tree still need a clear policy. H0/274 suggests that <50 mm stems are inflating stem-profile diagnostics even when the tree itself qualifies.

## Cases

### M3/359

| Field | Notes |
|---|---|
| `selection` | M3/359; UUID `a26b4e51d253336c`; linked to M3/911 by explicit tag-change assertion. |
| `related_uids` | `a26b4e51d253336c`; linked target `bb32debd90a06d9c` for M3/911. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction` x2; `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | June 2019 alive, DBH 159, health 2; June 2020 through May 2024 observed dead/health 0; October 2024 DBH 162, health 6 but `alive=False`, interpreted alive; April 2025 and October 2025 dead/health 0. Candidate link says old M3/359 -> new M3/911 in 2023. |
| `interpretation` | The 2024 fall row is the direct mortality contradiction. Because `alive=False` but health is 6, this is probably a row-level health/status transcription or field-entry conflict. The M3/359 -> M3/911 link should not be accepted blindly because M3/359 continues to have post-2023 observations. |
| `recommended_action` | Source check / human call. Check October 2024 M3/359 row and the tag-change assertion to decide whether health 6 should be 0, whether alive/dead is wrong, or whether M3/911 is a duplicate tag. |
| `decision_scope` | Source row for October 2024 M3/359; candidate link M3/359 -> M3/911. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | None; high-health single row in otherwise dead tree should be review, not auto. |
| `source_rows_to_check` | `2024_fall.csv:687`; candidate link `link_d42fb926b4695175`; M3/911 rows below. |

### L6/49

| Field | Notes |
|---|---|
| `selection` | L6/49; UUID `3595ec013f46ca9e`. |
| `related_uids` | `3595ec013f46ca9e`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `single_survey_death_label_outlier`; `explicit_note_mortality_correction_candidate`; `qualifying_rank_gap`; `health_rebound_new_stem_context`; `observed_mortality_event`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Alive DBH 195 health 10/10/7 in 2019-2021; June 2022 has no DBH, health 0, observed dead, note `standing`; June 2023 resumes alive DBH 200 health 7 with note `Marked dead last year`; alive through April 2025; October 2025 observed dead health 0. |
| `interpretation` | June 2022 is a high-confidence false death/not-found row. The 2023 note explicitly says the previous death label was suspect. October 2025 is a separate later mortality event and should remain. |
| `recommended_action` | Source-row correction candidate. Convert June 2022 observed-dead/health-0 to uncertain/not-found or otherwise suppress its mortality status while preserving the blank DBH gap. |
| `decision_scope` | Source row mortality/status and health for June 2022. |
| `confidence` | High. |
| `needs_riley_call` | No, unless choosing exact representation for uncertain status. |
| `candidate_auto_rule` | Single dead row with no DBH bracketed by alive observations plus later note like `marked dead last year` -> treat earlier death label as uncertain. |
| `source_rows_to_check` | `2023_and_prior.csv:400`; supporting `2023_and_prior.csv:4636`. |

### H5/912

| Field | Notes |
|---|---|
| `selection` | H5/912; UUID `c19ccaed81425011`; linked from H5/559. |
| `related_uids` | `c19ccaed81425011`; linked source `82d1defd5af0e96d` for H5/559. |
| `raw_flags` | `dead_tree_dbh_gap`; `prior_dead_first_qualifying_dbh`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | H5/912 appears as observed dead from June 2023 onward; DBH 198 in October 2024 and 184 in October 2025. Candidate link says H5/559 -> H5/912 in 2023. H5/559 had a dead 405 mm stem and an alive 217 mm second stem in June 2019, then mostly dead/no-DBH evidence. |
| `interpretation` | The explicit tag-change may refer to the smaller H5/559 stem continuing as H5/912, but as a whole-tree link the DBH profile is incompatible because H5/559 also carries a 405 mm dead stem. This may be a stem-level/tag bookkeeping issue. |
| `recommended_action` | Source check / human call before accepting or rejecting the candidate link. |
| `decision_scope` | Candidate link H5/559 -> H5/912; possibly stem-profile or split identity if source confirms. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Do not auto-accept explicit tag changes when source and target max DBH profiles differ by this much; require endpoint review. |
| `source_rows_to_check` | Candidate link `link_b3290fb5424f39cd`; H5/559 `2023_and_prior.csv:15`, `2023_and_prior.csv:3883`; H5/912 `2024_fall.csv:1082`, `import_recent_format_reviewed.csv:487`. |

### M5/2477

| Field | Notes |
|---|---|
| `selection` | M5/2477; UUID `85bb0f01da76a838`; linked to M5/910. |
| `related_uids` | `85bb0f01da76a838`; linked target `f5436c2fe4b220a4` for M5/910. |
| `raw_flags` | `I_INFERRED_DEAD` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | M5/2477 is dead pine with DBH 267 in 2019-2020, dead/no-DBH in 2021-2022, unknown in 2024. Candidate link says M5/2477 -> M5/910 in 2023. M5/910 is dead/unidentified, mostly no DBH, absent/not found by April 2025. |
| `interpretation` | The link is plausible only as a tag-change bookkeeping assertion, not from morphology. Taxon labels disagree in canonical output (`PINTAE` vs `UNISPP`) and target lacks DBH. |
| `recommended_action` | Source check / human call. Do not auto-alias from this evidence alone. |
| `decision_scope` | Candidate link M5/2477 -> M5/910. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Explicit tag change with no comparable target DBH should remain review-required unless independently confirmed. |
| `source_rows_to_check` | Candidate link `link_f8d22f99b97e05dd`; M5/2477 `2023_and_prior.csv:864`, `:885`, `:908`, `:922`; M5/910 `2023_and_prior.csv:4997`, `2025_spring.csv:1260`. |

### M3/911

| Field | Notes |
|---|---|
| `selection` | M3/911; UUID `bb32debd90a06d9c`; linked from M3/359. |
| `related_uids` | `bb32debd90a06d9c`; linked source `a26b4e51d253336c` for M3/359. |
| `raw_flags` | No direct raw diagnostic/invariant flags; flagged by candidate link. |
| `configured_decisions_applied` | None. |
| `current_flags` | No direct current flags; candidate link remains. |
| `evidence_summary` | M3/911 is dead/no-DBH in June 2023, unknown in May 2024, dead/no-DBH in October 2024 and April 2025 with note `fallen`. Candidate link says M3/359 -> M3/911 in 2023, while M3/359 continues to be observed afterward. |
| `interpretation` | This looks like a candidate duplicate/new tag for an already tracked dead juniper, but the continuing M3/359 rows make the link ambiguous. |
| `recommended_action` | Source check / human call together with M3/359. |
| `decision_scope` | Candidate link; possible reject link, alias, or duplicate-tag decision. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | None. |
| `source_rows_to_check` | Candidate link `link_d42fb926b4695175`; M3/911 `2023_and_prior.csv:4942`, `2025_spring.csv:1244`; M3/359 `2024_fall.csv:687`. |

### L7/25

| Field | Notes |
|---|---|
| `selection` | L7/25; UUID `edb035feeba1f683`. |
| `related_uids` | `edb035feeba1f683`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `dead_tree_dbh_gap`; `qualifying_rank_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Observed dead from 2019-2022; June 2023 has DBH 120, health 1, alive true, standing false; May/October 2024 dead health 0, with May note `zombie`; April 2025 not found; October 2025 dead/fallen. |
| `interpretation` | This is not a generic typo. The health 1 alive row plus later `zombie` note may represent a real weak live/resprout observation or field uncertainty around a fallen dead tree. |
| `recommended_action` | Source check / human call. |
| `decision_scope` | Mortality/status at June 2023 and possibly May 2024 note context. |
| `confidence` | Low. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | None; low-health alive row inside a dead sequence with explicit `zombie` note should be human-reviewed. |
| `source_rows_to_check` | `2023_and_prior.csv:4718`; `2024_spring.csv:505`; `import_recent_format_reviewed.csv:1377`. |

### L6/54

| Field | Notes |
|---|---|
| `selection` | L6/54; UUID `e04b3daca9ec5aaa`. |
| `related_uids` | `e04b3daca9ec5aaa`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `health_rebound_new_stem_context`; `qualifying_rank_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead health 0 from 2019-2022; June 2023 alive, DBH 93, health 6, standing true; October 2024 onward dead health 0, standing true, with October 2024 note `def. standing` and April 2025 note `new death`. |
| `interpretation` | June 2023 may be a real alive observation after a prior mistaken death sequence, followed by a real new death in 2024. The explicit `new death` note supports treating later mortality as separate from earlier dead labels. |
| `recommended_action` | Source check / human call. Likely convert early 2019-2022 death labels to uncertain if Riley confirms the 2023 alive row is credible. |
| `decision_scope` | Mortality/status for 2019-2022 or June 2023 depending source confirmation. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Cases with a later `new death` note after an alive rebound should not be collapsed by generic zombie handling. |
| `source_rows_to_check` | `2023_and_prior.csv:4654`; `2024_fall.csv:382`; `2025_spring.csv:368`. |

### L3/300

| Field | Notes |
|---|---|
| `selection` | L3/300; UUID `7e233aebccf296bc`. |
| `related_uids` | `7e233aebccf296bc`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `single_survey_death_label_outlier`; `mortality_contradiction`; `qualifying_rank_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Alive with DBH 75-77 from 2019-2021; June 2022 is the only observed-dead/health-0 row and has no DBH; alive again from 2023-2025 with DBH 74-82 and notes about another tree falling on it. |
| `interpretation` | High-confidence single-row false death or not-found row. The DBH profile is continuous before and after. |
| `recommended_action` | Source-row correction candidate. Suppress/correct June 2022 mortality status and health; preserve blank DBH gap. |
| `decision_scope` | Source row mortality/status for June 2022. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Single no-DBH death row bracketed by alive rows with similar DBH -> treat as uncertain/not-found rather than mortality. |
| `source_rows_to_check` | `2023_and_prior.csv:363`. |

### M5/2496

| Field | Notes |
|---|---|
| `selection` | M5/2496; UUID `8d0ba0743ae3d40f`. |
| `related_uids` | `8d0ba0743ae3d40f`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `W_DBH_JUMP` x2; `W_TREE_RANKED_DBH_JUMP` x2; `single_survey_death_label_outlier`; `single_survey_dbh_outlier` x4; `mortality_contradiction`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Alive DBH 204 in 2019-2020; June 2021 DBH 197, health 0, dead note; alive again from 2022 onward with DBH near 192-204; October 2024 isolated DBH 318, then April 2025 back to 202. |
| `interpretation` | Two likely row-level issues: June 2021 mortality/health is a false single-survey death label, and October 2024 DBH 318 is an isolated DBH typo or wrong-tree measurement. |
| `recommended_action` | Source-row correction candidate. Mark June 2021 mortality/health as uncertain or alive-with-missing-health; suppress October 2024 DBH to missing unless source confirms 318. |
| `decision_scope` | Source row mortality/status and health for June 2021; DBH field for October 2024. |
| `confidence` | High for Oct 2024 DBH suppression; medium-high for June 2021 mortality correction. |
| `needs_riley_call` | No for DBH suppression; optional for exact June 2021 health representation. |
| `candidate_auto_rule` | Single dead row with measured DBH bracketed by alive rows may be corrected to non-mortality but health should usually become missing rather than invented. Isolated DBH jump that returns to the baseline can be a suppress-field candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:291`; `2024_fall.csv:762`. |

### M7/331

| Field | Notes |
|---|---|
| `selection` | M7/331; UUID `0134ea34a7248f4b`. |
| `related_uids` | `0134ea34a7248f4b`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `single_survey_low_health_death_label_outlier`; `stem_mortality_context`; `mortality_contradiction`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Two-stem nyssa alive through May 2024. October 2024 marks stem 1 and stem 2 dead/health 0, with notes about merging a third stem. April 2025 and October 2025 both stems are alive again. |
| `interpretation` | October 2024 looks like a stem bookkeeping/mortality-entry problem rather than true whole-tree death. Because both stems are affected and notes mention merge/third stem, this should be checked before an automatic status rewrite. |
| `recommended_action` | Source-row correction candidate, with source check preferred. Likely convert October 2024 death labels/health 0 for stems 1-2 to uncertain/missing or alive if source supports. |
| `decision_scope` | Source rows for October 2024 stem 1 and stem 2; stem profile context. |
| `confidence` | Medium. |
| `needs_riley_call` | Maybe; source check first. |
| `candidate_auto_rule` | Multi-stem single-survey all-stem death followed by all-stem alive should be a review-priority pattern, not fully automatic. |
| `source_rows_to_check` | `2024_fall.csv:875`, `2024_fall.csv:858`, `2024_fall.csv:877`. |

### R2/634

| Field | Notes |
|---|---|
| `selection` | R2/634; UUID `2378f82e0fa57278`. |
| `related_uids` | `2378f82e0fa57278`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE` x2; `W_TREE_LARGE_STEM_DISAPPEARANCE`; `W_TREE_LARGE_STEM_APPEARANCE`; `new_persistent_large_stem` x3; `bounded_stem_rank_gap`; `blank_missing_stem_backfill_candidate`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Stem 2 is present in June 2023 at 52 mm, absent in May 2024, then present again at 54/53/55 in October 2024-April 2025-October 2025. Stem 1 remains stable at 113-117. |
| `interpretation` | Classic missing stem observation in one survey, not a new persistent stem. |
| `recommended_action` | Rule-generated decision candidate. Insert/represent a blank missing stem-2 row for May 2024 rather than treating it as disappearance/reappearance. |
| `decision_scope` | Stem profile gap for UUID `2378f82e0fa57278`, May 2024 stem 2. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | If a qualifying secondary stem is present before and after one-survey absence with similar DBH, backfill a blank/missing stem row for the gap. |
| `source_rows_to_check` | Surrounding rows: `2023_and_prior.csv:5165`; `2024_spring.csv:129`; `2024_fall.csv:1248`; `2025_spring.csv:690`; `import_recent_format_reviewed.csv:88`. |

### H0/274

| Field | Notes |
|---|---|
| `selection` | H0/274; UUID `6ec7d7766336441f`. |
| `related_uids` | `6ec7d7766336441f`; note says clustered with H0/275. |
| `raw_flags` | `W_BELOW_THRESHOLD_DBH` x10; stem-count changes; DBH/ranked DBH jump; large stem appearance/disappearance; `subthreshold_dbh_present`; `probable_duplicate_stem_artifact`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | 2019-2020 single stem DBH 80. From 2021 onward main stem is 55-60 and extra stems are mostly 38-44. May 2024 has two 58 mm stems plus subthreshold stems; later surveys return to one qualifying stem plus subthreshold dead/alive stems. |
| `interpretation` | Mixed issue: subthreshold stems should probably not count in canonical stem profile, and May 2024 stem 2 at 58 looks like a duplicate of stem 1. The early 80 -> later 55-60 shift may be source-era/tag alignment or measurement-point change. |
| `recommended_action` | Rule-generated decision candidate for subthreshold suppression and duplicate-stem suppression; source check / human call only for whether early 80 should be corrected or left as historical DBH. |
| `decision_scope` | Stem profile and DBH fields: suppress <50 mm stem observations from canonical stem slots; suppress probable duplicate May 2024 58 mm stem; source-era DBH review for 2019-2020. |
| `confidence` | High for subthreshold/duplicate handling; medium-low for early DBH era. |
| `needs_riley_call` | Yes for early 80 vs 55-60 interpretation; no for subthreshold policy if already accepted. |
| `candidate_auto_rule` | Do not let <50 mm stems inflate stem-count invariants when at least one qualifying stem exists; repeated same-DBH extra stem appearing for one survey is duplicate-stem artifact. |
| `source_rows_to_check` | `2023_and_prior.csv:3289`, `:3363`, `:1393`, `:2744-2746`, `:4008-4010`; `2024_spring.csv:402`, `:948`, `:981`, `:983`. |

### R2/622

| Field | Notes |
|---|---|
| `selection` | R2/622; UUID `3f19ac621a73c8ae`. |
| `related_uids` | `3f19ac621a73c8ae`. |
| `raw_flags` | `W_BELOW_THRESHOLD_DBH`; `W_DBH_JUMP`; `subthreshold_dbh_present`; `max_dbh_jump`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Ilex with DBH 69/64/64/65 from June 2023 through April 2025; October 2025 DBH is 7 with health 9 and alive/standing. |
| `interpretation` | October 2025 DBH 7 is an obvious transcription/data-entry issue. Since October 2025 DBH is optional and the value is below threshold, safest action is to suppress the DBH rather than infer 70. |
| `recommended_action` | Rule-generated decision candidate: suppress October 2025 DBH to missing. |
| `decision_scope` | DBH field for October 2025 R2/622. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | In October 2025, isolated subthreshold DBH on otherwise stable qualifying live tree -> suppress DBH to missing. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:70`. |

### L2/224

| Field | Notes |
|---|---|
| `selection` | L2/224; UUID `6c7f8257f5872790`. |
| `related_uids` | `6c7f8257f5872790`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction` x2; `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Observed dead from 2019 through May 2024; October 2024 is DBH 105, health 6, alive true, standing true; April 2025 and October 2025 are dead again. |
| `interpretation` | October 2024 is a single high-health alive row in an otherwise dead sequence. This looks like a row-level status/health error, but because DBH is plausible and the tree is standing, it deserves source check before automatic correction. |
| `recommended_action` | Source-row correction candidate. If source check does not support alive, set October 2024 health/status to dead/0. |
| `decision_scope` | Source row mortality/status and health for October 2024. |
| `confidence` | Medium-high. |
| `needs_riley_call` | Maybe; source check likely enough. |
| `candidate_auto_rule` | Single alive/high-health row bracketed by observed-dead rows should be review/correction candidate; do not auto if standing dead DBH is plausible. |
| `source_rows_to_check` | `2024_fall.csv:155`. |

### H6/523

| Field | Notes |
|---|---|
| `selection` | H6/523; UUID `fc766a068ca59338`. |
| `related_uids` | `fc766a068ca59338`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era` x2; `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead pine DBH 136 in 2019-2020; dead/no-DBH through 2023; May and October 2024 dead standing DBH 501/498; later dead/no DBH. Notes include `top fell on litter basket. dead` in 2020 and `didn't find` in April 2025. |
| `interpretation` | The 501/498 standing-dead DBH era is incompatible with the earlier 136 dead tree. Because very large DBH is possible for pines but this is a huge jump in a dead tree, likely wrong tag/source alignment or a different dead pine measured under this tag. |
| `recommended_action` | Source check / human call. |
| `decision_scope` | DBH field or identity alignment for May/October 2024 H6/523. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | None; large pine DBH can be real, so avoid blind suppression. |
| `source_rows_to_check` | `2024_spring.csv:269`; `2024_fall.csv:1091`; early context `2023_and_prior.csv:576`, `:653`. |

### M1/872

| Field | Notes |
|---|---|
| `selection` | M1/872; UUID `5e13f585cd3b6323`. |
| `related_uids` | `5e13f585cd3b6323`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era` x2; `health_rebound_alive_context`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | 2019-2020 DBH 182 with health 10; 2021 onward stable at 80-95, alive throughout. Dropping the leading `1` from the early rows gives 82, which fits the later DBH regime. |
| `interpretation` | High-confidence missing/extra-leading-digit carry-forward in the 2019-2020 source rows. Health rebound is context only because the tree stays alive. |
| `recommended_action` | Rule-generated decision candidate. Correct or suppress 2019-2020 DBH 182; preferred deterministic correction is 82 if source conventions permit, otherwise suppress to missing. |
| `decision_scope` | DBH field for 2019 and 2020 M1/872. |
| `confidence` | High. |
| `needs_riley_call` | No if using the leading-digit rule; otherwise optional. |
| `candidate_auto_rule` | Repeated early DBH with leading digit that, when removed, aligns with later stable DBH baseline -> corrected DBH candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:3251`, `2023_and_prior.csv:3222`. |

### H4/141

| Field | Notes |
|---|---|
| `selection` | H4/141; UUID `2e641cf180f2c199`. |
| `related_uids` | `2e641cf180f2c199`. |
| `raw_flags` | `W_DBH_JUMP` x3; `W_TREE_RANKED_DBH_JUMP` x3; `single_survey_dbh_outlier` x4; `stable_incompatible_dbh_era` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pine DBH 527 in 2019-2020, then stable around 259-265 from 2021 onward, except May 2024 isolated 201 followed by return to 260. Notes mention bare/thin canopy. |
| `interpretation` | Two issues: May 2024 DBH 201 is probably an isolated typo or measurement error; 2019-2020 DBH 527 is an incompatible early regime. Because 527 is large but possible for pine, and 527/2 roughly matches the later DBH, source inspection is needed. |
| `recommended_action` | Source check / human call. Likely suppress or correct May 2024 DBH; separately decide how to handle early 527 rows. |
| `decision_scope` | DBH field for May 2024; DBH fields or source-era review for 2019-2020. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Isolated DBH outlier returning to a stable baseline can be a suppress-field candidate, but this case also has an early-regime issue. |
| `source_rows_to_check` | `2024_spring.csv:1122`; early rows `2023_and_prior.csv:2438`, `:2451`. |

### L7/18

| Field | Notes |
|---|---|
| `selection` | L7/18; UUID `74a0271b5166d421`. |
| `related_uids` | `74a0271b5166d421`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniper DBH 90 in 2019-2020; DBH 221-231 from 2021 onward, alive throughout. |
| `interpretation` | Stable early and stable later regimes are incompatible. This does not look like a simple 10x or leading-digit correction. It may be old source/tag alignment. |
| `recommended_action` | Source check / human call. |
| `decision_scope` | DBH fields or identity alignment around the 2020/2021 boundary. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | None. |
| `source_rows_to_check` | `2023_and_prior.csv:2295`, `:2283`, `:2323`. |

### L4/248

| Field | Notes |
|---|---|
| `selection` | L4/248; UUID `b116e594f52ba84e`. |
| `related_uids` | `b116e594f52ba84e`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pine DBH 85 in 2019-2020, then stable around 309-315 from 2021 onward, alive throughout. |
| `interpretation` | Early DBH is almost certainly wrong for the same tree, but the correction is not obvious. Missing leading digit alone does not align cleanly. |
| `recommended_action` | Source check, possible rule candidate if source confirms early low-value source-era problem. |
| `decision_scope` | DBH field/source-era for 2019-2020. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Repeated early low DBH followed by stable much larger modern DBH should be routed to source-era review; not auto-correct unless a simple digit rule aligns. |
| `source_rows_to_check` | `2023_and_prior.csv:3741`, `:3711`, `:1424`. |

### M6/400

| Field | Notes |
|---|---|
| `selection` | M6/400; UUID `488ac2cbac845a41`. |
| `related_uids` | `488ac2cbac845a41`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `early_low_dbh_source_era_candidate` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 56 in 2019-2020; DBH 174-181 from 2021 onward, alive throughout. 2019 note says `Broken Branches`. |
| `interpretation` | Early DBH likely missing a leading digit or otherwise from a bad source-era/tag alignment. If 56 should be 156, the later 174-181 trajectory is plausible, but this needs source confirmation. |
| `recommended_action` | Source check, possible rule candidate. |
| `decision_scope` | DBH fields for 2019-2020. |
| `confidence` | Medium. |
| `needs_riley_call` | Maybe, after source row inspection. |
| `candidate_auto_rule` | Repeated early low DBH close to threshold followed by stable larger DBH can be a leading-digit candidate when adding 100/200 aligns with later values. |
| `source_rows_to_check` | `2023_and_prior.csv:2699`, `:2717`, `:1761`. |

### H5/567

| Field | Notes |
|---|---|
| `selection` | H5/567; UUID `9e36b641a1f8678b`. |
| `related_uids` | `9e36b641a1f8678b`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `persistent_dbh_regime_shift` x2. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 203 in 2019-2020, then 169-180 in 2021-2024, rising to 190/181/195 by late 2024-2025. Multiple notes say outside/out of plot and string context. |
| `interpretation` | This may be measurement-position/string context rather than a data error. The later values partially return toward the early 203 baseline. |
| `recommended_action` | No immediate change / watch context. Keep flagged as context unless future source review focuses on out-of-plot trees. |
| `decision_scope` | None for now. |
| `confidence` | Medium. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Persistent modest DBH regime shifts with notes about outside-plot/string context may be downgradable to watch/context rather than requiring one-off correction. |
| `source_rows_to_check` | Optional: `2023_and_prior.csv:3398`, `:4238`; `2024_spring.csv:252`; `2024_fall.csv:1074`; `2025_spring.csv:931`. |

### M1/843

| Field | Notes |
|---|---|
| `selection` | M1/843; UUID `2951506dc331f5b9`. |
| `related_uids` | `2951506dc331f5b9`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`. |
| `configured_decisions_applied` | None. |
| `current_flags` | Same as raw. |
| `evidence_summary` | June 2019-2020 observed dead/health 0 with DBH 110 and dead notes; 2021-2025 alive with DBH 102-115 and health 2-5 until October 2025 observed dead. Taxon is unidentified in 2019, juniper afterward. |
| `interpretation` | Early dead labels were likely wrong or uncertain: DBH continuity and several later alive observations make true death/revival unlikely. Later October 2025 mortality can remain. |
| `recommended_action` | Rule-generated decision candidate. Convert 2019-2020 mortality labels/health 0 to uncertain or alive-with-missing-health while preserving DBH/taxon evidence. |
| `decision_scope` | Source row mortality/status and health for June 2019 and June 2020. |
| `confidence` | Medium-high. |
| `needs_riley_call` | No if following the established rule that dead with low health followed by later alive should be treated as mistaken mortality; otherwise optional. |
| `candidate_auto_rule` | Consecutive early dead rows with DBH continuity and multiple later alive observations -> mortality status uncertain/incorrect, not a zombie. |
| `source_rows_to_check` | `2023_and_prior.csv:1162`, `2023_and_prior.csv:247`. |


# Agent 07 third-review shard

Date: 2026-05-11

Scope: assigned current flagged tags only. This report is investigation-only; no config, generated output, source data, or pipeline code was edited.

## Summary

| recommended_action | count |
|---|---:|
| source check / human call | 6 |
| mortality/status rule candidate | 5 |
| accept candidate identity link | 3 |
| source-row DBH correction candidate | 3 |
| watch / diagnostic threshold tuning | 3 |
| stem-profile decision candidate | 2 |

Recurring patterns:

- Explicit old-tag links on dead trees are usually clean when plot, taxon, and mortality state agree, even when the new tag lacks a comparable DBH profile.
- Several mortality cases match the emerging rule: an observed-dead health-0 row or short dead block followed by repeated observed-alive evidence should be converted to an uncertain/mortality-correction candidate, not treated as a true zombie.
- Dead-tree DBH changes should not automatically imply error. Isolated dead-tree increases still look suspicious, but post-death shrinkage can be legitimate.
- Stem-profile review is mostly about row/scoping mechanics: suppress probable duplicate extra stems and insert blank/not-reported stem rows where a qualifying stem disappears and later returns.
- Source-note DBH conflicts are not all corrections. Knot/measurement-point notes can explain real DBH regime changes and should sometimes route to watch/context instead of source-row suppression.

## Cases

### H4/992

| Field | Notes |
|---|---|
| `selection` | tag 992, plot H4, UUID `189b33fa3670d2d1`; linked source H4/136 UUID `fd65bc2ba3d3a410`. |
| `related_uids` | `189b33fa3670d2d1`, `fd65bc2ba3d3a410`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `source_note_dbh_conflict`, plus source H4/136 `stable_incompatible_dbh_era` and inferred-dead rows. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw: candidate identity link remains, May/Oct 2024 DBH jumps remain, and H4/136 still has stable incompatible DBH eras. |
| `evidence_summary` | H4/136 is Nyssa 91 mm in 2019-2020, then 178/183 mm in 2021-2022. H4/992 has explicit old-tag evidence from H4/136 in June 2023 with DBH 187, then May 2024 has a 111 mm alive row with note `might be 136`, October 2024 is 194, April 2025 is 200 with note `Broken but alive`, and October 2025 is 192. |
| `interpretation` | The identity link H4/136 -> H4/992 is plausible, but the May 2024 111 mm row is not compatible with the 187/194/200/192 sequence and is explicitly qualified. There are also duplicate inferred-dead rows under H4/136 after the tag change. |
| `recommended_action` | source check / human call. Likely accept the identity link, but review/strike or relocate May 2024 H4/992 DBH 111 before closing the case. |
| `decision_scope` | candidate link plus DBH field/source row for `2024_spring.csv:340`; possibly close/alias H4/136 after June 2023. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; note says `might be 136`, but action depends on whether that row belongs to the linked tree or another tree. |
| `source_rows_to_check` | `2024_spring.csv:340`, H4/136 rows `2023_and_prior.csv:3318`, `3368`, `3455`, `2434`, H4/992 row `2023_and_prior.csv:4219`. |

### M7/323

| Field | Notes |
|---|---|
| `selection` | tag 323, plot M7, UUID `ab991d9b18946a8e`. |
| `related_uids` | `ab991d9b18946a8e`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus 117.5 mm alive/health 9 in 2019-2020; missing in 2021; alive DBH 113/health 6 in 2022; June 2023 dead health 0/no DBH; missing in May 2024; alive DBH 113/health 3 in Oct 2024; DNF in Apr 2025; alive health 4 in Oct 2025. |
| `interpretation` | June 2023 is a single observed-dead row bracketed by repeated alive evidence with compatible DBH. This looks like a false death label or an uncertain/not-found row, not true mortality. |
| `recommended_action` | mortality/status rule candidate. Convert June 2023 observed-dead status to uncertain/not-found or route as a row-level mortality correction candidate. |
| `decision_scope` | mortality/status row `2023_and_prior.csv:5063`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing; yes only if choosing exact health replacement rather than suppressing/uncertain. |
| `candidate_auto_rule` | single dead/no-DBH row bracketed by alive observations with compatible DBH and later health recovery. |
| `source_rows_to_check` | `2023_and_prior.csv:5063`; context rows `1918`, `2024_fall.csv:850`, `import_recent_format_reviewed.csv:895`. |

### L3/919

| Field | Notes |
|---|---|
| `selection` | tag 919, plot L3, UUID `5d23902c137332af`; linked source L3/5029 UUID `272d0e2edfc6dfa6`. |
| `related_uids` | `5d23902c137332af`, `272d0e2edfc6dfa6`. |
| `raw_flags` | raw `W_ALIVE_HEALTH_CONFLICT` and `mortality_contradiction` from June 2023 alive=true/health 0; prior-live blank-DBH context. |
| `configured_decisions_applied` | `row_correction:0004` set June 2023 L3/919 to observed-dead because health 0 and later records indicate dead. |
| `current_flags` | corrected-row info plus `prior_dead_first_qualifying_dbh`; candidate identity link remains. |
| `evidence_summary` | June 2023 L3/919 has old tag 5029, health 0, no DBH, note `slightly outside plot strings`. Later records are dead/no DBH or dead with DBH 104/101. Taxon alternates between Juniperus and unidentified, with October 2024 note `species change not jun`. |
| `interpretation` | The mortality contradiction is already handled by the configured correction. The remaining candidate link is likely an explicit old-tag retag of a dead Juniperus/unidentified tree. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `L3/5029 -> L3/919`; keep existing row-level mortality correction. |
| `confidence` | high for accepting the link; medium on final taxon if the project wants a single species call. |
| `needs_riley_call` | no for link acceptance; optional for taxon finalization. |
| `candidate_auto_rule` | explicit old-tag link, same plot, dead-only target, no conflicting DBH profile. |
| `source_rows_to_check` | link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:13`; corrected row `2023_and_prior.csv:4532`; later rows `2024_fall.csv:242`, `2025_spring.csv:230`. |

### L7/39

| Field | Notes |
|---|---|
| `selection` | tag 39, plot L7, UUID `b8906ee5ac572d64`; linked target L7/973 UUID `fc824bb78db8af8d`. |
| `related_uids` | `b8906ee5ac572d64`, `fc824bb78db8af8d`. |
| `raw_flags` | inferred-dead context only; candidate identity link. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | inferred-dead context only; candidate identity link remains. |
| `evidence_summary` | L7/39 is a dead Pinus, DBH 321 in 2019-2020, then missing/inferred dead, dead/no DBH in 2023. L7/973 appears with explicit old tag 39 in June 2023 as dead/no DBH and remains dead or DNF. |
| `interpretation` | Clean dead-tree retag. The target lacks comparable DBH, but there is no conflicting taxon, status, or measurement evidence. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `L7/39 -> L7/973`. |
| `confidence` | high. |
| `needs_riley_call` | no, unless every link requires manual signoff. |
| `candidate_auto_rule` | explicit old-tag link, same plot/taxon, source and target dead-only, no DBH conflict. |
| `source_rows_to_check` | link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:19`; source rows `2023_and_prior.csv:751`, `612`; target row `2023_and_prior.csv:4753`. |

### M5/972

| Field | Notes |
|---|---|
| `selection` | tag 972, plot M5, UUID `5c5ceeb08462e9ad`; linked source M5/2484 UUID `85b7a0af0b4c029f`. |
| `related_uids` | `5c5ceeb08462e9ad`, `85b7a0af0b4c029f`. |
| `raw_flags` | inferred-dead context only; candidate identity link. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | inferred-dead context only; candidate identity link remains. |
| `evidence_summary` | M5/2484 is a dead Pinus, DBH 301 in 2019-2020, then dead/no DBH. M5/972 appears in June 2023 with old tag 2484, dead/no DBH, then remains dead, missing, or DNF. |
| `interpretation` | Clean dead-tree retag. Target lacks DBH, but the old-tag field is explicit and all status/taxon evidence agrees. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `M5/2484 -> M5/972`. |
| `confidence` | high. |
| `needs_riley_call` | no, unless every link requires manual signoff. |
| `candidate_auto_rule` | explicit old-tag link, same plot/taxon, dead-only target, no conflicting DBH. |
| `source_rows_to_check` | link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:27`; source rows `2023_and_prior.csv:865`, `886`, `909`, `921`; target row `2023_and_prior.csv:4998`. |

### L5/420

| Field | Notes |
|---|---|
| `selection` | tag 420, plot L5, UUID `427060270118d5df`. |
| `related_uids` | `427060270118d5df`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `health_rebound_new_stem_context`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pinus alive with DBH 356-359 and health 10/10/6/4 from 2019-2022; dead/no DBH in June 2023; dead DBH 349/352 in 2024 and dead/no DBH in Apr 2025; October 2025 returns as DBH 354 and health 6/alive. |
| `interpretation` | Long dead block followed by a healthy October 2025 row is suspicious. Because Oct 2025 is reviewed but DBH collection was being phased out, this needs source/field judgment before deciding whether the October 2025 health/status belongs to this tree. |
| `recommended_action` | source check / human call. |
| `decision_scope` | mortality/status for `import_recent_format_reviewed.csv:1225`, possibly source row if October 2025 health/status is wrong. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; this could be a real marginal-live/dead-status nuance or a source/transcription problem. |
| `source_rows_to_check` | `2023_and_prior.csv:4588`, `2024_spring.csv:702`, `2024_fall.csv:311`, `2025_spring.csv:316`, `import_recent_format_reviewed.csv:1225`. |

### M1/838

| Field | Notes |
|---|---|
| `selection` | tag 838, plot M1, UUID `a7a5097af1b6acd7`. |
| `related_uids` | `a7a5097af1b6acd7`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `dead_tree_dbh_gap`, `mortality_contradiction`, high-health-to-dead transition, sharp health rebound, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pinus alive DBH 236/health 9 in 2019-2020; dead/no DBH in 2021; dead DBH 229 in 2022; dead/no DBH in 2023; dead DBH 218 in May 2024; October 2024 alive health 5 DBH 219; April/October 2025 dead DBH 217/219 health 0. |
| `interpretation` | The October 2024 alive/health 5 row is the only live row inside a long dead sequence with compatible dead-tree DBH. Could be marginal live tissue noted by field crew, but it is also a classic one-row mortality/status outlier. |
| `recommended_action` | source check / human call. |
| `decision_scope` | mortality/status for `2024_fall.csv:565`. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | possible future rule: single alive row inside dead-only sequence with same dead-tree DBH, but do not auto-apply yet. |
| `source_rows_to_check` | `2024_fall.csv:565`, with context `2024_spring.csv:831`, `2025_spring.csv:1166`, `import_recent_format_reviewed.csv:622`. |

### L6/67

| Field | Notes |
|---|---|
| `selection` | tag 67, plot L6, UUID `bea9a4ccf59a5fb3`. |
| `related_uids` | `bea9a4ccf59a5fb3`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, sharp upward health rebound, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus dead health 0 in 2019-2020 with DBH 133; then alive health 7/5/5 with DBH 142/136/133 from 2021-2023; alive health 1 in Oct 2024 with poison ivy note; alive DBH 127/health 5 in Apr 2025; dead health 0 in Oct 2025. |
| `interpretation` | The early dead labels are contradicted by several years of compatible alive observations. October 2025 may represent later death, but the 2019-2020 mortality labels should not make this a zombie. |
| `recommended_action` | mortality/status rule candidate. |
| `decision_scope` | mortality/status rows `2023_and_prior.csv:142` and `88`; leave October 2025 as a separate later mortality event unless reviewed otherwise. |
| `confidence` | high for early death-label error; medium on October 2025 final death. |
| `needs_riley_call` | no for routing early rows; optional for exact health replacement. |
| `candidate_auto_rule` | early health-0 dead block followed by multi-year observed-alive compatible DBH should become row-level mortality-correction candidates. |
| `source_rows_to_check` | `2023_and_prior.csv:142`, `88`, `2105`, `1739`, `4666`; `2024_fall.csv:395`; `import_recent_format_reviewed.csv:1289`. |

### R1/960

| Field | Notes |
|---|---|
| `selection` | tag 960, plot R1, UUID `100d52f8be411f2f`. |
| `related_uids` | `100d52f8be411f2f`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `probable_duplicate_stem_artifact`, `new_persistent_large_stem`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Acer has one stem DBH 171 in June 2023. May 2024 has three rows: 182, duplicate 182, and 170. October 2024 onward settles into two stems around 184/169, 182/170, 187/168. |
| `interpretation` | May 2024 includes a probable duplicate 182 row plus a real second stem around 170 that persists afterward. The second stem likely existed in June 2023 but was not separately reported. |
| `recommended_action` | stem-profile decision candidate. Suppress the duplicate May 2024 182 row and consider a blank/not-reported second-stem backfill for June 2023. |
| `decision_scope` | stem profile plus source row, especially `2024_spring.csv:1050`; possible blank stem-row backfill at UUID/survey scope for June 2023. |
| `confidence` | high for duplicate May 2024 row; medium for June 2023 blank backfill. |
| `needs_riley_call` | no for routing; yes only if deciding whether to backfill blanks automatically. |
| `candidate_auto_rule` | duplicate DBH plus stem-count increase when the same profile appears immediately as an extra stem. |
| `source_rows_to_check` | `2023_and_prior.csv:5120`, `2024_spring.csv:88`, `1050`, `1059`, `2024_fall.csv:1181`, `1190`. |

### R4/5220

| Field | Notes |
|---|---|
| `selection` | tag 5220, plot R4, UUID `f01fb6e366e6b454`. |
| `related_uids` | `f01fb6e366e6b454`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_TREE_LARGE_STEM_APPEARANCE`, `bounded_stem_rank_gap`, `blank_missing_stem_backfill_candidate`, `new_persistent_large_stem`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Acer has two stems 147/129 in June 2023; May 2024 reports only one stem 150; Oct 2024 and later return to two stems around 154/126, 150/126, 149/125. |
| `interpretation` | This is a bounded missing second-stem gap, not a true stem birth/death. The second stem was likely not reported in May 2024. |
| `recommended_action` | stem-profile decision candidate. Insert/represent a blank/not-reported second-stem row for May 2024 rather than treating it as disappearance/reappearance. |
| `decision_scope` | UUID/survey stem profile for May 2024. |
| `confidence` | high. |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | bounded disappearance of a qualifying secondary stem with same-sized stem before and after should generate a blank missing-stem backfill candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:5250`, `5251`; `2024_spring.csv:184`; `2024_fall.csv:1319`, `1363`; `2025_spring.csv:778`, `779`. |

### L7/15

| Field | Notes |
|---|---|
| `selection` | tag 15, plot L7, UUID `e0b3b7366630fba0`. |
| `related_uids` | `e0b3b7366630fba0`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `explicit_note_mortality_correction_candidate`, sharp health rebound. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus dead health 0/DBH 99 in 2019-2020; June 2021 alive DBH 112/health 5 with note `Alive (marked dead last year)`; alive thereafter through Oct 2025 with DBH around 100-107 and health 4-9. |
| `interpretation` | The early dead labels are explicitly contradicted by the 2021 note and long alive history. |
| `recommended_action` | mortality/status rule candidate. |
| `decision_scope` | mortality/status rows `2023_and_prior.csv:152` and `73`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | explicit note `marked dead last year` plus later alive compatible DBH should generate row-level mortality corrections for prior dead rows. |
| `source_rows_to_check` | `2023_and_prior.csv:152`, `73`, `1699`, `1946`, `4707`. |

### L3/295

| Field | Notes |
|---|---|
| `selection` | tag 295, plot L3, UUID `ff2565f1cb094ffd`. |
| `related_uids` | `ff2565f1cb094ffd`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pinus alive DBH 342-349 from 2019-2023 with health declining 9 to 5; May 2024 is dead health 0/DBH 346; Oct 2024, Apr 2025, and Oct 2025 are alive with health 3/2/2 and compatible DBH where measured. |
| `interpretation` | May 2024 is a single observed-dead row bracketed by low-health alive observations. It looks like a mortality label error or an uncertain row, not true death. |
| `recommended_action` | mortality/status rule candidate. |
| `decision_scope` | mortality/status row `2024_spring.csv:605`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing; yes only for exact health replacement. |
| `candidate_auto_rule` | single health-0 dead row bracketed by alive compatible DBH/low-health observations. |
| `source_rows_to_check` | `2024_spring.csv:605`, with context `2023_and_prior.csv:4504`, `2024_fall.csv:212`, `2025_spring.csv:215`. |

### R1/961

| Field | Notes |
|---|---|
| `selection` | tag 961, plot R1, UUID `dfca83d75bc31075`. |
| `related_uids` | `dfca83d75bc31075`. |
| `raw_flags` | `W_DBH_JUMP`, stem count changes, large stem appearance/disappearance, duplicate-stem artifact, `max_dbh_jump`, `ranked_dbh_jump`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Acer has DBH 155 in June 2023; May 2024 has duplicate 156 rows; Oct 2024 and Apr 2025 continue around 156-157; Oct 2025 is 127 with health 9. |
| `interpretation` | There are two issues: the May 2024 duplicate stem artifact and a suspicious Oct 2025 DBH 127 after a stable 155-157 regime. The October value is especially suspect given the October 2025 transition away from routine DBH collection. |
| `recommended_action` | source-row DBH correction candidate. Suppress duplicate May 2024 extra-stem row and source-check/likely suppress Oct 2025 DBH 127 while preserving health/status. |
| `decision_scope` | DBH field/source rows `2024_spring.csv:1051` and `import_recent_format_reviewed.csv:36`; possible stem-profile duplicate-suppression scope. |
| `confidence` | high for duplicate row; medium-high for Oct 2025 DBH suppression. |
| `needs_riley_call` | yes for Oct 2025 source interpretation. |
| `candidate_auto_rule` | repeated DBH duplicate with stem-count increase; Oct 2025 DBH outlier should route to source-check/optional-DBH suppression. |
| `source_rows_to_check` | `2024_spring.csv:89`, `1051`, `2024_fall.csv:1182`, `2025_spring.csv:641`, `import_recent_format_reviewed.csv:36`. |

### M7/319

| Field | Notes |
|---|---|
| `selection` | tag 319, plot M7, UUID `8474d1c2e7e5ef7a`. |
| `related_uids` | `8474d1c2e7e5ef7a`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `dead_tree_dbh_gap`, `dead_tree_dbh_increase`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Dead Juniperus DBH 111.5 in 2019-2020; dead/no DBH in 2021; isolated dead DBH 136 in June 2022; no DBH in 2023; then dead DBH 109/113/109 in 2024-2025. |
| `interpretation` | Dead-tree DBH can change, but the isolated 136 is incompatible with both earlier and later dead-tree measurements. It is probably a source-row DBH error or wrong-row measurement. |
| `recommended_action` | source-row DBH correction candidate. Suppress June 2022 DBH 136 unless the source supports an exact corrected value. |
| `decision_scope` | DBH field for `2023_and_prior.csv:358`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing; optional source check for exact value. |
| `candidate_auto_rule` | isolated dead-tree DBH outlier that returns to prior/later dead-stem regime. |
| `source_rows_to_check` | `2023_and_prior.csv:358`; context rows `239`, `270`, `302`, `2024_spring.csv:753`, `2024_fall.csv:846`. |

### M7/5834

| Field | Notes |
|---|---|
| `selection` | tag 5834, plot M7, UUID `3bea8de78fb4acd4`. |
| `related_uids` | `3bea8de78fb4acd4`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `prior_dead_first_qualifying_dbh`, sharp health rebound. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | June 2023 is dead/no DBH with note `*not present on last year`; May/Oct 2024 are dead DBH 90/93; Apr 2025 DNF; Oct 2025 is alive health 8/no DBH. |
| `interpretation` | The Oct 2025 alive health 8 row is incompatible with a dead-new-tag sequence unless it reflects a real rediscovery/reclassification. Needs source or field call. |
| `recommended_action` | source check / human call. |
| `decision_scope` | mortality/status for `import_recent_format_reviewed.csv:923`, possibly UUID/tag identity if source review suggests wrong tag. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; latest-survey alive-after-dead cases should remain human reviewed for now. |
| `source_rows_to_check` | `2023_and_prior.csv:5082`, `2024_spring.csv:775`, `2024_fall.csv:868`, `2025_spring.csv:1392`, `import_recent_format_reviewed.csv:923`. |

### L1/107

| Field | Notes |
|---|---|
| `selection` | tag 107, plot L1, UUID `c44231146dcf026a`. |
| `related_uids` | `c44231146dcf026a`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `source_note_dbh_conflict`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus DBH 81/81/85 in 2019-2021; 104/105 in 2022-2023; 95 in May 2024; 84/85 in Oct 2024/Apr 2025. Apr 2025 note says `105 below knot DBH`. |
| `interpretation` | This looks like a DBH measurement-point problem around a knot, not a simple typo. The 104/105 regime may reflect measuring on a different side/position relative to the knot. |
| `recommended_action` | watch / diagnostic threshold tuning. Keep as context unless source review establishes the 104/105 rows should be struck. |
| `decision_scope` | diagnostic annotation / measurement-context note, not automatic DBH correction. |
| `confidence` | medium. |
| `needs_riley_call` | no immediate one-off call; yes if this remains in a final manual DBH queue. |
| `candidate_auto_rule` | source notes about knot/measurement position should downgrade DBH jump severity to context/watch rather than auto-correction. |
| `source_rows_to_check` | `2023_and_prior.csv:1530`, `4368`, `2025_spring.csv:63`. |

### L1/146

| Field | Notes |
|---|---|
| `selection` | tag 146, plot L1, UUID `13ec7f449ab4f29d`. |
| `related_uids` | `13ec7f449ab4f29d`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus DBH 282 in 2019-2020, then a stable 164-177 regime from 2021-2025 with no mortality/taxon explanation. |
| `interpretation` | This is a stable incompatible era, not an isolated typo. It may be an early source/identity/tag error, a different measurement convention, or a historical carry-forward mistake. |
| `recommended_action` | source check / human call. |
| `decision_scope` | DBH era / source rows for 2019-2020, possibly identity/tag if source check finds a tag mix-up. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; stable incompatible eras should route to source/identity review, not automatic suppression. |
| `source_rows_to_check` | `2023_and_prior.csv:3123`, `3091`, then transition row `2023_and_prior.csv:2582`. |

### L2/214

| Field | Notes |
|---|---|
| `selection` | tag 214, plot L2, UUID `54aba5017ecfefc9`. |
| `related_uids` | `54aba5017ecfefc9`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus DBH 106.5 in 2019-2020; isolated 123 in 2021; 102/101/103/103 afterward, then 115 in Apr 2025. Health remains alive/high. |
| `interpretation` | The 2021 123 is an outlier, but not extreme enough to confidently strike without source review. Later 115 suggests some measurement variation is possible. |
| `recommended_action` | watch / diagnostic threshold tuning. |
| `decision_scope` | diagnostic threshold/context; source-row check only if this remains in a final DBH cleanup queue. |
| `confidence` | medium-low. |
| `needs_riley_call` | no immediate one-off call. |
| `candidate_auto_rule` | mild single-survey DBH outliers under roughly 20-25 mm should route to watch/context unless paired with stronger evidence. |
| `source_rows_to_check` | `2023_and_prior.csv:3195`, with context `3129`, `3025`, `3247`, `4445`. |

### M7/317

| Field | Notes |
|---|---|
| `selection` | tag 317, plot M7, UUID `ff8ea3974b22de52`. |
| `related_uids` | `ff8ea3974b22de52`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pinus DBH is stable around 192-197 from 2019-2025 except June 2022, which is 138. Health/status remain alive. |
| `interpretation` | June 2022 DBH 138 is a clear isolated outlier and likely a source-row DBH error. |
| `recommended_action` | source-row DBH correction candidate. Suppress June 2022 DBH 138 unless source review recovers an exact corrected value. |
| `decision_scope` | DBH field for `2023_and_prior.csv:2510`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing; optional if correcting to a value instead of suppressing. |
| `candidate_auto_rule` | isolated large DBH drop in a living pine with immediate return to prior regime. |
| `source_rows_to_check` | `2023_and_prior.csv:2510`; context `3815`, `3868`, `1590`, `5057`. |

### L1/453

| Field | Notes |
|---|---|
| `selection` | tag 453, plot L1, UUID `22d35751aca6cae4`. |
| `related_uids` | `22d35751aca6cae4`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `max_dbh_jump`, `ranked_dbh_jump`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Morella DBH 111-117 while alive through May 2024; Oct 2024 alive health 1/DBH 112; Apr 2025 dead health 0/DBH 72; Oct 2025 dead/no DBH. |
| `interpretation` | The DBH drop happens at death. Given project guidance that dead trees can lose chunks and DBH can legitimately shrink after mortality, this should not be treated as an automatic DBH error. |
| `recommended_action` | watch / diagnostic threshold tuning. |
| `decision_scope` | diagnostic threshold/context; no source-row correction unless field/source review contradicts. |
| `confidence` | medium-high. |
| `needs_riley_call` | no immediate one-off call. |
| `candidate_auto_rule` | DBH decreases coincident with observed death should be downgraded unless the value is impossible or contradicted by later evidence. |
| `source_rows_to_check` | `2025_spring.csv:104`, with context `2024_fall.csv:105`, `import_recent_format_reviewed.csv:1024`. |

### L2/611

| Field | Notes |
|---|---|
| `selection` | tag 611, plot L2, UUID `4428948dc491c927`. |
| `related_uids` | `4428948dc491c927`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Morella first appears May 2024 dead health 0/DBH 90; Oct 2024 alive health 3/DBH 94; Apr 2025 dead health 0/DBH 94; Oct 2025 dead health 0/no DBH. |
| `interpretation` | Single alive row inside otherwise dead sequence. Could be true marginal live tissue in October 2024 or a status/health recording error. |
| `recommended_action` | source check / human call. |
| `decision_scope` | mortality/status for `2024_fall.csv:183`. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | possible future rule for single low-health alive row bracketed by dead rows, but needs more examples before auto-routing. |
| `source_rows_to_check` | `2024_spring.csv:577`, `2024_fall.csv:183`, `2025_spring.csv:182`, `import_recent_format_reviewed.csv:1093`. |

### L6/96

| Field | Notes |
|---|---|
| `selection` | tag 96, plot L6, UUID `d945c13f85a7edf4`. |
| `related_uids` | `d945c13f85a7edf4`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, sharp upward health rebound. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus dead health 0/DBH 115 in 2019-2020; alive with DBH 118-125 and health 3-5 from 2021 through Oct 2025. |
| `interpretation` | Early dead labels are contradicted by long compatible live evidence. This is the same pattern as L6/67 and L7/15, without the explicit `marked dead` note. |
| `recommended_action` | mortality/status rule candidate. |
| `decision_scope` | mortality/status rows `2023_and_prior.csv:150` and `83`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | early health-0 dead block followed by multi-year observed-alive compatible DBH should become row-level mortality-correction candidates. |
| `source_rows_to_check` | `2023_and_prior.csv:150`, `83`, `1698`, `1379`, `4695`; `2024_fall.csv:424`, `2025_spring.csv:409`. |

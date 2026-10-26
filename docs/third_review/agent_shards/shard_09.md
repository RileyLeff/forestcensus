# Agent 09 third-review shard

Date: 2026-05-11

Scope: assigned current flagged tags only. Investigation only; no config, source data, generated outputs, or pipeline code were edited.

## Summary counts

| recommended_action | count |
|---|---:|
| source check / human call | 7 |
| source-row correction candidate | 3 |
| rule-generated decision candidate | 3 |
| accept candidate identity link | 3 |
| stem-profile decision candidate | 2 |
| already partially handled / still needs call | 1 |
| source check, possible rule candidate | 1 |
| no immediate change / watch | 1 |

## Recurring patterns

- Dead-only explicit old-tag links look safe when taxon, plot, and status agree and the target lacks contradictory DBH evidence: `L5/413 -> L5/985`, `M7/5832 -> M7/914`, and likely `L7/506 -> L7/974`.
- Some candidate links should stay blocked when the source endpoint has unresolved mortality noise: `L7/982` is only clean if `L7/5029` is first resolved.
- One-survey death labels bracketed by live evidence remain strong rule-generated decision candidates, especially with explicit notes such as `marked as dead last year`.
- Dead-tree DBH decreases should be preserved, but isolated dead-tree DBH increases surrounded by smaller compatible values are good source-row DBH strike candidates.
- Stem-profile flags divide cleanly into blank-backfill cases: a missing secondary stem between observed secondary stems, or a new persistent large secondary stem that probably needs retrospective blank rows.
- Stable incompatible DBH eras remain source-era/tag-alignment review cases, not safe automatic edits, unless a repeated early low value is obviously missing a leading digit.

## Cases

### L6/91

| Field | Notes |
|---|---|
| `selection` | tag 91, plot L6, UUID `55d350ad28f9e8ad`. |
| `related_uids` | `55d350ad28f9e8ad`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `dead_tree_dbh_gap`; `tag_scope_note_review`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw: dead-tree bounded DBH gap plus tag/stem-scope note review. |
| `evidence_summary` | Dead Juniperus DBH 86 in 2019-2020, dead/no DBH in 2021, June 2022 note `could be one of the new tags`, dead/no DBH or DBH 84 through April 2025, then October 2025 alive health 1 with no DBH. |
| `interpretation` | This is not a DBH issue; the review-worthy part is the note plus a possible dead-to-alive reversal in October 2025. Could be a refound low-vigor tree, a tag/new-tag ambiguity, or latest-survey status ambiguity. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID/tag-plot mortality/status and tag-scope note. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | none; notes containing `could be one of the new tags` should remain human identity/stem-scope review. |
| `source_rows_to_check` | `2023_and_prior.csv:3911`, plus October 2025 reviewed row `import_recent_format_reviewed.csv:1314`. |

### L5/413

| Field | Notes |
|---|---|
| `selection` | tag 413, plot L5, UUID `f4529e9a4e6e22d2`; linked target `L5/985`. |
| `related_uids` | `f4529e9a4e6e22d2`, target `L5/985` UUID from candidate link. |
| `raw_flags` | `dead_tree_dbh_gap` info only. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw; candidate identity link remains `needs_human` because target lacks comparable DBH. |
| `evidence_summary` | `413` is dead Juniperus: DBH 85 in 2019-2020, dead/no DBH in 2021-2022, dead DBH 83 in 2024, dead/not-found afterward. `985` appears in June 2023 with `old_tag=413`, same taxon, dead/no DBH; later rows remain inferred dead or DNF. |
| `interpretation` | Clean dead-tree retag. The target lacks DBH, but there is no taxon/status contradiction and the source DBH profile is boring. |
| `recommended_action` | accept candidate identity link |
| `decision_scope` | candidate link / identity alias `L5/413 -> L5/985`. |
| `confidence` | high |
| `needs_riley_call` | no, unless every link accept needs explicit approval. |
| `candidate_auto_rule` | Accept explicit old-tag links where source and target are same plot/taxon, dead-only or inferred-dead, and target has no conflicting DBH. |
| `source_rows_to_check` | link evidence row 15; `2023_and_prior.csv:4619`, source rows `124`, `64`, `194`, `334`, `2024_spring.csv:695`, `2024_fall.csv:304`. |

### L7/982

| Field | Notes |
|---|---|
| `selection` | tag 982, plot L7, UUID `b3105e264931fae3`; linked source `L7/5029`. |
| `related_uids` | `b3105e264931fae3`, source `6dee2ac0a2e04a36` (`L7/5029`). |
| `raw_flags` | target: `nonqualifying_tree_excluded`; source has mortality contradictions and zombie evidence. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw; candidate link remains because source endpoint has unresolved mortality/DBH findings. |
| `evidence_summary` | Target `982` is dead/nonqualifying with `old_tag=5029` in June 2023 and a May 2024 note `fell`; no comparable DBH. Source `5029` is low-vigor Juniperus: alive DBH 103 health 2 in 2021, dead in 2022, alive DBH 103 health 1 in May 2024, dead in April 2025, alive DBH 101 health 1 in October 2025. |
| `interpretation` | The target itself is simple, but accepting the link would merge it into a source with unresolved alive/dead oscillation. Resolve `5029` mortality first. |
| `recommended_action` | source check / human call |
| `decision_scope` | candidate link plus source UUID mortality/status rows. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Explicit old-tag dead-target links should be excluded from auto-accept when the source endpoint has active mortality contradictions. |
| `source_rows_to_check` | target `2023_and_prior.csv:4758`; source `2023_and_prior.csv:1297`, `312`, `2024_spring.csv:1068`, `2025_spring.csv:499`, `import_recent_format_reviewed.csv:1396`. |

### M7/5832

| Field | Notes |
|---|---|
| `selection` | tag 5832, plot M7, UUID `1cbf3e349dccbfc1`; linked target `M7/914`. |
| `related_uids` | `1cbf3e349dccbfc1`, target `c71bbe1153464562`. |
| `raw_flags` | `I_INFERRED_DEAD` in 2024; no contradictory warning. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw; candidate link remains because one endpoint lacks comparable DBH. |
| `evidence_summary` | `5832` is dead Juniperus/no DBH in 2021-2022, then inferred dead in 2024. `914` has `old_tag=5832` in June 2023, dead/no DBH, then dead DBH 171-173 in 2024 and dead/not-found later. |
| `interpretation` | Plausible dead-tree retag. A first measured DBH after the tag change is not itself suspicious for a dead standing tree. |
| `recommended_action` | accept candidate identity link |
| `decision_scope` | candidate link / identity alias `M7/5832 -> M7/914`. |
| `confidence` | high |
| `needs_riley_call` | no, unless all explicit links require approval. |
| `candidate_auto_rule` | Same dead-only explicit old-tag rule as `L5/413`, allowing first post-link dead DBH when there is no conflict. |
| `source_rows_to_check` | link evidence row 28; `2023_and_prior.csv:5085`, source rows `307`, `309`, target rows `2024_spring.csv:778`, `2024_fall.csv:871`. |

### L7/974

| Field | Notes |
|---|---|
| `selection` | tag 974, plot L7, UUID `967919820f93bb56`; linked source `L7/506`. |
| `related_uids` | `967919820f93bb56`, source `L7/506`. |
| `raw_flags` | none on target; candidate link because target lacks comparable DBH. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Source `506` is Pinus DBH 312 health 6 in June 2021, then missing/no GPS coordinates in 2022 and inferred dead later. Target `974` appears in June 2023 with `old_tag=506`, same taxon, dead/no DBH, remains dead/missing. |
| `interpretation` | Likely retag of a Pinus that disappeared or died between 2021 and 2023. Less clean than fully dead-only source links, but taxon/plot/old-tag evidence is consistent and there is no contradictory target DBH. |
| `recommended_action` | accept candidate identity link |
| `decision_scope` | candidate link / identity alias `L7/506 -> L7/974`; preserve mortality transition around 2022-2023. |
| `confidence` | medium |
| `needs_riley_call` | no, unless link accepts are manually gated. |
| `candidate_auto_rule` | Explicit old-tag link with same taxon and source missing before target dead appearance may be a lower-confidence auto-link class. |
| `source_rows_to_check` | link evidence row 20; source `2023_and_prior.csv:2008`, `3970`; target `2023_and_prior.csv:4754`, `2024_fall.csv:492`, `2025_spring.csv:480`. |

### L5/435

| Field | Notes |
|---|---|
| `selection` | tag 435, plot L5, UUID `b49a9f7347eb20a9`. |
| `related_uids` | `b49a9f7347eb20a9`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `health_rebound_new_stem_context`; qualifying rank gaps. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive DBH 338 health 9 in 2019-2020; dead/no DBH in 2021-2023; dead DBH 322-325 in 2024; April 2025 dead/no DBH; October 2025 alive health 6 DBH 317. |
| `interpretation` | The October 2025 live row is the real issue. It could be a refound low/partial live tree, a status/health error, or a different stem/tree under the same tag. The DBHs are compatible with the old tree, so this is not a DBH mismatch. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID mortality/status, especially October 2025; possibly blank DBH gaps for dead intervals. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | none; latest trusted survey revives a long-dead Pinus with compatible DBH, so this needs field judgment. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:1240`, plus dead interval rows `831`, `952`, `4602`, `2024_spring.csv:717`, `2024_fall.csv:326`. |

### L1/108

| Field | Notes |
|---|---|
| `selection` | tag 108, plot L1, UUID `0d1a370be1ab6669`. |
| `related_uids` | `0d1a370be1ab6669`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `single_survey_death_label_outlier`; qualifying rank gaps. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive DBH 318.5 health 8 in 2019-2020; June 2021 dead/no DBH; June 2022 alive DBH 333 health 1; June 2023 onward observed dead, with later DBHs 321-318 and then missing. |
| `interpretation` | June 2021 is likely an uncertain/missed row rather than true death because it is bracketed by alive measured rows. June 2023+ can still be real mortality after the low-health 2022 observation. |
| `recommended_action` | rule-generated decision candidate |
| `decision_scope` | mortality/status for June 2021 source row; keep June 2023+ dead evidence. |
| `confidence` | high for June 2021 being uncertain; medium for exact replacement health/status. |
| `needs_riley_call` | no for routing; yes only if choosing an exact health replacement. |
| `candidate_auto_rule` | Alive measured row -> one dead/no-DBH row -> alive measured row should reinterpret the dead row as uncertain/missing, not whole-tree death. |
| `source_rows_to_check` | `2023_and_prior.csv:789`; surrounding rows `2459`, `2443`, `1289`, `4369`. |

### R2/5303

| Field | Notes |
|---|---|
| `selection` | tag 5303, plot R2, UUID `0433f08b5019aa64`. |
| `related_uids` | `0433f08b5019aa64`. |
| `raw_flags` | none. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | `new_in_october_2025` review bucket only. |
| `evidence_summary` | First appears in October 2025 as Ilex opaca DBH 65, health 6, standing/alive. |
| `interpretation` | Looks like a normal newly qualifying tree above threshold. No contradiction found in current artifacts. |
| `recommended_action` | no immediate change / watch |
| `decision_scope` | none unless the project wants every new October 2025 tree manually accepted. |
| `confidence` | medium |
| `needs_riley_call` | no |
| `candidate_auto_rule` | New October 2025 trees with DBH >= 50, positive health, and no conflicting prior evidence can be routed to watch/accept rather than needs-review. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:107`. |

### L7/19

| Field | Notes |
|---|---|
| `selection` | tag 19, plot L7, UUID `3381658bb8c5b64f`. |
| `related_uids` | `3381658bb8c5b64f`. |
| `raw_flags` | `W_BELOW_THRESHOLD_DBH`; `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `dead_tree_dbh_increase`; `dead_tree_dbh_loss`; `subthreshold_dbh_present`; `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus DBH 50 in 2019-2020, dead/no DBH in 2021, dead DBH 112 in June 2022, dead/no DBH in 2023, then dead subthreshold DBH 47-49 in 2024-2025. |
| `interpretation` | Dead-tree DBH loss from 50 to high-40s is plausible and should be preserved as evidence. The isolated June 2022 DBH 112 is not compatible with the earlier/later dead profile and should be source-row reviewed or struck. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | DBH field for June 2022 source row; preserve dead status and later subthreshold dead evidence separately. |
| `confidence` | high that 112 is wrong; medium on exact correction versus suppress-to-missing. |
| `needs_riley_call` | no for suppressing 112; yes if selecting a corrected numeric DBH. |
| `candidate_auto_rule` | Isolated large DBH increase on an observed-dead tree surrounded by smaller compatible dead DBHs should be a DBH-suppress candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:408`; below-threshold rows `2024_spring.csv:498`, `2024_fall.csv:446`, `import_recent_format_reviewed.csv:1371`. |

### R4/5227

| Field | Notes |
|---|---|
| `selection` | tag 5227, plot R4, UUID `568f925040c6ec87`. |
| `related_uids` | `568f925040c6ec87`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`; `W_TREE_LARGE_STEM_DISAPPEARANCE`; `W_TREE_LARGE_STEM_APPEARANCE`; `bounded_stem_rank_gap`; `blank_missing_stem_backfill_candidate`; `new_persistent_large_stem`; `stem_mortality_context`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Acer has two stems in June 2023: 106 and 90, both alive. May 2024 records only the 100 mm main stem. October 2024 onward records two stems again: main stem alive around 102-104 and secondary stem 85-89, dead/health 0. |
| `interpretation` | Clean bounded missing secondary-stem gap. May 2024 likely omitted the second stem; the later dead secondary stem is consistent with the June 2023 second stem. |
| `recommended_action` | stem-profile decision candidate |
| `decision_scope` | insert blank/missing rank-2 row for May 2024; preserve later dead secondary-stem evidence. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Prior and later same-sized secondary stem with a one-survey omission should generate blank missing-stem backfill, not a new-stem review. |
| `source_rows_to_check` | `2023_and_prior.csv:5259`, `5260`; `2024_spring.csv:190`; `2024_fall.csv:1325`, `1366`; `2025_spring.csv:787`, `788`; October 2025 rows `198`, `199`. |

### H1/242

| Field | Notes |
|---|---|
| `selection` | tag 242, plot H1, UUID `8ea91d9d7c2afbc4`. |
| `related_uids` | `8ea91d9d7c2afbc4`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`; `W_TREE_LARGE_STEM_APPEARANCE`; `new_persistent_large_stem`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa single main stem 115 in 2019-2020 and 101 in 2021. A second stem appears in June 2022 at 66 mm and persists at 68-73 mm through 2025. October 2025 records both stems dead/health 0. |
| `interpretation` | Secondary stem was already well above threshold when first recorded, so it likely needs retrospective blank history before June 2022 rather than being treated as a brand-new stem with no prior evidence. |
| `recommended_action` | stem-profile decision candidate |
| `decision_scope` | stem profile / blank history for rank 2 before June 2022; preserve October 2025 mortality for both stems. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | New persistent qualifying stem first appearing above 60 mm should generate prior blank stem-history rows. |
| `source_rows_to_check` | `2023_and_prior.csv:1555`, `1556`, `4080`, `4081`; `2024_fall.csv:1415`, `1432`; `2025_spring.csv:1015`, `1016`; October 2025 rows `330`, `331`. |

### H7/459

| Field | Notes |
|---|---|
| `selection` | tag 459, plot H7, UUID `5cdc5eb564940f29`. |
| `related_uids` | `5cdc5eb564940f29`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `explicit_note_mortality_correction_candidate`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus recorded dead/0 DBH 408 in June 2021; June 2022 is alive health 6 DBH 408 with note `marked as dead last year`; subsequent surveys stay alive with DBH 405-417 and health 2-7. |
| `interpretation` | Very clean source-note correction. June 2021 dead label should be uncertain/wrong; DBH is compatible with the same live tree. |
| `recommended_action` | rule-generated decision candidate |
| `decision_scope` | mortality/status for June 2021 source row. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Notes like `marked as dead last year` on a compatible live follow-up should reinterpret the previous dead row as uncertain/alive-label-error. |
| `source_rows_to_check` | `2023_and_prior.csv:775`, `2036`; later rows `4283`, `2024_spring.csv:299`, `2024_fall.csv:1122`, `2025_spring.csv:941`. |

### L6/99

| Field | Notes |
|---|---|
| `selection` | tag 99, plot L6, UUID `5a2ba2c11f3793c9`. |
| `related_uids` | `5a2ba2c11f3793c9`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa alive DBH 240 health 9 in 2019-2020. June 2021 has alive flag false but health 3 and interpreted alive; June 2022-2023 alive health 2-3. October 2024 is dead/0 DBH 203, then April/October 2025 alive health 1. |
| `interpretation` | The October 2024 dead/0 row is bracketed by low-health live evidence and should likely be uncertain/missing rather than death. June 2021 alive/dead field conflict is also consistent with health being more reliable than the binary label. |
| `recommended_action` | rule-generated decision candidate |
| `decision_scope` | mortality/status for October 2024 row; possibly label reconciliation for June 2021 if not already handled by health-first interpretation. |
| `confidence` | high for October 2024 being uncertain; medium for June 2021 field-label treatment. |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Low-health alive -> one observed-dead/zero-health row -> later alive should reinterpret the dead row as uncertain. |
| `source_rows_to_check` | `2024_fall.csv:428`; June 2021 row `2023_and_prior.csv:1396`; follow-up `2025_spring.csv:412`, October 2025 row `1322`. |

### M6/383

| Field | Notes |
|---|---|
| `selection` | tag 383, plot M6, UUID `1a5b7be08e38ba4c`. |
| `related_uids` | `1a5b7be08e38ba4c`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `observed_mortality_event`; `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus dead DBH 97 in 2019-2020, dead/no DBH through 2023, dead DBH 100 with poison ivy in May 2024, October 2024 alive health 8/no DBH with poison ivy, then dead DBH 100-101 in 2025. |
| `interpretation` | October 2024 is a lone high-health live row inside a long dead sequence, with poison ivy context. Could be a status/health typo, a wrong tag, or difficult measurement/refinding around poison ivy. |
| `recommended_action` | source check / human call |
| `decision_scope` | mortality/status for October 2024; preserve dead-tree DBH gaps. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Isolated healthy alive rows inside long-dead sequences should flag for review, but should not auto-correct. |
| `source_rows_to_check` | `2024_fall.csv:801`, `2024_spring.csv:1145`, `2025_spring.csv:1320`, October 2025 row `851`. |

### L3/5881

| Field | Notes |
|---|---|
| `selection` | tag 5881, plot L3, UUID `a5e6bc5486b26914`. |
| `related_uids` | `a5e6bc5486b26914`. |
| `raw_flags` | raw included `W_BELOW_THRESHOLD_DBH` for June 2022 DBH 30, `W_DBH_JUMP`, `source_note_dbh_conflict`, `mortality_contradiction`, `single_survey_death_label_outlier`, `prior_live_blank_dbh_history`, and inferred-dead rows. |
| `configured_decisions_applied` | `row_correction:0038` suppresses June 2022 DBH 30 while preserving the alive/new-tree evidence. |
| `current_flags` | DBH/subthreshold flags resolved; remaining `I_ZOMBIE_TREE`, inferred-dead context, `mortality_contradiction`, `single_survey_death_label_outlier`, and prior live blank DBH history. |
| `evidence_summary` | June 2022 unidentified alive health 10 with note `New tree in 2022?` after DBH suppression. June 2023 Pinus dead/0. May 2024 Pinus DBH 380 health 2 alive but fallen; October 2024 Pinus DBH 364 dead plus second unidentified dead row with note `error? (pointing to "30/10/1/NA")`; later inferred dead. |
| `interpretation` | The existing correction fixed the clear below-threshold DBH problem. Remaining issue is not mechanical: the 2022 unidentified live/new-tree evidence, 2023 dead row, and 2024 large fallen Pinus may be tag/species/source alignment noise. |
| `recommended_action` | already partially handled / still needs call |
| `decision_scope` | UUID/source-row mortality and identity/species context after the already-applied DBH suppression. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Existing subthreshold-suppress rule worked; do not auto-resolve the remaining mortality/identity ambiguity. |
| `source_rows_to_check` | `2023_and_prior.csv:3879`, `4527`; `2024_spring.csv:629`, `630`; `2024_fall.csv:236`, `237`. |

### L1/116

| Field | Notes |
|---|---|
| `selection` | tag 116, plot L1, UUID `dc596c0f1d7c1e28`. |
| `related_uids` | `dc596c0f1d7c1e28`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 260 in 2019-2020, then stable 163-173 from 2021-2025, alive throughout. |
| `interpretation` | Stable incompatible DBH eras, likely source-era/tag-alignment or early carried-forward wrong DBH. Not a one-row typo because each side has repeated support. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID-level source-era DBH block, especially 2019-2020 versus 2021+. |
| `confidence` | high that this is not biological growth/decay; medium on which era is correct. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Stable incompatible eras should create a grouped source-era queue, not an automatic numeric correction. |
| `source_rows_to_check` | `2023_and_prior.csv:3114`, `3090`, `2081`, `1935`, `4377`, `2024_spring.csv:1313`, `2024_fall.csv:71`. |

### H4/148

| Field | Notes |
|---|---|
| `selection` | tag 148, plot H4, UUID `67bff9fe98541e3a`. |
| `related_uids` | `67bff9fe98541e3a`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `early_low_dbh_source_era_candidate`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus DBH 67 in 2019-2020, then stable large Pinus DBH 371-393 from 2021-2025, alive throughout. |
| `interpretation` | Very likely a repeated early low source-era artifact, possibly missing leading digit/carry-forward (`67` should maybe be `367` or similar). The post-2021 large Pinus profile is coherent. |
| `recommended_action` | source check, possible rule candidate |
| `decision_scope` | source-era DBH block for 2019-2020 rows. |
| `confidence` | high that 67 is wrong; medium on exact corrected value. |
| `needs_riley_call` | yes if choosing exact numeric replacement; no if suppressing early DBH to missing is acceptable. |
| `candidate_auto_rule` | Repeated early DBH below/near threshold followed by a stable large Pinus profile could be a missing-leading-digit/source-era candidate, but exact correction needs source review. |
| `source_rows_to_check` | `2023_and_prior.csv:3965`, `3710`, and transition row `2477`. |

### H1/233

| Field | Notes |
|---|---|
| `selection` | tag 233, plot H1, UUID `b7f43fa53a55ec8c`. |
| `related_uids` | `b7f43fa53a55ec8c`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 353 in 2019-2020, then stable small Nyssa DBH 67-78 from 2021-2025, alive throughout with health declining to 2 by October 2025. |
| `interpretation` | Stable incompatible eras. The later 67-78 mm regime is coherent for five surveys; the early 353 mm values may belong to a different tree/tag or source block. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID/source-era DBH alignment; possibly early rows only. |
| `confidence` | high that eras are incompatible; medium on whether to suppress early DBH versus split identity. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Group with stable incompatible source-era cases; do not auto-fix without known block mapping. |
| `source_rows_to_check` | `2023_and_prior.csv:3341`, `3352`, `2671`, `1975`, `4071`. |

### M3/349

| Field | Notes |
|---|---|
| `selection` | tag 349, plot M3, UUID `9ea87e906e811ef3`. |
| `related_uids` | `9ea87e906e811ef3`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Large Pinus is stable around 514-519 in 2019-2020 and 2022-2025. June 2021 alone reports DBH 418 health 9. October 2025 has no DBH because DBH collection stopped, note `Potential missing tag`. |
| `interpretation` | June 2021 DBH 418 is an isolated low outlier in an otherwise very stable large pine. Health/taxon/status do not suggest a real 100 mm loss and rebound. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | DBH field for June 2021 source row; preserve alive/status. |
| `confidence` | high |
| `needs_riley_call` | no if suppressing DBH to missing; yes if selecting an exact corrected value. |
| `candidate_auto_rule` | Single-survey DBH outlier bracketed by stable same-sized values should generate source-row DBH suppress candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:2892`; neighbors `3840`, `2250`, `4923`. |

### L5/5049

| Field | Notes |
|---|---|
| `selection` | tag 5049, plot L5, UUID `c002c829b1bdad22`. |
| `related_uids` | `c002c829b1bdad22`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 156 in 2021, 178 in 2022, 165 in 2023, then May 2024 DBH 115, October 2024 162, April 2025 173, October 2025 164 with note `- Elbow`. |
| `interpretation` | May 2024 DBH 115 is an isolated low outlier. Later rows return to the 160-170 range; the October 2025 elbow note may explain measurement variability but not the 50 mm drop. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | DBH field for May 2024 source row; preserve alive/health. |
| `confidence` | high |
| `needs_riley_call` | no if suppressing May 2024 DBH; yes if choosing exact corrected value. |
| `candidate_auto_rule` | Isolated one-survey DBH outlier with immediate return to baseline should become DBH suppress/review candidate. |
| `source_rows_to_check` | `2024_spring.csv:732`; neighbors `2023_and_prior.csv:4617`, `2024_fall.csv:341`, `2025_spring.csv:349`, October 2025 row `1265`. |

### L7/7

| Field | Notes |
|---|---|
| `selection` | tag 7, plot L7, UUID `56958e23449dffa2`. |
| `related_uids` | `56958e23449dffa2`. |
| `raw_flags` | `W_DBH_JUMP`; `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus alive DBH 342 in 2019-2020, then stable 168-177 from 2021-2025, alive throughout. |
| `interpretation` | Stable incompatible DBH eras. Later small-tree regime has five surveys of support; early 342 values are likely source-era/tag-alignment or wrong-unit/wrong-tree artifacts. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID-level source-era DBH block, likely 2019-2020 rows. |
| `confidence` | high that eras are incompatible; medium on corrective action. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Same stable-era queue as `L1/116` and `H1/233`; no automatic correction unless a broader source-era mapping is confirmed. |
| `source_rows_to_check` | `2023_and_prior.csv:1878`, `1877`, `1501`, `1386`, `4749`. |

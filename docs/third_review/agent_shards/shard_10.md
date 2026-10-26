# Agent 10 shard

Assigned current flagged tags reviewed: 21.

## Summary

| recommended_action | count | cases |
|---|---:|---|
| `source check / human call` | 8 | L1/5052, L1/5050, H3+L0/153, L7/498, L6/101, H1/249, L6/59, H1/235 |
| `source-row correction candidate` | 7 | L1/110, L7/12, L5/412, H4/150, M6/362, L1/5060, L6/70 |
| `rule-generated decision candidate` | 3 | L2/222, H6/529, H7/460 |
| `candidate identity link review` | 2 | M2/5883, L5/985 |
| `no immediate change / watch context` | 1 | L1/122 |

Top recurring patterns:

- Raw and current flags are almost identical for this shard. Except for the already-applied L7/12 taxon override, these are unresolved post-decision cases rather than configured decisions failing to propagate.
- Several clean DBH cases look like source-row scoped field suppression/correction candidates: isolated dead-tree DBH rebound rows, early low DBH source-era rows that are probably missing a leading digit, and one-survey high DBH outliers bracketed by stable values.
- Mortality contradictions split into two flavors: true human-call zombie/marginal-live cases, and stronger rule candidates where a single death row is followed by durable alive evidence.
- Candidate tag links often need endpoint-specific treatment: accept the identity link only if the source evidence is explicit, then handle duplicate/overlapping rows or DBH outliers separately.
- Stem-profile flags are most useful when they point to a missing-stem blank backfill or a wrong-tag/wrong-stem row, not when they imply persistent stem identity.

## Cases

### L1/5052

| Field | Notes |
|---|---|
| `selection` | L1/5052; UUID `33a6719e51c59619`; neighbor context L1/5051 UUID `8116d9c6e44ee424`. |
| `related_uids` | `33a6719e51c59619`, `8116d9c6e44ee424`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `tag_scope_note_review`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | L1/5052 is a Juniperus/unknown stem around 198 -> 176 -> 166 -> 184 mm, then October 2024 has two stems: 216 mm in slot 2 and 169 mm in slot 1. April 2025 keeps only 169 mm with note `to 5051`; October 2025 has a normal stem plus a blank second row noted `NO second stem`. L1/5051 is a nearby stable Juniperus around 207-210 mm, missing in October 2024, then April 2025 note `connected belowgr.` |
| `interpretation` | The October 2024 216 mm row under 5052 looks like it may belong to 5051, while the 169 mm row continues 5052. The notes strongly suggest a tag/stem-scope confusion around belowground-connected junipers rather than a true new 5052 stem. |
| `recommended_action` | `source check / human call`: inspect October 2024 L1 rows 110-127 and decide whether `2024_fall.csv:127` should be reassigned from 5052 to 5051 or suppressed as a duplicate/wrong-tag row. |
| `decision_scope` | Source row / tag-plot / possible stem-profile reassignment. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Tag-scope notes like `to X` plus complementary missing neighbor DBH should route to a wrong-tag/complementary-tree review, not a generic stem-count review. |
| `source_rows_to_check` | L1/5052 `2024_fall.csv:111`, `2024_fall.csv:127`, `2025_spring.csv:113`, October 2025 rows `1031-1032`; compare L1/5051 `2024_fall.csv:110`, `2025_spring.csv:112`. |

### L1/5050

| Field | Notes |
|---|---|
| `selection` | L1/5050; UUID `5bb83fab7f93aa9d`. |
| `related_uids` | `5bb83fab7f93aa9d`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Unidentifiable stem alive in 2021-2022 at 124-125 mm with health 3, dead health 0/no DBH in June 2023, alive again May 2024 DBH 125 health 2 with note `zombie?`, alive October 2024 and April 2025, then dead health 0 in October 2025. |
| `interpretation` | This is not a clean typo. The May 2024 `zombie?` note suggests the field crew recognized possible live tissue after a death label. October 2025 later death could be real. |
| `recommended_action` | `source check / human call`: Riley should decide whether June 2023 is a true dead interval, uncertain/not-found, or a mortality-label error. |
| `decision_scope` | Mortality/status for June 2023 and possibly the May 2024 zombie note. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Do not auto-correct single death rows when later notes explicitly say `zombie?`; route to marginal-live review. |
| `source_rows_to_check` | `2023_and_prior.csv:4414`, `2024_spring.csv:1352`, `2025_spring.csv:111`, October 2025 row `1029`. |

### H3+L0/153

| Field | Notes |
|---|---|
| `selection` | Bare tag 153 covers two independent scopes: H3/153 UUID `d3b7e571fd02d6d3` and L0/153 UUID `3dc6e5ba231dcb88`; L0/153 also has candidate link to L0/921 UUID `c905ff266d7e4c1f`. |
| `related_uids` | `d3b7e571fd02d6d3`, `3dc6e5ba231dcb88`, `c905ff266d7e4c1f`. |
| `raw_flags` | H3: DBH/stem-count/ranked-jump flags plus `measurement_note_dbh_context`, `stem_mortality_context`, `near_duplicate_stem_artifact`, `stable_incompatible_dbh_era`, `bounded_stem_rank_gap`, `probable_duplicate_stem_artifact`. L0: `I_INFERRED_DEAD` and candidate link. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | H3/153 is Nyssa. 2019-2020 has one 139 mm stem despite 2019 note `Two trunks`; 2021-2023 has three stems around 236/129-149/129-131; May 2024 has 232/131/131; October 2024 has the two smaller DBHs but the slot 1/largest stem has health 9 and no DBH; April 2025 returns to 235/133/129. L0/153 is a dead Pinus 298 mm in 2019-2020, later dead/not-found, and has an explicit candidate link to dead/no-DBH L0/921. |
| `interpretation` | H3/153 needs stem-profile/source-era review: the October 2024 largest-stem DBH is blank rather than biologically absent, and the 2019-2020 one-stem era may be missing the larger stem. L0/153 -> L0/921 is a separate dead-pine tag-change question and should not be entangled with H3. |
| `recommended_action` | `source check / human call`: split review into H3 UUID stem-profile decisions and L0 candidate-link decision. |
| `decision_scope` | H3: source-row/stem-profile blank backfill or DBH-field decisions. L0: candidate identity link. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Bare-tag review should split by plot/UUID when the same tag exists in multiple plots; blank DBH for a known large stem should become a missing-stem/backfill candidate rather than a ranked DBH jump. |
| `source_rows_to_check` | H3/153 `2023_and_prior.csv:3303`, `3381`, `2381-2382`, `1750`, `3561-3563`, `4136-4138`, `2024_fall.csv:971`, `999`, `1001`; L0 link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:5`; L0/921 rows `2023_and_prior.csv:4363`, `2024_spring.csv:52`, `2024_fall.csv:54`, `2025_spring.csv:51`. |

### M2/5883

| Field | Notes |
|---|---|
| `selection` | M2/5883; UUID `0e11403b2685d1b0`; candidate target M2/5863 UUID `e64ad49eb5a8f561`. |
| `related_uids` | `0e11403b2685d1b0`, `e64ad49eb5a8f561`. |
| `raw_flags` | None on M2/5883 itself. Candidate link exists; target M2/5863 has `single_survey_dbh_outlier`, `W_DBH_JUMP`, and `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw/link state. |
| `evidence_summary` | M2/5883 is unidentifiable alive at 114-119 mm in 2021-2022, then M2/5863 appears in 2023 at 127 mm and continues 125/121 mm in 2024-2025. M2/5863 has one suspicious May 2024 DBH 163 with unknown status. Explicit link evidence says 5883 -> 5863. |
| `interpretation` | The identity link is plausible, but the target endpoint has an isolated DBH outlier that should be handled separately. |
| `recommended_action` | `candidate identity link review`: likely accept the 5883 -> 5863 link after source check, and separately suppress/correct M2/5863 May 2024 DBH 163. |
| `decision_scope` | Candidate link plus DBH field at `2024_spring.csv:920`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Candidate links should not be blocked by an isolated endpoint DBH outlier; route as link decision plus row-level DBH decision. |
| `source_rows_to_check` | Link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:23`; M2/5883 `2023_and_prior.csv:2515`, `2256`, `2024_fall.csv:657`; M2/5863 `2023_and_prior.csv:4909`, `2024_spring.csv:920`, `2024_fall.csv:656`, `2025_spring.csv:880`. |

### L5/985

| Field | Notes |
|---|---|
| `selection` | L5/985; UUID `5ec0bad70738738e`; candidate source L5/413 UUID `f4529e9a4e6e22d2`. |
| `related_uids` | `5ec0bad70738738e`, `f4529e9a4e6e22d2`. |
| `raw_flags` | `I_INFERRED_DEAD`; candidate identity link. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | L5/985 is Juniperus dead/no-DBH from June 2023 onward with inferred-dead/not-found rows. L5/413 is Juniperus dead 85 mm in 2019-2020, dead/no-DBH in 2021-2022, then measured dead 83 mm in 2024. Candidate link says L5/413 -> L5/985, but the two tags overlap in the later accepted rows. |
| `interpretation` | The explicit tag-change evidence is plausible, but overlap means this may be duplicate continuation rows rather than a simple alias window. |
| `recommended_action` | `candidate identity link review`: source-check the explicit old/new tag evidence; if accepted, also decide how to suppress or reconcile overlapping dead rows under 413 and 985. |
| `decision_scope` | Candidate link plus possible duplicate row suppression after the effective change date. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Dead-only tag links with overlapping endpoints should require source review before aliasing. |
| `source_rows_to_check` | Link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:15`; L5/985 `2023_and_prior.csv:4619`, `2024_spring.csv:734`, `2024_fall.csv:343`, `2025_spring.csv:342`; L5/413 `2023_and_prior.csv:124`, `64`, `194`, `334`, `2024_spring.csv:695`, `2024_fall.csv:304`. |

### L7/498

| Field | Notes |
|---|---|
| `selection` | L7/498; UUID `2f61f41ba489ce73`. |
| `related_uids` | `2f61f41ba489ce73`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `health_rebound_new_stem_context`, `stem_mortality_context`, `mortality_contradiction`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Morella cluster alive 88 mm health 10 in 2021, dead in 2022-2023, alive 85 mm health 5 in May 2024 with note `1 dead trunk`, dead again October 2024 and April 2025, then October 2025 note `Dead fallen`. |
| `interpretation` | The `cluster` and `1 dead trunk` notes make this a real plant/stem-scope ambiguity, not a clean mortality typo. |
| `recommended_action` | `source check / human call`: decide whether May 2024 represents a live stem on a mostly dead cluster or should be treated as a mortality-label error. |
| `decision_scope` | Mortality/status plus stem-profile context. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Morella/cluster cases with dead-trunk notes should route to human stem-scope review rather than automatic zombie correction. |
| `source_rows_to_check` | `2023_and_prior.csv:3276`, `417`, `4733`, `2024_spring.csv:1065`, `2024_fall.csv:470`, `2025_spring.csv:476`, October 2025 row `1390`. |

### L1/110

| Field | Notes |
|---|---|
| `selection` | L1/110; UUID `787f462cd06e006a`. |
| `related_uids` | `787f462cd06e006a`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `dead_tree_dbh_increase`, `single_survey_dbh_outlier`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive around 331-340 mm through 2022, dead/no-DBH in 2023, dead 332 mm in May 2024, dead 132 mm in October 2024, dead 330 mm in April 2025 and dead in October 2025. |
| `interpretation` | October 2024 132 mm is an isolated dead-tree DBH outlier bracketed by 332 and 330. It is likely a dropped leading digit or wrong field entry, not decay. |
| `recommended_action` | `source-row correction candidate`: source-check and then suppress/correct only the October 2024 DBH. |
| `decision_scope` | DBH field at `2024_fall.csv:65`. |
| `confidence` | High. |
| `needs_riley_call` | No, unless source image is ambiguous. |
| `candidate_auto_rule` | Dead-tree DBH can decline, but a single low dead DBH bracketed by near-identical high dead DBHs should become a row-level DBH correction candidate. |
| `source_rows_to_check` | `2024_spring.csv:1307`, `2024_fall.csv:65`, `2025_spring.csv:66`. |

### L6/101

| Field | Notes |
|---|---|
| `selection` | L6/101; UUID `9259cb4fec20be45`. |
| `related_uids` | `9259cb4fec20be45`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `single_survey_dbh_outlier`, `mortality_contradiction`, `observed_mortality_event`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus is dead health 0 at 143 mm in 2019-2020, alive health 10 in 2021, alive through 2025, May 2024 has isolated low DBH 101 between 150 and 144/165, then October 2025 dead health 0. |
| `interpretation` | This combines two separate problems: early dead labels before a robust alive history, and a May 2024 DBH outlier that may be 151 or a wrong-row value. |
| `recommended_action` | `source check / human call`: inspect early dead rows and May 2024 source. Do not auto-resolve mortality and DBH together. |
| `decision_scope` | Mortality/status for 2019-2020; DBH field at `2024_spring.csv:455`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | When a mortality contradiction co-occurs with a DBH outlier, split the decision scopes before applying any rule. |
| `source_rows_to_check` | `2023_and_prior.csv:129`, `92`, `3198`, `2024_spring.csv:455`, `2024_fall.csv:352`, `2025_spring.csv:414`, October 2025 row `1324`. |

### L2/222

| Field | Notes |
|---|---|
| `selection` | L2/222; UUID `88f7e3d5ecaca3ac`. |
| `related_uids` | `88f7e3d5ecaca3ac`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `health_rebound_alive_context`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive with declining health from 2019-2024, health 2 in May 2024, then October 2024 dead health 0, April 2025 alive health 1, October 2025 alive health 6. DBH remains stable around 236-237 through the contested row. |
| `interpretation` | This is the cleanest mortality rule candidate in the shard: a single death row bracketed by alive observations and later health rebound, with no DBH/profile evidence that the tree actually disappeared. |
| `recommended_action` | `rule-generated decision candidate`: treat October 2024 death as uncertain/alive-status error after source check; likely set the mortality signal to missing/low-health alive rather than true dead. |
| `decision_scope` | Mortality/status and possibly health at `2024_fall.csv:153`. |
| `confidence` | Medium-high. |
| `needs_riley_call` | Maybe; rule should likely generate a reviewable decision unless source images are checked. |
| `candidate_auto_rule` | Single observed-dead health 0 row bracketed by observed-alive rows, with later health rebound and stable DBH, should be a mortality correction candidate. |
| `source_rows_to_check` | `2024_spring.csv:547`, `2024_fall.csv:153`, `2025_spring.csv:152`, October 2025 row `1067`. |

### H6/529

| Field | Notes |
|---|---|
| `selection` | H6/529; UUID `c6ea65482ee494db`. |
| `related_uids` | `c6ea65482ee494db`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_TREE_LARGE_STEM_APPEARANCE`; invariants `new_persistent_large_stem`, `bounded_stem_rank_gap`, `blank_missing_stem_backfill_candidate`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus has two large stems in 2019, one recorded stem in 2020, then two large stems consistently from 2021 through October 2025. The missing 2020 stem is bracketed by comparable large-stem profiles. |
| `interpretation` | The 2020 one-stem row is almost certainly a missed/blank stem observation, not a new persistent large stem appearing biologically in 2021. |
| `recommended_action` | `rule-generated decision candidate`: insert a blank missing-stem placeholder for June 2020 rank/slot context rather than flagging a new stem. |
| `decision_scope` | Stem profile / blank missing-stem backfill for June 2020. |
| `confidence` | High. |
| `needs_riley_call` | No for routing; source check optional. |
| `candidate_auto_rule` | If a large secondary stem exists before and after a one-survey gap, generate a blank missing-stem backfill candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:3964`, `3593`, `3661`, `2217-2218`, `2034`, `1834`, `4262-4263`. |

### H1/249

| Field | Notes |
|---|---|
| `selection` | H1/249; UUID `498d5e2230eb8eb0`. |
| `related_uids` | `498d5e2230eb8eb0`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus dead health 0 in 2019-2020, alive 2021-2024 with DBH 245-264 and low-moderate health, dead health 0 in April 2025, then October 2025 alive health 7 with DBH 268. |
| `interpretation` | There are two mortality contradictions: the early dead era before a long alive run, and a single April 2025 death row before strong October 2025 alive evidence. This may be tag/source confusion or repeated dead-label mistakes. |
| `recommended_action` | `source check / human call`: source-check early rows and April 2025 before applying any mortality correction. |
| `decision_scope` | Mortality/status, possibly DBH/source-era review. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Durable alive evidence after dead rows should trigger mortality review, but repeated early-plus-late death contradictions should not be auto-collapsed without source context. |
| `source_rows_to_check` | `2023_and_prior.csv:585`, `681`, `1563`, `1346`, `4088`, `2024_fall.csv:1422`, `2025_spring.csv:1023`, October 2025 row `338`. |

### H7/460

| Field | Notes |
|---|---|
| `selection` | H7/460; UUID `2a84c5fd0a750d87`. |
| `related_uids` | `2a84c5fd0a750d87`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `explicit_note_mortality_correction_candidate`, `mortality_contradiction`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Large Pinus dead health 0 at 486 mm in June 2021; June 2022 alive health 5 at 486 mm with note `marked as dead last year`; alive robustly from 2023 through October 2025, DBH 486-494. |
| `interpretation` | The 2021 death label is almost certainly not a true tree death. The 2022 note confirms the prior source label existed, but the long healthy continuation argues for a mortality-label correction rather than a true zombie. |
| `recommended_action` | `rule-generated decision candidate`: convert June 2021 dead status into uncertain/alive-status error after source check, preserving the source note trail. |
| `decision_scope` | Mortality/status at `2023_and_prior.csv:776`; possibly health 0 handling. |
| `confidence` | High. |
| `needs_riley_call` | Maybe; high-confidence but changes a death observation. |
| `candidate_auto_rule` | A single dead row followed by a source note `marked as dead last year` and multiple healthy alive observations should become a mortality correction candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:776`, `1836`, `4284`, `2024_spring.csv:300`, `2024_fall.csv:1123`, `2025_spring.csv:942`. |

### L7/12

| Field | Notes |
|---|---|
| `selection` | L7/12; UUID `368674de00dd9d16`. |
| `related_uids` | `368674de00dd9d16`. |
| `raw_flags` | Raw `W_TAXON_CONFLICT`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `taxon_conflict`, `dead_tree_dbh_gap`, `dead_tree_dbh_increase`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | `taxon_override:0010` sets L7/12 to Pinus taeda and treats the May 2024 Juniperus row as a taxon slip. |
| `current_flags` | Taxon conflict resolved; DBH flags remain: `dead_tree_dbh_gap`, `dead_tree_dbh_increase`, `single_survey_dbh_outlier`. |
| `evidence_summary` | Dead Pinus 162 mm in 2019-2020, dead/no-DBH 2021-2023, dead 158 mm in May 2024, dead 126 mm in October 2024, dead/no-DBH April 2025, then dead 158 mm in October 2025. |
| `interpretation` | Existing taxon decision worked. The remaining October 2024 126 mm value is an isolated dead-tree DBH outlier bracketed by 158 mm values. Dead trees can shrink, but the rebound makes this likely measurement/source error. |
| `recommended_action` | `source-row correction candidate`: source-check and suppress/correct only October 2024 DBH 126. |
| `decision_scope` | DBH field at `2024_fall.csv:439`. |
| `confidence` | High. |
| `needs_riley_call` | No, unless source image is ambiguous. |
| `candidate_auto_rule` | Taxon overrides can resolve one axis while leaving DBH corrections as separate row-level decisions. |
| `source_rows_to_check` | `2024_spring.csv:491`, `2024_fall.csv:439`, October 2025 row `1364`. |

### L5/412

| Field | Notes |
|---|---|
| `selection` | L5/412; UUID `9e10d48ccbb3260f`. |
| `related_uids` | `9e10d48ccbb3260f`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `dead_tree_dbh_gap`, `dead_tree_dbh_increase`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead unidentifiable/Juniperus stem 86 mm in 2019-2020, dead/no-DBH 2021-2023, dead 61 mm in May 2024, dead 83 mm in October 2024, DNF April 2025, dead 90 mm in October 2025. |
| `interpretation` | May 2024 61 mm is the most suspicious value; it is followed by 83/90 mm dead measurements. Could be a 81/86-style typo or a different measurement point, but the later rebound makes it hard to accept as decay alone. |
| `recommended_action` | `source-row correction candidate`: source-check May 2024 DBH 61 and likely suppress/correct the DBH field. |
| `decision_scope` | DBH field at `2024_spring.csv:694`; optional taxon cleanup if source confirms Juniperus. |
| `confidence` | Medium. |
| `needs_riley_call` | Maybe. |
| `candidate_auto_rule` | Dead-tree DBH decreases are allowed, but decreases followed by larger later dead DBH should be row-level outlier candidates. |
| `source_rows_to_check` | `2024_spring.csv:694`, `2024_fall.csv:303`, `2025_spring.csv:309`, October 2025 row `1217`. |

### L6/59

| Field | Notes |
|---|---|
| `selection` | L6/59; UUID `c58d071b84a52509`. |
| `related_uids` | `c58d071b84a52509`. |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `dead_tree_dbh_gap`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus dead health 0 at 56 mm in 2019-2020, dead/no-DBH through 2023, dead 55 mm in October 2024, DNF April 2025, then October 2025 alive health 6/no DBH. |
| `interpretation` | A single 2025 alive health 6 row after years of dead/not-found evidence is suspicious. This could be a source/LLM/manual transcription issue or a wrong tree, but latest survey trust means it needs human review. |
| `recommended_action` | `source check / human call`: inspect the October 2025 source/edit context before changing it; likely either mark October 2025 uncertain/dead or split if it is a new live plant under old tag. |
| `decision_scope` | Mortality/status for October 2025; possible identity split if source shows a different tree. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Long-dead small stems with a single late alive/no-DBH row should route to source review, not automatic zombie correction. |
| `source_rows_to_check` | `2023_and_prior.csv:140`, `41`, `209`, `394`, `4658`, `2024_fall.csv:387`, `2025_spring.csv:372`, October 2025 row `1283`. |

### L1/122

| Field | Notes |
|---|---|
| `selection` | L1/122; UUID `e6326098d232708d`. |
| `related_uids` | `e6326098d232708d`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `max_dbh_jump`, `ranked_dbh_jump`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus stable around 79-85 mm through May 2024 with low health, then 71 mm in October 2024 and April 2025, still alive with health 1-2; October 2025 alive health 1 with no DBH. |
| `interpretation` | This may be a real decline/measurement-point change on a low-health small juniper. Unlike the dead-tree rebound cases, there is no later DBH rebound to prove the 71 mm values wrong. |
| `recommended_action` | `no immediate change / watch context`: keep flagged as context unless a source image shows 71 is a typo. |
| `decision_scope` | None for now; optional DBH source check if batching. |
| `confidence` | Medium. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Sustained smaller DBH in a low-health live tree should be downgraded relative to isolated one-survey outliers. |
| `source_rows_to_check` | Optional: `2024_fall.csv:77`, `2025_spring.csv:78`. |

### H4/150

| Field | Notes |
|---|---|
| `selection` | H4/150; UUID `f76452ae68cac793`. |
| `related_uids` | `f76452ae68cac793`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `early_low_dbh_source_era_candidate`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus recorded 67 mm in 2019-2020, then 377-395 mm from 2021 through 2025, except May 2024 lower at 338 mm. |
| `interpretation` | The 67 mm early era is almost certainly missing a leading digit, likely 367 mm. A Pinus cannot move from 67 to 377 mm in one year, and large pines commonly occupy this DBH range. |
| `recommended_action` | `source-row correction candidate`: source-check and likely correct/suppress 2019-2020 DBH 67 values. |
| `decision_scope` | DBH fields at `2023_and_prior.csv:2785` and `2821`. |
| `confidence` | High. |
| `needs_riley_call` | No, unless handwriting/source is ambiguous. |
| `candidate_auto_rule` | Early two-year low DBH followed by stable large Pinus DBH should become a leading-digit correction candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:2785`, `2821`, compare `1788`, `1861`, `4213`, `2024_spring.csv:335`, `2024_fall.csv:1044`. |

### H1/235

| Field | Notes |
|---|---|
| `selection` | H1/235; UUID `14fbad301362379d`. |
| `related_uids` | `14fbad301362379d`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus is 194 mm in 2019-2020, then 303-318 mm from 2021 onward with plausible health continuity. |
| `interpretation` | This is a stable incompatible DBH era rather than a one-row typo. It could be an early source/tag alignment problem, a missing leading digit that is not obvious, or two similar tags/trees. |
| `recommended_action` | `source check / human call`: inspect 2019-2021 H1 source context before making a DBH correction. |
| `decision_scope` | Source-era DBH or possible identity/tag alignment. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Stable incompatible eras should remain source-era review unless the implied correction is obvious. |
| `source_rows_to_check` | `2023_and_prior.csv:3572`, `3717`, `1785`, `2512`, `4073`. |

### M6/362

| Field | Notes |
|---|---|
| `selection` | M6/362; UUID `8070c572f341c433`. |
| `related_uids` | `8070c572f341c433`. |
| `raw_flags` | Repeated `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus sequence alternates around stable low-120s with two high values: 122.5 in 2019, 155 in 2020, 123/122 in 2021-2022, 162 in 2023, then 120/125/128/119 in 2024-2025. |
| `interpretation` | The 2020 155 and 2023 162 values are likely source-row DBH outliers or a source-era misalignment, while 120-128 appears to be the stable track. |
| `recommended_action` | `source-row correction candidate`: source-check 2020 and 2023 high DBHs and likely suppress/correct them rather than treating this as biological variation. |
| `decision_scope` | DBH fields at `2023_and_prior.csv:3229` and `4999`. |
| `confidence` | Medium. |
| `needs_riley_call` | Maybe. |
| `candidate_auto_rule` | Recurrent isolated high DBHs returning to the same stable baseline should be grouped as row-level DBH outlier candidates. |
| `source_rows_to_check` | `2023_and_prior.csv:3206`, `3229`, `1505`, `1519`, `4999`, `2024_spring.csv:1125`, `2024_fall.csv:781`, `2025_spring.csv:1300`. |

### L1/5060

| Field | Notes |
|---|---|
| `selection` | L1/5060; UUID `786924bf23d517ed`. |
| `related_uids` | `786924bf23d517ed`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus 96 mm in 2021, isolated 130 mm in 2022, then 101-103 mm from 2023-2025 with live status. |
| `interpretation` | June 2022 130 mm is an isolated high DBH outlier. The later stable 101-103 mm track makes it unlikely to be true growth. |
| `recommended_action` | `source-row correction candidate`: source-check and suppress/correct June 2022 DBH 130. |
| `decision_scope` | DBH field at `2023_and_prior.csv:2336`. |
| `confidence` | High. |
| `needs_riley_call` | No, unless source image is ambiguous. |
| `candidate_auto_rule` | One-year high DBH spike bracketed by stable lower DBHs should be a source-row DBH decision candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:2086`, `2336`, `4423`, `2024_spring.csv:1361`, `2024_fall.csv:118`, `2025_spring.csv:120`. |

### L6/70

| Field | Notes |
|---|---|
| `selection` | L6/70; UUID `c25c14ecd44d788e`. |
| `related_uids` | `c25c14ecd44d788e`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `early_low_dbh_source_era_candidate`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus recorded 77.5 mm in 2019-2020, then 161-176 mm from 2021 onward. |
| `interpretation` | The early 77.5 mm values are likely missing a leading digit or otherwise scaled wrong, probably intended near 177.5 mm. |
| `recommended_action` | `source-row correction candidate`: source-check and likely correct/suppress the 2019-2020 DBHs. |
| `decision_scope` | DBH fields at `2023_and_prior.csv:2291` and `2281`. |
| `confidence` | High. |
| `needs_riley_call` | No, unless source image is ambiguous. |
| `candidate_auto_rule` | Early repeated half-mm low DBHs followed by stable ~160-170 mm Juniperus should be a leading-digit/source-era correction candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:2291`, `2281`, `1695`, `1738`, `4669`, `2024_fall.csv:398`, `2025_spring.csv:383`. |

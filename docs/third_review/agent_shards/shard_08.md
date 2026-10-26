# Third review shard 08

Agent: 08  
Date: 2026-05-11  
Scope: assigned current flagged bare tags only. Investigation only; no config, source data, generated outputs, or pipeline code was edited.

## Summary counts

| recommended_action | count |
|---|---:|
| source check / human call | 13 |
| source-row correction candidate | 5 |
| accept candidate identity link | 1 |
| stem-profile decision candidate | 1 |
| mortality/status human call | 1 |

## Recurring patterns

- Bracketed death-label artifacts remain the cleanest high-confidence row-level decisions: L5/425, M3/339, L0/970, H4/113, and H1/221 each have one dead/0 row bracketed by compatible alive evidence.
- Explicit old-tag links split into two groups: dead-only targets with no conflicting evidence look safe to accept by rule, but live-source to dead-target links or large DBH mismatch links should stay human-scoped.
- Source-era DBH regime shifts are still clustered in H4/L6 style cases, often with stable early and stable modern regimes. These should be reviewed as source-era blocks, not corrected tree-by-tree unless the source pattern is approved.
- Stem-profile flags are useful when a qualifying secondary stem disappears for one survey and then returns. R4/5224 is a clean blank rank-gap candidate; R1/963 and H2/186 are not clean because the stem profile is tangled with identity/taxon/mortality evidence.
- Current post-decision flags sometimes mean "decision worked, but a remaining biological/status question persists" rather than "the old correction failed": M7/336 and M7/5835 are examples.

## Cases

### M4/2444

| Field | Notes |
|---|---|
| `selection` | `M4/2444`, UUID `d09359aae88dee31`; related reassigned row goes to `M4/2452` UUID `404778f5c326765d`. |
| `related_uids` | `d09359aae88dee31`, `404778f5c326765d`. |
| `raw_flags` | Raw had `W_TAXON_CONFLICT`, DBH/ranked jumps around the October 2024 Quercus row, `I_ZOMBIE_TREE`, `mortality_contradiction`, `qualifying_rank_gap`, `single_survey_dbh_outlier`, and `taxon_conflict`. |
| `configured_decisions_applied` | `row_reassignment:0003` moves the October 2024 `M4/2444` Quercus phellos DBH 132 row to `M4/2452`. |
| `current_flags` | Remaining `taxon_conflict` between older unidentifiable/dead evidence, May 2024 Pinus note, April 2025 unidentifiable DBH 182/dead note `change to pine`, and October 2025 Quercus row with note `mixup`. |
| `evidence_summary` | `2444` is dead/unidentifiable 194 mm in 2019-2020, dead/no DBH through 2023, May 2024 `Confirmed Kill Pin tae`, April 2025 dead DBH 182 with `change to pine`, and October 2025 has two no-DBH rows: Quercus with `mixup` and unidentifiable. `2452` is a separate small dead/later alive tree around 128-141 mm with willow oak notes; the October 2024 Quercus row fits `2452`, not `2444`. |
| `interpretation` | Existing row reassignment fixed the obvious October 2024 row. The remaining problem is unresolved taxon/status labeling on a dead/missing `2444`; October 2025 `mixup` suggests the new Quercus row may still be a bad tag/source row rather than real `2444` evidence. |
| `recommended_action` | source check / human call |
| `decision_scope` | source rows for `M4/2444`, especially October 2025 rows and April 2025 taxon note; do not scope as a bare-tag merge. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | none; notes explicitly say `mixup` and taxon evidence conflicts after one row was already reassigned. |
| `source_rows_to_check` | `2025_spring.csv:885`, `import_recent_format_reviewed.csv:730`, `import_recent_format_reviewed.csv:731`; existing decision cites `2024_fall.csv:705`. |

### M3/356

| Field | Notes |
|---|---|
| `selection` | `M3/356`, UUID `39beccb22e9199df`. |
| `related_uids` | `39beccb22e9199df`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, and `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus is alive 198 mm health 8 in 2019-2020, alive health 2 in 2021 with note `mostly dead`, dead/no DBH in 2022-2023, alive 193-200 health 2 in 2024 with note `alive !!!!`, dead DBH 190 health 0 in April 2025 with note `out of plot`, and alive health 3 in October 2025. |
| `interpretation` | This is not a single-row artifact; it is a low-health tree with a two-survey dead block and a later one-survey death label. The repeated alive refinding makes the dead rows suspicious, but the `mostly dead` and `out of plot` notes make this a field judgment case. |
| `recommended_action` | mortality/status human call |
| `decision_scope` | mortality/status rows for June 2022, June 2023, and April 2025; DBH gaps should follow from status decision. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Low-health dead blocks bracketed by alive observations should be queued, but not auto-corrected when the dead interval spans multiple surveys. |
| `source_rows_to_check` | `2023_and_prior.csv:351`, `2023_and_prior.csv:4930`, `2025_spring.csv:1237`; context rows `2024_fall.csv:684`, `import_recent_format_reviewed.csv:775`. |

### L4/925

| Field | Notes |
|---|---|
| `selection` | `L4/925`, UUID `dd1faca50fa5290b`; candidate source `L4/243` UUID `dd4e34803c95b769`. |
| `related_uids` | `dd1faca50fa5290b`, `dd4e34803c95b769`. |
| `raw_flags` | `prior_dead_first_qualifying_dbh` only. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Candidate identity link remains `needs_human`; `prior_dead_first_qualifying_dbh` is info context. |
| `evidence_summary` | Explicit tag-change assertion says `L4_243_Pin -> L4_925_Pin`. Source `243` is dead Pinus DBH 332 in 2019-2020, then dead/missing/inferred dead. Target `925` is dead Pinus/no DBH from 2023-2024, then dead DBH 93/90 in 2025 with October 2024 note `rotten core standing`. |
| `interpretation` | The tag-change assertion is real, but the DBH profiles differ too much for a whole-tree alias. This could be a partial remnant, wrong old tag, or an old-tag clerical carry-forward. |
| `recommended_action` | source check / human call |
| `decision_scope` | candidate link `L4/243 -> L4/925`, with DBH compatibility/source review before aliasing. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Explicit dead-tree links should exclude cases where both endpoints have DBH and differ by this much. |
| `source_rows_to_check` | tag-change row 14; source `2023_and_prior.csv:729`, `615`; target `2023_and_prior.csv:4569`, `2025_spring.csv:282`, `import_recent_format_reviewed.csv:1201`. |

### L7/506

| Field | Notes |
|---|---|
| `selection` | `L7/506`, UUID `211ac3a22204ed6f`; candidate target `L7/974` UUID `967919820f93bb56`. |
| `related_uids` | `211ac3a22204ed6f`, `967919820f93bb56`. |
| `raw_flags` | Source has `I_INFERRED_DEAD` after not found/unknown rows. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Candidate identity link remains `needs_human`; inferred-dead context remains. |
| `evidence_summary` | Explicit tag-change says `L7_506_Pin -> L7_974_Pin`. Source `506` is alive Pinus DBH 312 health 6 in 2021, then not found in 2022 and unknown/inferred dead in 2024. Target `974` is dead/no DBH in 2023-2025 and unknown/missing in October 2025. |
| `interpretation` | Plausible retag after loss of `506`, but the source was live when last measured and the target has no DBH. This is not as clean as dead-only tag links. |
| `recommended_action` | source check / human call |
| `decision_scope` | candidate link `L7/506 -> L7/974`; possibly retain as explicit assertion without alias until source/field confidence improves. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Explicit tag-change links where source was last observed alive should not auto-merge into no-DBH dead targets. |
| `source_rows_to_check` | tag-change row 20; `2023_and_prior.csv:2008`, `3970`, `4754`; `2024_fall.csv:484`, `492`; `2025_spring.csv:480`. |

### L7/973

| Field | Notes |
|---|---|
| `selection` | `L7/973`, UUID `fc824bb78db8af8d`; candidate source `L7/39` UUID `b8906ee5ac572d64`. |
| `related_uids` | `fc824bb78db8af8d`, `b8906ee5ac572d64`. |
| `raw_flags` | Target has only inferred-dead info rows after its dead/no-DBH 2023 observation. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Candidate identity link remains `needs_human`; inferred-dead context remains. |
| `evidence_summary` | Explicit tag-change says `L7_39_Pin -> L7_973_Pin`. Source `39` is dead Pinus DBH 321 in 2019-2020, then missing/inferred dead. Target `973` is dead Pinus/no DBH in 2023 and inferred dead/not found afterward. |
| `interpretation` | This fits the clean dead-tree retag pattern: same plot/taxon, source already dead, target dead/no conflicting DBH, explicit old-tag evidence. |
| `recommended_action` | accept candidate identity link |
| `decision_scope` | candidate link / identity alias `L7/39 -> L7/973`. |
| `confidence` | high |
| `needs_riley_call` | no, unless every explicit link requires manual signoff. |
| `candidate_auto_rule` | Accept explicit same-plot/same-taxon links when source is already dead or inferred dead, target is dead/no DBH, and no contradictory taxon/DBH evidence exists. |
| `source_rows_to_check` | tag-change row 19; source `2023_and_prior.csv:751`, `612`, `3967`, `3975`; target `2023_and_prior.csv:4753`, `2024_fall.csv:491`, `2025_spring.csv:479`. |

### L5/425

| Field | Notes |
|---|---|
| `selection` | `L5/425`, UUID `7f1cdff90e7baa61`. |
| `related_uids` | `7f1cdff90e7baa61`. |
| `raw_flags` | Raw had taxon conflict plus `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_death_label_outlier`, `qualifying_rank_gap`, and health rebound/stem context. |
| `configured_decisions_applied` | `taxon_override:0008` sets the tree to Pinus taeda, resolving the one Juniperus label slip. |
| `current_flags` | Taxon conflict resolved. Remaining mortality/gap flags are driven by May 2024 dead/0 no-DBH row bracketed by alive DBH 239 and alive DBH 240-250. |
| `evidence_summary` | Pinus is alive and stable 225-241 mm from 2019-2023, May 2024 says dead/0/no DBH, then October 2024 through October 2025 are alive 234-250 with poison ivy/angled DBH notes. October 2025 also has a second missing stem row. |
| `interpretation` | May 2024 is a classic one-survey death-label artifact. The taxon decision already handled the species slip. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | mortality/status and health for `2024_spring.csv:707`; preserve DBH as missing, and likely reinterpret dead/0 as uncertain/not found or alive unknown. |
| `confidence` | high |
| `needs_riley_call` | no for routing; yes only for exact replacement health/status semantics. |
| `candidate_auto_rule` | Single dead/0 row bracketed by multiple compatible alive DBH observations after taxon conflict is resolved. |
| `source_rows_to_check` | `2024_spring.csv:707`; context `2023_and_prior.csv:4593`, `2024_fall.csv:316`, `2025_spring.csv:321`, `import_recent_format_reviewed.csv:1231`. |

### R1/963

| Field | Notes |
|---|---|
| `selection` | `R1/963`, UUID `4a7b148b20f0ccd0`. |
| `related_uids` | `4a7b148b20f0ccd0`. |
| `raw_flags` | `I_ZOMBIE_TREE`, DBH/ranked jumps, stem count change, large stem disappearance, `source_note_dbh_conflict`, `probable_duplicate_stem_artifact`, `stem_mortality_context`, `health_rebound_new_stem_context`, and mortality contradiction. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | June 2023 is dead/no DBH unidentifiable. May 2024 has one alive Ilex 156 health 9 row plus two duplicate-looking unidentifiable dead 71 mm rows. October 2024 onward is dead/unidentifiable around 70-73 mm with note `knot @ dbh`; October 2025 is unknown/not standing. |
| `interpretation` | The May 2024 156 mm alive Ilex looks like a different stem/tree or wrong tag layered onto a dead 70 mm unidentifiable profile. The repeated 71 mm dead rows in May 2024 are likely duplicate stem artifacts. |
| `recommended_action` | source check / human call |
| `decision_scope` | source rows and possibly identity split for May 2024 `R1/963_Ile` vs dead `R1/963_Uni` profile. |
| `confidence` | high that the May 2024 profile is garbled; medium on exact fix. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Duplicate same-survey DBH rows can be suggested, but not auto-corrected when a same-survey live taxon/DBH outlier suggests possible identity conflict. |
| `source_rows_to_check` | `2023_and_prior.csv:5123`, `2024_spring.csv:1043`, `2024_spring.csv:91`, `2024_spring.csv:1053`, `2024_fall.csv:1184`, `2025_spring.csv:643`. |

### M1/850

| Field | Notes |
|---|---|
| `selection` | `M1/850`, UUID `f7fa6359d34d1a84`. |
| `related_uids` | `f7fa6359d34d1a84`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, and `qualifying_rank_gap`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead/unidentifiable or Juniperus 144 mm from 2019-2021, alive Juniperus DBH 135 health 3 in June 2022, dead again in 2023 and May 2024 with poison ivy, alive/no DBH health 2 in October 2024 with poison ivy, dead/no DBH in 2025. |
| `interpretation` | This could be a marginal/refound low-health Juniperus with poison ivy interfering, not a clean one-row typo. Mortality flips several times and DBH is only observed during the brief alive interval. |
| `recommended_action` | source check / human call |
| `decision_scope` | mortality/status rows for June 2022 and October 2024, preserving poison ivy context. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | none; repeated status flips with poison ivy should stay human-scoped. |
| `source_rows_to_check` | `2023_and_prior.csv:1163`, `248`, `278`, `1370`, `4835`; `2024_spring.csv:843`, `2024_fall.csv:577`, `2025_spring.csv:1179`, `import_recent_format_reviewed.csv:635`. |

### H4/140

| Field | Notes |
|---|---|
| `selection` | `H4/140`, UUID `472898290f8c7724`. |
| `related_uids` | `472898290f8c7724`. |
| `raw_flags` | DBH/ranked jump at June 2021, stem count changes around 2019-2021, large stem appearance/disappearance, `stable_incompatible_dbh_era`, `probable_duplicate_stem_artifact`, `bounded_stem_rank_gap`, and stem mortality context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Acer rubrum has 2019 two stems 91/91, 2020 one stem 91, then from 2021 onward a stable two-stem profile around 194-219 and 78-89. Notes include `two trunks` in 2019. |
| `interpretation` | This looks like early-source/stem alignment trouble, not biological growth. The 2019 duplicate 91/91 may be a duplicated-stem artifact or may represent a missed larger stem; the modern profile is stable and credible. |
| `recommended_action` | source check / human call |
| `decision_scope` | UUID-level DBH/stem source-era rows for 2019-2020, not whole tag. |
| `confidence` | medium-high on source-era problem; low on exact row fix without source sheets. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | H4 early low/small DBH era should route as a grouped source-era queue; do not auto-rescale or split per tree. |
| `source_rows_to_check` | `2023_and_prior.csv:2908`, `3880`, `2911`, `2920`, `2919`, `2928`, `2927`. |

### R4/5224

| Field | Notes |
|---|---|
| `selection` | `R4/5224`, UUID `fb69ecaef1cf1096`. |
| `related_uids` | `fb69ecaef1cf1096`. |
| `raw_flags` | Stem count change, large stem disappearance in May 2024, large stem appearance in October 2024, `blank_missing_stem_backfill_candidate`, `bounded_stem_rank_gap`, and `new_persistent_large_stem`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Ilex has two stems 123/54 in June 2023, only primary 125 in May 2024, then two stems again from October 2024 onward: primary 125-127 and secondary 52-61. |
| `interpretation` | Clean bounded missing secondary stem. The secondary stem did not appear from nowhere; May 2024 simply omitted it. |
| `recommended_action` | stem-profile decision candidate |
| `decision_scope` | insert blank/missing rank-2 observation for May 2024 under UUID `fb69ecaef1cf1096`. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | If rank-2 DBH is present before and after with compatible taxon/status and a one-survey gap, insert/preserve a blank rank observation rather than flag as new stem. |
| `source_rows_to_check` | `2023_and_prior.csv:5255`, `5256`; `2024_spring.csv:187`; `2024_fall.csv:1322`, `1365`; `2025_spring.csv:783`, `784`. |

### Tag 186, H2 and L0

| Field | Notes |
|---|---|
| `selection` | Bare tag `186` appears as `H2/186` UUID `e4f5e9a476ac659d` and `L0/186` UUID `cd46ffa140aafbfd`. |
| `related_uids` | `e4f5e9a476ac659d`, `cd46ffa140aafbfd`; nearby H2 notes also mention `H2/185` and `H2/191`. |
| `raw_flags` | H2 has DBH/ranked jump from 94 to ~52, one-survey duplicate stem profile 52/52, near/probable duplicate stem artifact, stable incompatible DBH era. L0 has `I_ZOMBIE_TREE`, `dead_tree_dbh_gap`, and mortality contradiction. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | H2/186 is Nyssa 94 in 2019-2020, then stable 52-57 from 2021 onward, with notes `191-186 could be one tree`, `snapped`, and `186-191 likely one multistem tree`; May 2024 has duplicate 52/52 rows. Nearby H2/185 and H2/191 have similar `185-191 same tree` notes and duplicate same-DBH second-stem May 2024 rows. L0/186 is dead Juniperus 79 in 2019-2022, alive/no DBH health 6 in 2023, then dead 78-83 from 2024 onward with note `zombie???`. |
| `interpretation` | This bare tag needs two separate scopes. H2 is a tag/neighborhood/stem-scope problem involving 185/186/191 notes and likely duplicate rank rows. L0 is a mortality-status oddity on a separate plot/tag and should not be coupled to H2. |
| `recommended_action` | source check / human call |
| `decision_scope` | split tag-level review into UUID/plot scopes; H2 neighborhood source review, L0 mortality/status source row review. |
| `confidence` | high that bare-tag review is wrong scope; medium on exact H2/L0 fixes. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Bare-tag assignments crossing plots should be decomposed before recommendations. One-survey same-DBH second stems with notes like `same tree` should be queued as probable duplicate/stem-scope review. |
| `source_rows_to_check` | H2/186 `2023_and_prior.csv:3926`, `3369`, `3440`, `1978`, `4112`, `2024_spring.csv:432`, `999`; L0/186 `2023_and_prior.csv:98`, `55`, `164`, `375`, `4346`, `2024_spring.csv:38`. |

### M3/339

| Field | Notes |
|---|---|
| `selection` | `M3/339`, UUID `56743a007151e61e`. |
| `related_uids` | `56743a007151e61e`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, and `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa is alive from 2019 through May 2024, declining from health 9 to health 2 with poison ivy/branch notes. October 2024 is dead/0 DBH 127, then April 2025 and October 2025 are alive/no DBH health 2 and 1. |
| `interpretation` | October 2024 dead/0 is likely a single-survey death-label artifact in a low-health tree. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | mortality/status and health for `2024_fall.csv:667`; DBH 127 can probably remain as measured. |
| `confidence` | high |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | Low-health alive sequence with one dead/0 row bracketed by later alive observations should become uncertain/alive status, preserving measured DBH. |
| `source_rows_to_check` | `2024_fall.csv:667`; context `2024_spring.csv:813`, `2025_spring.csv:1219`, `import_recent_format_reviewed.csv:755`. |

### L0/970

| Field | Notes |
|---|---|
| `selection` | `L0/970`, UUID `4e9c92eb6074d3fb`. |
| `related_uids` | `4e9c92eb6074d3fb`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, and `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus alive health 2 DBH 140 in 2023, alive health 2 DBH 126 in May 2024, alive health 1 DBH 111 in October 2024 with poison ivy, dead/0 no DBH in April 2025 with `P.I.`, then alive health 2 in October 2025. |
| `interpretation` | April 2025 dead/0 is likely a one-survey death-label artifact, especially with poison ivy notes and alive low-health rows on both sides. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | mortality/status and health for `2025_spring.csv:53`; DBH remains missing. |
| `confidence` | high |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | Low-health alive -> dead/0/no DBH with poison ivy note -> alive should be auto-queued for uncertain/alive status. |
| `source_rows_to_check` | `2025_spring.csv:53`; context `2024_fall.csv:56`, `import_recent_format_reviewed.csv:977`. |

### M7/336

| Field | Notes |
|---|---|
| `selection` | `M7/336`, UUID `ea0625493618310c`; nearby note references `M7/335` UUID `6260213564f4fc08`. |
| `related_uids` | `ea0625493618310c`, `6260213564f4fc08`. |
| `raw_flags` | Raw had huge DBH jumps from 775 to 77, `stable_incompatible_dbh_era`, `I_ZOMBIE_TREE`, `dead_tree_dbh_gap`, and mortality contradiction. |
| `configured_decisions_applied` | `row_correction:0030` and `row_correction:0031` convert June 2019/2020 DBH 775 to 77.5. |
| `current_flags` | DBH problem resolved. Remaining flags are `dead_tree_dbh_gap` and mortality contradiction from April 2025 alive health 1 between long dead history and October 2025 dead. |
| `evidence_summary` | Nyssa is dead 77.5 in 2019-2020, dead/no DBH through 2023, dead 77/78 in 2024, alive 76 health 1 in April 2025 with note `ivy sprouted low`, then dead/no DBH in October 2025. Notes also say `could be same tree as 335` and `A5336 one tree`; M7/335 is a distinct live Nyssa around 110-115 with low health in recent surveys. |
| `interpretation` | The DBH correction looks right. The remaining live row may reflect basal sprout/ivy/refinding ambiguity, not a generic zombie rule. |
| `recommended_action` | source check / human call |
| `decision_scope` | April 2025 mortality/status row for `M7/336`; keep existing DBH corrections. |
| `confidence` | high on existing DBH fix; medium-low on April 2025 status. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Existing decimal-place correction pattern is valid; isolated `ivy sprouted low` alive rows on otherwise dead trees should remain human-reviewed. |
| `source_rows_to_check` | `2025_spring.csv:1383`; context `2023_and_prior.csv:487`, `496`, `509`, `533`, `5077`, `2024_fall.csv:863`. |

### M7/5835

| Field | Notes |
|---|---|
| `selection` | `M7/5835`, UUID `5c4a1d151008300f`. |
| `related_uids` | `5c4a1d151008300f`. |
| `raw_flags` | Raw had `W_TAXON_CONFLICT`, `taxon_conflict`, `I_ZOMBIE_TREE`, mortality contradiction, prior-dead-first-qualifying DBH, and stem mortality context. |
| `configured_decisions_applied` | `taxon_override:0024` accepts the species change to Pinus taeda. |
| `current_flags` | Taxon conflict resolved. Remaining flags are mortality contradiction, prior dead first DBH, and stem mortality context because October 2025 has both live health 9 and dead health 0 rows. |
| `evidence_summary` | Tree is dead/no DBH in 2023, dead Pinus DBH 305-309 from 2024-April 2025, then October 2025 has a live Pinus stem health 9 and a dead Pinus stem health 0 with note `mis ID should be Pin 5835`. |
| `interpretation` | Taxon decision worked. The current issue is a stem/status interpretation: October 2025 may have both a live stem and dead stem on a previously dead record, or one October row may be an identity/scope issue. |
| `recommended_action` | source check / human call |
| `decision_scope` | October 2025 stem/status rows; do not reopen taxon unless source review contradicts the configured decision. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Do not auto-clear zombie flags when a same-survey tree has both live and dead stems after a long dead history. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:924`, `925`; context `2024_spring.csv:776`, `2024_fall.csv:869`, `2025_spring.csv:1393`. |

### H4/113

| Field | Notes |
|---|---|
| `selection` | `H4/113`, UUID `33c2c19676fe7cbf`. |
| `related_uids` | `33c2c19676fe7cbf`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, sharp upward health rebound, and `single_survey_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Large Pinus is alive health 9 DBH 574 in 2019-2020, dead/0 DBH 571 in June 2021 with note `dead`, then alive again from 2022 through October 2025 with DBH 575-585 and health 6-10. |
| `interpretation` | June 2021 dead/0 is a clear death-label artifact. The DBH is compatible with the same tree and all later evidence is alive/high health. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | mortality/status and health for `2023_and_prior.csv:766`; DBH 571 can remain. |
| `confidence` | high |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | High-health live, one dead/0 row with compatible DBH, then many high-health live rows should become uncertain/alive status. |
| `source_rows_to_check` | `2023_and_prior.csv:766`; context `2023_and_prior.csv:2792`, `2820`, `2049`, `4172`, `2024_fall.csv:1007`. |

### H4/147

| Field | Notes |
|---|---|
| `selection` | `H4/147`, UUID `a81e7bded5574359`. |
| `related_uids` | `a81e7bded5574359`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, and `early_low_dbh_source_era_candidate`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Liquidambar is stable 65 mm in 2019-2020, then stable 126-133 mm from 2021-2025 with good health. |
| `interpretation` | Classic early low DBH source-era candidate. The modern 126-133 sequence is consistent; the early 65 values are roughly half the modern regime. |
| `recommended_action` | source check / human call |
| `decision_scope` | DBH source-era rows for 2019-2020, probably as part of an H4 early-low-DBH block. |
| `confidence` | high that the early DBHs are incompatible; medium on exact correction. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Group H4 repeated early-low values preceding stable modern DBH for source-era review; do not auto-double values without source confirmation. |
| `source_rows_to_check` | `2023_and_prior.csv:3257`, `3260`, `3270`, `3271`, `4207`. |

### H1/221

| Field | Notes |
|---|---|
| `selection` | `H1/221`, UUID `cf7593327f6f53ab`. |
| `related_uids` | `cf7593327f6f53ab`. |
| `raw_flags` | `I_ZOMBIE_TREE`, mortality contradiction, sharp upward health rebound, and `single_survey_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa is alive 164 health 9 in 2019 with note about branches without leaf needles, dead/0 164 in 2020 with `no needles. dead`, then alive continuously 2021-2025 with DBH 151-159 and health 4-8. |
| `interpretation` | June 2020 dead/0 is likely a one-survey mortality label artifact; the note explains why a field worker might have called it dead, but subsequent evidence strongly supports survival. |
| `recommended_action` | source-row correction candidate |
| `decision_scope` | mortality/status and health for `2023_and_prior.csv:441`; DBH 164 can remain. |
| `confidence` | high |
| `needs_riley_call` | no for routing. |
| `candidate_auto_rule` | One dead/0 row bracketed by long compatible alive sequence should be converted to uncertain/alive, especially when later repeated measurements continue the same DBH regime. |
| `source_rows_to_check` | `2023_and_prior.csv:441`; context `2023_and_prior.csv:2652`, `2152`, `1976`, `4059`, `2024_fall.csv:1394`. |

### M7/318

| Field | Notes |
|---|---|
| `selection` | `M7/318`, UUID `e5520f4a6972326e`. |
| `related_uids` | `e5520f4a6972326e`. |
| `raw_flags` | `I_ZOMBIE_TREE` and mortality contradiction. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa is dead 78 in 2019-2020, alive 78-96 from 2021-May 2024 with health 1-3 except June 2023/May 2024 health 2, then dead from October 2024 through October 2025. |
| `interpretation` | Early dead labels followed by a long low-health alive interval may be wrong, but the later 2024-2025 death looks real. This is more than a single-row typo. |
| `recommended_action` | source check / human call |
| `decision_scope` | mortality/status for 2019-2021 transition, maybe preserve 2024 mortality as real. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Do not auto-correct multi-year early-dead to alive when the later sequence is low-health and eventually dies again. |
| `source_rows_to_check` | `2023_and_prior.csv:485`, `494`, `1278`, `1408`, `5058`; `2024_fall.csv:845`, `2025_spring.csv:1364`, `import_recent_format_reviewed.csv:890`. |

### L6/50

| Field | Notes |
|---|---|
| `selection` | `L6/50`, UUID `5c3ba58e41f1eb84`. |
| `related_uids` | `5c3ba58e41f1eb84`. |
| `raw_flags` | DBH/ranked jumps around May 2024 and October 2024; `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | No relevant configured decision. Coarse text matching surfaced unrelated L6 decisions for tags 85, 5027, and 75; these do not apply to `L6/50`. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus is stable 67.5-74 mm from 2019-2023, May 2024 drops to exactly 50 mm health 4, then October 2024 and April 2025 return to 70-71 mm. October 2025 is dead/0 no DBH. |
| `interpretation` | May 2024 DBH 50 is isolated and probably a measurement/source issue, but because it is exactly at the inclusion threshold it is safer to source-check before suppressing. |
| `recommended_action` | source check / human call |
| `decision_scope` | DBH field for `2024_spring.csv:469`; preserve status unless source contradicts it. |
| `confidence` | medium-high that 50 is an outlier; medium on exact correction. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Threshold-edge one-survey DBH drops bracketed by stable measurements should queue as DBH-source check, not auto-strike unless below threshold or source note confirms. |
| `source_rows_to_check` | `2024_spring.csv:469`; context `2023_and_prior.csv:4637`, `2024_fall.csv:366`, `2025_spring.csv:364`. |

### L6/69

| Field | Notes |
|---|---|
| `selection` | `L6/69`, UUID `c85840b1d8028432`. |
| `related_uids` | `c85840b1d8028432`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, and `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus is stable 162.5/162.6 mm in 2019-2020, then stable 78-83 mm from 2021-2025. No notes explain the break. |
| `interpretation` | Stable incompatible DBH eras. Early values are roughly double the later values, but not clean enough to auto-correct without source review. |
| `recommended_action` | source check / human call |
| `decision_scope` | DBH source-era rows for June 2019-2020, likely as part of L6 source-era review. |
| `confidence` | high that one era is wrong; medium on which correction to apply. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Stable early/modern regimes should be grouped by plot/source/year for review; avoid automatic halving/doubling. |
| `source_rows_to_check` | `2023_and_prior.csv:2568`, `2554`, `1893`, `1382`, `4668`, `2024_fall.csv:397`, `2025_spring.csv:382`. |

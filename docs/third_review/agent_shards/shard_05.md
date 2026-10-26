# Agent 05 third-review shard

Date: 2026-05-11

Scope: assigned current flagged tags only. This report is investigation-only; no config, generated output, source data, or pipeline code was edited.

## Summary

| recommended_action | count |
|---|---:|
| source check / human call | 8 |
| source-row correction candidate | 5 |
| accept candidate identity link | 3 |
| mortality/status human call | 3 |
| stem-profile decision candidate | 1 |
| watch / diagnostic threshold tuning | 1 |
| split tag-level review into UUID scopes | 1 |

Recurring patterns:

- Several high-confidence source-row corrections remain: isolated DBH outliers, direct source-note conflicts, and one duplicate stem artifact.
- Candidate tag-change links with old-tag evidence are often straightforward when both endpoints are dead and taxon-compatible, even when the target lacks DBH.
- Mortality flags are not one pattern: some are clear single-survey death-label outliers, while others may represent real marginal live tissue, broken/girdled stems, or latest-survey field judgments.
- Source-era DBH regime shifts are still appearing in H4, L7, and M1; these should be reviewed as grouped plot/year/source issues, not only as isolated tree defects.

## Cases

### H4/136

| Field | Notes |
|---|---|
| `selection` | tag 136, plot H4, UUID `fd65bc2ba3d3a410`; linked target H4/992 UUID `189b33fa3670d2d1`. |
| `related_uids` | `fd65bc2ba3d3a410`; candidate link to `189b33fa3670d2d1`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `stable_incompatible_dbh_era`, plus inferred-dead info in 2024. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw: stable incompatible DBH era and candidate identity link. |
| `evidence_summary` | H4/136 Nyssa is 91 mm in 2019-2020, then 178/183 mm in 2021-2022, then missing/inferred dead in 2024. Explicit link says H4/136 became H4/992. H4/992 is 187 in 2023, 111 in May 2024 with note `might be 136`, then 194/200/192. |
| `interpretation` | This is both the H4 early-source DBH regime problem and a real candidate-link problem. The May 2024 H4/992 111 mm row may belong to H4/136 or may be a bad measurement. |
| `recommended_action` | source check / human call. Review H4/136 and H4/992 together before accepting the link or moving/striking the May 2024 111 mm row. |
| `decision_scope` | candidate link plus source row, especially `2024_spring.csv:340` for H4/992 and H4/136 rows in `2023_and_prior.csv:3318,3368,3455,2434`. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; source note says `might be 136`, but the link/action still needs judgment. |
| `source_rows_to_check` | `2024_spring.csv:340`, `2023_and_prior.csv:4219`, `2023_and_prior.csv:3318`, `3368`, `3455`, `2434`. |

### M0/585

| Field | Notes |
|---|---|
| `selection` | tag 585, plot M0, UUID `61858120983d9906`. |
| `related_uids` | `61858120983d9906`. |
| `raw_flags` | `max_dbh_jump`, `ranked_dbh_jump`, `persistent_dbh_regime_shift`, `qualifying_rank_gap`, `I_ZOMBIE_TREE`, explicit-note mortality correction context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Dead Juniperus/unidentified 68 mm in 2019-2020; dead/no DBH in 2021; June 2022 is 235 mm, health 7, alive, note `marked dead last year`; later 2024-2025 rows are dead around 53-57 mm or no DBH. |
| `interpretation` | June 2022 is not compatible with either the earlier dead 68 mm regime or the later dead 53-57 mm regime. The note questions the earlier dead label, but the DBH looks like a wrong row/tag or transcription/source problem. |
| `recommended_action` | source check / human call; likely strike or relocate the June 2022 235 mm DBH and decide whether the alive/health 7 row is a separate tree or a bad status row. |
| `decision_scope` | source row / DBH field / mortality status for June 2022. |
| `confidence` | high that the June 2022 DBH is wrong; medium on status interpretation. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | possible only for direct source-note plus massive DBH-regime conflict, but do not auto-apply here without review. |
| `source_rows_to_check` | `2023_and_prior.csv:2121`, year workbook row 476, dated entry rows 759/835. |

### M7/914

| Field | Notes |
|---|---|
| `selection` | tag 914, plot M7, UUID `c71bbe1153464562`; linked source M7/5832 UUID `1cbf3e349dccbfc1`. |
| `related_uids` | `c71bbe1153464562`, `1cbf3e349dccbfc1`. |
| `raw_flags` | no raw issues; info-only `prior_dead_first_qualifying_dbh`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | info-only `prior_dead_first_qualifying_dbh`; candidate identity link. |
| `evidence_summary` | M7/5832 is dead Juniperus/no DBH in 2021-2022 and then inferred dead in 2024. M7/914 has old tag 5832 in June 2023, dead/no DBH, then dead DBH 171/173 in 2024. |
| `interpretation` | Plausible retag of a dead Juniperus. Later first DBH on a dead tree is acceptable context rather than a missing live history. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `M7/5832 -> M7/914`. |
| `confidence` | high. |
| `needs_riley_call` | no, unless the project wants every tag-change link manually confirmed. |
| `candidate_auto_rule` | explicit old-tag link, same plot, same taxon, dead-only evidence, target lacks conflicting DBH. |
| `source_rows_to_check` | link evidence source row 28 in `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx`; `2023_and_prior.csv:5085`. |

### M5/2484

| Field | Notes |
|---|---|
| `selection` | tag 2484, plot M5, UUID `85b7a0af0b4c029f`; linked target M5/972 UUID `5c5ceeb08462e9ad`. |
| `related_uids` | `85b7a0af0b4c029f`, `5c5ceeb08462e9ad`. |
| `raw_flags` | inferred-dead info only; candidate identity link. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | inferred-dead info only; candidate identity link. |
| `evidence_summary` | M5/2484 is dead Pinus, 301 mm in 2019-2020, dead/no DBH in 2021-2022, then missing/inferred dead in 2024. M5/972 appears in 2023 with old tag 2484, dead/no DBH, and remains dead/not found. |
| `interpretation` | Very plausible dead-tree retag. The target lacks a comparable DBH, but the old-tag field is explicit and the taxon/status match. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `M5/2484 -> M5/972`. |
| `confidence` | high. |
| `needs_riley_call` | no, unless all link accepts require manual signoff. |
| `candidate_auto_rule` | explicit old-tag link, same plot/taxon, source is dead, target is dead/no conflicting DBH. |
| `source_rows_to_check` | link evidence row 27; `2023_and_prior.csv:4998`, source history rows 865/886/909/921. |

### L0/921

| Field | Notes |
|---|---|
| `selection` | tag 921, plot L0, UUID `c905ff266d7e4c1f`; linked source L0/153 UUID `3dc6e5ba231dcb88`. |
| `related_uids` | `c905ff266d7e4c1f`, `3dc6e5ba231dcb88`. |
| `raw_flags` | inferred-dead info only; candidate identity link. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | inferred-dead info only; candidate identity link. |
| `evidence_summary` | L0/153 is dead Pinus 298 mm in 2019-2020, not found/dead afterward. L0/921 appears in June 2023 with old tag 153, dead/no DBH, then not found/inferred dead. |
| `interpretation` | Plausible dead-tree retag; target has no DBH, so DBH compatibility cannot be proven, but the old-tag evidence is explicit. |
| `recommended_action` | accept candidate identity link. |
| `decision_scope` | candidate link `L0/153 -> L0/921`. |
| `confidence` | high. |
| `needs_riley_call` | no, unless all link accepts require manual signoff. |
| `candidate_auto_rule` | explicit old-tag link, same plot/taxon, dead-only target, no conflicting DBH. |
| `source_rows_to_check` | link evidence row 5; `2023_and_prior.csv:4363`; L0/153 rows 691/685/780/1003. |

### M7/320

| Field | Notes |
|---|---|
| `selection` | tag 320, plot M7, UUID `2d805a06179f0556`. |
| `related_uids` | `2d805a06179f0556`. |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `source_note_dbh_conflict`, dead-tree gap context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Alive Juniperus 239 mm in 2019-2020; newly dead/no DBH in 2021; June 2022 has dead DBH 451; May 2024 note says `dbh approx. 200 not 450`; Oct 2024 DBH 214 with note `200 range, not 450`; Apr 2025 224. |
| `interpretation` | June 2022 451 is directly contradicted by later field notes and incompatible with the 200-range dead-stem regime. |
| `recommended_action` | source-row correction candidate: suppress/strike June 2022 DBH 451 to missing unless original source gives a corrected exact value. Preserve dead status. |
| `decision_scope` | DBH field for `2023_and_prior.csv:357` and matching workbook rows. |
| `confidence` | high. |
| `needs_riley_call` | no for suppressing 451; yes only if choosing an exact replacement value. |
| `candidate_auto_rule` | direct source-note conflict like `not 450` plus compatible later repeated DBH regime. |
| `source_rows_to_check` | `2023_and_prior.csv:357`, `2024_spring.csv:754`, `2024_fall.csv:847`. |

### M0/577

| Field | Notes |
|---|---|
| `selection` | tag 577, plot M0, UUID `a4ce7274ecea9097`. |
| `related_uids` | `a4ce7274ecea9097`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, sharp health rebound, DBH jump with poison ivy measurement context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | 2019 is dead unidentified, 130 mm; 2020 is Juniperus 147 mm, alive health 5; 2021-2023 dead/no DBH; 2024-2025 dead around 118-119 mm with May 2024 poison ivy note. |
| `interpretation` | DBH variation can be explained by poison ivy/dead-tree context. The unresolved issue is whether 2019 dead or 2020 alive was the bad mortality label, or whether this is a tag/identity mismatch. |
| `recommended_action` | mortality/status human call. |
| `decision_scope` | mortality/status for 2019-2021 interval, possibly UUID identity if source review suggests a row/tag mismatch. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no. |
| `source_rows_to_check` | `2023_and_prior.csv:1051`, `1672`, `226`, `329`, `4770`; `2024_spring.csv:1259`. |

### M3/5189

| Field | Notes |
|---|---|
| `selection` | tag 5189, plot M3, UUID `9f7443e1495009aa`. |
| `related_uids` | `9f7443e1495009aa`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, qualifying DBH gap. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Alive Juniperus 127 mm/health 5 in 2021; dead/no DBH in 2022-2023; alive again from 2024 onward with DBH 129/129/148 and October 2024 note `alive !!!!!`; October 2025 alive health 3. |
| `interpretation` | Later field evidence strongly asserts the tree is alive. The 2022-2023 dead rows may be missed/uncertain observations rather than true mortality. |
| `recommended_action` | mortality/status human call; likely convert 2022-2023 observed-dead rows to uncertain/not found if source review supports that. |
| `decision_scope` | mortality/status rows for June 2022 and June 2023. |
| `confidence` | medium-high. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | single dead block bracketed by live DBH-compatible observations with explicit later `alive` note. |
| `source_rows_to_check` | `2023_and_prior.csv:310`, `4938`; `2024_fall.csv:692`. |

### L6/76

| Field | Notes |
|---|---|
| `selection` | tag 76, plot L6, UUID `d69c264caa87dba3`. |
| `related_uids` | `d69c264caa87dba3`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `single_survey_death_label_outlier`, `mortality_contradiction`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus 114 mm in 2019-2020, then stable 228-238 mm from 2021-2024. April 2025 is dead/0/fallen with note `broken at girdle`; October 2025 is alive health 8 with note `Bole`. |
| `interpretation` | Two issues are overlaid: a 2019-2020 versus 2021+ DBH regime shift, and a 2025 mortality reversal that may reflect broken/girdled bole/stem interpretation rather than whole-tree death. |
| `recommended_action` | source check / human call. |
| `decision_scope` | DBH source-era rows plus April/October 2025 mortality/status. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; structural note and DBH shift make this too contextual. |
| `source_rows_to_check` | `2023_and_prior.csv:3176`, `3032`, `2106`, `1941`; `2025_spring.csv:389`; Oct 2025 reviewed row 1299. |

### L7/500

| Field | Notes |
|---|---|
| `selection` | tag 500, plot L7, UUID `5cdb3a074f9d67b1`. |
| `related_uids` | `5cdb3a074f9d67b1`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, stem mortality context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Morella in a cluster, consistently alive 2021-2024 with DBH 65-67 and health 10->6. April 2025 is DBH 63, health 0, dead. October 2025 returns alive, DBH 66, health 7. |
| `interpretation` | Classic one-survey death-label outlier with compatible DBH before/after; the April 2025 dead/0 row is not convincing whole-tree mortality. |
| `recommended_action` | source-row correction candidate: reinterpret April 2025 dead/0 as alive/uncertain, or at minimum suppress the observed-dead status while preserving DBH. |
| `decision_scope` | mortality/status and health for `2025_spring.csv:477`. |
| `confidence` | high. |
| `needs_riley_call` | no for routing; yes if choosing exact replacement health. |
| `candidate_auto_rule` | single observed-dead/health-0 row bracketed by observed-alive rows with compatible DBH and taxon. |
| `source_rows_to_check` | `2025_spring.csv:477`; Oct 2025 reviewed row 1391. |

### R3/641

| Field | Notes |
|---|---|
| `selection` | tag 641, plot R3, UUID `25a5632dd8eb9889`. |
| `related_uids` | `25a5632dd8eb9889`. |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_TREE_LARGE_STEM_APPEARANCE`, `blank_missing_stem_backfill_candidate`, `bounded_stem_rank_gap`, `new_persistent_large_stem`, stem mortality context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Acer has two stems in June 2023: 191 and 94, both alive. May 2024 records only the main stem 196. From Oct 2024 onward the second stem is present again around 85 mm and dead/health 0, with later notes `girdled` and `broke off bh`. |
| `interpretation` | Bounded missing rank-2 gap, not a true new stem. The May 2024 row likely omitted the secondary stem. |
| `recommended_action` | stem-profile decision candidate: insert a blank/missing rank-2 observation for May 2024 and preserve the later dead second-stem evidence. |
| `decision_scope` | stem profile / blank row for May 2024 rank 2. |
| `confidence` | high. |
| `needs_riley_call` | no. |
| `candidate_auto_rule` | bounded missing stem backfill when a qualifying rank disappears for one survey then returns with compatible stem/taxon/status context. |
| `source_rows_to_check` | `2023_and_prior.csv:5183-5184`, `2024_spring.csv:132`, `2024_fall.csv:1252,1295`, `2025_spring.csv:709-710`. |

### H0/286

| Field | Notes |
|---|---|
| `selection` | tag 286, plot H0, UUID `4941f98701a10d1e`. |
| `related_uids` | `4941f98701a10d1e`. |
| `raw_flags` | isolated `single_survey_dbh_outlier`, duplicate-stem artifact, stem count changes. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pine is 315 mm in 2019-2020, 155 in June 2021, then 307-310 from 2022-2025. May 2024 contains two identical 310 mm alive rows. |
| `interpretation` | June 2021 155 is an isolated DBH error. May 2024 second 310 is a duplicate stem artifact, not a real second stem. |
| `recommended_action` | source-row correction candidate: suppress/strike June 2021 DBH 155; suppress May 2024 duplicate second stem row. |
| `decision_scope` | DBH field for `2023_and_prior.csv:1781`; suppress duplicate observation/source row `2024_spring.csv:960` or the lower-priority duplicate. |
| `confidence` | high. |
| `needs_riley_call` | no. |
| `candidate_auto_rule` | isolated DBH returns to baseline; exact duplicate DBH plus one-survey stem-count increase. |
| `source_rows_to_check` | `2023_and_prior.csv:1781`; `2024_spring.csv:414` and `960`. |

### H7/880

| Field | Notes |
|---|---|
| `selection` | tag 880, plot H7, UUID `d7c6970a3b361e09`. |
| `related_uids` | `d7c6970a3b361e09`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Nyssa alive through May 2024, health declines to 4. October 2024 is dead/0. April 2025 is alive health 5 with note `girdle`. October 2025 is dead/0. |
| `interpretation` | Could be real marginal live tissue on a failing/girdled tree; not necessarily a row typo. |
| `recommended_action` | mortality/status human call; keep Oct 2024 dead and Apr 2025 live separate until field/source review. |
| `decision_scope` | mortality/status rows in Oct 2024, Apr 2025, Oct 2025. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; girdle context argues against automatic correction. |
| `source_rows_to_check` | `2024_fall.csv:1127`, `2025_spring.csv:946`, Oct 2025 reviewed row 528. |

### Tag 236: H1/236 and L2/236

| Field | Notes |
|---|---|
| `selection` | tag 236, plots H1 and L2; UUIDs `3623d15549e0a288` and `16c8ff210589523c`. |
| `related_uids` | H1/236 `3623d15549e0a288`; L2/236 `16c8ff210589523c`. |
| `raw_flags` | H1: dead-tree DBH gap/increase and ranked DBH jump. L2: mortality contradiction/latest observed-alive after dead sequence. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | H1/236 is dead Pinus: 400 mm in 2019-2020, no DBH 2021, then 180/179/179/168, then Oct 2025 jumps to 232 while still dead. L2/236 is dead Juniperus 63 mm in 2019-2020, dead/no DBH or 61-66 through Apr 2025, then Oct 2025 alive health 9. |
| `interpretation` | Bare tag combines two independent UUID cases. H1 is a dead-tree DBH increase/source question; L2 is a latest-survey mortality revival/source question. |
| `recommended_action` | split tag-level review into UUID scopes. H1 needs source/field review of Oct 2025 DBH 232. L2 needs source/field review of Oct 2025 alive health 9. |
| `decision_scope` | H1: DBH field/source row. L2: mortality/status/health for Oct 2025. |
| `confidence` | high that scopes are separate; medium on each final correction. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | bare tags with multiple plots/UUIDs should fan out automatically in review synthesis. |
| `source_rows_to_check` | H1 Oct 2025 reviewed row 324; L2 Oct 2025 reviewed row 1080; historical H1 rows 592/636/756/978; L2 rows 108/46/176/370. |

### R4/5261

| Field | Notes |
|---|---|
| `selection` | tag 5261, plot R4, UUID `9625e93c08f59d83`. |
| `related_uids` | `9625e93c08f59d83`. |
| `raw_flags` | `dead_tree_dbh_increase`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `prior_dead_first_qualifying_dbh`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Liquidambar dead/no DBH in June 2023, dead DBH 52 in Oct 2024, dead/no DBH in Apr 2025, then dead DBH 81 in Oct 2025 with note `No sprout`. |
| `interpretation` | Dead-tree DBH increase could be a different measurement point or a row/source issue; `No sprout` does not explain a larger stem. |
| `recommended_action` | source check / human call for Oct 2025 DBH 81 versus Oct 2024 52. |
| `decision_scope` | DBH field/source row for Oct 2025 and Oct 2024. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | no; dead-tree increases should stay review unless directly contradicted by notes/source. |
| `source_rows_to_check` | `2024_fall.csv:1356`, Oct 2025 reviewed row 231. |

### H7/885

| Field | Notes |
|---|---|
| `selection` | tag 885, plot H7, UUID `bc2a81512545fd8f`. |
| `related_uids` | `bc2a81512545fd8f`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, observed mortality event, dead-tree DBH gaps. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Long-dead Pinus from 2019 onward. October 2024 has DBH 81, health 8, alive flag false, standing true, and is interpreted alive; April 2025 and Oct 2025 return dead/0 with Apr 2025 note `girdle`. |
| `interpretation` | October 2024 health 8/interpreted-alive is almost certainly the odd row in an otherwise dead sequence, but source confirmation is still useful because the alive flag is false while health is high. |
| `recommended_action` | source-row correction candidate: likely set Oct 2024 health/status to dead/0 unless source confirms live tissue. |
| `decision_scope` | mortality/status and health for `2024_fall.csv:1132`. |
| `confidence` | medium-high. |
| `needs_riley_call` | yes for final mortality call; no for flagging the row. |
| `candidate_auto_rule` | isolated high-health alive interpretation inside multi-year dead sequence with alive flag false. |
| `source_rows_to_check` | `2024_fall.csv:1132`, `2025_spring.csv:951`. |

### H4/142

| Field | Notes |
|---|---|
| `selection` | tag 142, plot H4, UUID `9f5cd90d1ca96ebe`. |
| `related_uids` | `9f5cd90d1ca96ebe`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Liquidambar is 109 mm in 2019-2020 with 2019 note `bare branches`, then stable 72-78 mm from 2021-2025, with April 2025 `top missing/broken`. |
| `interpretation` | Smaller version of H4 source-era mismatch, but structural/broken-top notes could also indicate measurement-point change or top loss. |
| `recommended_action` | source check / human call; likely mark 2019-2020 DBH uncertain/strike only if grouped H4 source review supports it. |
| `decision_scope` | DBH source-era rows for 2019-2020. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | grouped H4 source-era review, not standalone auto-correction. |
| `source_rows_to_check` | `2023_and_prior.csv:2624`, `2631`, `1948`, `2142`; April 2025 row 1140. |

### L7/20

| Field | Notes |
|---|---|
| `selection` | tag 20, plot L7, UUID `a7632adfd26e9cf4`. |
| `related_uids` | `a7632adfd26e9cf4`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Pine 307 mm in 2019-2020, then stable 468-473 mm from 2021-2025. Health declines but tree stays alive. |
| `interpretation` | Clear source-era/tag-alignment mismatch; 161 mm growth in one year is implausible. |
| `recommended_action` | source check / human call; likely strike or relocate 2019-2020 DBH 307 if source review cannot support it. |
| `decision_scope` | DBH source-era rows for 2019-2020. |
| `confidence` | high that there is an issue; medium on exact correction. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | grouped early-regime DBH review for L6/L7 stable source-era shifts. |
| `source_rows_to_check` | `2023_and_prior.csv:3756`, `3729`, `2007`, `2051`. |

### L3/291

| Field | Notes |
|---|---|
| `selection` | tag 291, plot L3, UUID `8e7d63457d87d188`. |
| `related_uids` | `8e7d63457d87d188`. |
| `raw_flags` | `max_dbh_jump`, `ranked_dbh_jump` at June 2021. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus 80 mm in 2019-2020, then 99/95/93/91/95/94 through 2025; alive throughout. |
| `interpretation` | Moderate regime shift, but not obviously impossible compared with the stronger source-era cases. Could be measurement location, early under-measurement, or threshold tuning noise. |
| `recommended_action` | watch / diagnostic threshold tuning; no immediate correction without nearby complementary/source evidence. |
| `decision_scope` | none yet, or DBH source rows if grouped L3 review later finds alignment evidence. |
| `confidence` | medium. |
| `needs_riley_call` | no for now. |
| `candidate_auto_rule` | use a higher bar for live Juniperus DBH jumps around 20 mm unless persistent-era mismatch is much larger or source context exists. |
| `source_rows_to_check` | `2023_and_prior.csv:2564`, `2542`, `1688`, `1727`. |

### L5/405

| Field | Notes |
|---|---|
| `selection` | tag 405, plot L5, UUID `3836c95884a27b56`. |
| `related_uids` | `3836c95884a27b56`. |
| `raw_flags` | `single_survey_dbh_outlier`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus is 87/87/90, then isolated June 2022 DBH 169, then returns to 92/90/93/95/96. Notes include `horizontal` in 2019 and `leaning` in 2025, but those do not explain a one-year 169. |
| `interpretation` | June 2022 169 is a clear isolated DBH outlier. |
| `recommended_action` | source-row correction candidate: suppress/strike June 2022 DBH 169 unless source gives exact correction. |
| `decision_scope` | DBH field for `2023_and_prior.csv:2124` and matching workbook rows. |
| `confidence` | high. |
| `needs_riley_call` | no for suppressing outlier; yes only if replacing with a value. |
| `candidate_auto_rule` | isolated DBH outlier bracketed by stable pre/post DBH regime. |
| `source_rows_to_check` | `2023_and_prior.csv:2124`, dated entry rows around 2023-06-09/2023-06-16 for L5/405. |

### M1/5860

| Field | Notes |
|---|---|
| `selection` | tag 5860, plot M1, UUID `d6dda35c769d9f0c`. |
| `related_uids` | `d6dda35c769d9f0c`; note nearby M1/860 appears in evidence output but is a separate assigned case. |
| `raw_flags` | `mortality_contradiction`, `single_survey_death_label_outlier`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Unidentified/Nyssa 166-171 mm, alive health 8/8/7 in 2022-2024 spring. October 2024 is dead/0/fallen. April 2025 alive health 4, October 2025 Nyssa alive health 1 plus an extra unknown/missing row with note `nyssa`. |
| `interpretation` | October 2024 death/fallen row is bracketed by live evidence and may be an uncertain/fallen-stem status rather than whole-tree death. October 2025 duplicate/extra note row suggests source ambiguity remains. |
| `recommended_action` | mortality/status human call; likely convert Oct 2024 dead to uncertain unless source confirms whole-tree death, and separately handle Oct 2025 extra row. |
| `decision_scope` | mortality/status for `2024_fall.csv:555`; possible suppress/annotate Oct 2025 extra row 665. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | single-survey dead/fallen row bracketed by alive compatible DBH, but extra row means manual review here. |
| `source_rows_to_check` | `2024_fall.csv:555`, `2025_spring.csv:1209`, Oct 2025 reviewed rows 664-665. |

### M1/860

| Field | Notes |
|---|---|
| `selection` | tag 860, plot M1, UUID `459274c9028138a6`. |
| `related_uids` | `459274c9028138a6`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | same as raw. |
| `evidence_summary` | Juniperus 274 mm in 2019-2020 with note `growing horizontally`, then stable 129-143 mm from 2021-2025. |
| `interpretation` | Strong DBH regime shift, but horizontal-growth context makes measurement-location change plausible. Also appears near M1/5860 in evidence, so avoid an automatic tag/identity decision without source review. |
| `recommended_action` | source check / human call; preserve structural measurement context. |
| `decision_scope` | DBH source-era rows for 2019-2020 or measurement-context annotation. |
| `confidence` | medium. |
| `needs_riley_call` | yes. |
| `candidate_auto_rule` | structural-note DBH regime shifts should stay human-review/context, not auto-strike. |
| `source_rows_to_check` | `2023_and_prior.csv:2621`, `2599`, `1900`, `1302`; current rows `2024_spring.csv:853`, `2024_fall.csv:587`. |


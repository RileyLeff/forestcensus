# Shard 03 third-review report

Assigned current flagged bare tags: 22

## Summary

Recommended action counts:

| recommended_action | count |
|---|---:|
| source check | 11 |
| human call | 8 |
| rule candidate | 3 |

Top recurring patterns:

- **Source-era DBH blocks**: stable but incompatible eras remain the dominant DBH problem in this shard: H4/138, L4/247, H5/550, M1/831, and probably M6/399. These should be reviewed as grouped source/era alignment problems, not as independent biological jumps.
- **One-row measurement/status outliers**: M7/326, R4/5206, H3/160, H1/199, and M1/852 each have one row that conflicts with otherwise coherent history. These are good candidates for source-row scoped decisions.
- **Stem-profile gap vs duplicate distinction**: R2/626 is a clean blank-backfill case; H2/208 and H2/5859 show the dangerous version where exact duplicates and later real/maybe-real stems interact.
- **Nonqualifying tag-change endpoints**: M0/909, M5/2470, and M5/910 are candidate-link cases where one endpoint lacks comparable DBH. These should not auto-merge solely from DBH logic, even when explicit tag-change assertions exist.
- **Note-only rows can create taxon/stem artifacts**: R2/631 still has a post-decision taxon conflict from an October 2025 note-only Pinus row after the April 2025 Pinus DBH row was correctly reassigned.

## Cases

### R2/631

| Field | Value |
|---|---|
| `selection` | bare tag 631; plot R2; UUID `5c3963688ff48be3` |
| `related_uids` | Current UUID `5c3963688ff48be3`; configured row reassignment points April 2025 Pinus row to R2/931. |
| `raw_flags` | `W_BELOW_THRESHOLD_DBH`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `W_TAXON_CONFLICT`; invariants include `prior_live_blank_dbh_history`, `subthreshold_dbh_present`, `taxon_conflict`. |
| `configured_decisions_applied` | `row_reassignment:0002`: April 2025 R2/631 Pinus DBH 563 row reassigned to R2/931. |
| `current_flags` | `W_BELOW_THRESHOLD_DBH`, `W_TAXON_CONFLICT`; `subthreshold_dbh_present`, `threshold_edge_dbh_context`, `taxon_conflict`. |
| `evidence_summary` | Ilex stem grows 45, 48, 49, 49, 55 mm from June 2023 to October 2025. October 2025 also has a note-only row: `should be Pin 93 no Pin 6 in p`, currently surfacing as PINTAE stem 2 with no DBH/health/status. |
| `interpretation` | The real tree is a threshold-edge Ilex. The remaining taxon conflict is likely a note association artifact, not a true second Pinus stem. The April 2025 Pinus DBH problem is already handled; the October 2025 note row is not. |
| `recommended_action` | source check |
| `decision_scope` | source row / taxon / stem profile: `import_recent_format_reviewed.csv:83`; likely suppress as observation evidence or attach as note to R2/931 context. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Note-only rows with no DBH, no health, and no status should not introduce a new taxon or stem without explicit observation fields. |
| `source_rows_to_check` | `output/llm_transcription/oct_2025_reviewed/import_recent_format_reviewed.csv:83`; compare reassigned `2025_spring.csv:696`. |

### M7/326

| Field | Value |
|---|---|
| `selection` | bare tag 326; plot M7; UUID `913cd3bd0248550d` |
| `related_uids` | `913cd3bd0248550d` |
| `raw_flags` | `I_ZOMBIE_TREE`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants include `explicit_note_mortality_correction_candidate`, `health_rebound_new_stem_context`, `qualifying_rank_gap`, `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus at 73 mm in 2019-2020, dead/no DBH in 2021-2022, then June 2023 alive DBH 116 health 6 with note `Marked dead last year`, followed by dead 74, 74, 75 and October 2025 not found. |
| `interpretation` | June 2023 is the only row that disagrees with both DBH and mortality trajectory. It is likely a wrong/misassigned row or a transcription/source problem, not a biological recovery. |
| `recommended_action` | source check |
| `decision_scope` | source row / mortality-status / DBH field: `2023_and_prior.csv:5066`. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Single alive/high-DBH row bracketed by dead rows with stable smaller dead DBH should be queued as source-row correction, not handled as zombie biology. |
| `source_rows_to_check` | `data/raw/forest_census/2023_and_prior.csv:5066`; old evidence workbooks also carry the same June 2023 row. |

### M0/909

| Field | Value |
|---|---|
| `selection` | bare tag 909; plot M0; UUID `085312e055354ca3` |
| `related_uids` | Candidate link from M0/813 UUID `dea7dfb53eb55aed` to M0/909 UUID `085312e055354ca3`. |
| `raw_flags` | `nonqualifying_tree_excluded` |
| `configured_decisions_applied` | `taxon_override:0023`: accept October 2024 species change to Juniperus virginiana. |
| `current_flags` | `nonqualifying_tree_excluded`; candidate identity link remains. |
| `evidence_summary` | M0/909 has dead/nonqualifying evidence: June 2023 no DBH health 0, May/Oct 2024 DBH 33/35 health 0, April 2025 no DBH health 0 leaning, October 2025 health 0. Candidate link says M0/813 -> M0/909, explicit tag change, year 2023. M0/813 is old dead Ilex with DBH 57 in 2019-2020. |
| `interpretation` | This is a tag-change/link question with a nonqualifying target endpoint. The configured taxon decision resolves species for 909, but not whether 813 and 909 should be one identity. |
| `recommended_action` | human call |
| `decision_scope` | candidate link / UUID identity |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Explicit tag-change links with one nonqualifying endpoint should remain human-link queue items unless supported by stronger notes/source context. |
| `source_rows_to_check` | candidate link `M0/813 -> M0/909`; M0/909 rows `2023_and_prior.csv:4811`, `2024_spring.csv:1299`, `2024_fall.csv:549`, `2025_spring.csv:552`, October 2025 row 604. |

### M5/2470

| Field | Value |
|---|---|
| `selection` | bare tag 2470; plot M5; UUID `fccfe1583a7146ea` |
| `related_uids` | Candidate link from M5/2470 UUID `fccfe1583a7146ea` to M5/904 UUID `23a371da2025d5d9`. |
| `raw_flags` | none on the source tree; candidate link present. |
| `configured_decisions_applied` | none |
| `current_flags` | none on the source tree; candidate identity link remains. |
| `evidence_summary` | M5/2470 is dead Pinus: DBH 303 in 2019-2020, dead/no DBH in 2021-2022, October 2024 missing. Candidate target M5/904 has dead/no DBH from June 2023 onward, with May 2024 `confirmed kill` and April 2025 `dnf`. |
| `interpretation` | Explicit tag-change assertion is plausible but DBH cannot independently confirm because the target has no comparable DBH. |
| `recommended_action` | human call |
| `decision_scope` | candidate link / UUID identity |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Same as M0/909: keep explicit links with DBH-missing endpoint in human queue. |
| `source_rows_to_check` | candidate link `M5/2470 -> M5/904`; source rows `2023_and_prior.csv:859`, `880`, `903`, `927`; target rows `2023_and_prior.csv` M5/904, `2024_spring.csv`, `2024_fall.csv`, `2025_spring.csv`. |

### M5/910

| Field | Value |
|---|---|
| `selection` | bare tag 910; plot M5; UUID `f5436c2fe4b220a4` |
| `related_uids` | Candidate link from M5/2477 UUID `85bb0f01da76a838` to M5/910 UUID `f5436c2fe4b220a4`. |
| `raw_flags` | `I_INFERRED_DEAD` |
| `configured_decisions_applied` | none |
| `current_flags` | `I_INFERRED_DEAD`; candidate identity link remains. |
| `evidence_summary` | M5/910 is unidentifiable/dead/no DBH from June 2023 to April 2025. Link source M5/2477 is old dead Pinus with DBH 267 in 2019-2020, then dead/no DBH. |
| `interpretation` | Candidate link may be real, but taxon and no-DBH target make it insufficient for automatic identity merge. |
| `recommended_action` | human call |
| `decision_scope` | candidate link / UUID identity / taxon context |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Nonqualifying target plus taxon ambiguity should block auto-link acceptance. |
| `source_rows_to_check` | candidate link `M5/2477 -> M5/910`; M5/910 rows `2023_and_prior.csv:4997`, `2024_spring.csv:1214`, `2024_fall.csv:771`, `2025_spring.csv:1260`. |

### M4/2461

| Field | Value |
|---|---|
| `selection` | bare tag 2461; plot M4; UUID `ef834b963f1be3f9` |
| `related_uids` | `ef834b963f1be3f9` |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants include `health_rebound_new_stem_context`, `mortality_contradiction`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Pinus DBH 363 in 2019-2020, dead/no DBH in 2021, alive DBH 389 health 6 in June 2022, dead/no DBH June 2023, May 2024 note `Confirmed Kill`, dead DBH 340/330 in Oct 2024/Apr 2025, dead health 0 in Oct 2025. |
| `interpretation` | June 2022 alive/389 row is the conflict. It may be a wrong row or identity mix-up; later confirmed-kill/dead evidence supports actual death by 2023-2024. |
| `recommended_action` | source check |
| `decision_scope` | source row / mortality-status / DBH field: `2023_and_prior.csv:2024`. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Dead -> one alive medium-health row -> dead with confirmed kill should stay human/source-review, not auto-zombie. |
| `source_rows_to_check` | `data/raw/forest_census/2023_and_prior.csv:2024`; compare `2024_spring.csv:804` note `Confirmed Kill`. |

### R4/5206

| Field | Value |
|---|---|
| `selection` | bare tag 5206; plot R4; UUID `e7238f39c2208a2f` |
| `related_uids` | `e7238f39c2208a2f` |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants include `mortality_contradiction`, `observed_mortality_event`, `qualifying_rank_gap`, `single_survey_death_label_outlier`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Alive Pinus DBH 246 health 7 in June 2023; May 2024 dead/health 0 DBH 244; October 2024 alive DBH 247 health 7; April 2025 dead/no DBH; October 2025 dead DBH 240. |
| `interpretation` | May 2024 is a classic single-survey death-label outlier between high-health alive rows. Later 2025 death may be real and should be treated separately. |
| `recommended_action` | rule candidate |
| `decision_scope` | source row / mortality-status: `2024_spring.csv:172`; do not alter April/October 2025 death. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Single observed-dead health-0 row bracketed by high-health alive evidence and comparable DBH should generate a source-row decision to mark that row uncertain/alive-status-suppressed. |
| `source_rows_to_check` | `data/raw/forest_census/2024_spring.csv:172`. |

### L7/23

| Field | Value |
|---|---|
| `selection` | bare tag 23; plot L7; UUID `c66c5264d2331364` |
| `related_uids` | `c66c5264d2331364` |
| `raw_flags` | `I_ZOMBIE_TREE`; invariants include `mortality_contradiction`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus DBH 108.5 in 2019-2020, dead/no DBH 2021, alive DBH 103 health 3 in 2022, alive DBH 105 health 6 in 2023, missing May 2024, dead DBH 101/103/105 health 0 from Oct 2024 onward. |
| `interpretation` | Not a one-row outlier: two alive years sit between early and late dead eras. Could be early dead-label error, later tag confusion, or a real stressed/fallen live period. |
| `recommended_action` | human call |
| `decision_scope` | UUID-level mortality/status history |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Multi-year alive island inside dead history should remain human queue; do not collapse with single-survey zombie rules. |
| `source_rows_to_check` | `2023_and_prior.csv:155`, `79`, `222`, `1385`, `4716`; modern rows `2024_fall.csv:451`, `2025_spring.csv:461`, October 2025 row 1375. |

### H2/208

| Field | Value |
|---|---|
| `selection` | bare tag 208; plot H2; UUID `fb41279d3f01319a` |
| `related_uids` | `fb41279d3f01319a` |
| `raw_flags` | Stem-count changes, large-stem appearance/disappearance; after decision, `I_CORRECTED_ROW` indicates taxon correction. |
| `configured_decisions_applied` | `taxon_override:0004`: April 2025 Nyssa label treated as Pinus taxon slip. |
| `current_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`; `bounded_stem_rank_gap`, `new_persistent_large_stem`, `probable_duplicate_stem_artifact`. |
| `evidence_summary` | Large Pinus single stem near 461-480 through April 2025. May 2024 has exact duplicate stems 480/480. October 2025 has two large stems 475/471. |
| `interpretation` | May 2024 exact duplicate is suspicious, but October 2025 suggests a real second large stem may exist and was missed or unrecorded earlier. This is the dangerous duplicate-vs-real-stem case. |
| `recommended_action` | human call |
| `decision_scope` | UUID stem profile; likely source-row plus blank-backfill decisions if second stem is accepted. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Do not auto-suppress exact duplicate stems when a later comparable second stem appears; route to stem-profile review. |
| `source_rows_to_check` | `2024_spring.csv:450`, `2024_spring.csv:1017`, October 2025 rows 382-383. |

### M2/2420

| Field | Value |
|---|---|
| `selection` | bare tag 2420; plot M2; UUID `cd3ce3a2f5211020` |
| `related_uids` | `cd3ce3a2f5211020` |
| `raw_flags` | `W_BELOW_THRESHOLD_DBH`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants include `prior_live_blank_dbh_history`, `subthreshold_dbh_present`, `max_dbh_jump`, `persistent_dbh_regime_shift`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus listed alive at 38 mm in 2019-2020, jumps to 245 in 2021, then stable 360-366 from 2022-2025 with notes `sprayed`, `girdle`, and dead in October 2025. |
| `interpretation` | The 38 mm era is below threshold and inconsistent with later large pine; 245 -> 362 is also a major jump. This is likely source/tag alignment or missing digit/field problem, not normal growth. |
| `recommended_action` | source check |
| `decision_scope` | source-era / DBH field; likely source rows for 2019-2021 or identity alignment. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Below-threshold early live rows followed by a much larger stable Pinus regime should be grouped into source-era review, not treated as valid qualifying history. |
| `source_rows_to_check` | `2023_and_prior.csv:2866`, `2883`, `1580`, `1608`; modern rows corroborate 360 mm regime. |

### R2/626

| Field | Value |
|---|---|
| `selection` | bare tag 626; plot R2; UUID `946297becb8a75fd` |
| `related_uids` | `946297becb8a75fd` |
| `raw_flags` | `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`; invariants include `blank_missing_stem_backfill_candidate`, `bounded_stem_rank_gap`, `new_persistent_large_stem`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Two-stem Ilex in June 2023: 165/62. May 2024 records only main stem 170. Two stems return in Oct 2024, Apr 2025, Oct 2025 with second stem 59-61. |
| `interpretation` | Clean bounded missing-stem gap. The second stem is real and was simply not reported in May 2024. |
| `recommended_action` | rule candidate |
| `decision_scope` | UUID stem profile / blank backfill for May 2024 rank 2. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | If a non-primary qualifying stem appears before and after a single-survey gap with stable DBH, insert a blank missing/not-reported stem for the gap rather than flagging identity. |
| `source_rows_to_check` | May 2024 main row `2024_spring.csv:121`; second-stem evidence rows `2023_and_prior.csv:5155`, `2024_fall.csv:1246`, `2025_spring.csv:680`, October 2025 row 78. |

### H0/260

| Field | Value |
|---|---|
| `selection` | bare tag 260; plot H0; UUID `cd9b42cebced19cd` |
| `related_uids` | `cd9b42cebced19cd` |
| `raw_flags` | DBH/ranked jumps, stem-count changes, duplicate-stem artifact, stable incompatible DBH era. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa mostly 252-264 through 2022, dips to 210 in June 2023 and 200 in May 2024. May 2024 has exact duplicate 200/200 with `poison ivy` note. It returns to 261/260 in Oct 2024/Apr 2025. |
| `interpretation` | May 2024 duplicate is likely an extra duplicated stem artifact; 2023-2024 low DBH is plausibly poison ivy / measurement-position context, not identity change. |
| `recommended_action` | source check |
| `decision_scope` | source row for duplicate stem; DBH field/measurement-context for June 2023 and May 2024. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Exact duplicate DBH plus stem-count spike with poison-ivy note can generate a duplicate-stem review/candidate decision, but nearby non-duplicate DBH depression should remain context/source review. |
| `source_rows_to_check` | `2023_and_prior.csv:3994`; `2024_spring.csv:388`, `2024_spring.csv:934`. |

### H2/5859

| Field | Value |
|---|---|
| `selection` | bare tag 5859; plot H2; UUID `f511bf0e74b90eb4` |
| `related_uids` | `f511bf0e74b90eb4` |
| `raw_flags` | `I_ZOMBIE_TREE`, stem-count changes, large-stem appearance/disappearance; `mortality_contradiction`, `probable_duplicate_stem_artifact`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | June 2021 Pinus dead health 0 DBH 322; alive and stable from 2022 onward at 328-341. May 2024 exact duplicate 341/341; subsequent rows return to one stem 335/334. |
| `interpretation` | Two separate problems: June 2021 dead row is likely a mortality-label error or should be uncertain; May 2024 second stem is a classic exact duplicate artifact. |
| `recommended_action` | human call |
| `decision_scope` | source row mortality for June 2021; source row/stem profile for May 2024 duplicate. |
| `confidence` | high for duplicate; medium for 2021 mortality. |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Exact duplicate one-survey extra stem can be auto-suggested for suppression when no later second stem appears; dead health 0 followed by stable alive high DBH should be queued separately. |
| `source_rows_to_check` | `2023_and_prior.csv:760`; `2024_spring.csv:453`, `2024_spring.csv:1020`. |

### H1/199

| Field | Value |
|---|---|
| `selection` | bare tag 199; plot H1; UUID `bc35d8a5014f5efc` |
| `related_uids` | `bc35d8a5014f5efc` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `dead_tree_dbh_gap`, `dead_tree_dbh_increase`, `dead_tree_dbh_loss`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Nyssa DBH 95 in 2019-2020, dead/no DBH 2021-2023, May 2024 DBH 66, then 86/83/87 while still dead. |
| `interpretation` | Dead-tree DBH loss is plausible, but May 2024 66 is isolated below the later dead-tree measurements. Later 83-87 could be real decay from 95. |
| `recommended_action` | source check |
| `decision_scope` | DBH field: May 2024 row only; keep dead status. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Dead-tree DBH decreases should not be automatically flagged as errors, but isolated dead-tree low outliers followed by rebound can remain source-row review. |
| `source_rows_to_check` | `2024_spring.csv:353`; compare `2024_fall.csv:138`, `2025_spring.csv`, October 2025 row. |

### L1/5063

| Field | Value |
|---|---|
| `selection` | bare tag 5063; plot L1; UUID `41ed4b36e5876b0b` |
| `related_uids` | `41ed4b36e5876b0b` |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`, `prior_live_blank_dbh_history`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead/fallen/no DBH from 2021-2023; May 2024 `couldn't find`; October 2024 alive DBH 88 health 1 with note `Fallen still live`; April 2025 DNF; October 2025 health 2 standing, note `JUNIPERUS`. |
| `interpretation` | This is probably a fallen-live-stem case where tree-level death labels are too coarse. Later live evidence should be preserved; older dead labels may need reinterpretation as fallen/uncertain rather than true dead. |
| `recommended_action` | human call |
| `decision_scope` | UUID-level mortality/status and taxon note; possible update to taxon Juniperus. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Fallen-still-live notes should override blanket zombie simplification and route to a mortality nuance queue. |
| `source_rows_to_check` | `2024_fall.csv` row with `Fallen still live`; October 2025 row with `JUNIPERUS`; early rows `2023_and_prior.csv` for 2021-2023 fallen/dead labels. |

### M1/852

| Field | Value |
|---|---|
| `selection` | bare tag 852; plot M1; UUID `8bfd9d603186cf2d` |
| `related_uids` | `8bfd9d603186cf2d` |
| `raw_flags` | `I_ZOMBIE_TREE`; `dead_tree_dbh_gap`, `mortality_contradiction`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus/unidentified from 2019-2023, missing May 2024, dead DBH 84 in October 2024, April 2025 alive health 1 DBH 83, October 2025 dead health 0 DBH 83. |
| `interpretation` | April 2025 is a single low-health alive row bracketed by dead observations at the same DBH. Could be tiny live tissue, but without a note it is likely alive/dead ambiguity. |
| `recommended_action` | human call |
| `decision_scope` | source row / mortality-status: `2025_spring.csv:1181`. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Single alive health-1 row bracketed by dead health-0 rows with same DBH should be queued for mortality call; possible decision to set dead/0 or uncertain. |
| `source_rows_to_check` | `data/raw/forest_census/2025_spring.csv:1181`. |

### H4/138

| Field | Value |
|---|---|
| `selection` | bare tag 138; plot H4; UUID `e640efaf3d56062c` |
| `related_uids` | `e640efaf3d56062c` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Liquidambar DBH 270 in 2019-2020, then stable 104-108 from 2021 through 2025. Health remains alive/high throughout. |
| `interpretation` | Stable early high era vs stable modern low era; likely source/tag alignment problem in 2019-2020 rather than biology. |
| `recommended_action` | source check |
| `decision_scope` | source-era DBH field / possible identity alignment for 2019-2020 rows. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Stable incompatible early era should be grouped for source-era review; do not auto-correct without source mapping. |
| `source_rows_to_check` | `2023_and_prior.csv:3256`, `3264`; compare stable modern rows starting `2023_and_prior.csv:2633`. |

### H3/160

| Field | Value |
|---|---|
| `selection` | bare tag 160; plot H3; UUID `ed8d77ee2f5ee4fb` |
| `related_uids` | `ed8d77ee2f5ee4fb` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `single_survey_dbh_outlier`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Large Pinus stable near 493-501 from 2019-2023, May 2024 DBH 407, then 491/496 afterward; October 2025 no DBH but alive health 6. |
| `interpretation` | May 2024 DBH 407 is an isolated low outlier. |
| `recommended_action` | rule candidate |
| `decision_scope` | source row / DBH field: `2024_spring.csv:209`; likely suppress DBH only. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Single-survey DBH outlier bracketed by stable DBH before/after in a live single-stem tree can generate a DBH-suppression decision candidate. |
| `source_rows_to_check` | `data/raw/forest_census/2024_spring.csv:209`. |

### L4/247

| Field | Value |
|---|---|
| `selection` | bare tag 247; plot L4; UUID `f29518aa175ea313` |
| `related_uids` | `f29518aa175ea313` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 314 in 2019-2020, then 84-102 from 2021-2025. Alive throughout, with 2019 note `small canopy`. |
| `interpretation` | Strong source-era/tag-alignment problem. The modern small-juniper trajectory is coherent; early 314 values likely belong elsewhere or should be marked uncertain. |
| `recommended_action` | source check |
| `decision_scope` | source-era DBH/identity rows for 2019-2020. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Same grouped early-era rule as H4/138. |
| `source_rows_to_check` | `2023_and_prior.csv:2289`, `2287`; modern comparison from `2023_and_prior.csv:2094` onward. |

### M6/399

| Field | Value |
|---|---|
| `selection` | bare tag 399; plot M6; UUID `77492b4e67a11a10` |
| `related_uids` | `77492b4e67a11a10` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `max_dbh_jump`, `ranked_dbh_jump`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 56 in 2019-2020, then 160, 179, 185, 181, 166, 163, 164 from 2021 onward. Alive throughout. |
| `interpretation` | Early 56/56 may be missing leading digit (`156`) or an early source/tag alignment issue. The repeated value makes it a carried-forward/source-era issue rather than a one-off typo. |
| `recommended_action` | source check |
| `decision_scope` | source-era DBH field for 2019-2020. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Repeated early low value followed by stable 160+ Juniperus should be grouped with early-low/source-era review; only auto-correct to +100 if handwriting/source confirms. |
| `source_rows_to_check` | `2023_and_prior.csv:3214`, `3237`; compare `2023_and_prior.csv:1707`, `1915`, `5036`. |

### H5/550

| Field | Value |
|---|---|
| `selection` | bare tag 550; plot H5; UUID `db7e4abdee844f08` |
| `related_uids` | `db7e4abdee844f08` |
| `raw_flags` | Raw included `W_BELOW_THRESHOLD_DBH`, DBH jumps, `subthreshold_dbh_present`, `early_low_dbh_source_era_candidate`, `max_dbh_jump`, `qualifying_rank_gap`. |
| `configured_decisions_applied` | `row_correction:0017`: June 2022 DBH 33.7 corrected to 337. |
| `current_flags` | `I_CORRECTED_ROW`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; `early_low_dbh_source_era_candidate`. |
| `evidence_summary` | Pinus DBH 57 in 2019-2020, then 333-339 from 2021 onward. The June 2022 33.7 decimal-place error is already corrected to 337. |
| `interpretation` | One local typo is fixed, but the early 57/57 era remains inconsistent with the stable 333+ pine. This is a grouped early source/tag-alignment problem. |
| `recommended_action` | source check |
| `decision_scope` | source-era DBH/identity rows for 2019-2020; keep existing June 2022 correction. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Already-corrected decimal-place row should not distract from remaining early-era regime issue. |
| `source_rows_to_check` | `2023_and_prior.csv:2763`, `2819`; corrected row `2023_and_prior.csv:1618`; modern rows from `2023_and_prior.csv:2214` onward. |

### M1/831

| Field | Value |
|---|---|
| `selection` | bare tag 831; plot M1; UUID `ffb8c7206becf39d` |
| `related_uids` | `ffb8c7206becf39d` |
| `raw_flags` | `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; repeated `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus DBH 390/390/380 in 2019-2021, then 315/315 in 2022-2023, then 387/391/388/392 from 2024-2025. April 2025 note `p.i.` but the DBH matches the high regime. |
| `interpretation` | The 2022-2023 middle era is incompatible with both earlier and later measurements. Because multiple 2022 source files repeat 315, this is likely a carried-forward source/data-entry alignment problem rather than parser noise. |
| `recommended_action` | source check |
| `decision_scope` | source-era DBH fields for June 2022 and June 2023. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Middle-era stable incompatible block should be routed separately from early-era-only patterns. |
| `source_rows_to_check` | `2023_and_prior.csv:1825`, `4815`; dated 2022 entry workbooks with repeated 315; compare 2024+ rows. |

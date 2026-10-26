# Agent 06 shard

Assigned current flagged tags reviewed: 22.

## Summary

| recommended_action | count | cases |
|---|---:|---|
| `source check` | 12 | M2/5863, L3/918, L3/301, L0/922, L5/419, L3/5886, H0/293, L3/298, M0/580, H4/144, L6/61, H7/887 |
| `rule candidate` | 6 | R2/612, R4/5213, R3/684, L7/21, L7/3, L5/414 |
| `human call` | 4 | M2/2408, M5/5870, L6/92, L6/105 |

Top recurring patterns:

- Isolated DBH outliers bracketed by stable neighboring measurements are good candidates for source-row scoped DBH suppression, not whole-row suppression.
- Bounded missing rank-2 stems in otherwise stable two-stem Ilex histories are good candidates for blank missing-stem backfill.
- Early stable DBH eras that are incompatible with later stable eras should be reviewed as source-era/tag-alignment blocks, not as biological jumps.
- Mortality contradictions split into two different workflows: low-health marginal "zombie" cases need Riley/source judgment, while strong late revivals after long dead histories should be source-checked as likely field/transcription errors.
- Threshold-edge second stems around 48-50 mm should not pollute qualifying profiles before they cross the 50 mm inclusion threshold.

## Cases

### M2/5863

| Field | Notes |
|---|---|
| `selection` | M2/5863; UUID `e64ad49eb5a8f561`; linked candidate M2/5883 UUID `0e11403b2685d1b0`. |
| `related_uids` | `e64ad49eb5a8f561`, `0e11403b2685d1b0`. |
| `raw_flags` | `single_survey_dbh_outlier`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw: isolated May 2024 DBH outlier plus candidate link. |
| `evidence_summary` | M2/5883 is alive 114-119 mm in 2021-2022, then M2/5863 appears 127 mm in June 2023 and 125/121 mm in 2024-2025. May 2024 M2/5863 has 163 mm with missing/unknown health/status, then returns to 125/121. October 2025 has two no-DBH live rows, one noted `J.vir`. Candidate link score 95, source row `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:23`. |
| `interpretation` | The 5883 -> 5863 link is plausible, but the May 2024 163 mm value is likely a bad DBH or wrong-row value. The October 2025 two-row/stem signal may also need later stem-profile review, but does not block the tag-link call. |
| `recommended_action` | `source check`: likely accept the 5883 -> 5863 identity link and suppress/correct only May 2024 DBH 163 after source check. |
| `decision_scope` | Candidate link plus DBH field at `2024_spring.csv:920`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Isolated DBH outlier within a candidate-link endpoint should not block link review; route to link plus DBH-field decision. |
| `source_rows_to_check` | `2024_spring.csv:920`; link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:23`; compare M2/5883 rows `2023_and_prior.csv:2515`, `2023_and_prior.csv:2256`, `2024_fall.csv:657`. |

### M2/2408

| Field | Notes |
|---|---|
| `selection` | M2/2408; UUID `5df2123eba128dba`. |
| `related_uids` | `5df2123eba128dba`. |
| `raw_flags` | `explicit_note_mortality_correction_candidate`, `qualifying_rank_gap`, `single_survey_death_label_outlier`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive 325 mm health 7 in 2019-2020; June 2021 is observed dead health 0 with no DBH; June 2022 is alive health 1 DBH 308 with note `marked dead last year`; dead health 0 from 2023 through October 2025, with dead-tree DBHs around 299-310. |
| `interpretation` | Classic marginal-live mortality case. The 2022 field note explicitly knows the tree was marked dead in 2021, so 2022 may be real observed live tissue rather than a simple typo. |
| `recommended_action` | `human call`: decide whether June 2022 health 1 alive is real marginal tissue and whether June 2021 dead should become uncertain. |
| `decision_scope` | Mortality/status at `2023_and_prior.csv:896` and/or `2023_and_prior.csv:1285`; optional blank DBH gap. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Do not auto-correct low-health alive rows with explicit "marked dead last year" notes. Route to marginal-live mortality queue. |
| `source_rows_to_check` | `2023_and_prior.csv:896`, `2023_and_prior.csv:1285`. |

### L3/918

| Field | Notes |
|---|---|
| `selection` | L3/918; UUID `2dd66f4dec9e4e46`; linked candidate L3/301 UUID `e628a8ca8af09913`. |
| `related_uids` | `2dd66f4dec9e4e46`, `e628a8ca8af09913`. |
| `raw_flags` | `threshold_edge_dbh_context`, raw `mortality_contradiction`, `taxon_conflict`, `W_ALIVE_HEALTH_CONFLICT`, `W_TAXON_CONFLICT`. |
| `configured_decisions_applied` | `row_correction:0003` trusts health 0 over alive flag in June 2023; `taxon_override:0035` sets L3/918 to Juniperus virginiana. |
| `current_flags` | `prior_dead_first_qualifying_dbh`; corrected-row audit info. |
| `evidence_summary` | L3/918 is dead health 0 in June 2023, dead DBH 60-61 in May/October 2024, missing in April 2025, dead in October 2025. Candidate link from L3/301 has score 95, but review reason says DBH profiles differ too much. |
| `interpretation` | Existing taxon/status decisions cleaned up the raw contradictions. The remaining link to L3/301 is weak: both are dead sequences, but L3/301 has 105 mm early DBH and L3/918 has 60-61 mm later DBH. This could be a tag-change/decomposition story, but the evidence is not enough to auto-merge. |
| `recommended_action` | `source check`: keep separate unless source evidence confirms L3/301 -> L3/918. |
| `decision_scope` | Candidate link only; no further row correction recommended from current evidence. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Candidate tag links with materially incompatible DBH profiles should remain review-only even when taxon/dead-status match. |
| `source_rows_to_check` | Link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:12`; L3/918 rows `2023_and_prior.csv:4531`, `2024_spring.csv:634`, `2024_fall.csv:241`. |

### L3/301

| Field | Notes |
|---|---|
| `selection` | L3/301; UUID `e628a8ca8af09913`; linked candidate L3/918 UUID `2dd66f4dec9e4e46`. |
| `related_uids` | `e628a8ca8af09913`, `2dd66f4dec9e4e46`. |
| `raw_flags` | `I_INFERRED_DEAD` only. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | `I_INFERRED_DEAD`; candidate identity link. |
| `evidence_summary` | L3/301 is Nyssa dead health 0 with DBH 105 in 2019-2020, then dead/no-DBH through 2022, then inferred dead in 2024. Candidate link to L3/918 has score 95 but review reason says DBH profiles differ too much. |
| `interpretation` | This is probably a closed dead tree record. The L3/918 link may be historical paperwork, but the DBH/taxon evidence is not enough to combine them automatically. |
| `recommended_action` | `source check`: preserve as separate dead UUID unless tag-change evidence proves otherwise. |
| `decision_scope` | Candidate link. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Same as L3/918: incompatible dead DBH profiles should not be auto-linked. |
| `source_rows_to_check` | L3/301 rows `2023_and_prior.csv:448`, `433`, `469`, `537`; link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:12`. |

### L0/922

| Field | Notes |
|---|---|
| `selection` | L0/922; UUID `6bb4dc5788760204`; linked candidate L0/157 UUID `c6236b0d598c05c5`. |
| `related_uids` | `6bb4dc5788760204`, `c6236b0d598c05c5`. |
| `raw_flags` | None on L0/922 itself. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Candidate identity link only. |
| `evidence_summary` | L0/922 is Pinus observed dead/no-DBH in 2023-2025, with April 2025 note `fallen`. Candidate source L0/157 is Pinus dead with DBH 299 in 2019-2020, then dead/no-DBH and inferred dead. Candidate link score 95; reason says one endpoint lacks comparable DBH. |
| `interpretation` | Plausible closed-tree tag-change: L0/157 may be the old measured dead pine and L0/922 the later dead/fallen no-DBH continuation. The lack of overlapping DBH after the alleged change prevents auto-merge. |
| `recommended_action` | `source check`: likely accept L0/157 -> L0/922 if source/notes establish tag change; otherwise keep as separate dead records. |
| `decision_scope` | Candidate link. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Dead-tree links with old DBH then later no-DBH require source evidence; do not auto-link from taxon/dead status alone. |
| `source_rows_to_check` | Link evidence `Forest_Disturbance_Plot_Trees_All_Years_InProgress.xlsx:6`; L0/157 rows `2023_and_prior.csv:692`, `686`, `782`, `1001`; L0/922 rows `2023_and_prior.csv:4364`, `2024_spring.csv:53`, `2024_fall.csv:55`, `2025_spring.csv:52`. |

### L5/419

| Field | Notes |
|---|---|
| `selection` | L5/419; UUID `3c6b75f60b75a9bc`. |
| `related_uids` | `3c6b75f60b75a9bc`. |
| `raw_flags` | `dead_tree_dbh_gap`, `health_rebound_new_stem_context`, `mortality_contradiction`, `qualifying_rank_gap`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus dead health 0 from 2019 through April 2025, with dead-tree DBHs around 303-310 when measured. October 2025 reports DBH 301 and health 6 alive. |
| `interpretation` | A health 6 live revival after a six-year dead sequence is unlikely biologically and smells like an October 2025 status/health transcription or field-status error, especially because DBH is consistent with the dead stem. |
| `recommended_action` | `source check`: check October 2025 source/field notes; likely set October 2025 to dead health 0 unless live tissue was explicitly observed. |
| `decision_scope` | Mortality/status/health at `import_recent_format_reviewed.csv:1224`. |
| `confidence` | Medium-high. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Strong live-health revival after long observed-dead history should route to source check, not low-health zombie handling. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:1224`; compare prior dead rows `2024_spring.csv:701`, `2024_fall.csv:310`, `2025_spring.csv:315`. |

### M5/5870

| Field | Notes |
|---|---|
| `selection` | M5/5870; UUID `82415d2b8e660858`. |
| `related_uids` | `82415d2b8e660858`. |
| `raw_flags` | `mortality_contradiction`, `prior_live_blank_dbh_history`, `qualifying_rank_gap`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa dead health 0 in 2021, alive health 3 DBH 71 in 2022, unfound in 2023, then dead health 0 with DBH 65-68 from 2024-2025 and missing in October 2025. |
| `interpretation` | Low-health zombie/marginal-live case. The 2022 alive row could be real marginal tissue, but the surrounding death/missing sequence prevents a confident automatic call. |
| `recommended_action` | `human call`: decide whether to preserve June 2022 alive health 3 or treat the earlier/later dead labels as uncertain. |
| `decision_scope` | Mortality/status around `2023_and_prior.csv:565`, `1409`, `4993`; optional blank DBH gap. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Low-health one-year revivals in Nyssa should stay human-review unless stronger source text exists. |
| `source_rows_to_check` | `2023_and_prior.csv:565`, `1409`, `4993`; later dead rows `2024_spring.csv:1210`, `2024_fall.csv:767`, `2025_spring.csv:1290`. |

### L3/5886

| Field | Notes |
|---|---|
| `selection` | L3/5886; UUID `34ea5e89fde2bf5c`. |
| `related_uids` | `34ea5e89fde2bf5c`. |
| `raw_flags` | `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, repeated `source_note_dbh_conflict`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Unidentified/Juniperus is alive DBH 168 health 6 in 2021, then June 2022 jumps to DBH 319 health 0 dead, then returns to alive DBH 170-183 and health 4-7 through April 2025. October 2025 has missing/no-DBH rows. April 2025 note is `???`. |
| `interpretation` | June 2022 is almost certainly the wrong DBH/status row or a wrong-tree entry. It is not a plausible death/revival event and not a plausible growth jump. |
| `recommended_action` | `source check`: high-confidence correction candidate; suppress June 2022 DBH and probably convert its dead/status/health evidence to unknown or remove the row from canonical mortality evidence after source check. |
| `decision_scope` | Source row / DBH field / mortality status at `2023_and_prior.csv:1205`. |
| `confidence` | High. |
| `needs_riley_call` | Yes, only to choose suppress-field vs suppress-observation. |
| `candidate_auto_rule` | Single-row DBH outlier plus dead label bracketed by multi-year alive stable DBH should be a high-priority source-row correction candidate. |
| `source_rows_to_check` | `2023_and_prior.csv:1205`; compare `2023_and_prior.csv:2053`, `4530`, `2024_spring.csv:633`, `2024_fall.csv:240`, `2025_spring.csv:245`. |

### R2/612

| Field | Notes |
|---|---|
| `selection` | R2/612; UUID `0e11e8c7ac6bd178`. |
| `related_uids` | `0e11e8c7ac6bd178`. |
| `raw_flags` | `subthreshold_dbh_present`, `new_persistent_large_stem`, `W_BELOW_THRESHOLD_DBH`, `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Ilex with large stem ~194-197 mm throughout. Second stem is 48 mm in June 2023, absent May 2024, 49 mm in October 2024, then 50 mm in April/October 2025. |
| `interpretation` | This is threshold-edge recruitment, not a data error. The subthreshold 48/49 values should be evidence but should not contribute to a qualifying stem profile until the stem reaches 50 mm. |
| `recommended_action` | `rule candidate`: suppress subthreshold DBH values from canonical qualifying profile; accept 50 mm stem from April 2025 onward; no Riley call needed unless source notes disagree. |
| `decision_scope` | DBH field/profile qualification for `2023_and_prior.csv:5139` and `2024_fall.csv:1244`; no whole-row suppression. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | For secondary stems with DBH <50 followed by >=50 in later surveys, mark pre-threshold DBH as non-qualifying evidence and start canonical stem at first >=50 measurement. |
| `source_rows_to_check` | `2023_and_prior.csv:5139`, `2024_fall.csv:1244`, `2025_spring.csv:664`, `import_recent_format_reviewed.csv:59`. |

### R4/5213

| Field | Notes |
|---|---|
| `selection` | R4/5213; UUID `97da6e4fc79a636c`. |
| `related_uids` | `97da6e4fc79a636c`. |
| `raw_flags` | `blank_missing_stem_backfill_candidate`, `bounded_stem_rank_gap`, `new_persistent_large_stem`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_TREE_STEM_COUNT_CHANGE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Two-stem Ilex: 91/72 in June 2023, only 86 in May 2024, then 90/70 in October 2024, 93/69 in April 2025, 92/69 in October 2025. |
| `interpretation` | May 2024 simply missed the second qualifying stem; the two-stem profile is stable on both sides. |
| `recommended_action` | `rule candidate`: insert a blank/not-reported rank-2 stem row for May 2024, preserving stem evidence before/after. |
| `decision_scope` | Stem profile blank backfill for May 2024, UUID `97da6e4fc79a636c`, rank 2. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Bounded rank-2 gaps in stable multi-stem trees should produce blank stem rows, not review flags. |
| `source_rows_to_check` | Gap at `2024_spring.csv:177`; surrounding stem-2 rows `2023_and_prior.csv:5242`, `2024_fall.csv:1361`, `2025_spring.csv:770`, `import_recent_format_reviewed.csv:178`. |

### R3/684

| Field | Notes |
|---|---|
| `selection` | R3/684; UUID `1bb59fe5d3505e14`. |
| `related_uids` | `1bb59fe5d3505e14`. |
| `raw_flags` | `blank_missing_stem_backfill_candidate`, `bounded_stem_rank_gap`, `new_persistent_large_stem`, `W_TREE_LARGE_STEM_APPEARANCE`, `W_TREE_LARGE_STEM_DISAPPEARANCE`, `W_TREE_STEM_COUNT_CHANGE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Two-stem Ilex: 100/84 in June 2023, only 101 in May 2024, then 102/81 in October 2024, 104/83 in April 2025, and two live no-DBH rows in October 2025. |
| `interpretation` | Same as R4/5213: stable two-stem tree with one May 2024 missing rank-2 row. |
| `recommended_action` | `rule candidate`: insert blank/not-reported May 2024 rank-2 stem. |
| `decision_scope` | Stem profile blank backfill for May 2024, UUID `1bb59fe5d3505e14`, rank 2. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Same bounded rank-2 gap rule. |
| `source_rows_to_check` | Gap at `2024_spring.csv:159`; surrounding stem-2 rows `2023_and_prior.csv:5214`, `2024_fall.csv:1298`, `2025_spring.csv:740`, `import_recent_format_reviewed.csv:141`. |

### H0/293

| Field | Notes |
|---|---|
| `selection` | H0/293; UUID `6b6ee38c43431267`. |
| `related_uids` | `6b6ee38c43431267`. |
| `raw_flags` | Taxon conflict before configured taxon override; current stem-profile flags. |
| `configured_decisions_applied` | `taxon_override:0011` sets H0/293 to Liquidambar styraciflua. |
| `current_flags` | `blank_missing_stem_backfill_candidate`, `new_persistent_large_stem`, corrected-row audit info. |
| `evidence_summary` | Liquidambar single-stem history: 140 in 2019-2020, 131 in 2021-2023, then May 2024 has two rows 147 and 131, followed by single-stem 130/131 and October 2025 no-DBH health 4. |
| `interpretation` | May 2024 likely contains an extra/duplicate stem row rather than a real persistent second stem. The 131 row matches the long-running single-stem profile; 147 is the suspicious one-survey extra. |
| `recommended_action` | `source check`: inspect May 2024 source; likely suppress the May 2024 147 mm extra row/value rather than backfilling a second stem. |
| `decision_scope` | Source row / stem profile at `2024_spring.csv:967` and `2024_spring.csv:968`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Single-survey extra stem whose smaller row matches the long-term stem should route to duplicate/extra-stem review, not bounded-gap backfill. |
| `source_rows_to_check` | `2024_spring.csv:967`, `2024_spring.csv:968`; compare `2023_and_prior.csv:4030`, `2024_fall.csv:917`, `2025_spring.csv:599`. |

### L6/92

| Field | Notes |
|---|---|
| `selection` | L6/92; UUID `2401ed2359e66751`. |
| `related_uids` | `2401ed2359e66751`. |
| `raw_flags` | `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa dead health 0 DBH 103 in 2019-2020, alive low health 1 DBH 95-102 from 2021-2024, dead health 0 DBH 101 in April 2025, then alive health 1/no-DBH in October 2025. |
| `interpretation` | The early dead labels are probably wrong or not whole-tree death; the late April 2025 dead row is also questionable because October 2025 sees low-health alive tissue again. |
| `recommended_action` | `human call`: decide whether to reinterpret early dead rows and April 2025 dead row as uncertain rather than true mortality. |
| `decision_scope` | Mortality/status for `2023_and_prior.csv:456`, `432`, and `2025_spring.csv:405`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Repeated low-health Nyssa alive sequences with isolated dead labels should be queued for marginal-live review, not auto-dead. |
| `source_rows_to_check` | `2023_and_prior.csv:456`, `432`, `2025_spring.csv:405`, `import_recent_format_reviewed.csv:1315`. |

### L3/298

| Field | Notes |
|---|---|
| `selection` | L3/298; UUID `77307f8018b7c9a8`. |
| `related_uids` | `77307f8018b7c9a8`. |
| `raw_flags` | `dead_tree_dbh_gap`, `mortality_contradiction`, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus dead health 0 from 2019 through April 2025, including note `dead. pushed over by tree` in June 2020 and dead DBHs 62/64 in 2024. October 2025 reports alive health 4/no-DBH. |
| `interpretation` | Latest-survey revival after a long dead/pushed-over sequence is suspicious. October 2025 may be a wrong status/health or wrong tag. |
| `recommended_action` | `source check`: inspect October 2025 row; likely set to dead/0 or uncertain unless field evidence confirms live tissue. |
| `decision_scope` | Mortality/status/health at `import_recent_format_reviewed.csv:1132`. |
| `confidence` | Medium-high. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Strong late revival after long observed-dead history should source-check the latest row. |
| `source_rows_to_check` | `import_recent_format_reviewed.csv:1132`; compare `2023_and_prior.csv:114`, `44`, `183`, `364`, `4507`, `2024_spring.csv:608`, `2024_fall.csv:215`, `2025_spring.csv:218`. |

### M0/580

| Field | Notes |
|---|---|
| `selection` | M0/580; UUID `2ed10e791739264b`. |
| `related_uids` | `2ed10e791739264b`. |
| `raw_flags` | `health_rebound_alive_context`, `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa alive 214 mm health 6 in 2019-2020, then stable 76-78 mm alive from 2021-2025. Health fluctuates but all statuses are alive. |
| `interpretation` | This is not a mortality problem. It is a stable incompatible DBH-era problem, likely source-era/tag alignment or wrong early DBH. |
| `recommended_action` | `source check`: review 2019-2020 source-era/tag alignment; likely strike/relocate early 214 mm DBHs rather than alter modern rows. |
| `decision_scope` | DBH field/source-era for `2023_and_prior.csv:1951` and `1953`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Health rebound among all-alive rows should downgrade to context; stable incompatible DBH eras route to source-era DBH review. |
| `source_rows_to_check` | `2023_and_prior.csv:1951`, `1953`; compare `1956`, `1320`, `4773`, `2024_spring.csv:1262`, `2024_fall.csv:512`, `2025_spring.csv:514`. |

### L6/105

| Field | Notes |
|---|---|
| `selection` | L6/105; UUID `e4325ef91efa611d`. |
| `related_uids` | `e4325ef91efa611d`. |
| `raw_flags` | `mortality_contradiction`, sharp health rebound, `I_ZOMBIE_TREE`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus dead health 0 DBH 130 in 2019-2020, then alive health 10/6/7 with DBH 143-152 from 2021 through October 2025. |
| `interpretation` | Early dead labels are almost certainly wrong-label/source-row artifacts, not true mortality, because the later live sequence is strong and persistent. |
| `recommended_action` | `human call`: likely reinterpret 2019-2020 dead rows as uncertain or wrong-label; decide whether to preserve DBH as measured but suppress mortality evidence. |
| `decision_scope` | Mortality/status/health for `2023_and_prior.csv:131` and `28`. |
| `confidence` | Medium-high. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Early dead rows followed by many years of strong live same-taxon DBH should route to early-death-label review. |
| `source_rows_to_check` | `2023_and_prior.csv:131`, `28`; compare live rows `3199`, `1937`, `4627`, `2024_spring.csv:459`, `2024_fall.csv:356`, `2025_spring.csv:418`, `import_recent_format_reviewed.csv:1328`. |

### H4/144

| Field | Notes |
|---|---|
| `selection` | H4/144; UUID `15429ee4d25437e2`. |
| `related_uids` | `15429ee4d25437e2`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive 136 mm in 2019-2020, then stable 519-539 mm from 2021-2025. April 2025 note: `2nd tag "807"`. |
| `interpretation` | Part of the known H4 2019-2020 tag/source alignment problem. The later 519+ mm pine history is coherent; the early 136 mm values are not biologically compatible. |
| `recommended_action` | `source check`: handle as H4 source-era block; likely strike/relocate 2019-2020 DBHs after checking raw sheets and tag 807 clue. |
| `decision_scope` | DBH field/source-era for `2023_and_prior.csv:3633` and `3714`; possible identity context with tag 807. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Stable incompatible early era in H4 should be grouped rather than fixed as independent per-tag jumps. |
| `source_rows_to_check` | `2023_and_prior.csv:3633`, `3714`; later rows `2476`, `2514`, `4204`, `2024_spring.csv:329`, `2024_fall.csv:1038`, `2025_spring.csv:1142`, `import_recent_format_reviewed.csv:448`. |

### L7/21

| Field | Notes |
|---|---|
| `selection` | L7/21; UUID `7e3cd92dcfe69e6a`. |
| `related_uids` | `7e3cd92dcfe69e6a`. |
| `raw_flags` | `single_survey_dbh_outlier`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 57/57/59, then June 2022 outlier 100, then 64-69 from 2023-2025. |
| `interpretation` | June 2022 DBH 100 is an isolated erroneous value; source could reveal 60, but current evidence supports suppressing it rather than inventing an exact correction. |
| `recommended_action` | `rule candidate`: suppress June 2022 DBH 100 to missing unless source confirms a corrected value. |
| `decision_scope` | DBH field at `2023_and_prior.csv:2137`. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Stable small Juniperus plus one isolated high DBH outlier -> source-row DBH suppression. |
| `source_rows_to_check` | `2023_and_prior.csv:2137`; compare `3183`, `3006`, `2110`, `4714`, `2024_spring.csv:501`, `2024_fall.csv:449`, `2025_spring.csv:459`, `import_recent_format_reviewed.csv:1373`. |

### L7/3

| Field | Notes |
|---|---|
| `selection` | L7/3; UUID `9b07ca8c6e12935d`. |
| `related_uids` | `9b07ca8c6e12935d`. |
| `raw_flags` | `single_survey_dbh_outlier`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 97-100 from 2019-2023, May 2024 outlier 199, then 100/106/105. |
| `interpretation` | May 2024 199 is almost certainly a typo or wrong-row value, perhaps intended as 99. |
| `recommended_action` | `rule candidate`: suppress May 2024 DBH 199 to missing unless source confirms 99. |
| `decision_scope` | DBH field at `2024_spring.csv:510`. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Isolated near-duplicate leading digit outlier bracketed by stable DBH should be suppress-field/correct-if-source. |
| `source_rows_to_check` | `2024_spring.csv:510`; compare `2023_and_prior.csv:3187`, `3022`, `2324`, `2362`, `4723`, `2024_fall.csv:458`, `2025_spring.csv:441`, `import_recent_format_reviewed.csv:1356`. |

### L5/414

| Field | Notes |
|---|---|
| `selection` | L5/414; UUID `e426fa41f35ba95e`. |
| `related_uids` | `e426fa41f35ba95e`. |
| `raw_flags` | `single_survey_dbh_outlier`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 92-98 alive through 2023, May 2024 outlier 63 health 2 alive, then dead DBH 95/94/94 from October 2024 onward. |
| `interpretation` | The May 2024 DBH 63 is inconsistent with both prior live and later dead measurements. The later death appears real and should be preserved. |
| `recommended_action` | `rule candidate`: suppress/correct only May 2024 DBH 63; keep May 2024 alive health 2 and later dead rows. |
| `decision_scope` | DBH field at `2024_spring.csv:696`. |
| `confidence` | High. |
| `needs_riley_call` | No. |
| `candidate_auto_rule` | Isolated DBH outlier immediately before death should suppress DBH only, not erase health/mortality evidence. |
| `source_rows_to_check` | `2024_spring.csv:696`; compare `2023_and_prior.csv:1954`, `1952`, `1312`, `1771`, `4582`, `2024_fall.csv:305`, `2025_spring.csv:310`, `import_recent_format_reviewed.csv:1219`. |

### L6/61

| Field | Notes |
|---|---|
| `selection` | L6/61; UUID `b66d33ce35179436`. |
| `related_uids` | `b66d33ce35179436`. |
| `raw_flags` | `stable_incompatible_dbh_era`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive 181 mm in 2019-2020, then stable larger DBH 339-369 from 2021-2025. |
| `interpretation` | Another stable incompatible source-era DBH shift. The modern larger pine profile is coherent; early 181 values probably need source-era/tag review. |
| `recommended_action` | `source check`: group with L6/L7 early-regime source shifts; likely strike/relocate 2019-2020 DBHs after source review. |
| `decision_scope` | DBH field/source-era for `2023_and_prior.csv:2199` and `2194`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Stable incompatible early era should be grouped for source review, not auto-corrected. |
| `source_rows_to_check` | `2023_and_prior.csv:2199`, `2194`; compare `1796`, `1479`, `4660`, `2024_fall.csv:389`, `2025_spring.csv:374`, `import_recent_format_reviewed.csv:1285`. |

### H7/887

| Field | Notes |
|---|---|
| `selection` | H7/887; UUID `957768d058f57f52`. |
| `related_uids` | `957768d058f57f52`. |
| `raw_flags` | `early_low_dbh_source_era_candidate`, `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`. |
| `configured_decisions_applied` | None matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Pinus alive 62 mm in 2019-2020, then stable 333-344 mm from 2021-2025. |
| `interpretation` | Early repeated 62 mm values are incompatible with the later stable pine. Could be omitted leading digit or source/tag alignment, but exact correction cannot be inferred safely. |
| `recommended_action` | `source check`: review 2019-2020 source rows; likely strike/relocate early DBH values unless source supports a corrected 362-ish value. |
| `decision_scope` | DBH field/source-era for `2023_and_prior.csv:3568` and `3709`. |
| `confidence` | Medium. |
| `needs_riley_call` | Yes. |
| `candidate_auto_rule` | Early repeated low DBH before large stable pine profile should be source-era review, not automatic 10x/leading-digit correction. |
| `source_rows_to_check` | `2023_and_prior.csv:3568`, `3709`; compare `2855`, `2507`, `4295`, `2024_spring.csv:311`, `2024_fall.csv:1134`, `2025_spring.csv:953`, `import_recent_format_reviewed.csv:535`. |

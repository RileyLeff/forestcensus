# Third review shard 02

Agent: 02
Date: 2026-05-11

Assigned bare tags reviewed: 22.

## Summary

Recommended action counts:

| recommended_action | count |
|---|---:|
| source check | 10 |
| rule candidate | 5 |
| human call | 5 |
| already handled | 1 |
| no change | 1 |

Top recurring patterns:

- Single observed-dead rows bracketed by observed-alive rows remain common. Several look high-confidence enough for a rule-generated row-level mortality decision, but the decision should still preserve the original evidence.
- Isolated DBH outliers often have obvious local context, but the exact correction is not always safe without a source-row check. Many should become source-row scoped DBH suppress/correct decisions rather than tag-level decisions.
- Stable incompatible DBH eras remain distinct from isolated outliers. These should be routed to source/identity review rather than auto-corrected.
- Multi-stem Morella cases are noisy because stem rank is emergent, not persistent stem identity. Stem-level mortality/reappearance flags should be treated as context unless the whole tree state is contradictory.
- Tag-change assertions with `old_tag` evidence are useful, but they still need UUID/link-scoped decisions when DBH histories do not line up cleanly.

## Cases

### Tag 87, L6

- `selection`: bare tag 87; L6/87; UUID `78aaf0998132a4d4`.
- `related_uids`: `78aaf0998132a4d4`.
- `raw_flags`: `I_ZOMBIE_TREE`; invariants `qualifying_rank_gap`, `tag_scope_note_review`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Juniperus virginiana. DBH 65 and observed dead in June 2019/2020, then DBH 65 health 2 alive in June 2021. June 2022 note says "could be one of the new tags"; June 2023 says "unfound"; absent/missing through Oct 2024; alive again April 2025 with DBH 73 health 2 and note "not girdled"; missing again Oct 2025.
- `interpretation`: This is a tag-scope uncertainty case, not a clean mortality/DBH correction. The 2022 note hints the tag may have been confused with a new tag, but the same tag later reappears alive with compatible DBH.
- `recommended_action`: human call.
- `decision_scope`: tag-plot / candidate link search.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: none; keep as review queue pattern for notes mentioning possible new tags.
- `source_rows_to_check`: `2023_and_prior.csv:3914`, `2025_spring.csv:400`.

### Tag 325, M7

- `selection`: bare tag 325; M7/325; UUID `44a802c0761f5a6e`.
- `related_uids`: `44a802c0761f5a6e`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `I_ZOMBIE_TREE`; invariants include `single_survey_dbh_outlier`, `qualifying_rank_gap`, `explicit_note_mortality_correction_candidate`, `single_survey_low_health_death_label_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Juniperus virginiana. DBH 110 in 2019/2020, isolated 150 in June 2021, dead/no DBH in June 2022, then DBH 110 in June 2023 with note "Marked dead last year"; 114/116 in 2024/2025 and alive health 4-6.
- `interpretation`: Two likely issues: June 2021 DBH 150 is an isolated outlier, and the June 2022 dead row is contradicted by later alive evidence plus an explicit note.
- `recommended_action`: rule candidate.
- `decision_scope`: source row DBH field plus mortality/status row.
- `confidence`: high.
- `needs_riley_call`: no for routing, yes only for exact DBH value if correcting rather than suppressing.
- `candidate_auto_rule`: Single death row bracketed by alive evidence with explicit "marked dead last year" note should generate a row-level mortality correction candidate.
- `source_rows_to_check`: `2023_and_prior.csv:1710` for DBH 150; `2023_and_prior.csv:355` for death row; `2023_and_prior.csv:5065` for contradiction note.

### Tag 895, H7

- `selection`: bare tag 895; H7/895; UUID `a0d0a10efd2964e2`.
- `related_uids`: `a0d0a10efd2964e2`.
- `raw_flags`: `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, `qualifying_rank_gap`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Nyssa sylvatica. Healthy/alive from 2019-2022 with DBH 173 -> 164 and health 9/9/9/4. June 2023 is dead health 0 with no DBH. May/Oct 2024 notes mention poison ivy; Oct 2024, Apr 2025, and Oct 2025 are alive with health 4/6/1.
- `interpretation`: The June 2023 death row is probably a field/status error or poison-ivy-related nonmeasurement, not true mortality.
- `recommended_action`: rule candidate.
- `decision_scope`: mortality/status row.
- `confidence`: high.
- `needs_riley_call`: no for routing; optional source check for exact field note.
- `candidate_auto_rule`: Single observed-dead/no-DBH row bracketed by live observations, especially around poison ivy notes, should become a mortality-correction candidate.
- `source_rows_to_check`: `2023_and_prior.csv:4304`, `2024_spring.csv:318`, `2024_fall.csv:1141`.

### Tag 243, H1 and L4

- `selection`: bare tag 243; H1/243 UUID `248e9082ddee6491`; L4/243 UUID `dd4e34803c95b769`.
- `related_uids`: `248e9082ddee6491`, `dd4e34803c95b769`, candidate `dd1faca50fa5290b` for L4/925.
- `raw_flags`: H1 has `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `single_survey_dbh_outlier`; L4 has inferred-dead info rows and a candidate tag-change assertion.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: H1/243 is a live Pinus taeda with DBH 388/388, isolated 76 in June 2021, then 374-386 afterward. L4/243 is a dead Pinus taeda with DBH 332 in 2019/2020 and dead/no DBH afterward. Candidate link says L4/243 may relate to L4/925, but L4/925 is dead with later DBH about 90, not 332.
- `interpretation`: H1/243 has a high-confidence DBH data error. The L4/243 -> L4/925 link is not a clean whole-tree identity link because the DBH profiles are incompatible.
- `recommended_action`: source check.
- `decision_scope`: source row DBH field for H1; candidate link for L4.
- `confidence`: high for H1 DBH error; low for L4 link.
- `needs_riley_call`: yes for L4 link; probably no for suppressing H1 DBH 76 if source check cannot resolve.
- `candidate_auto_rule`: Isolated DBH value less than one quarter of adjacent large-pine measurements should be routed to row-scoped source check/suppression.
- `source_rows_to_check`: H1 `2023_and_prior.csv:2204`; L4 `candidate_links.csv` link `link_e80c6b32f50cdbb2`; L4/925 rows `2023_and_prior.csv:4569`, `2025_spring.csv:282`.

### Tag 904, M5

- `selection`: bare tag 904; M5/904; UUID `23a371da2025d5d9`.
- `related_uids`: `23a371da2025d5d9`, candidate old tag UUID `fccfe1583a7146ea` for M5/2470.
- `raw_flags`: inferred-dead info rows; candidate identity link.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: M5/904 first appears June 2023 as dead Pinus taeda with `old_tag_raw=2470`; later rows are inferred dead / did-not-find, with May 2024 note "confirmed kill". M5/2470 is a dead Pinus taeda DBH 303 in 2019/2020, dead/no DBH through 2022, missing in Oct 2024.
- `interpretation`: The old-tag field strongly suggests M5/904 is a retag/view of the M5/2470 dead tree, but because the 904 side has no DBH profile, this should be an explicit identity-link decision rather than an automatic merge.
- `recommended_action`: human call.
- `decision_scope`: candidate link / UUID alias.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Old-tag assertions on dead trees should enter the human identity-link queue even when DBH comparison is unavailable.
- `source_rows_to_check`: `2023_and_prior.csv:4996`; M5/2470 `2023_and_prior.csv:859`, `2023_and_prior.csv:880`.

### Tag 2451, M4

- `selection`: bare tag 2451; M4/2451; UUID `0e89b0eeb1853b55`.
- `related_uids`: `0e89b0eeb1853b55`.
- `raw_flags`: `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `single_survey_death_label_outlier`, `health_rebound_new_stem_context`, `qualifying_rank_gap`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Large live Pinus taeda. DBH 398/398/391 with health 10/10/8, then June 2022 dead health 0/no DBH, then alive again with DBH 389-395 and health 5-8 through Oct 2025.
- `interpretation`: June 2022 death is a classic single-row false mortality label.
- `recommended_action`: rule candidate.
- `decision_scope`: mortality/status row.
- `confidence`: high.
- `needs_riley_call`: no for routing.
- `candidate_auto_rule`: Healthy live tree -> one dead/no-DBH row -> healthy live tree should generate row-level mortality correction candidate.
- `source_rows_to_check`: `2023_and_prior.csv:929`.

### Tag 5188, M3

- `selection`: bare tag 5188; M3/5188; UUID `e02f2a4270fb0245`.
- `related_uids`: `e02f2a4270fb0245`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`; invariants `single_survey_dbh_outlier`, `new_persistent_large_stem`, `persistent_dbh_regime_shift`, `health_rebound_alive_context`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Morella cerifera. Main stem DBH 134, 160, 164, isolated 104 in May 2024, then 157/162. April 2025 adds stems 72 and 56. Oct 2025 has three stems with health but no DBH.
- `interpretation`: May 2024 DBH 104 is likely a row-level DBH error. The 72 mm new stem probably should receive retrospective blank/ghost stem rows; the 56 mm stem is near-threshold and could be legitimate new qualification.
- `recommended_action`: source check.
- `decision_scope`: DBH field plus stem profile.
- `confidence`: medium.
- `needs_riley_call`: yes for whether to add ghost blanks for new stems.
- `candidate_auto_rule`: New persistent stem first appearing above 60 mm should route to ghost-blank decision candidate; 50-60 mm should be lower priority/context.
- `source_rows_to_check`: `2024_spring.csv:1236`; `2025_spring.csv:1255`, `2025_spring.csv:1256`.

### Tag 170, L0

- `selection`: bare tag 170; L0/170; UUID `44352bab9d156f29`.
- `related_uids`: `44352bab9d156f29`.
- `raw_flags`: raw `W_ALIVE_HEALTH_CONFLICT`, `I_ZOMBIE_TREE`; invariants include `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, `qualifying_rank_gap`.
- `configured_decisions_applied`: `row_correction:0010` `set_status` on Oct 2024 L0/170.
- `current_flags`: `I_ZOMBIE_TREE`, `I_CORRECTED_ROW`; invariants still include `mortality_contradiction`, `single_survey_death_label_outlier`, `qualifying_rank_gap`.
- `evidence_summary`: Nyssa sylvatica. Alive DBH 73 in 2019/2020; missing 2021; dead 2022; rediscovered alive June 2023 health 1; dead from May/Oct 2024 onward. Existing decision trusts health 0 over alive=true for Oct 2024.
- `interpretation`: This case already embodies a prior Riley call: keep the June 2023 low-health alive rediscovery and treat later health 0 as dead. Remaining flags are expected diagnostic noise after a legitimate complicated history.
- `recommended_action`: already handled.
- `decision_scope`: mortality/status already row-scoped.
- `confidence`: high.
- `needs_riley_call`: no.
- `candidate_auto_rule`: Diagnostics should be able to suppress/soften mortality contradiction when an accepted configured decision explicitly documents the intended interpretation.
- `source_rows_to_check`: existing decision selector `2024_fall.csv:22`.

### Tag 816, M0

- `selection`: bare tag 816; M0/816; UUID `a2f8576ead9c0bb0`.
- `related_uids`: `a2f8576ead9c0bb0`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`, `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `dead_tree_dbh_increase`, `single_survey_dbh_outlier`, `dead_tree_dbh_gap`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Dead Pinus taeda DBH 110 in 2019/2020, dead/no DBH through 2023, DBH 99 in May 2024, isolated 196 in Oct 2024, DBH 97 in Apr 2025, then Oct 2025 health 6 interpreted alive with no DBH.
- `interpretation`: Two likely row-level errors: Oct 2024 DBH 196 should probably be 96 or suppressed, and Oct 2025 health/status is probably wrong for a consistently dead tree.
- `recommended_action`: source check.
- `decision_scope`: DBH field plus mortality/status row.
- `confidence`: high.
- `needs_riley_call`: yes for exact Oct 2025 interpretation.
- `candidate_auto_rule`: Dead-tree DBH increases that are isolated between similar lower measurements should route to source check/correction; dead trees can lose DBH, but isolated large increases are suspicious.
- `source_rows_to_check`: `2024_fall.csv:536`; `import_recent_format_reviewed.csv:588`.

### Tag 239, H1 and L2

- `selection`: bare tag 239; H1/239 UUID `6ad63a869c4f1c5e`; L2/239 UUID `873d7a82188b5efd`.
- `related_uids`: `6ad63a869c4f1c5e`, `873d7a82188b5efd`.
- `raw_flags`: H1 has `stable_incompatible_dbh_era`; L2 has `mortality_contradiction`, `single_survey_low_health_death_label_outlier`, and measurement-note DBH context.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: H1/239 is Pinus taeda DBH 109/109 in 2019/2020, then stable 343-355 afterward. L2/239 is Nyssa sylvatica DBH 130-136, a June 2023 estimated DBH 110 due to poison ivy, alive low health in 2024/2025, dead Oct 2024, alive Apr 2025, dead Oct 2025.
- `interpretation`: H1 is a stable incompatible era or possible tag/source alignment problem, not an isolated typo. L2 is a low-health Nyssa with poison ivy measurement noise and mortality ambiguity.
- `recommended_action`: human call.
- `decision_scope`: source-era/identity review for H1; mortality/status row for L2.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Stable era shifts should not auto-fix; poison-ivy estimated DBH should be routed as context, not necessarily a correction.
- `source_rows_to_check`: H1 `2023_and_prior.csv:3569`, `2023_and_prior.csv:1985`; L2 `2023_and_prior.csv:4471`, `2024_fall.csv:170`, `2025_spring.csv:170`.

### Tag 615, L4

- `selection`: bare tag 615; L4/615; UUID `3bc73642d8aabce6`.
- `related_uids`: `3bc73642d8aabce6`.
- `raw_flags`: `W_BELOW_THRESHOLD_DBH`, `W_DBH_JUMP`, stem count/large stem appearance/disappearance flags; invariants `source_note_dbh_conflict`, `subthreshold_dbh_present`, `threshold_multistem_gap_context`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Morella cerifera. Single stem 62 in May 2024; two stems 74/51 in Oct 2024; two stems 64/53 in Apr 2025; Oct 2025 stems 73 and 42, with note `?` on the 42 mm row.
- `interpretation`: Stem 2 previously qualified but Oct 2025 has a subthreshold uncertain DBH. This should likely preserve alive health evidence while suppressing or source-checking the 42 mm DBH.
- `recommended_action`: source check.
- `decision_scope`: DBH field / stem profile.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Subthreshold DBH with explicit uncertainty note on a previously qualifying stem should route to DBH suppression candidate, not tree exclusion.
- `source_rows_to_check`: `import_recent_format_reviewed.csv:1198`.

### Tag 252, H1

- `selection`: bare tag 252; H1/252; UUID `7ef844bdff8dde3c`.
- `related_uids`: `7ef844bdff8dde3c`.
- `raw_flags`: `I_ZOMBIE_TREE`; invariants `mortality_contradiction`, `single_survey_low_health_death_label_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Pinus taeda. DBH 303/303 alive health 10, then 288 health 1 alive in June 2021, one dead health 0 row in June 2022, alive again June 2023 health 6, then truly dead from Oct 2024 onward with decaying DBH 272 -> 267 -> 265.
- `interpretation`: June 2022 is likely a false death row. Later dead DBH loss looks biologically plausible and should be preserved.
- `recommended_action`: rule candidate.
- `decision_scope`: mortality/status row.
- `confidence`: high.
- `needs_riley_call`: no for routing.
- `candidate_auto_rule`: Single dead row bracketed by alive rows should be a row-scoped mortality correction even if the same tree dies later.
- `source_rows_to_check`: `2023_and_prior.csv:975`.

### Tag 5039, L7

- `selection`: bare tag 5039; L7/5039; UUID `07ebde232f373e6b`.
- `related_uids`: `07ebde232f373e6b`.
- `raw_flags`: `W_TREE_STEM_COUNT_CHANGE`, `W_TREE_LARGE_STEM_APPEARANCE`; invariant `new_persistent_large_stem`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: One small unidentified tree DBH 64-75 from 2022-2025. Oct 2024 note says "species change" and taxon is Juniperus virginiana. Oct 2025 has two rows for same tag: one Juniperus row DBH 76 with missing status, and one unidentified row DBH 73 health 3 standing alive.
- `interpretation`: This looks like duplicate/split taxon reporting for one physical stem, not a new second stem. It also needs a taxon call.
- `recommended_action`: human call.
- `decision_scope`: taxon plus stem profile / duplicate row.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Same tag/survey with two same-sized stems and incompatible taxon labels should be routed as duplicate/taxon conflict before being treated as a new persistent large stem.
- `source_rows_to_check`: `2024_fall.csv:482`; `import_recent_format_reviewed.csv:1408`, `import_recent_format_reviewed.csv:1409`.

### Tag 198, L2

- `selection`: bare tag 198; L2/198; UUID `260e7ea089b64933`.
- `related_uids`: `260e7ea089b64933`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `dead_tree_dbh_increase`, `single_survey_dbh_outlier`, `dead_tree_dbh_gap`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Dead Pinus taeda. DBH 280 in 2019/2020, dead/no DBH through 2023, DBH 203 in May 2024, 258 in Oct 2024, 264 in Apr 2025, dead/no DBH Oct 2025.
- `interpretation`: Dead-tree DBH decrease is plausible, but 203 is an isolated low outlier relative to 258/264 and earlier 280. Could be a bad measurement or missing leading digit.
- `recommended_action`: source check.
- `decision_scope`: DBH field.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Dead-tree DBH decreases should not be automatically flagged as errors, but isolated dead-tree outliers bracketed by similar later values still need source check.
- `source_rows_to_check`: `2024_spring.csv:525`.

### Tag 487, M5

- `selection`: bare tag 487; M5/487; UUID `da734e478e249c7a`.
- `related_uids`: `da734e478e249c7a`.
- `raw_flags`: stem count/disappearance flags plus `I_ZOMBIE_TREE`; invariants `stem_mortality_context`, `mortality_contradiction`, `single_survey_death_label_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Morella cerifera. Oct 2024 has three stems 77 alive, 72 dead, 60 alive. Apr 2025 stem 1 is 80 dead and stems 2/3 are DNF. Oct 2025 has three standing live stems with health 8/8/5 and no DBH.
- `interpretation`: This is a multi-stem status/scoping problem. Because stem rank is by DBH and not persistent identity, the apparent zombie/death pattern may be partly rank/scoping noise, but Apr 2025 stem 1 death is still suspicious.
- `recommended_action`: human call.
- `decision_scope`: stem profile / mortality/status row.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Multi-stem mortality contradictions should be reviewed at tree/survey profile level, not by assuming stem rank identity persists.
- `source_rows_to_check`: `2025_spring.csv:1296`, `2025_spring.csv:1297`, `2025_spring.csv:1298`; Oct 2025 rows `796-798`.

### Tag 704, L5

- `selection`: bare tag 704; L5/704; UUID `b312512fb6873550`.
- `related_uids`: `b312512fb6873550`.
- `raw_flags`: DBH/ranked DBH/stem count flags; invariants `stem_mortality_context`, `single_survey_dbh_outlier`, `bounded_stem_rank_gap`, `morella_cluster_rank_jump_context`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Morella cerifera multi-stem cluster. May 2024 profile is 90 dead, 80 dead, 60 alive. Oct 2024 profile is 95 dead, 61 alive, 51 dead. Apr 2025 has one live 60 and two dead rows without DBH. Oct 2025 is 96/81/59 all health 0/dead.
- `interpretation`: This looks like legitimate messy multi-stem decline with rank reshuffling and partial measurements, not a clear typo. Tree-level mortality by Oct 2025 is coherent.
- `recommended_action`: no change.
- `decision_scope`: none; diagnostic tuning.
- `confidence`: medium.
- `needs_riley_call`: no.
- `candidate_auto_rule`: Treat Morella multi-stem rank churn as context unless whole-tree state or duplicate same-survey rows are contradictory.
- `source_rows_to_check`: none unless Riley wants to audit the cluster manually.

### Tag 137, H4

- `selection`: bare tag 137; H4/137; UUID `f732716c15fa11dd`.
- `related_uids`: `f732716c15fa11dd`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `stable_incompatible_dbh_era`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Pinus taeda. DBH 197/197 in 2019/2020, then stable 289-300 from 2021 onward. Health is alive throughout, with early notes "small canopy" and "thin canopy".
- `interpretation`: Stable incompatible DBH eras; not safe to infer a single row typo. Could be old source/tag alignment problem or measurement protocol issue.
- `recommended_action`: source check.
- `decision_scope`: source-era / identity alignment.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Stable incompatible eras should remain human/source review, not auto correction.
- `source_rows_to_check`: `2023_and_prior.csv:2770`, `2023_and_prior.csv:2824`, `2023_and_prior.csv:1324`.

### Tag 155, H3

- `selection`: bare tag 155; H3/155; UUID `73ba86b1c0856edf`.
- `related_uids`: `73ba86b1c0856edf`.
- `raw_flags`: multiple `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `single_survey_dbh_outlier`, `stable_incompatible_dbh_era`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Nyssa sylvatica. DBH 280/280 in 2019/2020, then 209/211/217 in 2021-2023, isolated 270 in May 2024, then 214/218 afterward. Alive throughout.
- `interpretation`: Two phenomena may overlap: old stable era at 280 and a later isolated May 2024 reversion/outlier. This needs source review before deciding whether to suppress only May 2024, old rows, or neither.
- `recommended_action`: source check.
- `decision_scope`: source-era plus DBH field.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Later one-survey reversion toward an old incompatible era should be flagged separately from the era shift.
- `source_rows_to_check`: `2023_and_prior.csv:3337`, `2023_and_prior.csv:3351`, `2024_spring.csv:204`.

### Tag 2453, M4

- `selection`: bare tag 2453; M4/2453; UUID `dde3c6fa34675fb0`.
- `related_uids`: `dde3c6fa34675fb0`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `single_survey_dbh_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Very large Pinus taeda. DBH 537/537 in 2019/2020, isolated 428 in June 2021, then 520-527 afterward. Pine over 500 mm is plausible in this dataset.
- `interpretation`: June 2021 428 is almost certainly a row-level DBH typo or source transcription error, likely intended to be around 528.
- `recommended_action`: rule candidate.
- `decision_scope`: DBH field.
- `confidence`: high.
- `needs_riley_call`: no if suppressing; yes if choosing corrected value.
- `candidate_auto_rule`: Large pine with one isolated DBH about 100 mm below both neighbors should generate a source-check/correction candidate.
- `source_rows_to_check`: `2023_and_prior.csv:2893`.

### Tag 397, M6

- `selection`: bare tag 397; M6/397; UUID `a6351a195fb61f27`.
- `related_uids`: `a6351a195fb61f27`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `stable_incompatible_dbh_era`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Pinus taeda. DBH 270/270 in 2019/2020, then stable 202-208 from 2021 through 2025. Alive but low health after 2021.
- `interpretation`: Stable incompatible DBH eras. Not an isolated outlier; could be tag/source alignment or measurement problem.
- `recommended_action`: source check.
- `decision_scope`: source-era / identity alignment.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Same as other stable-era cases: route to human/source, not auto DBH suppression.
- `source_rows_to_check`: `2023_and_prior.csv:2874`, `2023_and_prior.csv:2891`, `2023_and_prior.csv:1333`.

### Tag 5236, R4

- `selection`: bare tag 5236; R4/5236; UUID `e5baec2a2242f5d6`.
- `related_uids`: `e5baec2a2242f5d6`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariant `single_survey_dbh_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Nyssa sylvatica. DBH 94/93 in 2023/May 2024, isolated 58 in Oct 2024, then 94/93 in 2025. Alive throughout.
- `interpretation`: Oct 2024 DBH 58 is a high-confidence isolated outlier; exact intended value is unclear without source check.
- `recommended_action`: source check.
- `decision_scope`: DBH field.
- `confidence`: high.
- `needs_riley_call`: yes if correcting, no if suppressing.
- `candidate_auto_rule`: Isolated low DBH bracketed by stable same-size values should become source-check/suppress candidate.
- `source_rows_to_check`: `2024_fall.csv:1334`.

### Tag 83, L6

- `selection`: bare tag 83; L6/83; UUID `b994769c4c59516c`.
- `related_uids`: `b994769c4c59516c`.
- `raw_flags`: `W_DBH_JUMP`, `W_TREE_RANKED_DBH_JUMP`; invariants `max_dbh_jump`, `ranked_dbh_jump`, `single_survey_dbh_outlier`.
- `configured_decisions_applied`: none matched.
- `current_flags`: same as raw.
- `evidence_summary`: Juniperus virginiana. DBH 98.5/98.5 in 2019/2020, then 201 in 2021, isolated 281 in 2022, then 206/200 in 2023/2024, dead/fallen by April 2025.
- `interpretation`: The 2022 DBH 281 is a high-confidence isolated outlier relative to the 200-ish modern era. The early 98.5 era remains a separate source/identity issue.
- `recommended_action`: source check.
- `decision_scope`: DBH field plus source-era review.
- `confidence`: medium.
- `needs_riley_call`: yes.
- `candidate_auto_rule`: Separate single-survey outlier handling from broader stable-era shift handling; do not let one mask the other.
- `source_rows_to_check`: `2023_and_prior.csv:1737`; early rows `2023_and_prior.csv:2293`, `2023_and_prior.csv:2284`.

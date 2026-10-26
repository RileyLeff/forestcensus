# Third review shard 01

Agent: 01  
Date: 2026-05-11  
Scope: current flagged bare tags assigned to shard 01. Investigation only; no config/source/output edits.

## Summary counts

| recommended_action | count |
|---|---:|
| rule candidate | 9 |
| source check | 9 |
| human call | 3 |
| already handled | 1 |

## Recurring patterns

- Single-survey death labels remain the biggest rule candidate: L7/5032, L7/14, M5/2500, L0/477, L1/131, and M0/514 all have one observed-dead/health-0 row bracketed by observed-alive evidence.
- Stable incompatible DBH eras are still source-era/tag-alignment cases rather than biological growth: H4/L1 tag 145, H4/152, H1/241, M6/363, and L6/77.
- Explicit tag-change assertions with dead/nonqualifying targets may be safe to accept by rule only when taxon/status evidence is otherwise boring: L0/157 looks like the cleanest example; M0/813 is not clean because the target later changes Ilex/Juniperus.
- Dead-tree DBH loss is acceptable, but dead-tree DBH increase or isolated rebound remains source-check territory: L5/418 is a high-confidence isolated DBH strike candidate; L7/6 needs field/source review because the later dead DBHs are much larger than the old dead profile.
- Multi-stem dead-tree/stem-rank gaps should not be overcorrected. L2/227 already has a configured taxon decision; remaining stem-profile warnings are mostly blank-gap/dead-stem context.

## Cases

### L7/5029

| Field | Notes |
|---|---|
| `selection` | `L7/5029`, UUID `6dee2ac0a2e04a36`; linked target `L7/982`. |
| `related_uids` | `6dee2ac0a2e04a36`; candidate target `b3105e264931fae3`. |
| `raw_flags` | `I_ZOMBIE_TREE`; `mortality_contradiction`; `single_survey_low_health_death_label_outlier` for June 2022 and April 2025; qualifying rank gaps. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw: candidate identity link plus mortality contradictions. |
| `evidence_summary` | `5029` is Juniperus: June 2021 alive health 2 DBH 103; June 2022 dead/0 no DBH; May 2024 alive health 1 DBH 103; October 2024 missing; April 2025 dead/0; October 2025 alive health 1 DBH 101. Explicit tag-change assertion says `L7_5029_Jun -> L7_982_Jun`; target `982` is dead/nonqualifying with May 2024 note `fell`. |
| `interpretation` | This is both a mortality problem and a link problem. The source identity has repeated low-health alive/dead oscillation, so accepting the tag link before resolving mortality would hide the real issue. |
| `recommended_action` | human call |
| `decision_scope` | candidate link plus mortality/status rows for `L7/5029`; possibly source rows rather than bare tag. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Low-health single-survey death labels can become a rule candidate, but not this whole case because it also has an explicit tag link. |
| `source_rows_to_check` | `2023_and_prior.csv:1297`, `2023_and_prior.csv:312`, `2024_spring.csv:1068`, `2025_spring.csv:499`, `import_recent_format_reviewed.csv:1396`, tag-change row 21. |

### M7/5274

| Field | Notes |
|---|---|
| `selection` | `M7/5274`, UUID `c1be5f38c67214f8`. |
| `related_uids` | `c1be5f38c67214f8`; note mentions new tag `795`, but no canonical `M7/795` case was found in the current history. |
| `raw_flags` | October 2025 DBH jump, stem count change, large stem disappearance, ranked DBH jump, and `tag_scope_note_review`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | April 2025 has Morella stems 120/health 2 and 55/health 3, notes `new` and `tag on trunk 2`. October 2025 has 54/health 9 with note `new tag 795` plus a dead/0 row. |
| `interpretation` | This looks like tag/stem-scope ambiguity, not simple DBH shrinkage. October 2025 may have recorded the smaller/new tagged stem while the earlier 120 mm stem became unreported or dead. |
| `recommended_action` | human call |
| `decision_scope` | tag-plot/stem profile, possibly split or alias around `M7/5274` and tag `795`. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | none; notes with `tag on trunk`/`new tag` should stay human-review. |
| `source_rows_to_check` | `2025_spring.csv:1397`, `2025_spring.csv:1398`, `import_recent_format_reviewed.csv:918`, `import_recent_format_reviewed.csv:919`. |

### H5/559

| Field | Notes |
|---|---|
| `selection` | `H5/559`, UUID `82d1defd5af0e96d`; linked target `H5/912`. |
| `related_uids` | `82d1defd5af0e96d`, `c19ccaed81425011`. |
| `raw_flags` | Stem count change and large stem disappearance from 405/217 to one dead 405; inferred-dead rows later; dead-tree stem context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw; candidate link remains `needs_human` because DBH profiles differ too much. |
| `evidence_summary` | `559` is Acer. June 2019 has two trunks: 405 dead and 217 alive/blank-health. June 2020 onward is dead 405 or dead/no DBH. Explicit tag-change says `H5_559_Ace -> H5_912_Ace`; `912` is dead/no DBH in 2023-2024, then dead DBH 198 in October 2024 and 184 in October 2025. |
| `interpretation` | The link may refer to the smaller 217 mm stem rather than the whole old multi-stem identity. A bare UUID merge would likely garble stem history. |
| `recommended_action` | human call |
| `decision_scope` | candidate link and possibly stem-level/source-row split. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Explicit tag-change links should not auto-merge when source has multi-stem evidence and large DBH mismatch. |
| `source_rows_to_check` | `2023_and_prior.csv:15`, `2023_and_prior.csv:3883`, `2023_and_prior.csv:2`, target rows `2023_and_prior.csv:4247`, `2024_fall.csv:1082`, `import_recent_format_reviewed.csv:487`, tag-change row 3. |

### L0/157

| Field | Notes |
|---|---|
| `selection` | `L0/157`, UUID `c6236b0d598c05c5`; linked target `L0/922`. |
| `related_uids` | `c6236b0d598c05c5`, `6bb4dc5788760204`. |
| `raw_flags` | Only inferred-dead context on source; candidate link because target has no comparable DBH. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Source `157` is dead Pinus DBH 299 in 2019-2020, then dead/no DBH. Target `922` is dead Pinus/no DBH from 2023-2025, with April 2025 note `fallen`; old-tag evidence points back to `157`. |
| `interpretation` | Clean dead-tree retag/backfill. The lack of target DBH makes numeric confirmation impossible, but taxon/status/note evidence are consistent. |
| `recommended_action` | rule candidate |
| `decision_scope` | candidate link / identity alias window. |
| `confidence` | medium |
| `needs_riley_call` | no, unless all explicit dead-only links require human approval. |
| `candidate_auto_rule` | Accept explicit old-tag links where both endpoints are same taxon, dead/nonqualifying, and no contradictions. |
| `source_rows_to_check` | `2023_and_prior.csv:692`, `2023_and_prior.csv:686`, `2023_and_prior.csv:1001`, target `2023_and_prior.csv:4364`, `2025_spring.csv:52`, tag-change row 6. |

### M0/813

| Field | Notes |
|---|---|
| `selection` | `M0/813`, UUID `dea7dfb53eb55aed`; linked target `M0/909`. |
| `related_uids` | `dea7dfb53eb55aed`, `085312e055354ca3`. |
| `raw_flags` | Source has inferred-dead context; candidate link. Target is nonqualifying and has taxon drift in evidence. |
| `configured_decisions_applied` | none matched to `M0/813`. |
| `current_flags` | Same as raw for source; target remains nonqualifying. |
| `evidence_summary` | Source `813` is dead Ilex DBH 57 in 2019-2020, then dead/no DBH. Target `909` has old-tag `813`, dead/no DBH in 2023, subthreshold DBHs 33/35 in 2024, and later evidence says Juniperus, including October 2024 `species change` and October 2025 `M0_909_Jun`. |
| `interpretation` | The explicit tag link is plausible, but target taxon drift makes this less clean than L0/157. It may need a taxon decision on `909` before link acceptance. |
| `recommended_action` | source check |
| `decision_scope` | candidate link plus target taxon/source rows. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Dead-only explicit-link rule should exclude targets with unresolved taxon changes. |
| `source_rows_to_check` | `2023_and_prior.csv:19`, `2023_and_prior.csv:20`, target `2023_and_prior.csv:4811`, `2024_spring.csv:1299`, `2024_fall.csv:549`, `import_recent_format_reviewed.csv:604`, tag-change row 22. |

### L2/238

| Field | Notes |
|---|---|
| `selection` | `L2/238`, UUID `4e92c23dac58163d`. |
| `related_uids` | `4e92c23dac58163d`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `health_rebound_new_stem_context`, qualifying rank gap. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus 107/0 in 2019-2020; dead/no DBH in 2021; one alive row in June 2022 with DBH 121 health 6 note `tilted`; dead/no DBH from 2023 through October 2025, with poison ivy notes in 2024-2025. |
| `interpretation` | June 2022 is the only alive/healthy row in an otherwise dead sequence. Could be wrong row/tag or marginal refinding, but it is not a generic auto-fix because the DBH is plausible. |
| `recommended_action` | source check |
| `decision_scope` | source row / mortality-status row for June 2022. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Isolated healthy alive row inside long-dead sequence should be flagged for source check, not auto-corrected. |
| `source_rows_to_check` | `2023_and_prior.csv:1922` primarily; surrounding rows `109`, `78`, `177`, `4470`, `2024_spring.csv:563`, `2024_fall.csv:169`, `2025_spring.csv:169`. |

### L7/5032

| Field | Notes |
|---|---|
| `selection` | `L7/5032`, UUID `492bcdd017bb3e15`. |
| `related_uids` | `492bcdd017bb3e15`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, qualifying rank gap, `single_survey_death_label_outlier` for June 2022. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus alive DBH 110 health 9 in June 2021; June 2022 dead/0 no DBH; alive again from June 2023 onward with DBH 105-115 and health 4-7. |
| `interpretation` | Classic one-survey death-label artifact. June 2022 should likely become uncertain/missing rather than dead. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status source row, June 2022. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | High-health alive -> one dead/0 row -> later alive should generate a decision to reinterpret the dead row as uncertain/missing. |
| `source_rows_to_check` | `2023_and_prior.csv:311`; surrounding rows `2592`, `4738`, `2024_spring.csv:1070`, `2024_fall.csv:475`, `2025_spring.csv:487`, `import_recent_format_reviewed.csv:1399`. |

### Tag 145, H4 and L1

| Field | Notes |
|---|---|
| `selection` | Bare tag `145` appears in `L1/145` UUID `032e95549ca8af99` and `H4/145` UUID `2d30cfbc84fa2ddb`. |
| `related_uids` | `032e95549ca8af99`, `2d30cfbc84fa2ddb`. |
| `raw_flags` | `stable_incompatible_dbh_era`, DBH/ranked DBH jumps, plus L1 qualifying rank gap. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | `L1/145` Juniperus is 161.5 in 2019-2020, missing in 2021, then stable 284-300 from 2022-2025. `H4/145` Liquidambar is 372 in 2019-2020, then stable around 97-110 from 2021 onward. |
| `interpretation` | Two independent source-era DBH regime shifts under the same bare tag. H4 fits the known H4 early-year alignment block; L1 also looks like early values belong to a different measurement/tag regime. |
| `recommended_action` | source check |
| `decision_scope` | UUID-level DBH/source-era rows, not bare tag. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Stable incompatible eras should generate a source-era review queue, not direct correction, unless a known block decision is approved. |
| `source_rows_to_check` | L1 `2023_and_prior.csv:3122`, `3066`, `2356`; H4 `2023_and_prior.csv:3255`, `3259`, `3269`, `3272`, `4205`. |

### L7/14

| Field | Notes |
|---|---|
| `selection` | `L7/14`, UUID `850e7af2c70a35bc`. |
| `related_uids` | `850e7af2c70a35bc`. |
| `raw_flags` | DBH/ranked jumps near threshold, `I_ZOMBIE_TREE`, mortality contradiction, `single_survey_death_label_outlier`, and dead-tree threshold context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Small Juniperus alive 54/53 health 8 in 2019-2020; June 2021 dead/0 DBH 72; alive again 2022-2025 with DBH 58-86 and health 3-9. |
| `interpretation` | June 2021 death label is likely wrong. DBH noise is real but threshold/small-tree measurement variability, not a separate urgent correction. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status source row for June 2021; DBH remains context/watch. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Bracketed one-survey dead/0 rows should be reinterpreted as uncertain/missing; threshold DBH noise should be downgraded. |
| `source_rows_to_check` | `2023_and_prior.csv:219`; surrounding rows `2294`, `2280`, `1534`, `4706`, `2024_spring.csv:493`, `2024_fall.csv:441`, `2025_spring.csv:452`, `import_recent_format_reviewed.csv:1366`. |

### L2/227

| Field | Notes |
|---|---|
| `selection` | `L2/227`, UUID `cdc83033eed0df16`. |
| `related_uids` | `cdc83033eed0df16`. |
| `raw_flags` | Raw taxon conflict, stem count change, large stem disappearance, inferred-dead rows, observed mortality event, blank missing stem backfill, new persistent large stem, qualifying rank gap. |
| `configured_decisions_applied` | `taxon_override:0006` sets the tree to Nyssa sylvatica, treating one June 2020 Pinus row as a label slip. |
| `current_flags` | Taxon conflict is resolved; remaining warnings are stem-profile/dead-tree blank-gap context. |
| `evidence_summary` | Multi-stem Nyssa: 2019-2020 live two-stem profile 114/104; dead/no DBH from 2021 onward; April 2025 has one dead measured stem DBH 112 and another dead/fallen/no DBH row. |
| `interpretation` | Existing decision correctly resolves taxon. Remaining stem warnings should not block canonicalization; insert/preserve blank stem gaps if the canonical output needs complete rank-profile rows. |
| `recommended_action` | already handled |
| `decision_scope` | stem profile / blank rank gaps only, if needed. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Dead multi-stem trees with prior two-stem profiles and later one measured dead stem should route to blank-gap context, not urgent review. |
| `source_rows_to_check` | Existing decision cites all rows via taxon override; key rows `2023_and_prior.csv:2150`, `3413`, `2148`, `3648`, `2025_spring.csv:157`, `2025_spring.csv:158`. |

### M0/581

| Field | Notes |
|---|---|
| `selection` | `M0/581`, UUID `bccda220420e35d2`. |
| `related_uids` | `bccda220420e35d2`. |
| `raw_flags` | Subthreshold DBHs 40-44, DBH jump across threshold, `I_ZOMBIE_TREE`, explicit note mortality correction candidate from `not dead`, threshold-edge context. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 52 dead/0 in 2019-2020, then live subthreshold 40-44 with health 2-7 from 2021 onward. June 2021 note says `not dead`. October 2025 is alive health 1 with no DBH. |
| `interpretation` | Early dead labels are likely wrong/uncertain; later DBHs should not qualify because they are below 50 mm. This is a policy/rule case more than a one-off. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status rows for 2019-2020 plus DBH field suppression for subthreshold values. |
| `confidence` | medium |
| `needs_riley_call` | no, assuming the subthreshold policy is already settled. |
| `candidate_auto_rule` | `not dead` notes after early dead labels should generate mortality reinterpretation; repeated subthreshold DBHs should be excluded from qualifying profiles. |
| `source_rows_to_check` | `2023_and_prior.csv:418`, `422`, `1957`, `1402`, `4774`, `2024_fall.csv:513`, `2025_spring.csv:515`, `import_recent_format_reviewed.csv:567`. |

### M5/2500

| Field | Notes |
|---|---|
| `selection` | `M5/2500`, UUIDs `e33791bb212a17a2` and orphan `260e8b000a83286f`. |
| `related_uids` | `e33791bb212a17a2`, `260e8b000a83286f`. |
| `raw_flags` | Before decisions: taxon conflict, large stem disappearance, stem-count change, DBH regime shift, mortality contradiction. |
| `configured_decisions_applied` | `identity_split:0005` moves the 2019 live Pinus row into `orphan_2500_pinus_2019`. |
| `current_flags` | Split resolved taxon/stem/DBH chaos. Remaining Nyssa case has low-health single-survey death label in October 2024 plus later October 2025 dead/0. |
| `evidence_summary` | Orphan Pinus row: June 2019 DBH 287 health 7 note `bare branches`. Main Nyssa: 154/154 in 2019-2020, then 145, 130, 141, October 2024 dead/0 DBH 143, April 2025 alive health 3 DBH 145, October 2025 dead/0. |
| `interpretation` | Existing split is doing the right thing. October 2024 is likely a bracketed low-health death-label artifact; October 2025 may be a real later death and should remain separate. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status row for October 2024 on UUID `e33791bb212a17a2`; keep orphan split. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Low-health alive -> single dead/0 -> low-health alive should be reinterpreted as uncertain/missing, even when a later real death occurs. |
| `source_rows_to_check` | Split row `2023_and_prior.csv:2224`; main rows `2697`, `2715`, `2404`, `1964`, `4991`, `2024_spring.csv:1208`, `2024_fall.csv:765`, `2025_spring.csv:1289`, `import_recent_format_reviewed.csv:824`. |

### L0/477

| Field | Notes |
|---|---|
| `selection` | `L0/477`, UUID `3b13289cbd58419a`. |
| `related_uids` | `3b13289cbd58419a`. |
| `raw_flags` | `I_ZOMBIE_TREE`, `mortality_contradiction`, `single_survey_low_health_death_label_outlier`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa alive from 2021-2024 with declining health 3 -> 1 and DBH around 101-106. April 2025 dead/0 DBH 100 with note `P.I.`. October 2025 alive health 1. |
| `interpretation` | April 2025 is likely a poison-ivy/low-health single-survey death-label artifact. Preserve low health and notes; do not infer true death. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status source row for April 2025. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Low-health alive rows with one poison-ivy dead/0 row followed by alive should become uncertain/missing or alive-low-health, not dead. |
| `source_rows_to_check` | `2025_spring.csv:47`; surrounding rows `2023_and_prior.csv:1395`, `1321`, `4358`, `2024_spring.csv:49`, `2024_fall.csv:49`, `import_recent_format_reviewed.csv:973`. |

### L0/181

| Field | Notes |
|---|---|
| `selection` | `L0/181`, UUID `a9580e0e6f43638e`. |
| `related_uids` | `a9580e0e6f43638e`. |
| `raw_flags` | `I_ZOMBIE_TREE`, dead-tree DBH gap, mortality contradiction, sharp health rebound in October 2024. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Long-dead Juniperus: dead/0 from 2019-2023, dead DBH 64 in May 2024, October 2024 alive health 5 DBH 64, then April/October 2025 dead/0. |
| `interpretation` | October 2024 alive health 5 is the only revival and is probably a status/health error or source-row confusion. DBH continuity itself is not the problem. |
| `recommended_action` | source check |
| `decision_scope` | October 2024 mortality/status row. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Isolated mid/high-health alive row inside a long-dead sequence should be source-check, not auto-corrected. |
| `source_rows_to_check` | `2024_fall.csv:33`; surrounding rows `2023_and_prior.csv:97`, `47`, `163`, `376`, `4341`, `2024_spring.csv:33`, `2025_spring.csv:30`, `import_recent_format_reviewed.csv:956`. |

### L5/418

| Field | Notes |
|---|---|
| `selection` | `L5/418`, UUID `9e9e1f99c8678e60`. |
| `related_uids` | `9e9e1f99c8678e60`. |
| `raw_flags` | Dead-tree DBH gap, dead-tree DBH increase, `single_survey_dbh_outlier`, DBH/ranked jumps around May 2024. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Juniperus DBH 98 in 2019-2020, dead/no DBH 2021-2023, May 2024 dead DBH 144, October 2024 dead DBH 98, April 2025 dead/no DBH, October 2025 dead DBH 94. |
| `interpretation` | May 2024 DBH 144 is an isolated dead-tree DBH rebound; likely source/entry error. |
| `recommended_action` | rule candidate |
| `decision_scope` | DBH field source row for May 2024. |
| `confidence` | high |
| `needs_riley_call` | no, if isolated dead-tree rebound strikes are approved. |
| `candidate_auto_rule` | Dead-tree isolated DBH increase that returns exactly/near baseline should suppress the outlier DBH while preserving dead evidence. |
| `source_rows_to_check` | `2024_spring.csv:700`; surrounding rows `2023_and_prior.csv:126`, `72`, `196`, `332`, `4586`, `2024_fall.csv:309`, `2025_spring.csv:314`, `import_recent_format_reviewed.csv:1223`. |

### L7/6

| Field | Notes |
|---|---|
| `selection` | `L7/6`, UUID `e884d22ebf873849`. |
| `related_uids` | `e884d22ebf873849`. |
| `raw_flags` | Dead-tree DBH gap, dead-tree DBH increase, DBH/ranked jumps at May 2024. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Dead Pinus DBH 172 in 2019-2020; dead/no DBH through 2023; May 2024 dead DBH 303; October 2024/April 2025 dead no DBH; October 2025 dead DBH 270. |
| `interpretation` | The later dead DBHs are persistently much larger than the old dead profile. This might be wrong tag/tree, a missed large dead trunk, or a field-measurement reinterpretation. Too large for an automatic dead-tree outlier rule. |
| `recommended_action` | source check |
| `decision_scope` | DBH field/source rows for May 2024 and October 2025; possible identity/source-row relocation. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Dead-tree DBH increases should stay review when the new larger regime persists. |
| `source_rows_to_check` | `2024_spring.csv:1080`, `import_recent_format_reviewed.csv:1359`; surrounding old rows `2023_and_prior.csv:752`, `659`, `846`, `1032`, `4748`. |

### L1/131

| Field | Notes |
|---|---|
| `selection` | `L1/131`, UUID `d8bc7d3ae2534f24`. |
| `related_uids` | `d8bc7d3ae2534f24`. |
| `raw_flags` | `I_ZOMBIE_TREE`, mortality contradiction, `single_survey_death_label_outlier` for June 2021. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus alive health 10 DBH 124 in 2019-2020; June 2021 dead/0 DBH 117 note `dead`; alive again from 2022-2025 with DBH 110-122 and health 2-7. |
| `interpretation` | Classic one-survey death-label artifact. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status source row for June 2021. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Bracketed one-survey dead/0 rows should be reinterpreted as uncertain/missing. |
| `source_rows_to_check` | `2023_and_prior.csv:166`; surrounding rows `3118`, `2997`, `1376`, `4391`, `2024_spring.csv:1328`, `2024_fall.csv:86`, `2025_spring.csv:86`, `import_recent_format_reviewed.csv:1009`. |

### H4/152

| Field | Notes |
|---|---|
| `selection` | `H4/152`, UUID `812e6d21b85309d0`. |
| `related_uids` | `812e6d21b85309d0`. |
| `raw_flags` | DBH/ranked jumps in June 2021 and June 2023; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Acer DBH 99 in 2019-2020, then 61/64 in 2021-2022, then 96-102 from 2023-2025. Health remains high throughout. |
| `interpretation` | The middle era is incompatible with both surrounding eras. This is likely source-era/tag alignment or measurement field error for 2021-2022, not true shrink/growth. |
| `recommended_action` | source check |
| `decision_scope` | DBH fields for 2021-2022 on UUID `812e6d21b85309d0`. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Detect incompatible middle eras separately from early-era blocks. Do not auto-strike without source policy approval. |
| `source_rows_to_check` | `2023_and_prior.csv:2922`, `2924`; surrounding rows `2905`, `2912`, `4216`, `2024_spring.csv:337`, `2024_fall.csv:1046`, `2025_spring.csv:1153`, `import_recent_format_reviewed.csv:458`. |

### H1/241

| Field | Notes |
|---|---|
| `selection` | `H1/241`, UUID `a85c34d3e8ad60e4`. |
| `related_uids` | `a85c34d3e8ad60e4`. |
| `raw_flags` | June 2021 DBH/ranked jump; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Nyssa DBH 76 in 2019-2020, then stable 101-108 from 2021-2025. Health stays alive/high until October 2025 health 1. |
| `interpretation` | Persistent early-vs-modern DBH regime shift. This matches the H1 source-era review block, though the shift is smaller than H4/145. |
| `recommended_action` | source check |
| `decision_scope` | DBH fields for 2019-2020 or source-era block decision. |
| `confidence` | medium |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | H1 stable-incompatible-era cases should be grouped for source review rather than handled one by one. |
| `source_rows_to_check` | `2023_and_prior.csv:3288`, `3361`, `2155`, `2185`, `4079`, `2024_fall.csv:1414`, `2025_spring.csv:1014`, `import_recent_format_reviewed.csv:329`. |

### M6/363

| Field | Notes |
|---|---|
| `selection` | `M6/363`, UUID `65eb81afd9ad9917`. |
| `related_uids` | `65eb81afd9ad9917`. |
| `raw_flags` | DBH/ranked jumps in June 2020 and June 2021; `max_dbh_jump`; `persistent_dbh_regime_shift`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 365 in 2019, 180.5 in 2020, then stable 144-151 from 2021-2025. Health is consistently alive/high. |
| `interpretation` | Early rows are incompatible with the modern stable series. 2019 is almost certainly wrong/misassigned; 2020 may be transitional source-era or another wrong value. |
| `recommended_action` | source check |
| `decision_scope` | DBH/source rows for 2019 and 2020. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Persistent modern series after extreme early values should join source-era/tag-alignment queue. |
| `source_rows_to_check` | `2023_and_prior.csv:3207`, `3230`, `1905`, `1917`, `5000`, `2024_spring.csv:1126`, `2024_fall.csv:782`, `2025_spring.csv:1301`, `import_recent_format_reviewed.csv:832`. |

### M0/514

| Field | Notes |
|---|---|
| `selection` | `M0/514`, UUID `28b6aeda79926637`. |
| `related_uids` | `28b6aeda79926637`. |
| `raw_flags` | `I_ZOMBIE_TREE`, mortality contradiction, sharp health rebound, `single_survey_death_label_outlier` for June 2020. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Large Pinus alive DBH 347 health 10 in 2019; June 2020 dead/0 DBH 364 note `dead`; alive again 2021-2025 with DBH 337-355 and health 4-7. |
| `interpretation` | Classic one-survey death-label artifact; DBH profile supports continuity. |
| `recommended_action` | rule candidate |
| `decision_scope` | mortality/status source row for June 2020. |
| `confidence` | high |
| `needs_riley_call` | no |
| `candidate_auto_rule` | Bracketed one-survey dead/0 rows on otherwise stable live trees should be reinterpreted as uncertain/missing. |
| `source_rows_to_check` | `2023_and_prior.csv:627`; surrounding rows `3594`, `2221`, `2035`, `4766`, `2024_spring.csv:1255`, `2024_fall.csv:505`, `2025_spring.csv:507`, `import_recent_format_reviewed.csv:560`. |

### L6/77

| Field | Notes |
|---|---|
| `selection` | `L6/77`, UUID `bf7c6c6bfb8df73e`. |
| `related_uids` | `bf7c6c6bfb8df73e`. |
| `raw_flags` | DBH/ranked jumps in June 2021, June 2023, October 2024; `single_survey_dbh_outlier`; `stable_incompatible_dbh_era`. |
| `configured_decisions_applied` | none matched. |
| `current_flags` | Same as raw. |
| `evidence_summary` | Juniperus DBH 225 in 2019-2020, then 110-113 in 2021-2022 and 2024, with June 2023 isolated 133. April/October 2025 are dead/0; April note `new death- brown leaves`. |
| `interpretation` | Two issues: early 225 mm source-era mismatch, and June 2023 133 mm isolated high value within the modern ~110 baseline. Later death can remain. |
| `recommended_action` | source check |
| `decision_scope` | DBH fields for 2019-2020 and June 2023; UUID-level DBH/source-era decision. |
| `confidence` | high |
| `needs_riley_call` | yes |
| `candidate_auto_rule` | Split source-era review from isolated one-survey DBH outlier within the later era. |
| `source_rows_to_check` | `2023_and_prior.csv:3177`, `3085`, `1497`, `1381`, `4676`, `2024_fall.csv:405`, `2025_spring.csv:390`, `import_recent_format_reviewed.csv:1300`. |

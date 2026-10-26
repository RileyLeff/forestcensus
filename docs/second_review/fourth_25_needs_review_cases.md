# Second review: fourth 25 needs-review cases

Date: 2026-05-10

Input ordering: cases 76-100 from the rebuilt UI-like `needs_review` queue in `output/canonical_review/tree_cases.csv`.

## Quick synthesis

This batch is less about candidate links and more about diagnostic design. A few clear themes emerge:

- Several `dbh_review` cases are actually note-explained measurement cases: poison ivy, knots, split trunks, parasite/vines, or “not circle.”
- A cluster of cases are mortality/zombie problems that happen to have DBH jumps, especially “marked dead last year” rows.
- Multi-stem trees with stable modern profiles are being over-flagged when older surveys under-recorded stems or when stem ranks change.
- The duplicate-stem artifact rule is too broad for known multi-trunk trees. Exact duplicate DBHs are suspicious, but multi-stem trees can legitimately have close or even equal values.
- A few rows look like high-confidence correction candidates: M0/513 June 2020 347, M0/585 June 2022 235, M5/2492 May 2024 148, M7/325 June 2021 150, M7/326 June 2023 116, and maybe L1/145 pre-2022 values.

## Cases

### 76. L1/145

Bucket: `dbh_review`

History: living Juniperus. 161.5 mm in 2019-2020, missing in 2021, then stable 284-300 mm from 2022 onward.

Impression: persistent regime shift. This is too large for growth and too stable after 2022 to be random noise. Either early values belong to a different measurement/stem/tree, or 161.5 is a transcription/column problem.

Suggested action: source review for 2019-2020 and 2022. If 2022+ is trusted, keep modern regime and either correct/strike early DBHs or split identity if source supports that.

### 77. L1/5052

Bucket: `dbh_review`

History: living Juniperus. One stem 198 -> 176 -> 166 -> 184, then October 2024 has two stems 216/169, April 2025 returns to 169 with note `to 5051`, October 2025 says `NO second stem`.

Impression: tag/stem-scope problem, not ordinary stem growth. Notes imply one stem or tag moved/should belong to 5051.

Suggested action: investigate with tag 5051. Do not insert back-history for a second stem until that tag relationship is understood.

### 78. L4/462

Bucket: `dbh_review`

History: living Morella. One stem 104 in May 2024, October 2024 two stems 81/60 with note `knot in prior year`; second stem health was already manually corrected. April 2025 has 92/60.

Impression: likely real second stem plus measurement-location/knot issue on main stem. The 104 -> 81 -> 92 swing may be caused by measuring around a knot rather than a typo.

Suggested action: keep as manual/watch context. Preserve second stem; avoid correcting main DBH without source/field context.

### 79. L5/422

Bucket: `dbh_review`

History: living Juniperus with repeated vine/poison ivy/parasite notes. DBH ranges 245-275, then 328 in October 2025 with `DBH with parasite`.

Impression: note-explained DBH inflation/measurement inconsistency. This is not a clean typo because the parasite/vine may genuinely affect measured circumference/diameter if measured over it.

Suggested action: keep as measurement-consistency review/watch. Do not auto-correct; preserve notes prominently.

### 80. L5/704

Bucket: `dbh_review`

History: Morella with three stems in May/October 2024 and October 2025. April 2025 records only one live 60 mm stem and two dead/no-DBH stems, with note `leaves brown - all`.

Impression: April 2025 is a stem-measurement gap/condition issue, not necessarily true stem disappearance. October 2025 returns to three measured dead stems.

Suggested action: treat April 2025 missing DBHs for stems 2-3 as blank/not measured, preserving dead health. Do not infer new stems in October 2025.

### 81. M0/513

Bucket: `dbh_review`

History: Ilex with split/weird trunk notes. 116 in 2019, 347 in 2020, 75 in 2021, then 63-74 in 2023-2024. Notes include `split trunk` and `weirdo, split in half, not circle`.

Impression: June 2020 347 is almost certainly wrong or a different measurement basis. The stable later trajectory is 60-75 mm.

Suggested action: strike June 2020 347 DBH unless original source clearly supports a specific correction. Consider 2019 116 separately; it may also reflect split-trunk measurement inconsistency.

### 82. M0/577

Bucket: `dbh_review`

History: dead/alive/dead Juniperus. Dead 130 in 2019, alive 147 in 2020, then dead/no DBH, later dead 119 in 2024-2025. Has zombie diagnostic.

Impression: mortality contradiction matters more than DBH. DBH change 147 -> 119 after death is plausible; the weird part is dead -> alive -> dead.

Suggested action: route to mortality review. If 2020 alive is trusted, earlier 2019 dead label may be wrong; if not, 2020 alive may be wrong.

### 83. M0/578

Bucket: `dbh_review`

History: Nyssa. Alive 147/131 in 2019-2020, dead/no DBH for several surveys, then dead 97 in April 2025. Notes include bare branches, dead/standing, ivy.

Impression: dead-tree DBH loss/gap. The 131 -> 97 loss after years dead is plausible.

Suggested action: downgrade to watch/dead-tree structural context. No correction obvious.

### 84. M0/585

Bucket: `dbh_review`

History: dead/unidentified 68 in 2019-2020, then June 2022 alive 235 with note `marked dead last year`, then dead/no DBH, later dead 56/53.

Impression: June 2022 235 is very suspicious. It creates both a zombie and a giant DBH jump, then disappears back to the original size class.

Suggested action: manual/source review; likely strike or move June 2022 235 row. The `marked dead last year` note may mean the live row belongs to another nearby tag or a rediscovery error.

### 85. M1/833

Bucket: `dbh_review`

History: dead 66 in 2019-2020, June 2022 alive 52 with note `marked dead last year`, then dead around 51-55 through 2025.

Impression: mortality contradiction, but DBH itself is plausible and stable. Unlike M0/585, the June 2022 DBH is not wildly off.

Suggested action: route to mortality review. Decide whether June 2022 should be alive health 2 or whether it should become uncertain/dead; DBH can probably stay.

### 86. M3/5188

Bucket: `dbh_review`

History: Morella. One stem around 134-164 from 2021-2024, May 2024 isolated low 104, then April 2025 has three stems 162/72/56 and October 2025 has three alive no-DBH rows.

Impression: May 2024 104 is likely an isolated bad measurement; later appearance of smaller stems seems real or at least persistent as health rows.

Suggested action: correct/strike May 2024 104 after source check. Treat April/October 2025 smaller stems as new persistent stems needing blank back-history if appropriate.

### 87. M5/2492

Bucket: `dbh_review`

History: Nyssa alive 71/65 through 2021, dead/no DBH in 2022-2023, May 2024 alive 148, then dead 60 in October 2024 and April 2025.

Impression: May 2024 148 is likely wrong or wrong-tree, and the alive status creates a zombie. The rest of the trajectory is around 60-71.

Suggested action: source review; likely strike or move May 2024 148 and treat May 2024 alive/health 8 as suspect.

### 88. M6/384

Bucket: `dbh_review`

History: living Pinus with vine/poison ivy notes. 226/225 early, 180 in June 2023, 196 in May 2024, October 2024 no DBH due poison ivy, April 2025 241 with poison ivy, October 2025 213.

Impression: poison ivy/vine measurement inconsistency. April 2025 241 is flagged as isolated, but the whole series is affected by measurement over/under growth.

Suggested action: keep as measurement-consistency review/watch; do not auto-correct.

### 89. M6/387

Bucket: `dbh_review`

History: dead Juniperus. 106 in 2019-2020, dead/no DBH until May 2024 80 with poison ivy, October 2025 93.

Impression: dead-tree gap plus poison ivy measurement. 106 -> 80/93 is plausible structural/measurement variation.

Suggested action: downgrade to watch/dead-tree poison-ivy context.

### 90. M7/325

Bucket: `dbh_review`

History: Juniperus alive 110, one 150 in June 2021, dead/no DBH in 2022, then alive 110/114/116 afterward. Has zombie diagnostic from June 2022 dead followed by alive.

Impression: June 2021 150 is an isolated DBH outlier. June 2022 dead label may also be wrong given later alive recovery.

Suggested action: strike/correct June 2021 150 after source review; route June 2022 death to mortality review, likely convert to uncertain/missing if later alive evidence is trusted.

### 91. M7/326

Bucket: `dbh_review`

History: dead Juniperus 73 in 2019-2020, dead/no DBH, June 2023 alive 116 with note `Marked dead last year`, then dead 74/75 in 2024-2025.

Impression: June 2023 116/alive is isolated and suspicious. The surrounding dead-tree DBH is ~73-75.

Suggested action: source review; likely strike or move June 2023 116 and reconsider the alive label.

### 92. M7/454

Bucket: `dbh_review`

History: Morella, stable two stems around 125-130 and 50-87, October 2024/April 2025 adds a third 54-56 mm stem with note `new stem added`.

Impression: likely real new threshold-crossing stem or newly noticed stem. The note supports the diagnostic.

Suggested action: keep third stem from October 2024 onward; consider blank back-history only if we decide stems over 60 should have been present before. No correction needed.

### 93. R2/5303

Bucket: `new_in_october_2025`

History: first appears October 2025 as Ilex opaca, 65 mm, health 6.

Impression: true new tree/new tag candidate. Since October 2025 DBH exists, it qualifies.

Suggested action: search for compatible missing prior tree in R2 before treating as genuinely new; otherwise accept as new qualifying tree.

### 94. H0/275

Bucket: `stem_profile_review`

History: Nyssa, note `3 stems. one tree`. Early 3-stem profile around 63/54/53, then later mostly one stem around 71-77, May 2024 duplicate 76/76.

Impression: known multi-stem tree with small stems dropping below threshold or not being measured. May 2024 duplicate is suspicious, but the broader issue is inconsistent recording of secondary stems.

Suggested action: do not auto-merge/delete all duplicates blindly. Suppress subthreshold DBHs; treat May 2024 duplicate 76 as likely artifact unless original sheet supports two equal qualifying stems.

### 95. H0/281

Bucket: `stem_profile_review`

History: Nyssa, note `2 stems. one tree`. Early duplicate 60/60, later two stems hovering around threshold, May 2024 three stems 54/54/50, October 2024 53/45.

Impression: threshold-edge multi-stem tree. Exact duplicates may be real-ish or artifact; May 2024 extra third stem may be duplicate/noise.

Suggested action: review as multi-stem threshold case. Suppress subthreshold DBHs, but do not batch-delete duplicate equal values without source context.

### 96. H2/208

Bucket: `stem_profile_review`

History: large Pinus stable around 461-480. May 2024 has duplicate 480/480, October 2024 returns to one stem, October 2025 has two close large stems 475/471.

Impression: May 2024 duplicate 480 is likely artifact, but October 2025 may indicate a real second large stem or a newly recorded second trunk. This was exactly the kind of case where duplicate handling must not erase a real second stem.

Suggested action: suppress/review May 2024 duplicate as artifact; separately inspect October 2025 second 471 stem before deciding whether to backfill a second-stem history.

### 97. H4/149

Bucket: `stem_profile_review`

History: known Ilex, note `three trunks`, scratched tag. Multiple stems across years with threshold-edge small stems; June 2023 has four qualifying stems 70/70/62/52; May 2024 only 73 plus subthreshold stems; modern surveys return to two qualifying plus one subthreshold.

Impression: real multi-stem plant with an extra June 2023 duplicate/surplus stem problem. We already suspected June 2023 has an extra duplicate stem, but the rest of the multi-stem complexity is real.

Suggested action: review June 2023 specifically as possible duplicate/surplus row; preserve multi-stem structure and subthreshold evidence elsewhere.

### 98. H6/533

Bucket: `stem_profile_review`

History: Nyssa, note `two trunks`. Stable two-stem profile around 220/140, except June 2020 second stem missing and June 2021 second stem recorded as 14.

Impression: June 2021 second-stem 14 is almost certainly missing zero / decimal error or bad entry; given surrounding 148/140/144/143, it likely should be 140-ish.

Suggested action: correct June 2021 second-stem 14 to 140 if source supports it; otherwise strike. Treat June 2020 second stem as blank/not measured.

### 99. L0/192

Bucket: `stem_profile_review`

History: living Juniperus, mostly 42-44 mm, one qualifying 50 in June 2023, alive no-DBH in October 2025.

Impression: pure threshold-edge live tree. This can be handled later by threshold policy, as discussed.

Suggested action: downgrade to watch/policy case; suppress subthreshold DBHs, keep alive evidence.

### 100. L4/613

Bucket: `stem_profile_review`

History: living Morella 66-67 mm, April 2025 second dead 11 mm, October 2025 second dead 65 mm with note `?`.

Impression: second stem evidence is contradictory. April 2025 11 dead and October 2025 65 dead may be the same dead stem badly measured/recorded, or October 2025 may be a different stem.

Suggested action: manual stem review. Do not auto-backfill second stem without source context. Strike/suppress April 2025 11 as subthreshold, preserve dead evidence.

## Rules learned or reinforced

1. The review bucket should allow note-explained measurement contexts: poison ivy/vine/parasite/knot/split trunk should often downgrade DBH jumps to watch unless rebound-shaped.
2. Mortality/zombie diagnostics should be promoted ahead of DBH labels when a dead row is followed by alive evidence.
3. Known multi-stem trees need a distinct diagnostic path from duplicate-entry artifacts.
4. Close/equal DBHs are not sufficient for duplicate deletion in multi-stem trees.
5. Rows with `new stem added`, `new tag`, or `tag on trunk` notes should route to stem/tag workflow, not generic DBH review.
6. Several high-confidence per-case corrections are now queued: M0/513 347, M0/585 235, M5/2492 148, M7/325 150, M7/326 116, H6/533 14, and L1/110 132 from the prior batch.

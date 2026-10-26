# Human attention queue

Date: 2026-05-10

Purpose: keep per-case decisions from the second review pass from getting lost. This file tracks cases that need a Riley/Juan/source-sheet call before we encode corrections or accept review decisions.

## Highest-confidence correction candidates

These look strong enough to become correction-config entries after source confirmation, or immediately if you are comfortable with the inference.

| Case | Suspicious row/value | Proposed action | Why |
|---|---:|---|---|
| L1/110 | October 2024 DBH 132 | Correct to 332 or strike | Stable Pinus trajectory is 331-340, May 2024 is 332, April 2025 is 330. |
| M7/320 | June 2022 DBH 451 | Strike to missing, or correct only if source gives exact value | Later notes explicitly say `dbh approx. 200 not 450` and `200 range, not 450`. |
| M0/513 | June 2020 DBH 347 | Strike to missing unless original sheet gives a clear correction | Surrounding trajectory is 116 -> 75 -> 63-74; notes say split/weird/non-circular trunk. |
| M0/585 | June 2022 DBH 235 with alive status | Source review; likely strike or move row | Surrounding dead-tree size is ~53-68; note says `marked dead last year`; row creates zombie and huge DBH jump. |
| M5/2492 | May 2024 DBH 148 with alive status | Source review; likely strike or move row | Surrounding trajectory is ~60-71; May 2024 creates zombie and isolated DBH outlier. |
| M7/325 | June 2021 DBH 150 | Source review; likely strike/correct | Stable live trajectory is ~110-116; 150 is isolated. |
| M7/326 | June 2023 DBH 116 with alive status | Source review; likely strike or move row | Dead-tree trajectory is ~73-75; June 2023 creates zombie and isolated DBH outlier. |
| H6/533 | June 2021 second-stem DBH 14 | Correct to ~140 if source supports it; otherwise strike | Two-trunk Nyssa has surrounding second-stem DBHs 148, 140, 144, 143. |
| M2/5863 | May 2024 DBH 163 | Review/strike/correct | Same tree otherwise ~121-127/125; likely tied to M2/5883 tag-change case. |
| H4/992 | May 2024 DBH 111, note `might be 136` | Source review; likely strike or move to H4/136 | H4/992 is otherwise stable ~187-200. |

## Mortality / zombie calls

These need an explicit mortality interpretation before DBH/link decisions are useful.

| Case | Question | Current leaning |
|---|---|---|
| L7/5029 / L7/982 | Alive health 2, then dead, then alive health 1; also a tag-change assertion. | Resolve mortality first; do not auto-accept link yet. |
| H1/230 | Dead/no DBH in 2022-2023, alive in October 2024, dead/half-gone in October 2025. | Likely convert 2022-2023 dead/no-DBH to missing/uncertain if later alive is trusted; keep October 2025 dead if field context supports it. |
| M3/359 / M3/911 | Long-dead Juniperus has October 2024 alive health 6. | Likely October 2024 alive/health is wrong or belongs elsewhere, unless source/field notes support rediscovery. |
| M0/577 | Dead 2019, alive 2020, dead afterward. | Decide whether 2019 dead or 2020 alive is the bad label. |
| M1/833 | Dead 2019-2021, alive health 2 in 2022, dead afterward. | DBH is plausible; only mortality label needs review. |
| M5/2492 | Dead 2022-2023, alive May 2024 DBH 148/health 8, dead afterward. | May 2024 row likely wrong/misassigned. |
| M7/325 | Dead June 2022 between alive observations. | Likely convert June 2022 dead to uncertain/missing if later alive evidence is trusted. |
| M7/326 | Dead sequence with one alive June 2023 DBH 116. | June 2023 row likely wrong/misassigned. |
| L5/419 | Dead health 0 from 2019-April 2025, then October 2025 alive health 6 with DBH 301. | Review October 2025 source/field context; likely set to dead/0 unless live tissue was truly observed. |
| L7/25 | Dead 2019-2022, alive health 1 in 2023, dead afterward; May 2024 note says `zombie`. | Decide whether 2023 should be dead/0, low-health alive, or uncertain. |
| M1/838 | Dead 2021-May 2024, alive health 5 in October 2024, dead afterward. | Review October 2024 alive/health; likely dead/0 or uncertain. |
| H7/895 | Alive through 2022, dead June 2023, poison ivy context, alive from October 2024 onward. | Likely convert June 2023 dead/0 to uncertain/missing if no source death evidence. |
| L1/5050 | Low-health alive, one dead row in June 2023, then low/moderate alive again. | Review June 2023 dead row; likely uncertain rather than true death. |
| L1/5063 | Dead/fallen rows followed by `Fallen still live` in October 2024 and alive health 2 in October 2025. | Fallen-live case; preserve later live evidence and revisit older dead labels. |
| L2/238 | Dead sequence interrupted by June 2022 alive health 6/DBH 121. | Review June 2022 row; likely wrong/misassigned unless source confirms live tissue. |
| L3/300 | Alive through 2021, one dead row in June 2022, then alive afterward. | Likely convert June 2022 dead/0 to uncertain/missing. |
| L3/5881 | New/unidentified 2022, dead 2023, huge Pinus DBH in 2024, error notes afterward. | Keep as source/identity review; do not handle as generic mortality. |
| L5/420 | Large pine dead 2023-April 2025, then October 2025 alive health 6 with stable DBH. | Review October 2025 source/field context; likely dead/0 unless confirmed. |
| L5/425 | One May 2024 dead/0 row between healthy alive observations. | High-confidence single-survey death-label correction candidate. |
| L5/435 | Dead 2021-April 2025, then October 2025 alive health 6 with DBH 317. | Review October 2025 source/field context; likely dead/0 unless confirmed. |
| L6/49 | June 2022 dead row between healthy alive observations; October 2025 may be later real death. | Review/correct June 2022 dead row; keep October 2025 separate. |
| L6/54 | Dead 2019-2022, alive health 6 in 2023, dead later with `new death` note. | Decide whether early dead labels or 2023 alive label are wrong. |
| L6/67 | Dead 2019-2020, alive 2021-April 2025, dead October 2025. | Likely early dead labels should become uncertain/missing or wrong-label corrections. |
| L6/87 | Dead 2019-2020, later low-health alive after a long missing run. | Source/identity review for early dead labels and later refinding. |
| L7/23 | Dead 2019-2021, alive 2022-2023, dead 2024-2025. | Source review; likely early dead rows or later live rows need reinterpretation. |
| L7/5032 | June 2022 dead/0 row between healthy alive observations. | Likely one-survey death-label outlier; convert to uncertain/missing unless source proves death. |
| M1/839 | Dead sequence interrupted by June 2022 alive health 3 with `marked dead last year`. | Human low-health mortality call. |
| M1/850 | Dead sequence interrupted by June 2022 alive health 3 and October 2024 poison-ivy alive health 2. | Human low-health/poison-ivy mortality call. |
| M2/2408 | Alive 2019-2020, dead 2021, alive health 1 in 2022, then dead. | Decide whether 2022 low-health alive is true marginal tissue. |
| M3/356 | Dead 2022-2023, later low-health alive with notes `alive !!!!`. | Later field notes likely matter; review older dead rows vs marginal live tissue. |
| M3/5189 | Dead 2022-2023, alive from 2024 with note `alive !!!!!`. | Review older dead rows; later alive evidence may be trustworthy. |
| M4/2451 | June 2022 dead/0 row between healthy alive observations. | High-confidence one-survey death-label correction candidate. |
| M4/2452 | Early dead rows followed by repeated live low-health Quercus/willow oak evidence. | Source/identity/mortality review; early identity may be wrong. |
| M4/2461 | Dead early, alive DBH 389/health 6 in 2022, then confirmed killed/dead later. | Review June 2022 row and identity. |
| M5/5870 | Dead 2021, alive health 3 in 2022, then missing/dead. | Human low-health mortality call. |
| M7/323 | June 2023 dead/0 row between alive observations. | Likely one-survey death-label correction candidate. |
| M7/5834 | Dead 2023-2024, then October 2025 alive health 8. | Source/field review for suspicious latest-survey revival. |
| M7/5835 | October 2025 has health 9 and 0 with note `mis ID should be Pin 5835`. | Source/identity review; decide whether live row belongs to this UUID. |
| R4/5206 | May 2024 dead/0 row between alive June 2023 and alive October 2024; dead later. | Review/correct May 2024 separately from later death. |
| M0/816 | October 2025 alive health 6 after long dead sequence; also DBH outlier. | Review October 2025 live status and October 2024 DBH 196. |
| L6/101 | Early dead labels followed by strong live tree; later real-death possibility. | Review early dead rows and May 2024 DBH outlier. |
| L6/76 | April 2025 dead then October 2025 alive health 8, plus DBH regime shift. | Source/identity/status review. |
| L7/14 | June 2021 dead/0 row in otherwise alive small Juniperus. | Likely one-survey death-label correction candidate. |
| M5/2496 | June 2021 dead/0 row between alive rows. | Likely one-survey death-label correction candidate. |
| L1/119 | June 2022 dead/no-DBH between live Juniperus rows; 2023 note says `Marked dead last year`. | Likely convert June 2022 dead row to uncertain/missing. |
| L1/129 | June 2022 dead/no-DBH between live Juniperus rows; 2023 note says `Marked dead last year`. | Likely convert June 2022 dead row to uncertain/missing. |
| L2/222 | October 2024 dead/0 between low-health alive rows and later alive health 6. | Likely one-survey death-label outlier despite previous health being low. |
| H7/885 | October 2024 alive health 8 inside otherwise dead pine sequence. | Review/correct October 2024 row, likely dead/0 unless source confirms live tissue. |
| L0/181 | October 2024 alive health 5 inside otherwise dead Juniperus sequence. | Review/correct October 2024 row, likely dead/0. |
| L2/224 | October 2024 alive health 6 inside otherwise dead Juniperus sequence. | Review/correct October 2024 row, likely dead/0. |
| L2/236 | October 2025 alive health 9 after long dead Juniperus sequence. | Source/field review latest-survey revival. |
| L3/298 | October 2025 alive health 4 after long dead/pushed-over Juniperus sequence. | Source/field review latest-survey revival. |
| L6/59 | October 2025 alive health 6 after dead/snapped Juniperus and April 2025 DNF. | Source/field review latest-survey revival. |
| L6/91 | October 2025 alive health 1 after long dead Juniperus; 2022 note says `could be one of the new tags`. | Source/tag review before mortality correction. |
| M1/852 | April 2025 alive health 1 inside otherwise dead Juniperus sequence. | Human mortality call; likely dead/0 or uncertain unless source confirms live tissue. |
| M6/383 | October 2024 alive health 8 with poison ivy note inside otherwise dead Juniperus sequence. | Review/correct October 2024 row, likely dead/0. |
| M7/331 | Two-stem Nyssa has both stems dead/0 in October 2024 with merge notes, then alive again. | Source review; likely convert October 2024 dead/0 rows to alive/uncertain and keep merge context. |
| M7/336 | April 2025 alive health 1 with note `ivy sprouted low` inside dead Nyssa sequence. | Human/source call; low sprout may not revive whole tree. |
| H1/221 | June 2020 dead/0 row inside otherwise alive Nyssa sequence. | Correct/reinterpret June 2020 dead/0 as alive or uncertain. |
| H1/249 | Early dead labels, alive 2021-2024, dead April 2025, alive October 2025. | Source/field review early dead rows and April 2025 death. |
| H1/252 | June 2022 dead/0 between low-health alive 2021 and alive 2023; later death from October 2024 may be real. | Correct/reinterpret June 2022 dead/0 separately from later death. |
| H4/113 | June 2021 dead/0 row inside otherwise alive very large pine sequence. | Correct/reinterpret June 2021 dead/0 as alive or uncertain. |
| H7/459 | June 2021 dead/0 row followed by alive row noting `marked as dead last year`. | Correct/reinterpret June 2021 dead/0 as alive or uncertain. |
| H7/460 | June 2021 dead/0 row followed by alive row noting `marked as dead last year`. | Correct/reinterpret June 2021 dead/0 as alive or uncertain. |
| H7/880 | October 2024 dead/0, April 2025 alive health 5 with `girdle`, then dead October 2025. | Human mortality call; could be real marginal live tissue in a failing/girdled tree. |
| L0/477 | April 2025 dead/0 with poison ivy between low-health alive rows. | Likely low-health/poison-ivy single-survey death-label outlier. |
| L0/970 | April 2025 dead/0 with poison ivy between low-health alive rows. | Likely low-health/poison-ivy single-survey death-label outlier. |
| L1/131 | June 2021 dead/0 row inside otherwise alive Juniperus sequence. | Correct/reinterpret June 2021 dead/0 as alive or uncertain. |
| L2/611 | Morella dead/0, then October 2024 alive health 3, then dead again. | Human low-health mortality call; likely marginal/uncertain rather than whole-tree revival. |
| L3/295 | May 2024 dead/0 row inside otherwise alive pine sequence. | Correct/reinterpret May 2024 dead/0 as alive or uncertain. |
| L6/105 | Dead in 2019-2020, then strong alive Juniperus from 2021 onward. | Source review; likely reinterpret early dead rows as uncertain/wrong-label. |
| L6/92 | Dead in 2019-2020, then long low-health alive Nyssa sequence with late dead/alive oscillation. | Source/mortality review; likely reinterpret early dead rows and handle late death as uncertain. |
| L6/96 | Dead in 2019-2020, then alive Juniperus from 2021 onward. | Source review; likely reinterpret early dead rows as uncertain/wrong-label. |
| L6/99 | Nyssa alive with June 2021 note `dead`, October 2024 dead/0, later alive health 1. | Human low-health mortality/status-note call. |
| L7/15 | Dead in 2019-2020, then alive in 2021 with note `Alive (marked dead last year)`. | Correct/reinterpret 2019-2020 dead rows as uncertain/wrong-label. |
| L7/500 | Morella cluster has April 2025 dead/0 between alive rows. | Correct/reinterpret April 2025 dead/0 as alive/uncertain. |
| M0/514 | June 2020 dead/0 row inside otherwise alive pine sequence. | Correct/reinterpret June 2020 dead/0 as alive or uncertain. |
| M0/584 | Very large pine dead in 2019-2020, then alive with note `not dead`. | Correct/reinterpret 2019-2020 dead rows as uncertain/wrong-label. |
| M1/5860 | October 2024 dead/fallen row in otherwise live unidentified/Nyssa sequence; October 2025 has extra Nyssa note row. | Source review; likely convert October 2024 dead to uncertain unless true fall/death confirmed. |
| M1/843 | Dead in 2019-2020, alive low-health from 2021 onward, dead October 2025. | Source review early dead rows; keep October 2025 death separate. |

## Candidate-link decisions needing human/source review

Most simple dead-tree links can probably become link-review decisions, but these should not be auto-accepted.

| Link | Why it needs attention |
|---|---|
| H5/559 -> H5/912 | Old source is multi-stem 405/217; target is ~184-198. May be partial-stem alias, not whole UUID merge. |
| L4/243 -> L4/925 | Huge DBH mismatch: old 332 vs target 90-93. |
| L7/5029 -> L7/982 | Source has zombie/mortality problem. |
| H4/136 -> H4/992 | Old H4/136 has persistent regime shift; H4/992 has May 2024 note `might be 136`. Review as pair. |
| M2/5883 -> M2/5863 | Likely link, but target May 2024 163 is suspicious. |
| L3/5029 -> L3/919 | Notes include plot-string/species-change ambiguity. |
| M3/359 -> M3/911 | Source mortality contradiction must be resolved first. |
| L1/5052 with tag 5051 | Notes say `to 5051` and `NO second stem`; likely tag/stem-scope issue. |
| M7/5274 with tag 795 | Notes say `tag on trunk 2` and `new tag 795`; not simple DBH shrinkage. |

## Stem / multi-stem cases

These should be reviewed with a multi-stem-aware display; exact DBH duplicates are not enough by themselves.

| Case | Issue | Current leaning |
|---|---|---|
| H3/153 | Known multi-stem Nyssa; early under-recording and May 2024 duplicate-ish stems. | Preserve multi-stem structure; do not auto-drop duplicates without source context. |
| H4/140 | `two trunks`; early 91/91 then stable modern ~200/80. | Review early rows; keep modern two-stem profile. |
| R1/938 | May 2024 duplicates both large stems, inflating 3 stems to 5. | Suppress May 2024 duplicate 218 and duplicate 212 from canonical profile. |
| R1/963 | May 2024 mixes live Ilex 156 with dead/unidentified 71/71 rows. | Identity/source review before duplicate cleanup. |
| H0/275 | `3 stems. one tree`; May 2024 duplicate 76/76 but broader secondary-stem inconsistency. | Treat May duplicate as likely artifact; preserve multi-stem history. |
| H0/281 | `2 stems. one tree`; threshold-edge second stems and May 2024 54/54/50. | Multi-stem threshold review; no blind duplicate deletion. |
| H2/208 | Stable large Pinus; May 2024 duplicate 480/480; October 2025 possible real second large stem 471. | Suppress/review May duplicate separately from October 2025 second stem. |
| H4/149 | Known three-trunk Ilex; June 2023 has four qualifying stems with duplicate 70/70. | Review June 2023 specifically; preserve multi-stem structure elsewhere. |
| L4/613 | Morella second stem: April 2025 dead 11, October 2025 dead 65 with `?`. | Manual stem review; suppress 11 as DBH but preserve dead evidence. |
| M7/454 | Morella `new stem added`; third stem appears around 54-56. | Likely real new/noticed stem; keep from October 2024 onward. |
| M1/842 | Two-trunk Nyssa with early equal DBHs and later stem-level dead/alive oscillation. | Preserve as multi-stem case; do not auto-drop 75/75 duplicate because `2 trunks` supports true equal stems. |
| L7/498 | Morella cluster with `1 dead trunk`, alive/dead oscillation across years. | Treat as stem/cluster-level mortality review, not simple tree-level zombie. |
| M0/486 | Nyssa with notes `dead second stem`; live/dead statuses coexist across stems. | Route to stem-level mortality review, not tree-level zombie. |
| M5/487 | Three-stem Morella with one dead stem and later mixed status. | Route to multi-stem mortality review; preserve evidence. |
| H6/521 | Two-trunk Ilex with missing second stem in June 2020. | Insert blank rank-2 gap; no identity correction. |
| H6/529 | Two-stem pine with missing second stem in June 2020. | Insert blank rank-2 gap; no identity correction. |
| H7/891 | Large pine with dead second stem appearing in October 2024. | Preserve dead second stem evidence; blank later missing DBH. |
| M0/803 | Two-trunk Nyssa with secondary stem gap in 2021-2022 and stem-level mortality. | Add blank rank-2 gaps; route mortality at stem level. |
| M0/817 | Two-trunk Nyssa with second stem appearing from 2020 onward. | Insert blank rank-2 history for 2019. |
| M1/870 | Two-trunk Nyssa with poison-ivy missing second-stem DBHs. | Add blank rank-2 gaps for poison-ivy surveys. |
| M3/347 | Two-trunk Juniperus with one dead stem and rank-2 gap in 2022-2023. | Add blank rank-2 gap; preserve dead stem evidence. |
| M4/2459 | Two-trunk Nyssa with one-stem rows and stem-level dead/alive transitions. | Add blank rank-2 gaps; do not treat as generic new stem. |
| R2/626 | Two-stem Ilex with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R2/632 | Morella gains dead second stem from October 2024 onward. | Preserve second-stem dead evidence. |
| R2/634 | Two-stem Ilex with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R3/641 | Two-stem Acer with May 2024 missing/dead rank-2 stem. | Add blank rank-2 gap; preserve dead stem evidence. |
| R3/684 | Two-stem Ilex with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R4/5205 | Large pine with note `2nd dead stem, left untagged`. | Preserve second-stem evidence; blank rank-2 gap where DBH missing. |
| R4/5213 | Two-stem Ilex with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R4/5220 | Two-stem Acer with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R4/5224 | Two-stem Ilex with May 2024 missing rank-2 stem. | Add blank rank-2 gap. |
| R4/5227 | Two-stem Acer with May 2024 missing/dead rank-2 stem. | Add blank rank-2 gap; preserve dead stem evidence. |
| R4/5243 | Two-stem Acer with April 2025 missing rank-2 stem. | Add blank rank-2 gap. |

## DBH / source cases from later review passes

| Case | Issue | Current leaning |
|---|---|---|
| L3/5886 | June 2022 DBH 319/dead between stable ~168-183 alive rows. | High-confidence source/correction candidate: strike or move June 2022 row/value. |
| L6/101 | May 2024 DBH 101 in otherwise ~140-165 Juniperus series. | Strike/correct May 2024 DBH after source review. |
| L6/76 | DBH regime shift 114 -> persistent ~228. | Source/identity review; likely early values under wrong tag/source. |
| M0/580 | DBH regime shift 214 -> persistent ~76. | Source/identity review; not a mortality issue. |
| M0/816 | October 2024 DBH 196 between 99 and 97 on dead pine. | Very likely DBH/source error; strike/correct after source review. |
| M1/872 | DBH regime shift 182 -> persistent ~80-95. | Source/identity review; early values likely wrong tag/source. |
| M5/2496 | October 2024 DBH 318 between stable ~200 values. | Strike/correct October 2024 DBH after source review. |
| L7/19 | June 2022 DBH 112 between dead DBHs around 47-50. | Likely source/entry error; strike/correct after source review. |
| H0/260 | May 2024 duplicate 200/200 and low DBH under poison ivy, then returns to 260. | Review/suppress extra duplicate; treat poison ivy as measurement context. |
| H4/130 | October 2025 two large dead stems 211/209 after one-stem dead profile. | Source/field review: true two dead stems vs duplicate/double measurement. |
| H2/5859 | May 2024 duplicate 341/341 and suspicious 2021 dead row before stable alive sequence. | Suppress extra duplicate; review/likely convert 2021 dead to uncertain/missing. |
| L6/74 | Dead/no DBH in 2023, then dead DBH 397 in October 2024. | Keep source/identity review; may be wrong tag/tree rather than generic dead-tree first measurement. |
| L7/5039 | October 2025 adds second qualifying stem 73 beside 76. | Source/stem review: true second stem vs duplicate/slot issue. |
| R1/942 | May 2024 near-duplicate 175/173 appears once, then vanishes. | Review/suppress extra near-duplicate unless source confirms two stems. |
| R1/951 | May 2024 near-duplicate 209/208 appears once, then vanishes. | Review/suppress extra near-duplicate. |
| R1/956 | May 2024 near-duplicate 454/451 appears once, then vanishes. | Source review before suppressing due to large pine size. |
| R1/961 | May 2024 duplicate 156/156 plus October 2025 DBH 127 outlier. | Suppress duplicate; review/correct October 2025 DBH. |
| R2/622 | October 2025 DBH 7 with health 9 after DBH 64-69. | High-confidence correction candidate: strike/correct DBH 7 after source check. |
| H1/236 | Dead pine Oct 2025 DBH 232 after several lower dead DBHs around 168-180. | Source/field review; dead-tree DBH increase is suspicious. |
| H0/286 | June 2021 DBH 155 between ~315 and ~307-310; May 2024 duplicate 310/310. | Strike/correct 2021 DBH 155; suppress May 2024 extra 310. |
| H6/523 | Dead pine 136 in 2019-2020, then dead DBH 501/498 in 2024. | Source/field review; likely strike or move 2024 DBHs. |
| L2/198 | Dead pine 280, May 2024 DBH 203, then 258/264. | Review/likely strike May 2024 DBH 203 as isolated low dead-tree measurement. |
| L5/412 | Dead unidentified 86, May 2024 DBH 61, then Juniperus 83/90. | Review/likely strike May 2024 DBH 61; modern Juniperus taxon likely acceptable. |
| L5/418 | Dead Juniperus 98, May 2024 DBH 144, then 98/94. | Strike/correct May 2024 DBH 144. |
| L7/12 | Dead pine 162/158, October 2024 DBH 126, October 2025 DBH 158. | Strike/correct October 2024 DBH 126. |
| L7/6 | Dead pine 172 in 2019-2020, then dead DBH 303 in May 2024 and 270 in October 2025. | Source/field review; likely strike or move later DBHs unless same dead pine is confirmed. |
| M7/319 | Dead Juniperus 111.5, isolated June 2022 DBH 136, then 109-113. | Strike/correct June 2022 DBH 136; preserve dead status. |
| H1/243 | Pine 388 in 2019-2020, June 2021 DBH 76, then 374-386. | Strike/correct June 2021 DBH 76. |
| H3/155 | Nyssa 280 in 2019-2020, stable ~209-217 later, May 2024 DBH 270. | Source review; likely strike/relocate early 280 and May 2024 270. |
| H3/160 | Large pine ~493-501, May 2024 DBH 407, then back to ~491-496. | Strike/correct May 2024 DBH 407. |
| H4/150 | H4 pine 67 in 2019-2020, then stable 377-395; May 2024 DBH 338. | Add to H4 source-era block; source review/strike early 67 and May 2024 338 unless supported. |
| L1/5060 | Juniperus 96, June 2022 DBH 130, then stable 101-103. | Strike/correct June 2022 DBH 130. |
| L5/405 | Juniperus ~87-96 except June 2022 DBH 169. | Strike/correct June 2022 DBH 169. |
| L5/414 | Nyssa ~92-98, May 2024 DBH 63, then dead at ~94-95. | Strike/correct May 2024 DBH 63; preserve later death rows. |
| L5/5049 | Juniperus 156/178/165, May 2024 DBH 115, then 162-173. | Strike/correct or mark uncertain May 2024 DBH 115. |
| L6/50 | Juniperus ~67-74, May 2024 DBH 50, then back ~70. | Strike/mark May 2024 DBH 50 uncertain; keep October 2025 death separate. |
| L6/77 | Juniperus early 225, then ~110-133, June 2023 DBH 133 before death in 2025. | Source review early 225; review/strike June 2023 DBH 133 if unsupported. |
| L6/83 | Juniperus source-era shift plus June 2022 DBH 281 before later fall due to girdling. | Source review early 98.5; strike/correct June 2022 DBH 281. |
| L7/21 | Juniperus ~57-69 except June 2022 DBH 100. | Strike/correct June 2022 DBH 100. |
| L7/3 | Juniperus ~97-106 except May 2024 DBH 199. | Strike/correct May 2024 DBH 199. |
| H2/186 with H2/191 | Notes repeatedly say 186/191 may be one tree or multistem tree; H2/186 also has May 2024 duplicate 52/52. | Review as paired tag/stem-scope case; likely suppress May 2024 duplicate for H2/186 only after deciding the 186/191 relationship. |
| M3/349 | June 2021 DBH 418 inside otherwise stable ~515 large pine. | Strike/correct June 2021 DBH 418; correct to 518-ish only if source supports it. |
| M4/2453 | June 2021 DBH 428 inside otherwise stable ~520-537 large pine. | Strike/correct June 2021 DBH 428; correct to 528-ish only if source supports it. |
| M6/362 | June 2020 DBH 155 and June 2023 DBH 162 inside otherwise ~120-128 Juniperus series. | Source review; likely strike/correct both high outliers. |
| M6/363 | June 2019 DBH 365 and June 2020 DBH 180.5 before stable modern 144-151 Juniperus series. | Source-era/tag review; likely strike/relocate 2019 and review 2020. |
| M6/397 | Pine 270/270 in 2019-2020, then stable 202-208 from 2021 onward. | Source-era review early 270s. |
| M6/399 | Juniperus 56/56 in 2019-2020, then 160+ from 2021 onward. | Check whether early 56 should be 156; otherwise mark early DBH uncertain/source-era. |
| M6/400 | Nyssa 56/56 in 2019-2020, then stable 174-181 from 2021 onward. | Source-era review early 56s; possible missing-leading-digit or tag alignment. |
| M7/317 | June 2022 DBH 138 inside otherwise ~192-197 pine series. | Strike/correct June 2022 DBH 138. |
| R4/5236 | October 2024 DBH 58 inside otherwise 93-94 Nyssa series. | Strike/correct October 2024 DBH 58. |

## Systematic source-era review blocks

These look bigger than per-tree typos and should be checked against raw/source sheets as a group.

| Block | Issue | Current leaning |
|---|---|---|
| H4 tags 136-150, 2019-2020 DBHs | Many 2019-2020 DBHs are biologically incompatible with stable 2021 onward trajectories. Examples: H4/144 136 -> 519+, H4/148 67 -> 371+, H4/145 372 -> 104. | Treat as systematic source/tag alignment problem; source review/strike or relocate early DBHs as a block. |
| H1 persistent regime shifts | H1/233, H1/235, H1/239, H1/241 have stable 2019-2020 plateaus followed by incompatible but stable 2021 onward DBHs. | Source review early DBHs; likely strike/relocate the 2019-2020 measurements where no compatible source support exists. |
| Broader early-regime source shifts | H5/550, H7/887, L1/116, L1/146, L4/247, and L4/248 show the same stable 2019-2020 vs incompatible stable 2021+ pattern. | Source review as grouped era/tag-alignment candidates rather than isolated biological changes. |
| H4/152 inverse regime issue | H4/152 has 2019-2020 and 2023+ near 99, but 2021-2022 near 61-64. | Source review/strike or mark uncertain the 2021-2022 DBHs; grouped diagnostic should handle incompatible middle eras too. |
| L6/L7 early-regime source shifts | L6/61, L6/69, L6/70, L6/77, L6/83, L7/18, L7/20, and L7/7 show stable incompatible early vs later DBH regimes. | Add to stable-incompatible-era grouped diagnostic; source review/strike or relocate early-era rows where unsupported. |
| M1 middle-era regime issue | M1/831 has 390/380, then 315 in 2022-2023, then back to 387-392. | Source review/strike or mark uncertain the 2022-2023 middle-era DBH regime. |

## Policy/watch cases

These are worth tracking but probably should not block canonical progress.

| Pattern | Cases | Likely treatment |
|---|---|---|
| Threshold-edge live trees | H1/224, H1/231, H6/540, L0/192 | Suppress subthreshold DBHs from qualifying profile; keep alive evidence; downgrade to watch. |
| Dead-tree DBH gaps/loss | H1/250, H6/530, M0/578, M6/387 | Preserve as structural/measurement context; downgrade unless rebound-shaped or contradicted by notes. |
| Poison ivy / vine / parasite measurement | L5/422, M6/384, M6/387 | Preserve notes and avoid deterministic correction unless a value is clearly impossible. |
| Knot / split / non-circular trunk measurement | L4/462, M0/513 | Route as measurement context; source review for extreme outliers. |
| New October 2025 tree | R2/5303 | Search for compatible missing prior tree; otherwise accept as new qualifying tree. |
| Cluster / clump measurement | H0/274 | Treat as measurement/stem context; early DBH may not be comparable to later ranked stems. |
| Persistent newly noticed secondary stem | H1/242 | Insert/watch blank rank-2 history rather than urgent identity review when later surveys are consistent. |
| Low sprout / ivy sprout mortality context | M7/336 | Notes like `ivy sprouted low` may describe marginal/low live tissue and should not automatically imply whole-tree revival. |
| Structural measurement context | L7/32, M1/860 | Notes like horizontal/falling/bent/elbow/girdling can create DBH regime shifts; keep human-readable context and avoid auto-correction. |

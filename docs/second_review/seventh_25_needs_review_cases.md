# Seventh 25 rebuilt needs-review cases

Date: 2026-05-10

Scope: next 25 rebuilt `needs_review` plot/tag cases not already mentioned in first- or second-review notes. This pass shifts from mortality into stem-profile, threshold, and dead-tree first-DBH cases.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| M1/872 | DBH regime shift 182 -> persistent ~80-95; health rebound but all rows alive. | Not a mortality issue. This is an old-source/identity/DBH regime shift. | Human DBH/source review for early 182 values; downgrade alive-to-alive health rebound. |
| M5/2496 | June 2021 dead/0 row between alive rows; October 2024 DBH 318 between ~200 values. | Two likely one-row problems: death-label blip and DBH outlier. | Source/correction candidate: review June 2021 status and strike/correct October 2024 DBH 318. |
| L6/503 | Morella gains qualifying second stem; third stems are subthreshold 41-46. | Looks like real multi-stem shrub/tree crossing threshold; subthreshold stems should not contribute. | Keep second qualifying stem; suppress subthreshold DBHs; route to watch/policy, not urgent human review. |
| M0/484 | Threshold-edge Nyssa: 47, then 50-51, then 45-47. | This is a threshold-edge live tree. First-qualifying-after-prior-observation is expected here. | Downgrade to threshold watch; suppress subthreshold DBHs but preserve live evidence. |
| R1/960 | One stem in 2023; May 2024 has 182/182/170; later stable two stems ~184/169. | May 2024 has an extra duplicated 182, but the second ~170 stem is real/persistent. | Suppress only the extra May 2024 duplicate 182; keep two-stem structure and consider blank back-history for second stem. |
| R2/612 | Ilex with large stem and threshold second stem 48/49/50. | Second stem crosses threshold in 2025; prior subthreshold values should not qualify. | Threshold watch; keep second stem from 50 onward, no correction needed. |
| R3/664 | Nyssa stays 49 until April 2025, then 52 and dead/girdled. | Threshold-edge tree that qualifies only at death/girdling. | Downgrade to threshold watch; no source correction. |
| R4/5222 | Multi-stem Ilex; second stem absent May 2024, then returns; third stem subthreshold. | May 2024 likely under-recorded the second stem. Third stem remains subthreshold. | Stem-profile review/watch; consider blank missing stem for May 2024, suppress third-stem subthreshold DBH. |
| H4/130 | Long-dead tree, DBH gap/loss, then October 2025 has two large dead stems 211/209. | Dead-tree measurement context, but the sudden two large stems may be double-measurement or true fallen/log split. | Human/source review for October 2025 two-stem dead profile; otherwise dead-tree DBH loss is valid context. |
| H7/890 | Two-trunk dead Nyssa; later only one large dead stem measured. | Second trunk likely no longer measurable/recorded. Dead-tree stem disappearance should be lower severity. | Downgrade dead-stem disappearance to watch unless source suggests wrong tag. |
| L1/5059 | Dead/no DBH first, then dead DBH 80/74/73. | Earlier dead rows simply lacked DBH; later field workers measured the dead stem. | Downgrade first-qualifying-after-prior-dead to watch. |
| L5/5046 | Dead/no DBH until dead Pinus DBH 336/315. | Same dead-tree first-measured pattern. | Downgrade to watch; no correction. |
| L7/19 | Dead Juniperus 50, then June 2022 DBH 112, then later 47-49. | June 2022 DBH 112 is suspicious against 50/47/49. | Source/correction candidate: strike/correct June 2022 DBH 112. |
| L7/5033 | Dead/no DBH, then dead Juniperus DBH 84-87. | Dead-tree first-measured pattern with species later clarified. | Downgrade to watch; no correction unless source says tag switch. |
| L7/5035 | Dead/no DBH, then dead DBH 103/101 after one unfound row. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L7/5036 | Dead/no DBH, later dead DBH 62/71 with poison ivy/species change note. | Dead-tree first-measured pattern plus note context. | Watch/species-note context; no immediate correction. |
| L7/5040 | Dead/no DBH, later dead DBH 60/58 with species change note. | Dead-tree first-measured pattern. | Downgrade to watch. |
| M6/5830 | Dead/no DBH, later dead DBH 73/77; notes say change to Juniperus. | Dead-tree first-measured pattern with species clarification. | Watch; no correction. |
| R4/5202 | Dead/no DBH, then dead Juniperus DBH 63-65. | Dead-tree first-measured pattern. | Downgrade to watch. |
| R4/5211 | Dead/no DBH, then dead DBH 141/139 with gaps. | Dead-tree first-measured pattern. | Downgrade to watch. |
| R4/5215 | Dead/no DBH, then dead Liquidambar DBH ~99-101; already corrected species. | Dead-tree first-measured pattern. | Downgrade to watch. |
| R4/5234 | Dead/no DBH, then dead Pinus DBH 164-167; note `snapped`. | Dead-tree first-measured pattern with structural note. | Downgrade to watch. |
| R4/5239 | Dead/no DBH, then dead Acer DBH 84/78. | Dead-tree first-measured pattern. | Downgrade to watch. |
| H0/260 | Nyssa DBH dips to 210, May 2024 duplicate 200/200 with poison ivy, then returns to 260. | May 2024 likely poison-ivy measurement/duplicate artifact; June 2023 210 may also be measurement-access related. | Source/measurement review; likely suppress extra May 2024 duplicate and treat poison ivy as explanatory context. |
| H0/5841 | Alive Ilex first observed without DBH, then stable ~91-101; note `knot@dbh`. | First-qualifying-after-prior-observation is just missing first DBH. | Watch/blank-history candidate, not urgent review. |

## What this pass teaches

`first_qualifying_after_prior_observation` needs to distinguish prior alive evidence from prior dead evidence. If the earlier rows are all observed dead/no DBH and later rows are dead with DBH, that is usually not a problem: it is just delayed measurement of a dead stem.

Threshold-edge live trees and threshold-edge second stems should usually be watch/policy cases. They become review only if the tree never really qualifies, if the threshold crossing is implausible, or if a subthreshold stem is being treated as a canonical qualifying stem.

Dead-tree stem disappearance also needs gentler routing. A dead second trunk disappearing from measured profiles can be decay/access/field-sheet behavior, not necessarily a canonical identity problem.

## Suggested rule changes

- Split `first_qualifying_after_prior_observation` into prior-live and prior-dead subtypes.
- Downgrade prior-dead -> later-dead-with-DBH cases to watch.
- Add threshold-edge watch handling for stems hovering around 48-52 mm.
- Add dead-tree stem disappearance watch handling when all involved surveys are observed dead.
- Treat poison ivy notes as explanatory context for temporary duplicate/low DBH measurements, not just generic notes.

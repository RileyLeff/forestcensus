# Fourteenth needs-review batch

Date: 2026-05-10

Scope: all remaining current `needs_review` plot/tag labels that were not already mentioned in the second-review notes or human-attention queue after the second consolidation. There were 19 unseen labels rather than a full 25.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| H2/186 | Early 94/94 DBH, then stable 52-57; repeated notes say 186/191 may be one tree or multistem tree; May 2024 duplicate 52/52. | This is probably tag/cluster/stem-scope ambiguity around H2/186 and H2/191, not ordinary growth. The May 2024 duplicate is likely an extra-stem artifact. | Review H2/186 with H2/191 together; likely suppress May 2024 extra 52 stem. Do not auto-correct the early 94 until the 186/191 relationship is decided. |
| M3/339 | Low-health Nyssa alive, October 2024 dead/0, then alive health 2/1; poison-ivy context. | Classic low-health one-survey death-label outlier. | Treat October 2024 dead/0 as uncertain or alive-low-health unless source confirms death. |
| M5/2500 | Nyssa alive health 3 in May 2024, October 2024 dead/0, April 2025 alive health 3, October 2025 dead/0. | October 2024 looks like a single-survey death-label outlier; October 2025 may be a later real death. | Correct/reinterpret October 2024 separately from October 2025. |
| H3/170 | Long-dead pine 224/218 early, then dead DBH 183/185 in 2024-2025. | This is probably dead-tree DBH loss/changed measurement, not a source-era identity problem. | Downgrade all-dead decreasing stable-era cases to dead-tree DBH-loss context; preserve values unless source says otherwise. |
| L2/207 | Long-dead pine 119/115 early, then 95/91 in 2024-2025. | Same all-dead decreasing stable-era pattern. | Downgrade to dead-tree DBH-loss context. |
| L6/103 | Long-dead unidentified tree 290 early, later dead DBH 213/212, notes `standing but broken` and `Brok of BH`. | Dead structural loss/change in measurement point is plausible. | Downgrade to structural/dead-tree DBH-loss context; no source correction yet. |
| M0/587 | Long-dead Juniperus 122 early, later stable 79-82. | Same all-dead decreasing stable-era pattern, but size change is large. | Keep visible as dead-tree DBH-loss context; source review only if nearby tag evidence suggests misassignment. |
| M4/2456 | Long-dead pine 102 early, later 79/79. | Same all-dead decreasing stable-era pattern. | Downgrade to dead-tree DBH-loss context. |
| M3/349 | Large pine ~515, one June 2021 DBH 418, then back to ~516. | Clear isolated DBH outlier. | Strike June 2021 DBH 418, or correct only if source gives a clear 518-style reading. |
| M3/603 | New 2024 Morella with three stems; rank-3 DBH 50 -> 63 -> 50; October 2024 note `347.2` on dead largest stem. | Ranked-stem jump is probably stem/rank instability in a Morella cluster. The `347.2` note may indicate a tag/stem relationship to M3/347, but DBHs do not obviously match the old M3/347 profile. | Keep as tag/cluster context; review M3/603 beside M3/347 before any identity operation. Do not treat rank-3 jump as a simple typo. |
| M4/2453 | Large pine ~520-537, one June 2021 DBH 428, then back to ~520. | Clear isolated DBH outlier. | Strike June 2021 DBH 428, or correct only if source supports 528-ish value. |
| M6/362 | Juniperus mostly ~120-128, but June 2020 DBH 155 and June 2023 DBH 162. | Two isolated high DBH outliers in an otherwise stable small Juniperus. | Source review; likely strike/correct June 2020 155 and June 2023 162. |
| M6/363 | Juniperus 365 in 2019, 180.5 in 2020, then stable 144-151 from 2021 onward. | Source-era/tag-alignment problem with a one-year extreme plus a transitional high year; current stable-era rule misses part of this shape. | Source review; likely strike/relocate 2019 365 and review 2020 180.5. |
| M6/397 | Pine 270/270 in 2019-2020, then stable 202-208 from 2021 onward. | Stable incompatible live DBH eras. | Source-era review; likely strike/relocate early 270 DBHs if unsupported. |
| M6/399 | Juniperus 56/56 in 2019-2020, then 160+ from 2021 onward. | Early values may be missing a leading `1` or may be source/tag-alignment noise; repeated 56 makes this a carried-forward source issue. | Source review; consider correcting early 56 to 156 if source/handwriting supports it, otherwise mark early DBH uncertain. |
| M6/400 | Nyssa 56/56 in 2019-2020, then stable 174-181 from 2021 onward. | Same repeated low early-regime issue, likely source/tag alignment or missing-leading-digit error. | Source review early 56 values; keep modern 174-181 regime. |
| M7/317 | Pine ~192 throughout, one June 2022 DBH 138. | Clear isolated DBH outlier. | Strike/correct June 2022 DBH 138. |
| M7/318 | Nyssa dead in 2019-2020, alive low-health 2021-May 2024, then dead from October 2024 onward. | Early dead labels are likely wrong or uncertain; later death may be real. | Correct/reinterpret 2019-2020 dead rows separately from later October 2024 death. |
| R4/5236 | Nyssa 94/93, one October 2024 DBH 58, then back to 94/93. | Clear isolated DBH outlier. | Strike/correct October 2024 DBH 58. |

## What this pass teaches

- The stable-era rule is useful, but it over-flags all-dead trees whose DBH decreases into a new stable lower regime. Those should usually become dead-tree DBH-loss or structural-measurement context, not urgent source-era identity review.
- Repeated early 56/56 values followed by modern 160-180 values may be a specific source-era subtype: either missing-leading-digit carry-forward or tag alignment, rather than a one-off typo.
- Morella/cluster ranked-stem jumps need a softer route. Rank-local jumps in a multistem cluster can be real stem-order instability, especially when stems are similar in size.
- The low-health one-survey death-label rule is finding the right cases. It should remain rule-assisted/context unless the tree stays dead afterward.

## Suggested rule changes

- Add a `dead_tree_stable_dbh_loss_context` route: if both incompatible DBH eras are observed-dead/deadish and the later era is lower, downgrade from `stable_incompatible_dbh_era`.
- Add a source-era subtype for repeated early low values followed by a much larger modern stable regime, especially when the early value could plausibly be missing a leading digit.
- Downgrade ranked DBH jumps for multistem Morella/cluster cases when the tree has only a short modern history and no taxon/identity conflict.

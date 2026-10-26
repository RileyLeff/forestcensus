# Second review: third 25 needs-review cases

Date: 2026-05-10

Input ordering: cases 51-75 from the rebuilt UI-like `needs_review` queue in `output/canonical_review/tree_cases.csv`.

## Quick synthesis

Cases 51-67 are almost entirely explicit tag-change endpoints, mostly dead trees with no recent DBH. Many are the old or new side of links already seen in the first two second-review files. This is now very strong evidence that link review should become a separate artifact/table.

Cases 68-75 are more data-focused. The interesting patterns are:

- dead-tree DBH jumps that are partly real decay/loss and partly obvious old entry errors,
- new tags on multi-stem shrubs where the tag may be on a different trunk than the old DBH rank,
- early multi-stem histories where one stem disappears/reappears because the old sheets under-recorded stems,
- one clean isolated DBH typo candidate: L1/110 October 2024 132 mm.

## Cases

### 51. L2/210

Bucket: `candidate_identity_link`

Link: `L2/210 -> L2/928`, explicit tag-change assertion.

History: old L2/210 is dead/unidentifiable, 95 mm in 2019, then not found or inferred dead. Target L2/928 was reviewed earlier as dead Juniperus around 70-75 mm.

Impression: plausible dead-tree retag, but this tag has shown duplicate/noise elsewhere, so it should stay link-reviewed rather than auto-accepted blindly.

Suggested action: review as one link with L2/928; likely accept if no overlapping source evidence conflicts.

### 52. L3/284

Bucket: `candidate_identity_link`

Link: `L3/284 -> L3/1000`, explicit tag-change assertion.

History: dead Juniperus, 88 mm in 2019-2020, then dead/no DBH or missing. Target L3/1000 is dead Juniperus around 70-72 mm.

Impression: plausible small dead-tree retag.

Suggested action: likely accept link.

### 53. L3/301

Bucket: `candidate_identity_link`

Link: `L3/301 -> L3/918`, explicit tag-change assertion.

History: dead Nyssa, 105 mm in 2019-2020, then dead/no DBH/inferred dead. Target L3/918 is the later dead Juniperus/Nyssa-reviewed case around 60-61 mm.

Impression: plausible but taxon/identity history has already been messy here.

Suggested action: review with L3/918 and source notes before accepting.

### 54. L4/243

Bucket: `candidate_identity_link`

Link: `L4/243 -> L4/925`, explicit tag-change assertion.

History: old dead Pinus 332 mm in 2019-2020, then dead/no DBH. Target L4/925 is dead Pinus around 90-93 mm.

Impression: same large-mismatch link seen from the old side. 332 -> 90 is too big to auto-accept even for a dead/fallen tree.

Suggested action: manual source/nearby-tree review before accepting.

### 55. L5/985

Bucket: `candidate_identity_link`

Link: `L5/413 -> L5/985`, explicit tag-change assertion.

History: target is dead/not-found Juniperus with no DBH from 2023 onward. Source L5/413 is dead Juniperus around 83-85 mm.

Impression: plausible dead-tree retag.

Suggested action: likely accept as link/alias.

### 56. L7/33

Bucket: `candidate_identity_link`

Link: `L7/33 -> L7/908`, explicit tag-change assertion.

History: old dead Pinus 422 mm in 2019-2020, then dead/no DBH/inferred dead. Target L7/908 is dead Pinus around 365-371 mm with `dangerous to DBH` note.

Impression: plausible dead-tree retag with reasonable DBH reduction.

Suggested action: likely accept.

### 57. L7/39

Bucket: `candidate_identity_link`

Link: `L7/39 -> L7/973`, explicit tag-change assertion.

History: old dead Pinus 321 mm in 2019-2020, outside-plot note in 2020, then missing/inferred dead. Target has no DBH.

Impression: plausible but target contributes only dead/no-DBH evidence.

Suggested action: accept only as a provenance/alias link if no overlap conflict; do not invent target DBH continuity.

### 58. L7/506

Bucket: `candidate_identity_link`

Link: `L7/506 -> L7/974`, explicit tag-change assertion.

History: source is alive Pinus 312 mm in 2021, then missing/no GPS and inferred dead. Target L7/974 is dead/no DBH in 2023-2025.

Impression: plausible tag-change/mortality continuation, but source has an alive-to-missing transition rather than a long dead history.

Suggested action: review as link; accept if target represents the same tree found dead later.

### 59. L7/973

Bucket: `candidate_identity_link`

Link: `L7/39 -> L7/973`, explicit tag-change assertion.

History: target dead/no DBH from 2023 onward, April 2025 DNF.

Impression: target side of case 57.

Suggested action: review once with L7/39; likely accept as dead/no-DBH continuation.

### 60. L7/974

Bucket: `candidate_identity_link`

Link: `L7/506 -> L7/974`, explicit tag-change assertion.

History: target dead/no DBH in 2023-2024, unknown/missing pending in October 2025.

Impression: target side of case 58.

Suggested action: review once with L7/506.

### 61. M0/813

Bucket: `candidate_identity_link`

Link: `M0/813 -> M0/909`, explicit tag-change assertion.

History: old dead Ilex, 57 mm in 2019-2020, then dead/no DBH and inferred dead. Target M0/909 was excluded as nonqualifying with 33-35 mm dead values.

Impression: plausible small dead-tree retag but target is below survey threshold.

Suggested action: accept link as provenance if desired; keep target DBHs nonqualifying.

### 62. M3/911

Bucket: `candidate_identity_link`

Link: `M3/359 -> M3/911`, explicit tag-change assertion.

History: target dead Juniperus/no DBH, April 2025 note `fallen`. Source M3/359 has mortality contradiction due to October 2024 alive health 6.

Impression: link cannot be cleanly resolved until source mortality issue is handled.

Suggested action: review with M3/359; likely correct or question October 2024 alive status before accepting.

### 63. M5/2477

Bucket: `candidate_identity_link`

Link: `M5/2477 -> M5/910`, explicit tag-change assertion.

History: old dead Pinus/unidentified-ish source, 267 mm in 2019-2020, then dead/no DBH. Target M5/910 is dead/no DBH unidentifiable.

Impression: plausible dead-tree retag, but taxon hint may be weaker than the many exact Pinus links.

Suggested action: likely accept if source/target notes agree that this is the same dead tree.

### 64. M5/2484

Bucket: `candidate_identity_link`

Link: `M5/2484 -> M5/972`, explicit tag-change assertion.

History: old dead Pinus 301 mm in 2019-2020, with note `correct size + dead no tag`, then dead/no DBH. Target M5/972 is dead/no DBH.

Impression: good explicit retag candidate.

Suggested action: likely accept.

### 65. M5/904

Bucket: `candidate_identity_link`

Link: `M5/2470 -> M5/904`, explicit tag-change assertion.

History: target dead/no DBH, May 2024 note `confirmed kill`, April 2025 DNF. Source M5/2470 is old dead Pinus 303 mm.

Impression: plausible dead-tree retag.

Suggested action: likely accept.

### 66. M5/910

Bucket: `candidate_identity_link`

Link: `M5/2477 -> M5/910`, explicit tag-change assertion.

History: target dead/no DBH unidentifiable, April 2025 DNF.

Impression: target side of case 63.

Suggested action: review once with M5/2477; likely accept if taxon/source context fits.

### 67. M7/5832

Bucket: `candidate_identity_link`

Link: `M7/5832 -> M7/914`, explicit tag-change assertion.

History: source is dead Juniperus/no DBH in 2021-2024. Target M7/914 is dead Juniperus with 171/173 mm in 2024.

Impression: plausible retag, though source has no DBH to compare.

Suggested action: likely accept if no overlap conflict.

### 68. H1/250

Bucket: `dbh_review`

History: unidentifiable tree, alive 70 mm in 2019-2020, dead/no DBH in 2021, dead 58 in 2022, dead/no DBH in 2023, dead 57 in 2024-2025.

Impression: this is mostly a dead-tree measurement gap and moderate DBH loss after death.

Suggested action: downgrade to watch/dead-tree DBH context. No obvious correction needed.

### 69. M7/320

Bucket: `dbh_review`

History: Juniperus alive 239 mm in 2019-2020, newly dead/no DBH in 2021, then 451 mm in 2022, later notes say `dbh approx. 200 not 450` and `200 range, not 450`, with October 2024 DBH 214.

Impression: June 2022 451 is almost certainly wrong. The later notes explicitly tell us not 450.

Suggested action: correct/strike June 2022 451. Given later notes, likely set to missing rather than invent 200-ish unless original sheet supports a specific value.

Teaches us: notes that directly negate a DBH value should promote a per-case correction.

### 70. M7/5274

Bucket: `dbh_review`

History: Morella, new in April 2025 with two stems 120/55, notes `new` and `tag on trunk 2`. October 2025 has 54 alive with note `new tag 795`, plus a no-DBH dead second row.

Impression: likely tag/stem identity problem. The tag may have moved to trunk 2 or a new tag was assigned, causing the 120 mm stem to disappear and the 55-ish stem to become rank 1.

Suggested action: manual identity/tag review, probably with tag 795. Do not treat this as simple DBH shrinkage.

Teaches us: notes like `tag on trunk 2` and `new tag N` should create a tag-change/stem-scope review, not DBH review alone.

### 71. R4/5261

Bucket: `dbh_review`

History: dead Liquidambar, no DBH in 2023/April 2025, 52 mm in October 2024, 81 mm in October 2025 with note `No sprout`.

Impression: dead-tree first-DBH-after-dead-evidence plus a 52 -> 81 jump. Could be measurement-location/remaining-stub issue, but not enough context.

Suggested action: keep manual review. Original sheet/context may clarify whether October 2024 52 or October 2025 81 is a bad value.

### 72. H4/151

Bucket: `dbh_review`

History: Acer rubrum, 2019 note `two trunks` with 102/67, then June 2020-2021 has one live Acer stem plus a dead/unidentified row, then from 2022 onward stable two-stem Acer around 90/60.

Impression: early multi-stem source/identity muddle. The modern two-stem profile is stable; June 2021 56 mm as rank 1 is the odd transition.

Suggested action: source review for 2020-2021 rows. Likely keep 2022+ as the stable canonical two-stem profile and treat early rows carefully.

### 73. H5/571

Bucket: `dbh_review`

History: Ilex, known two trunks. 2019 has 134/111, June 2020 only 111 with outside-plot note, then stable two stems around 107-120 and 103-115 from 2021 onward.

Impression: likely 2019/2020 source inconsistency, not ongoing data problem. Modern profile is stable.

Suggested action: review early source rows; likely keep two-stem history with a blank/missing second stem in June 2020 rather than treating it as disappearance.

### 74. H6/530

Bucket: `dbh_review`

History: Nyssa. Alive 64 mm with poor canopy/dead-ish notes in 2019-2020, dead/no DBH in 2021-2023, dead 50/53 in 2024, dead/no DBH in 2025.

Impression: dead-tree DBH gap and moderate loss from 64 to ~50 after death. This seems plausible.

Suggested action: downgrade to watch/dead-tree DBH context; no correction unless original source says otherwise.

### 75. L1/110

Bucket: `dbh_review`

History: Pinus, stable around 331-340 while alive, dead in 2023, May 2024 332 dead, October 2024 132 dead, April 2025 330 dead.

Impression: clean isolated DBH outlier. October 2024 132 should almost certainly be 332 or should be struck; given both neighboring values are 332/330, 332 is strongly supported.

Suggested action: correct October 2024 DBH 132 to 332, or strike if we want to avoid deterministic correction. I would correct to 332 because the trajectory is very clear.

## Rules learned or reinforced

1. Link endpoints are now flooding the review queue. We should review explicit tag-change assertions as link objects and suppress endpoint duplicates from the top queue.
2. Dead-tree DBH gaps and moderate post-mortality DBH loss should usually be watch, not needs-review.
3. Notes that explicitly contradict a DBH value, like `not 450`, should generate high-confidence per-case correction candidates.
4. `new tag N` and `tag on trunk N` notes should be routed as tag-change/stem-scope review.
5. Early multi-trunk source inconsistency should be treated differently from later modern stable multi-stem profiles.
6. Isolated rebound-shaped DBH outliers with clear adjacent support, like L1/110, are good correction candidates.

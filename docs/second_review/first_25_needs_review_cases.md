# Second review: first 25 needs-review cases

Date: 2026-05-10

Input ordering: first 25 rebuilt UI-like `needs_review` cases from `output/canonical_review/tree_cases.csv`, sorted by `priority_score` descending, then plot/tag. This is a review note only; no corrections are applied here.

## Quick synthesis

This batch is mostly not "25 unrelated bad trees." It is dominated by explicit historical tag-change assertions, and many linked pairs show up twice: once for the old UUID and once for the new UUID.

Immediate workflow lesson: candidate links should become their own review unit. A tag-change assertion like `old tag -> new tag` should be reviewed once as a link/merge/alias decision, with both UUID histories displayed side by side. Reviewing each endpoint separately doubles the work and makes simple retags look noisier than they are.

Suggested rule split:

- Auto-accept or downgrade explicit tag-change links when taxon is compatible, survey ranges do not conflict, and DBH difference is plausible for dead/fallen trees.
- Keep candidate links in human review when DBH differs drastically, old and new histories overlap as observed trees, old history is multi-stem, notes point to tag confusion, or there is a mortality/zombie contradiction.
- Treat `first_qualifying_after_prior_observation` on the new tag as likely tag-change/backfill context when an explicit old-tag link exists.

## Cases

### 1. R2/631

Bucket: `taxon_or_identity_conflict`

Pattern: threshold-edge Ilex becomes qualifying only in October 2025, but October 2025 also introduces an extra Pinus row with note text: `should be Pin 93 no Pin 6 in p`.

History: Ilex opaca at 45, 48, 49, 49, then 55 mm from June 2023 through October 2025. The Pinus row has no DBH/health and appears only in October 2025.

Impression: likely an October 2025 row/note association problem, not a real R2/631 species conflict. The Ilex tree looks real and just crosses the 50 mm threshold in October 2025.

Suggested action: keep R2/631 as Ilex opaca; suppress subthreshold DBHs from qualifying stem profile; inspect/move/exclude the October 2025 Pinus note row rather than treating it as taxon evidence for R2/631.

Teaches us: taxon conflicts from DBH-less October 2025 note rows should be a special review subtype.

### 2. L5/433

Bucket: `candidate_identity_link`

Link: `L5/433 -> L5/986`, explicit tag-change assertion, taxon match Pinus.

History: old L5/433 is dead Pinus, 239 mm in 2019-2020, then dead/no DBH and later missing. Target L5/986 is dead Pinus, 185/184 mm in 2024-2025.

Impression: plausible dead-tree retag with DBH loss or measurement-location change.

Suggested action: likely accept as an alias/link unless source evidence contradicts it. Review together with case 9, the target endpoint.

Teaches us: explicit tag-change links should be one review item, not two UUID cases.

### 3. L6/57

Bucket: `candidate_identity_link`

Link: `L6/57 -> L6/991`, explicit tag-change assertion, taxon match Unidentifiable/Juniperus-like.

History: old L6/57 is dead/unidentifiable at 56 mm in 2019-2020, then dead/no DBH. Target L6/991 is dead Juniperus at 54-55 mm in 2024.

Impression: very plausible retag of a small dead Juniperus/unidentified tree.

Suggested action: likely accept link. Review with case 20, the target endpoint.

### 4. M2/5883

Bucket: `candidate_identity_link`

Link: `M2/5883 -> M2/5863`, explicit tag-change assertion.

History: old M2/5883 is alive unidentified at 114-119 mm in 2021-2022. Target M2/5863 is alive around 121-127 mm before/after a May 2024 163 mm outlier.

Impression: likely same tree; May 2024 163 mm on the new tag looks like the real issue.

Suggested action: likely accept the tag link, and separately review/strike or correct May 2024 163 mm on M2/5863. Review with case 25.

### 5. M5/2470

Bucket: `candidate_identity_link`

Link: `M5/2470 -> M5/904`, explicit tag-change assertion.

History: old M5/2470 is dead Pinus, 303 mm in 2019-2020, then dead/no DBH. Target has no max DBH in the candidate-link table.

Impression: plausible retag, but target has too little measurement context in this view.

Suggested action: inspect M5/904 target history before accepting. If it is dead/no-DBH-only and non-overlapping, accept as an alias but do not invent DBH continuity.

### 6. M5/972

Bucket: `candidate_identity_link`

Link: `M5/2484 -> M5/972`, explicit tag-change assertion.

History: target M5/972 is dead/no DBH in 2023-2025, with April 2025 DNF.

Impression: likely a retag of a dead Pinus where the new tag carries mortality evidence but no DBH.

Suggested action: inspect M5/2484 source history; likely accept if the survey ranges and taxon are compatible.

### 7. H5/912

Bucket: `candidate_identity_link`

Link: `H5/559 -> H5/912`, explicit tag-change assertion, Acer match.

History: target H5/912 is dead Acer, no DBH in 2023-May 2024, 198 mm in October 2024, 184 mm in October 2025. It has a dead-tree gap plus first DBH after prior observed dead rows.

Impression: plausible retag, but the source H5/559 is multi-stem and had a 405 mm dead stem plus a 217 mm second stem in 2019. The target DBH near 198 mm may correspond to the smaller stem, not the whole old identity.

Suggested action: keep in manual review. This may require split/partial-alias semantics rather than a simple UUID merge.

### 8. L3/1000

Bucket: `candidate_identity_link`

Link: `L3/284 -> L3/1000`, explicit tag-change assertion.

History: target is dead Juniperus, 70-72 mm in 2024-2025, with earlier dead/no-DBH evidence.

Impression: plausible retag of a small dead Juniperus.

Suggested action: likely accept if L3/284 source is compatible.

### 9. L5/986

Bucket: `candidate_identity_link`

Link: `L5/433 -> L5/986`, explicit tag-change assertion.

History: target is dead Pinus, 185/184 mm in October 2024/2025, with earlier dead/no-DBH and April 2025 DNF.

Impression: same link as case 2, seen from target side.

Suggested action: review as one link with L5/433; likely accept.

### 10. L7/908

Bucket: `candidate_identity_link`

Link: `L7/33 -> L7/908`, explicit tag-change assertion.

History: target is dead Pinus, 371 mm in May 2024 and 365 mm in October 2025; October 2024 says `dangerous to DBH`.

Impression: plausible dead/fallen tree retag. Source max 422 mm to target 365-371 mm is not alarming for a dead/dangerous tree.

Suggested action: likely accept link.

### 11. H5/559

Bucket: `candidate_identity_link`

Link: `H5/559 -> H5/912`, explicit tag-change assertion.

History: source H5/559 has 405 mm dead stem and a 217 mm second stem in June 2019, then mostly dead/no DBH. Invariant flags include one stem disappearing after 2019.

Impression: not a simple retag. The old multi-stem source may contain a real second stem or two plant parts that later got confused with H5/912.

Suggested action: manual source review. Do not auto-merge all of H5/559 into H5/912 until the 2019 two-stem evidence is understood.

Teaches us: old multi-stem identities should block auto-accept of tag-change links when the new tag DBH matches only one old stem.

### 12. L0/905

Bucket: `candidate_identity_link`

Link: `L0/171 -> L0/905`, explicit tag-change assertion.

History: target is dead Pinus, first DBH 200 mm in April 2025, note `partially fallen`; old max is 268 mm.

Impression: plausible dead/fallen retag with DBH loss.

Suggested action: likely accept link, preserving no-DBH dead rows before the first measured target DBH.

### 13. L0/989

Bucket: `candidate_identity_link`

Link: `L0/177 -> L0/989`, explicit tag-change assertion.

History: target is dead Pinus, 200/196/196 mm in 2024-2025; source max 210 mm.

Impression: clean retag.

Suggested action: likely accept link.

### 14. L1/924

Bucket: `candidate_identity_link`

Link: `L1/144 -> L1/924`, explicit tag-change assertion.

History: target is dead Nyssa, 74-79 mm in 2024. Source max 64 mm.

Impression: plausible small dead-tree retag, with threshold-edge measurement variation.

Suggested action: likely accept link.

### 15. L1/927

Bucket: `candidate_identity_link`

Link: `L1/130 -> L1/927`, explicit tag-change assertion.

History: target is dead Pinus, 274/260 mm in 2024; source max 293 mm.

Impression: plausible dead-tree retag with modest DBH loss.

Suggested action: likely accept link.

### 16. L2/928

Bucket: `candidate_identity_link`

Link: `L2/210 -> L2/928`, explicit tag-change assertion.

History: target is dead Juniperus, 70-75 mm in 2024-2025; source max 95 mm.

Impression: plausible retag, though L2/210 should be checked because this tag has already had duplicate/noise cases elsewhere in the project.

Suggested action: inspect source L2/210 before accepting; likely okay if there is no overlap conflict.

### 17. L3/918

Bucket: `candidate_identity_link`

Link: `L3/301 -> L3/918`, explicit tag-change assertion.

History: target is dead Juniperus, 60-61 mm in 2024, with a June 2023 dead/no-DBH row and October 2024 `species change` note. Taxon was already manually resolved to Juniperus.

Impression: likely same dead tree if the DBH loss from source max 105 mm is believable. Because this was already reviewed taxonomically, the remaining question is identity continuity.

Suggested action: probably accept link if source L3/301 is a dead Juniperus/Nyssa-like predecessor and no better complementary candidate exists.

### 18. L3/919

Bucket: `candidate_identity_link`

Link: `L3/5029 -> L3/919`, explicit tag-change assertion.

History: target is dead Juniperus/unidentified, 101/104 mm in 2024-2025. Notes include `slightly outside plot strings` and `species change not jun`.

Impression: plausible but not automatic; plot-boundary and species-change notes make this a source/context case.

Suggested action: inspect source L3/5029 and original note context before accepting.

### 19. L4/925

Bucket: `candidate_identity_link`

Link: `L4/243 -> L4/925`, explicit tag-change assertion.

History: target is dead Pinus, 93/90 mm in 2025 after earlier dead/no-DBH rows; October 2024 note `rotten core standing`. Source max is 332 mm.

Impression: large DBH mismatch. Could be severe decay/remaining piece, but 332 -> 90 is too large to auto-accept.

Suggested action: manual review; search original sheets and nearby/complementary dead pines before accepting link.

### 20. L6/991

Bucket: `candidate_identity_link`

Link: `L6/57 -> L6/991`, explicit tag-change assertion.

History: target is dead Juniperus, 54-55 mm in 2024, with dead/no-DBH in 2023 and 2025.

Impression: same link as case 3 from target side; likely clean.

Suggested action: review once with L6/57; likely accept.

### 21. L7/5029

Bucket: `candidate_identity_link`

Link: `L7/5029 -> L7/982`, explicit tag-change assertion.

History: L7/5029 is alive in 2021 with health 2, dead in 2022, alive again in May 2024 and October 2025 with health 1. It has qualifying DBH gaps and a zombie diagnostic.

Impression: this is not primarily a tag-link problem; it is a mortality/zombie problem. Health 1 after dead rows could mean the dead labels were wrong or the tree was not found/confused.

Suggested action: manual mortality review before accepting link. This case should be routed as `mortality_contradiction`/zombie even if a tag-change assertion exists.

Teaches us: candidate identity links should not mask zombie/mortality issues.

### 22. M7/914

Bucket: `candidate_identity_link`

Link: `M7/5832 -> M7/914`, explicit tag-change assertion.

History: target is dead Juniperus, 171/173 mm in 2024, DNF in April 2025, dead/no DBH in October 2025.

Impression: plausible retag but source has no max DBH in the candidate table, so context is incomplete.

Suggested action: inspect M7/5832 source; accept if compatible and non-overlapping.

### 23. H4/136

Bucket: `candidate_identity_link`

Link: `H4/136 -> H4/992`, explicit tag-change assertion.

History: source H4/136 is Nyssa, 91 mm in 2019-2020, then 178/183 mm in 2021-2022, then inferred dead/missing in 2024. It has a persistent DBH regime shift.

Impression: tricky. The 91 -> 178/183 shift could be measurement identity confusion, and the linked target H4/992 has a May 2024 row noting `might be 136`.

Suggested action: manual pair review with H4/992. Do not auto-accept until the 2021-2022 jump and May 2024 note are reconciled.

### 24. H4/992

Bucket: `candidate_identity_link`

Link: `H4/136 -> H4/992`, explicit tag-change assertion.

History: target H4/992 is Nyssa, 187 in 2023, 111 in May 2024 with note `might be 136`, then 194/192/200 in later surveys. May 2024 is an isolated DBH outlier.

Impression: May 2024 111 likely belongs to H4/136 or is a bad measurement/tag note, while the rest of H4/992 is a stable ~190-200 mm tree.

Suggested action: likely strike or move May 2024 111 after original-sheet review; review together with H4/136.

### 25. M2/5863

Bucket: `candidate_identity_link`

Link: `M2/5883 -> M2/5863`, explicit tag-change assertion.

History: target is alive, around 121-127 mm in 2023/2025 and 125 mm in October 2024, with May 2024 at 163 mm. October 2025 has two no-DBH rows with mixed Unidentifiable/Juniperus labels and note `J.vir`.

Impression: likely same tree as M2/5883, with May 2024 163 mm as an isolated outlier and October 2025 taxon/stem representation noise.

Suggested action: likely accept tag link; review May 2024 163 mm as a candidate DBH correction/strike.

## Rules learned or reinforced

1. Candidate-link review should be link-scoped, not endpoint-scoped.
2. High-confidence explicit retags can probably become `watch` or auto-accepted alias proposals when taxon matches, survey ranges are compatible, and DBH changes are plausible.
3. Multi-stem source histories should block auto-accept because a new tag may correspond to one old stem, not the whole old UUID.
4. Zombie/mortality issues should outrank candidate-link status.
5. October 2025 DBH-less taxon rows with notes can create false taxon conflicts and need their own diagnostic subtype.
6. `first_qualifying_after_prior_observation` is often a tag-change/backfill artifact when the new tag has prior dead/no-DBH rows and an explicit old-tag link.

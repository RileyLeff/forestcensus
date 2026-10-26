# Next 25 needs-review tags

Date: 2026-05-10

Scope: bare tags 26-50 in the current `Tags -> needs_review` UI ordering. As with the first memo, bare tags are being used as a discovery surface. Decisions should be scoped to UUID/tag-plot, especially where one bare tag combines multiple plots.

The tags in this pass are: 181, 182, 183, 184, 185, 186, 187, 189, 190, 191, 193, 194, 196, 201, 202, 203, 204, 206, 207, 220, 255, 256, 258, 261, and 262.

## Additional process rules suggested by this pass

### 1. May 2024 duplicate-stem batch artifact

The transient exact duplicate-stem rule is now much stronger. A large fraction of this batch has the same shape:

- one stable stem before May 2024
- May 2024 gains a second stem with exactly the same DBH and usually the same health
- the second stem disappears by October 2024

This occurs on H2/181, H2/182, H2/183, H2/184, H2/185, H2/186, H2/187, H2/189, H2/190, H2/191, H2/193, H2/194, H2/196, H2/201, H2/202, H2/203, H2/204, H2/206, H2/207, H0/255, H0/256, H0/258, and H0/261.

Suggested handling: treat this as a batch-level correction candidate. The UI should still show the duplicate row and evidence, but these can be pre-classified as probable duplicate-entry stems. The action should probably be "suppress duplicate stem for canonical DBH/stem count" rather than "delete evidence".

### 2. Cluster notes should override automatic confidence

Tags H2/185 through H2/191 have notes like "191-186 could be one tree", "186-191 likely one multistem tree", and "185-191 same tree". These are not just isolated duplicate rows. They may represent a plant-boundary or tag-boundary issue where field workers were repeatedly uncertain whether several tags belonged to one multi-stem organism.

Suggested handling: duplicate rows inside this cluster can still be flagged, but the UUID-level review should surface tags 185-191 together. Do not automatically merge identities, and do not automatically strike all cross-tag ambiguity. This is exactly the kind of place where tag-level noise helps find UUID-level problems.

### 3. Dead-tree DBH gaps are still overflagged

Several same-bare-tag cases are dead or inferred-dead trees with intermittent DBH measurement: L0/181, L0/186, L0/194, L2/201, L2/206, L2/207, L2/220, and H0/262.

Suggested handling: downgrade DBH-gap-only findings for dead trees unless there is an alive/dead contradiction. If health/status says dead throughout, intermittent DBH is usually a measurement/finding artifact, not an identity problem.

### 4. Mortality contradictions need their own queue

Some dead-tree cases also have true mortality contradictions. L0/181 has observed dead, then October 2024 alive with health 5, then dead again. L0/186 has dead observations followed by a June 2023 alive/health 6 observation and later dead observations. Those are not DBH problems.

Suggested handling: route these to the zombie/dead-alive queue. The correction might be to change the isolated alive observation, or to reinterpret early death labels, but that call should be made from the mortality evidence, not the stem-count diagnostic.

### 5. Missing DBH with alive/health evidence is valid evidence

Several living trees have October 2025 health/alive evidence with missing DBH, especially H0/255, H0/258, and H0/261. We later clarified that October 2025 is the transition survey where DBH collection stopped partway through, so missing DBH from that point onward is protocol-valid, not a source artifact or invalid observation.

Suggested handling: keep the observation in canonical history with missing DBH. Do not let it create false stem disappearance unless the tree has a repeated missing pattern or a conflicting mortality signal.

## Tag-by-tag notes

### Tag 181

Cases: H2/181 and L0/181.

H2/181 is a Nyssa with a stable single stem around 84-92 mm. May 2024 has 85/85, then it returns to one stem. That is a clean transient duplicate-stem case. L0/181 is a dead juniper with a true mortality contradiction: dead in 2019-2023, alive/health 5 in October 2024, then dead again.

Suggested action: suppress or review-strike the H2/181 May 2024 duplicate stem. Send L0/181 to mortality/zombie review rather than DBH-gap review.

Process lesson: bare tag review correctly surfaces two distinct issues under the same tag, but actions must land on the two UUIDs separately.

### Tag 182

Case: H2/182.

H2/182 is a large Pinus taeda with one stable stem. May 2024 has 294/294, then October 2024 returns to one stem. Health is consistently alive but declining/moderate.

Suggested action: suppress or review-strike the May 2024 duplicate stem.

Process lesson: classic May 2024 duplicate-stem artifact.

### Tag 183

Case: H2/183.

H2/183 is another large pine. One stable stem, with a note about a crooked trunk. May 2024 has 321/321 and then returns to one stem.

Suggested action: suppress or review-strike the May 2024 duplicate stem.

Process lesson: notes like "crooked trunk" may explain measurement variation, but they do not explain an exact duplicate extra stem.

### Tag 184

Case: H2/184.

H2/184 is a Nyssa with one stable stem around 152-161 mm. May 2024 has 156/156, then returns to one stem. Health declines to 1 by October 2025 but remains alive-observed there.

Suggested action: suppress or review-strike the May 2024 duplicate stem. Separately, keep an eye on the health decline, but there is no death contradiction in this profile.

Process lesson: duplicate-stem cleanup and health-trend review should stay separate.

### Tag 185

Case: H2/185.

H2/185 is Nyssa with one stem around 118-128 mm. May 2024 has 118/118 and carries the note "185-191 same tree". October 2025 is dead/health 0.

Suggested action: suppress or review-strike the May 2024 duplicate stem if working only within this UUID. Also review H2/185 through H2/191 as a cluster because the notes explicitly question whether these tags describe one multi-stem tree.

Process lesson: exact duplicates are still suspicious, but cluster notes make the identity scope bigger than one UUID.

### Tag 186

Cases: H2/186 and L0/186.

H2/186 is Nyssa and belongs to the 185-191 cluster. It has an early 94 mm observation, then drops to about 52-57 mm from 2021 onward, with notes "snapped" and "186-191 likely one multistem tree". May 2024 has 52/52. L0/186 is a dead juniper with a zombie-style contradiction: dead early, June 2023 alive/health 6, then dead again, with a "zombie???" note in May 2024.

Suggested action: H2/186 needs cluster review, not just duplicate cleanup. The 94 -> 52 drop may be explained by snapped trunk, but it should be checked in context with H2/185-191. L0/186 belongs in mortality/zombie review.

Process lesson: "snapped" can explain large DBH drops, but tag-cluster notes mean we should still inspect identity boundaries.

### Tag 187

Case: H2/187.

H2/187 is in the same H2 185-191 cluster. It is a Nyssa around 74-83 mm, with May 2024 76/76 and cluster notes in 2019/2023/2024.

Suggested action: suppress/review the May duplicate within this UUID, but review the tag cluster as a unit before any identity-level decisions.

Process lesson: cluster notes should cause the UI to suggest related tags automatically.

### Tag 189

Case: H2/189.

H2/189 is another Nyssa in the 185-191 cluster. It has a stable one-stem profile around 73-89 mm, May 2024 75/75, and later death by October 2025.

Suggested action: likely May duplicate cleanup, plus cluster review.

Process lesson: repeated exact duplicate stems across adjacent cluster tags are probably a data-entry artifact layered on top of real field uncertainty.

### Tag 190

Case: H2/190.

H2/190 is in the same cluster, one-stem Nyssa around 92-105 mm. May 2024 has 94/94, then it returns to one stem and later dies by October 2025.

Suggested action: likely May duplicate cleanup, plus H2/185-191 cluster review.

Process lesson: the exact duplicate rule should not erase the field note that these may be one larger multi-stem organism.

### Tag 191

Case: H2/191.

H2/191 is in the same cluster, one-stem Nyssa around 77-86 mm. May 2024 has 77/77, then one stem later. It has explicit early notes that 191-186 could be one tree.

Suggested action: likely May duplicate cleanup, plus cluster review with H2/185-191.

Process lesson: this group is a good test case for the "related evidence" UI, because the meaningful unit for human reasoning is larger than one tag.

### Tag 193

Cases: H2/193 and L0/193.

H2/193 is a large pine with May 2024 445/445 and otherwise one stem. L0/193 is a living juniper with May/October 2024 missing DBH/status rows, then April 2025 DBH 100 and October 2025 alive/health 5 but missing DBH.

Suggested action: suppress/review-strike H2/193's May duplicate. L0/193 should be treated as missed/not-found or unmeasured DBH, not mortality, because alive evidence returns.

Process lesson: one- or two-survey missing rows on a living tree should not become death without the absence threshold and later evidence check.

### Tag 194

Cases: H2/194 and L0/194.

H2/194 is a pine with May 2024 269/269; otherwise one stem. It also has a corrected-row issue already recorded. L0/194 is a dead juniper with DBH 55 early, missing for years, DBH 53 in April 2025, and dead throughout.

Suggested action: suppress/review-strike H2/194's May duplicate. Downgrade L0/194 dead DBH gap.

Process lesson: configured corrections and duplicate diagnostics can coexist; the UI should show both but avoid making the user re-decide corrections already encoded.

### Tag 196

Cases: H2/196 and L2/196.

H2/196 is a pine with May 2024 319/319 and otherwise one stem. L2/196 is a living juniper with a missing 2021 observation and missing DBH in October 2025, but otherwise stable around 207-225.

Suggested action: suppress/review-strike H2/196's May duplicate. Treat L2/196's missing observations as missing/not found or unmeasured, not death.

Process lesson: the same `qualifying_rank_gap` code is too broad; living missed-tree gaps and dead-tree gaps should get different explanations.

### Tag 201

Cases: H2/201 and L2/201.

H2/201 is a pine with May 2024 161/161 and otherwise one stem. L2/201 is a dead juniper with intermittent DBH measurements and dead status throughout.

Suggested action: suppress/review-strike H2/201's May duplicate. Downgrade L2/201 dead DBH gap.

Process lesson: again, bare tag grouping combines an H2 duplicate artifact with an unrelated dead-tree gap.

### Tag 202

Case: H2/202.

H2/202 is a large pine with one stem and May 2024 351/351. It has health variation but no identity problem beyond the duplicate stem.

Suggested action: suppress/review-strike the May 2024 duplicate stem.

Process lesson: duplicate-stem cleanup should preserve the May 2024 health observation on the real stem.

### Tag 203

Case: H2/203.

H2/203 is a large pine with one stable stem around 447-453. May 2024 has 447/447.

Suggested action: suppress/review-strike the May 2024 duplicate stem.

Process lesson: classic May 2024 duplicate artifact.

### Tag 204

Case: H2/204.

H2/204 is a large pine with one stable stem around 436-448. May 2024 has 441/441.

Suggested action: suppress/review-strike the May 2024 duplicate stem.

Process lesson: classic May 2024 duplicate artifact.

### Tag 206

Cases: H2/206 and L2/206.

H2/206 is Nyssa with May 2024 97/97 and otherwise one stem. Health jumps upward to 10 in October 2025 after lower values, which is worth separate health-review attention. L2/206 is a dead pine with intermittent DBH measurement and dead status.

Suggested action: suppress/review-strike H2/206's May duplicate. Add H2/206 to a health-jump review queue if we build one. Downgrade L2/206 dead DBH gaps.

Process lesson: sudden health recovery should be its own diagnostic, independent of stem profile cleanup.

### Tag 207

Cases: H2/207 and L2/207.

H2/207 is Nyssa with May 2024 95/95 and otherwise one stable stem. L2/207 is a dead pine where DBH declines from 119 to 95/91 across later dead observations after gaps.

Suggested action: suppress/review-strike H2/207's May duplicate. For L2/207, treat the DBH decline as plausible dead-tree decomposition or measurement inconsistency unless original sheets suggest a typo.

Process lesson: large DBH drops on dead trees should not get the same severity as large drops on living trees.

### Tag 220

Case: L2/220.

L2/220 is dead throughout, with early taxon/notes around juniper/unidentified and "vine in DBH". DBH is 58.5 early, missing for several years, then 50-54 in 2024-2025, and October 2025 has two missing stem rows.

Suggested action: downgrade the dead-tree DBH gap. Normalize taxon only if the broader taxonomy pass decides to trust Juniperus here. The October 2025 two missing rows should not increase stem count.

Process lesson: missing rows should not count as measured stems, especially on dead trees.

### Tag 255

Case: H0/255.

H0/255 is a large pine with May 2024 361/361 and otherwise one stem. October 2025 has alive/health 4 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 as alive evidence with missing DBH.

Process lesson: missing DBH in a recent survey is not a stem disappearance if alive/health evidence exists.

### Tag 256

Case: H0/256.

H0/256 is Nyssa with May 2024 79/79, but the two duplicate rows have different health values, 8 and 6. It returns to one stem, then October 2025 is dead/health 0.

Suggested action: suppress/review-strike the duplicate stem, but preserve the correct May 2024 health decision carefully. Because duplicate rows disagree on health, this one may need manual choice rather than a blind row drop.

Process lesson: duplicate DBH rows can carry conflicting non-DBH fields. The correction action should specify which fields survive.

### Tag 258

Case: H0/258.

H0/258 is a large pine with May 2024 435/435 and otherwise one stem. October 2025 has alive/health 5 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: same as H0/255.

### Tag 261

Case: H0/261.

H0/261 is Nyssa with May 2024 70/70 and otherwise one stem. October 2025 has alive/health 3 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: same as H0/255 and H0/258.

### Tag 262

Case: H0/262.

H0/262 is dead throughout. It has DBH 198 in 2019-2020, then missing for several years, then 189/184 in 2024-2025, and October 2025 is dead/fallen with missing DBH. It also has a configured correction already recorded.

Suggested action: downgrade the dead-tree DBH gap. Preserve the correction record. No identity action suggested from this pass.

Process lesson: dead/fallen context should soften both DBH-gap and DBH-decline warnings.

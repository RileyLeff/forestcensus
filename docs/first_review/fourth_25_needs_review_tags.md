# Fourth 25 needs-review tags

Date: 2026-05-10

Scope: bare tags 76-100 in the current `Tags -> needs_review` UI ordering. Bare tags are still treated as discovery surfaces; suggested actions should be scoped to UUID/tag-plot.

The tags in this pass are: 113, 114, 116, 121, 122, 124, 125, 127, 129, 132, 138, 141, 142, 143, 145, 147, 150, 152, 155, 156, 158, 160, 163, 165, and 167.

Important context added during this pass: October 2025 is the transition survey where DBH collection stopped partway through. From October 2025 onward, missing DBH should be considered protocol-valid, not suspicious by itself. If an October 2025 DBH exists, preserve it; if it is missing but health/alive/status exists, keep the observation with missing DBH.

## Additional process rules suggested by this pass

### 1. DBH jump diagnostics need subtypes

This batch is mostly single-stem histories with jumps. They should not all go to one generic `max_dbh_jump` queue. The useful subtypes are:

- `single_survey_dbh_outlier`: one bad-looking point followed by return to prior level, e.g. H3/160 May 2024 407 between 500-ish values.
- `persistent_regime_shift`: a sharp jump/drop followed by several years at the new level, e.g. H4/138, H4/145, H4/150, H4/147.
- `dead_or_broken_structural_change`: a dead/broken/fallen tree where DBH plausibly changes because the measured structure changed, e.g. L1/127, H4/132, L6/103 from the prior batch.
- `missing_gap_only`: DBH absent then present again, with no strong biological conflict, e.g. many dead-tree cases.

### 2. Persistent regime shifts are identity/source-review cases

Several trees have a 2019-2020 value, then from 2021 onward a very different but internally stable value. These are not normal growth and not simple one-off typos. They may indicate old data integration mistakes, tag confusion, circumference/DBH confusion in older sources, or a measurement protocol/source-column issue.

Examples: H4/138, H4/145, H4/150, H4/147, H4/141, H4/142, L1/116, L1/145.

Suggested handling: review source evidence and nearby/complementary trees before applying a correction. If the later stable run is trusted, the early values may need to be corrected, struck, or moved to another identity.

### 3. Zombie/mortality cases keep appearing as a separate queue

This pass has several dead -> alive or alive -> dead -> alive cases that should not be solved through DBH rules:

- H4/113: dead/health 0 in 2021, then alive and healthy afterward.
- L1/129: dead in 2022, then alive from 2023 onward.
- L1/108 from the prior batch was the same type.

Suggested handling: send to mortality/zombie review. If health and repeated later alive observations are strong, the isolated dead label may be wrong.

### 4. Notes can explain missingness without canonical failure

Examples: H3/156 is explicitly out of plot/outside, H4/127 has split trunk with one missing DBH, H4/108 was broken but alive, L0/167 was missing/not found then reappeared.

Suggested handling: missing DBH or missing rows with explanatory notes should be preserved as evidence and usually downgraded unless there is a repeated absence threshold or identity conflict.

### 5. October 2025 DBH absence must not trigger stem disappearance

Several rows in this batch have October 2025 health/alive evidence with missing DBH. Under the updated protocol context, that is expected. Diagnostics should either ignore October 2025+ missing DBH for stem-disappearance purposes or annotate it as protocol-driven.

## Tag-by-tag notes

### Tag 113

Cases: H4/113 and L1/113.

H4/113 is a very large pine and mostly stable, but it has a mortality contradiction: health 0/dead in 2021, then alive and healthy afterward. L1/113 is a dead pine with early DBH 374.5, missing for years, then 341 in October 2024, then missing/dead.

Suggested action: send H4/113 to mortality/zombie review; repeated later alive/healthy observations make the isolated 2021 dead label suspicious. Downgrade L1/113 as dead-tree DBH gap/structural change.

Process lesson: same bare tag can combine a mortality contradiction with an unrelated dead-tree DBH gap.

### Tag 114

Case: H4/114.

H4/114 is Acer rubrum. It is alive through 2021, then dead from 2022 onward. DBH is absent in June 2023 and April 2025 but present in May/October 2024 and October 2025 around 137-139. April 2025 has a broken/fallen note.

Suggested action: treat as dead-tree intermittent DBH measurement. No identity action suggested.

Process lesson: dead trees can have DBH gaps and later DBH observations without being inconsistent.

### Tag 116

Case: L1/116.

L1/116 is a living juniper with 260 in 2019-2020, then a stable lower range around 163-173 from 2021 onward. That is too large a drop for normal growth, but it is persistent rather than one-off.

Suggested action: source/identity review for the 2019-2020 values versus 2021 onward. Do not auto-correct as a single typo.

Process lesson: persistent DBH regime shifts need source review, not a one-row fix.

### Tag 121

Case: L1/121.

L1/121 is dead throughout. DBH 142 in 2019-2020, missing for years, 144/141 in 2024, then missing/dead.

Suggested action: downgrade dead-tree DBH gap.

Process lesson: ordinary dead-tree intermittent DBH case.

### Tag 122

Case: L1/122.

L1/122 is a living juniper with DBH around 79-85 through May 2024, then 71 in October 2024 and April 2025. Health is low but alive. This could be real measurement-position change, decay/damage, or a small-stem measurement issue; it is not a huge typo.

Suggested action: human review, but low priority. Keep as DBH jump unless notes/source evidence clarify.

Process lesson: small absolute DBH drops near declining health may be real enough to avoid automatic correction.

### Tag 124

Case: L1/124.

L1/124 is a living juniper with a one-survey October 2024 missing/not-found row, then observed alive again in April and October 2025. DBH values otherwise stay around 116-131.

Suggested action: treat October 2024 as missing/not found, not death. No DBH correction.

Process lesson: one-survey missing rows on living trees should downgrade after later alive evidence.

### Tag 125

Case: L1/125.

L1/125 is dead throughout. DBH 333 early, missing, then 332 in May 2024, then missing/dead.

Suggested action: downgrade dead-tree DBH gap.

Process lesson: ordinary dead-tree intermittent DBH case.

### Tag 127

Cases: H4/127 and L1/127.

H4/127 is living Ilex with split trunk notes and a May 2024 missing DBH but alive/health evidence; DBH resumes afterward. L1/127 is a dead pine with snapped/confirmed-kill notes and a DBH drop from 105 to 80 while dead.

Suggested action: H4/127 should be missing DBH only, not identity or death. L1/127 can be treated as dead/broken structural change; no auto-typo unless source sheets contradict it.

Process lesson: split/snapped notes are exactly the evidence needed to interpret DBH gaps/drops.

### Tag 129

Case: L1/129.

L1/129 is a juniper with alive observations, then a 2022 dead row, then alive again from 2023 onward. June 2023 explicitly notes "Marked dead last year". Later rows are alive with poison ivy/lean notes.

Suggested action: mortality/zombie review. The 2022 dead label is likely wrong or should be converted to missing/uncertain if source context supports it.

Process lesson: notes can directly point to a prior mortality-label mistake.

### Tag 132

Case: H4/132.

H4/132 is a dead pine with broken notes. DBH 365 early, then missing while broken/dead, then 307/308 later. This is a large drop, but the tree is dead/broken.

Suggested action: treat as dead/broken structural change unless source review suggests a transcription error.

Process lesson: broken dead pines can have large DBH changes that should not be auto-typed as typos.

### Tag 138

Cases: H4/138 and L1/138.

H4/138 is Liquidambar with 270 in 2019-2020, then a stable 104-108 range from 2021 onward. L1/138 is a dead pine with snapped note and later DBH drop from 245 to 196.

Suggested action: H4/138 needs source/identity review for a persistent regime shift. L1/138 is likely dead/broken structural change.

Process lesson: the H4/138 pattern is not one-row typo; it is either early-history wrong, later-history wrong, or a tag/source mapping issue.

### Tag 141

Cases: H4/141 and L1/141.

H4/141 is a pine with 527 in 2019-2020, then around 259-265 from 2021 onward, except May 2024 has 201 and October 2024 returns to 260. L1/141 is a leaning/fallen juniper watch case without invariant issues.

Suggested action: H4/141 needs two layers of review: persistent early-to-later regime shift, plus a likely one-off May 2024 low value. No action on L1/141 from this pass.

Process lesson: one tree can have both a regime shift and a single-survey outlier.

### Tag 142

Cases: H4/142 and L1/142.

H4/142 is Liquidambar with 109 in 2019-2020, then stable 71-78 from 2021 onward, with top missing/broken notes later. L1/142 is a dead juniper with intermittent dead DBH.

Suggested action: H4/142 needs source/identity review for the early-to-later regime shift, but broken-top notes may explain later low/stable values. Downgrade L1/142 dead DBH gap.

Process lesson: regime shifts with later damage notes require original-source context.

### Tag 143

Case: L1/143.

L1/143 is dead throughout with broken notes. DBH 329 early, missing, then 305/301 in 2024, then missing/dead.

Suggested action: downgrade dead-tree DBH gap; treat DBH decrease as plausible dead/broken structural change.

Process lesson: same dead-tree gap pattern.

### Tag 145

Cases: H4/145 and L1/145.

H4/145 is Liquidambar with 372 in 2019-2020, then stable around 97-110 from 2021 onward. L1/145 is a juniper with 161.5 in 2019-2020, missing in 2021, then stable 284-300 from 2022 onward.

Suggested action: both need source/identity review for persistent regime shifts. H4/145's early 372 is especially suspicious relative to later stable ~100. L1/145 may represent early wrong value, tag confusion, or a missed/changed measurement target.

Process lesson: opposite-direction regime shifts can happen: early too high on H4/145, early too low on L1/145.

### Tag 147

Cases: H4/147 and L1/147.

H4/147 is Liquidambar with 65 in 2019-2020, then stable 126-133 from 2021 onward. L1/147 is a dead juniper with intermittent DBH.

Suggested action: H4/147 source review for persistent regime shift. L1/147 downgrade as dead-tree DBH gap.

Process lesson: a jump from 65 to 126 that persists is not normal growth and should not be treated as one-survey noise.

### Tag 150

Cases: H4/150 and L0/150.

H4/150 is a pine with 67 in 2019-2020, then 377-395 from 2021 onward, with May 2024 low at 338 and return afterward. L0/150 is a pine watch case with recent couldn't-find/missing rows.

Suggested action: H4/150 needs urgent source/identity review. The early 67 almost certainly does not describe the same measured stem as the later 380-ish pine. May 2024 338 may be a separate one-off low value. L0/150 should go through absence-threshold logic if missing continues.

Process lesson: some regime shifts are so large that they likely represent wrong tag/source mapping, not measurement variation.

### Tag 152

Cases: H4/152 and L0/152.

H4/152 is Acer rubrum with 99 in 2019-2020, 61/64 in 2021-2022, then back to 96-102 from 2023 onward. L0/152 is a dead pine with missing/dead rows.

Suggested action: H4/152 looks like a two-year bad measurement/source issue in 2021-2022 rather than a permanent regime shift. Review those two DBHs as likely wrong or measuring a different stem/place. Downgrade L0/152 dead/missing context.

Process lesson: multi-survey outliers exist; the diagnostic should catch short bad runs, not only single rows.

### Tag 155

Cases: H3/155 and L0/155.

H3/155 is Nyssa with 280 in 2019-2020, then 209-218 from 2021 onward, but May 2024 jumps back to 270 for one survey before returning to 214. L0/155 is a dead pine with intermittent dead DBH.

Suggested action: H3/155 needs source/identity review for early high values and the May 2024 high outlier. L0/155 downgrade as dead-tree DBH gap.

Process lesson: old high values plus later one-off high recurrence can point to a repeated source/measurement confusion rather than random noise.

### Tag 156

Case: H3/156.

H3/156 is a pine around 320-344 with notes saying untagged/out of plot/outside. October 2024 is missing/out of plot, April 2025 is outside, and October 2025 has health 3 with missing DBH under the new protocol.

Suggested action: keep as same tree but mark out-of-plot/missing context. Do not treat missing DBH as death or stem disappearance.

Process lesson: location/scope notes should be first-class evidence in absence handling.

### Tag 158

Case: L0/158.

L0/158 is a living juniper with a one-survey May 2024 missing row, then DBH returns in October 2024 and April 2025. October 2025 has health 5 with missing DBH under the new protocol.

Suggested action: treat May 2024 as missing/not found. No DBH correction.

Process lesson: one-survey missing alive tree, later found, should downgrade.

### Tag 160

Cases: H3/160 and L0/160.

H3/160 is a large pine around 493-501 except May 2024 is 407 and October 2024 returns to 491. L0/160 is a dead pine with early 343, later dead DBH around 299-291 after gaps.

Suggested action: H3/160 May 2024 DBH 407 is a strong single-survey outlier; review/correct/strike that point. L0/160 downgrade as dead-tree gap/structural change.

Process lesson: rebound-shaped one-off DBH drops are high-confidence typo or bad-measurement candidates.

### Tag 163

Case: L0/163.

L0/163 is dead throughout. DBH 422 early, later 441/430, then April 2025 360 with "Tag fell" notes and October 2025 tag-fell note.

Suggested action: review April 2025 DBH 360 as a possible bad measurement due to tag-fell context, but keep the dead-tree structural-change possibility open.

Process lesson: tag-fell notes should reduce identity confidence and raise measurement uncertainty.

### Tag 165

Case: H3/165.

H3/165 is Ilex with split trunk notes. DBH is around 50-60 for most years, but June 2022 is 100, then 50 again in 2023. Notes include trunk split, trunk half gone, split down middle.

Suggested action: June 2022 DBH 100 is likely a one-survey measurement-target issue on a split trunk; review/strike or annotate rather than treating it as growth. Keep the split-trunk context.

Process lesson: split/multi-part stems can create one-off double-size measurements without being a duplicate row.

### Tag 167

Cases: H3/167 and L0/167.

H3/167 is a stable pine watch case with notes about three trunks, but only one canonical measured stem in this profile. L0/167 is a living juniper with missing/not-found rows in 2021-2022, then found alive again from 2023 onward.

Suggested action: no action on H3/167 from this pass. Treat L0/167's 2021-2022 absence as missing/not found, not death, because later alive evidence returns.

Process lesson: multiple consecutive missing rows can be converted back to missing/unknown if later alive evidence appears.


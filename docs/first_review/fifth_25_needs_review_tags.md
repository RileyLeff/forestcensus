# Fifth 25 needs-review tags

Date: 2026-05-10

Scope: bare tags 101-125 in the current `Tags -> needs_review` UI ordering. Bare tags are discovery surfaces; suggested actions should be scoped to UUID/tag-plot.

The tags in this pass are: 168, 169, 170, 172, 174, 195, 197, 198, 199, 200, 205, 213, 214, 215, 219, 221, 222, 223, 224, 225, 229, 230, 231, 233, and 235.

Important context carried forward: October 2025 is the protocol transition away from DBH collection. Missing DBH in October 2025+ is expected. If an October 2025 DBH exists, preserve it; if DBH is absent but health/status exists, keep that as a valid observation with missing DBH.

## Additional process rules suggested by this pass

### 1. Threshold-edge trees need an explicit canonical policy

Several H1 trees hover around the 50 mm inclusion threshold: H1/198, H1/224, H1/230, H1/231, and L2/233. These can be alive, dead, found again, or partially broken, while DBH moves above and below 50.

Suggested handling: treat `50` as qualifying if the survey threshold is inclusive. DBH values below 50 should not contribute to canonical stem profiles, but health/alive/status evidence can still matter if the tree had ever qualified. For trees that never convincingly qualify, exclude them from canonical live-tree evidence.

### 2. Persistent regime shifts continue to point at old-source or identity problems

This pass adds more dramatic persistent shifts:

- H1/233: 353 in 2019-2020, then stable 67-78 from 2021 onward.
- H1/235: 194 in 2019-2020, then stable 303-318 from 2021 onward.
- H1/197/H1/199/H1/200 have smaller dead-tree versions of the same early/later shift.

Suggested handling: do not auto-correct as a single typo. Review source evidence and nearby/complementary trees. For extreme cases like H1/233, it may be wrong tag/source mapping rather than measurement noise.

### 3. Dead-tree DBH loss is real signal, with narrow typo exceptions

Dead/broken structure can explain gradual or moderate DBH loss, and those losses should be preserved as meaningful evidence. A few one-off values still look suspicious when the shape is rebound-like or digit-loss-like:

- L2/219: 155/155, then April 2025 is 55.
- L2/198: 280, then May 2024 is 203, then back to 258/264.
- L2/223 has much larger identity-scale swings and should not be treated as ordinary decay.

Suggested handling: dead-tree status should soften DBH-jump severity because decomposition and chunk loss are real. It should not fully silence rebound-shaped or digit-loss-looking outliers.

### 4. May 2024 duplicate stems still appear, but less often

The duplicate-stem batch artifact appears again on H2/195 and H2/205: a stable one-stem tree gains an exact duplicate DBH in May 2024 and returns to one stem afterward.

Suggested handling: same probable duplicate-entry stem action as prior memos.

### 5. Mortality/zombie review intersects with threshold cleanup

Some threshold-edge trees also have dead -> alive or alive -> dead contradictions: L0/170, H1/221, L2/224, H1/230. These should not be solved through DBH rules alone.

Suggested handling: route mortality contradictions to zombie/dead-alive review, then apply DBH threshold cleanup after the health/status interpretation is settled.

## Tag-by-tag notes

### Tag 168

Case: L0/168.

L0/168 is a dead pine. DBH is 354 in 2019-2020, then missing for years, then 325/309 in 2024-2025 with notes like lost tag and mostly fallen.

Suggested action: downgrade as dead-tree gap/structural change. Preserve the lost-tag/fallen notes.

Process lesson: fallen/dead context can explain later lower DBH, but tag-loss notes should keep evidence confidence visible.

### Tag 169

Case: L0/169.

L0/169 is a living juniper with a missing 2021 row, then stable DBH around 102-106, and October 2025 health 2 with missing DBH under the new protocol.

Suggested action: treat 2021 as missing/not found, not death. No DBH correction.

Process lesson: one-survey missing living trees should downgrade after later alive evidence.

### Tag 170

Cases: H3/170 and L0/170.

H3/170 is a dead pine with intermittent DBH and later lower measurements around 183-185. L0/170 is Nyssa with missing rows, a June 2023 alive/health 1 row, then dead/health 0 afterward; configured correction evidence is already present.

Suggested action: H3/170 can be downgraded as dead-tree DBH gap/structural change. L0/170 belongs in mortality/zombie review before DBH cleanup.

Process lesson: low-health alive followed by dead is a mortality interpretation problem, not a DBH problem.

### Tag 172

Case: L0/172.

L0/172 is dead throughout. DBH 154 early, missing, then 149/145/144 in 2024-2025.

Suggested action: downgrade dead-tree DBH gap.

Process lesson: ordinary dead-tree intermittent DBH case.

### Tag 174

Case: L0/174.

L0/174 is dead throughout, with early DBH 91, missing for years, then 103/90/92 in 2024-2025.

Suggested action: downgrade dead-tree DBH gap. May 2024 103 is somewhat high but not enough to force a typo call without source context.

Process lesson: small dead-tree measurement variation can stay low priority.

### Tag 195

Cases: H2/195 and L2/195.

H2/195 is a Nyssa with the May 2024 exact duplicate pattern: 103/103, then back to one stem. L2/195 is a dead pine with early DBH 396, one later dead DBH 378, then missing/dead.

Suggested action: suppress/review-strike H2/195's May duplicate stem. Downgrade L2/195 dead-tree DBH gap.

Process lesson: the May 2024 duplicate artifact keeps appearing beyond the dense H2/H0 runs.

### Tag 197

Cases: H1/197 and L2/197.

H1/197 is a dead unidentified tree with early DBH 81, then later 62/63. L2/197 is a dead pine with intermittent DBH around 242-252.

Suggested action: downgrade both as dead-tree DBH gaps/structural changes unless source sheets suggest a specific typo.

Process lesson: dead low-DBH trees can shrink below prior measurements without implying identity failure.

### Tag 198

Cases: H1/198 and L2/198.

H1/198 is a dead low-threshold unidentified tree: 53 early, then 43/45 later, which is subthreshold. L2/198 is a dead pine with 280 early, 203 in May 2024, then 258/264 later.

Suggested action: for H1/198, keep early qualifying evidence but strike later subthreshold DBH from the canonical DBH profile. For L2/198, review May 2024 203 as a likely one-survey outlier or bad measurement because it rebounds afterward.

Process lesson: dead-tree softening should not hide rebound-shaped outliers.

### Tag 199

Case: H1/199.

H1/199 is a dead Nyssa with early DBH 95, missing for years, then 66 in May 2024 followed by 86/83/87. May 2024 is low relative to later values.

Suggested action: downgrade the gap but review May 2024 66 as a possible low outlier if source evidence is easy to inspect.

Process lesson: even in dead trees, a lone low value followed by rebound should get a lighter outlier flag.

### Tag 200

Cases: H1/200 and L3/200.

H1/200 is a dead unidentified tree with early DBH 69 and later stable 57. L3/200 is a pine that dies after earlier alive observations, with configured corrections already recorded.

Suggested action: H1/200 can be downgraded as dead-tree structural change. L3/200 should preserve existing correction decisions; no new action from this pass.

Process lesson: the review UI should show configured corrections as prior resolved context.

### Tag 205

Cases: H2/205 and L2/205.

H2/205 is Nyssa with the May 2024 exact duplicate pattern: 201/201, then back to one stem. L2/205 is a dead pine watch case with missing/dead rows.

Suggested action: suppress/review-strike H2/205's May duplicate stem. No action on L2/205 beyond inferred-dead tracking.

Process lesson: classic duplicate artifact plus unrelated dead context under the same bare tag.

### Tag 213

Case: L2/213.

L2/213 is dead throughout. DBH 352.5 early, intermittent later measurements around 345-360, then missing.

Suggested action: downgrade dead-tree DBH gap.

Process lesson: ordinary dead-tree intermittent DBH case.

### Tag 214

Case: L2/214.

L2/214 is a living juniper. DBH is 106.5 in 2019-2020, jumps to 123 in 2021, returns around 101-103, then 115 in April 2025. Health stays alive.

Suggested action: human DBH review, low-medium priority. This could be measurement-position or vine/irregular-stem variability rather than a clear typo.

Process lesson: small living-tree DBH jumps need context but often should not be auto-corrected.

### Tag 215

Case: L2/215.

L2/215 is dead throughout. DBH is 371/373 early, then 323/325 in 2024, then 229 in April 2025. A correction row already exists.

Suggested action: preserve existing correction context. Treat as dead-tree structural change unless April 2025 229 looks like a source typo on inspection.

Process lesson: multi-step dead-tree DBH decline may be real structure loss, not one typo.

### Tag 219

Case: L2/219.

L2/219 is dead throughout. DBH is 156/155 through October 2024, then April 2025 is 55. That looks like a digit-loss or bad-measurement outlier more than gradual decay.

Suggested action: review April 2025 DBH 55 as likely typo or strike-to-missing candidate.

Process lesson: a drop of roughly 100 mm to a plausible digit-lost value should stay high-confidence even on a dead tree.

### Tag 221

Cases: H1/221 and L2/221.

H1/221 is a Nyssa watch case with a clear mortality contradiction: dead/no needles in 2020, then alive/health 7 in 2021 and alive thereafter. L2/221 is a dead pine with intermittent dead DBH around 262-270.

Suggested action: H1/221 to mortality/zombie review. L2/221 downgrade as dead-tree DBH gap.

Process lesson: mortality review is still its own queue.

### Tag 222

Case: H1/222.

H1/222 is a pine that dies after early alive observations. DBH 337 early, then dead/standing, later DBH around 311-320 including October 2025 DBH 315.

Suggested action: treat as death followed by intermittent dead-tree DBH measurement. No identity correction suggested.

Process lesson: if October 2025 DBH exists, preserve it; the protocol change means missing DBH is allowed, not that all DBH after that date is forbidden evidence.

### Tag 223

Case: L2/223.

L2/223 is the standout messy case. It is a living juniper with DBH 170/174, then 247 in 2022-2023, then 480 in May 2024, then 183/181 afterward. October 2024 notes "wtf is the history".

Follow-up evidence review: no explicit candidate link or tag-change assertion is present, and no clean complementary nearby L2 juniper/pine explains the whole sequence. The 2022 source records `24.7 cm`, so the pipeline correctly normalized that to `247 mm`; this is not a parser unit bug. Given the field-team context, 2022-2023 were undergrad-entered and less trusted, while October 2024 and October 2025 were collected by Riley/Juan and are more trusted. The 2022-2023 `247` values are likely an organizational/source error, and the May 2024 `480` is likely a data-entry typo.

Suggested action: keep the L2/223 UUID/identity. Strike the DBH values for June 2022, June 2023, and May 2024 from the canonical DBH profile, while preserving the observation rows and health/alive/status evidence. Treat October 2024 `183`, April 2025 `181`, and October 2025 health 8/no DBH as the trusted recent evidence.

Process lesson: reviewer notes like "wtf is the history" are high-signal and should escalate the case.

### Tag 224

Cases: H1/224 and L2/224.

H1/224 is a threshold-edge Nyssa: 46/46, then 54, then 39/45, then 55/50/50/59 with low health. L2/224 is a dead juniper with an October 2024 alive/health 6 row between dead rows.

Suggested action: for H1/224, strike subthreshold DBH values but keep qualifying observations at 50+ and health evidence. For L2/224, route the isolated alive/health 6 row to mortality/zombie review.

Process lesson: threshold cleanup and mortality review can overlap but should be sequenced separately.

### Tag 225

Case: L2/225.

L2/225 is dead throughout. DBH 310 early, missing for years, then 314/315/317, then missing/dead.

Suggested action: downgrade dead-tree DBH gap.

Process lesson: ordinary dead-tree intermittent DBH case.

### Tag 229

Case: H1/229.

H1/229 is living Ilex with a May 2024 missing row, then observed with DBH again in October 2024 and April/October 2025. Health remains alive.

Suggested action: treat May 2024 as missing/not found. No DBH correction.

Process lesson: one-survey missing living tree, later found, should downgrade.

### Tag 230

Cases: H1/230 and L2/230.

H1/230 is threshold-edge Ilex with early 58, then 49, then dead/missing rows, then 45/57/54 with low health and "half gone" note. L2/230 is a snapped juniper watch case.

Suggested action: H1/230 needs threshold cleanup plus mortality review. Strike subthreshold DBH values, preserve qualifying values, and decide whether the dead rows should become missing/uncertain given later alive evidence. No action on L2/230 from this pass.

Process lesson: damaged threshold-edge trees are exactly where DBH and mortality rules should stay modular.

### Tag 231

Case: H1/231.

H1/231 is living Ilex growing horizontally. It has early 59, then 46, then couldn't-find/missing, then 50/53/53/51 with alive evidence.

Suggested action: strike subthreshold 46 from canonical DBH profile, keep missing rows as missing/not found, and preserve 50+ qualifying observations.

Process lesson: a tree can qualify, dip below threshold by measurement, then requalify; below-threshold DBH should not erase the identity.

### Tag 233

Cases: H1/233 and L2/233.

H1/233 is a dramatic persistent regime shift: 353 in 2019-2020, then stable 67-78 from 2021 onward. L2/233 is a dead low-threshold unidentified tree with early 55, then missing, then 56.

Suggested action: H1/233 needs source/identity review, likely wrong early value or wrong tag/source mapping. L2/233 downgrade as dead-tree gap.

Process lesson: huge early-to-later shifts are identity/source problems until proven otherwise.

### Tag 235

Case: H1/235.

H1/235 is a pine with 194 in 2019-2020, then stable 303-318 from 2021 onward. Health declines but the tree remains observed.

Suggested action: source/identity review for the early 194 values versus the later stable 300+ series.

Process lesson: persistent regime shift in the upward direction likely means early measurements are wrong, a different stem/tree was measured, or source mapping changed.

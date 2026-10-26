# First 25 needs-review tags

Date: 2026-05-10

Scope: first 25 bare tags in the current `Tags -> needs_review` UI ordering, using the evidence and canonical-review outputs already materialized in this project. This is a diagnostic memo only. No canonical edits are applied here.

The current tag-level view intentionally groups observations by bare tag, so several entries below mix unrelated trees from different plots. The suggested actions should generally be made at the tag-plot or UUID level, not against the bare tag as a whole.

## Process rules suggested by this pass

### 1. Transient exact duplicate stem

Candidate rule: if a survey gains one extra stem, the new stem has exactly the same DBH as an existing stem, there is no supporting note for a new stem, and the extra stem disappears in the next survey, mark it as a probable duplicate-entry stem.

Suggested handling: preselect "strike duplicate stem DBH/row from canonical profile" for review, or auto-suppress after we are comfortable with the rule.

This pattern is especially strong in May 2024. It appears on H2/175, H2/176, H2/178, H2/179, H2/180, H2/188, H0/257, H0/275, and others. That makes it look like a batch-level data-entry/import artifact, not many simultaneous biological events.

Important exception: if a plausible second stem appears again later, do not auto-suppress the whole idea of a second stem. H2/208 is the warning case: May 2024 has an exact duplicate 480/480, but Oct 2025 has two large pine stems, 475/471. The May 2024 duplicate is suspicious, but the later second stem may be real.

### 2. Dead-tree DBH gaps

Candidate rule: if a tree is dead throughout a period and DBH is intermittently measured, absent, then measured again, do not treat the DBH gap alone as a high-priority canonical problem.

Suggested handling: downgrade `qualifying_rank_gap` on dead-only histories to `watch` or `info`, unless the gap coincides with a taxon, tag, or alive/dead contradiction.

Examples: L3/274, L1/140, L0/175, L3/297, H2/102, L2/208, L2/227.

### 3. Subthreshold stems on otherwise qualifying trees

Candidate rule: DBH values below 50 mm should not contribute to canonical stem profiles. If the tree has at least one qualifying stem, preserve the alive/health/status evidence, but set subthreshold DBH to missing in the canonical DBH profile.

Suggested handling: these should usually be cleanup actions, not full identity reviews, unless the whole plant never qualifies.

Examples: H4/149, H0/274, H2/192, H0/281, H0/275, H1/105.

### 4. Large persistent stem appears after earlier surveys

Candidate rule: if a new stem appears above 60 mm and persists, it probably was either newly found after being missed or crossed the threshold before we captured it. For big stems, this is not a normal threshold-crossing event.

Suggested handling: review original sheets if possible. If the stem is plausible and persistent, represent earlier surveys as blank/missing stem observations rather than pretending the stem did not exist.

Examples: H3/153, H1/242, H4/119.

### 5. One-survey missing/non-reporting

Candidate rule: a one-survey absence in an otherwise stable alive history should usually be treated as missing/not found, not death or identity failure.

Suggested handling: keep the absence visible, but downgrade review severity unless it is part of a repeated absence threshold, an alive/dead contradiction, or a major DBH/taxon discontinuity.

Examples: L1/149, H3/153 in Oct 2024 for the largest stem, and many dead-tree DBH gaps.

### 6. Zombie and health rules should stay distinct

Candidate rule: do not infer zombie events from missing rows alone. A zombie requires observed dead/health 0 or dead status followed by observed alive/nonzero health.

Suggested handling: handle mortality/status review separately from DBH/stem-profile review. Dead status with health 1-3 that never recovers can probably be normalized to health 0. Dead status with low health followed by alive evidence probably means the mortality label was wrong.

Examples in this sample mostly appear as same-bare-tag context rather than the needs-review tag-plot itself: L6/105, L1/131, H1/249, L1/119.

### 7. Tag-level review is useful for discovery but noisy for decisions

Bare tags collide across plots. A bare tag can contain a clean stable tree in one plot and a messy tree in another. The final action workflow should make decisions at tag-plot or UUID scope, with related bare-tag evidence available nearby.

## Tag-by-tag notes

### Tag 149

Cases: H4/149 and L1/149.

H4/149 is an Ilex opaca multi-stem plant with notes like "three trunks" and "scratched tag". The profile has several small stems around or below the 50 mm threshold and a suspicious 2023 duplicate-ish pair around 70/70, but the general picture is a real multi-stem tree with measurement inconsistency. L1/149 is a single juniper with a one-survey May 2024 gap and then reappears.

Addendum: June 2023 on H4/149 is a clear duplicate-stem candidate. The canonical rows show 70, 70, 62, and 52 mm, and two rows point back to datasheet slot 2. That means the duplicate changes apparent stem count, and it should be treated like the transient exact duplicate-stem family unless original sheet review proves four distinct stems.

Suggested action: for H4/149, strike subthreshold DBH values from the canonical DBH profile while preserving health/alive evidence. Keep the multi-stem interpretation. Treat the L1/149 gap as missing/not found, not a hard review issue.

Process lesson: subthreshold stems and one-survey absences should not carry the same review weight as identity/taxon conflicts.

### Tag 153

Cases: H3/153 and L0/153.

H3/153 is Nyssa sylvatica. It has one stem around 139 mm in 2019-2020, then a persistent three-stem profile beginning in 2021 with a large stem around 236 mm and two smaller stems around 130 mm. In Oct 2024 the largest stem is missing, then it returns in 2025. L0/153 is a dead Pinus taeda with an explicit candidate identity/tag-change link to L0/921.

Suggested action: review H3/153 as a likely missed large stem in early surveys plus one missed main-stem measurement in Oct 2024. Do not treat it as mortality. Review L0/153 in the identity/tag-change workflow, not as a DBH anomaly.

Process lesson: persistent large-stem appearances need a "blank back-history" option, and explicit tag-change evidence should be routed to identity review.

### Tag 274

Cases: H0/274 and L3/274.

H0/274 is a low-DBH Nyssa with many subthreshold stems and cluster notes near H0/275. It has a May 2024 duplicate 58/58 pattern. L3/274 is dead with intermittent DBH measurement, which looks like normal dead-tree measurement inconsistency.

Suggested action: review H0/274 together with H0/275 as a small multi-stem/cluster case. Strike subthreshold DBH values. Treat May 2024 duplicate as probable duplicate-entry stem if unsupported by notes. Downgrade L3/274 dead DBH gap.

Process lesson: H0/274 and H0/275 show why cluster notes and adjacent tags should be surfaced together.

### Tag 188

Cases: H2/188 and L0/188.

H2/188 has exact duplicate 65/65 in May 2024, then the extra stem disappears. Notes mention a larger cluster: "185-191 same tree" and "186-191 likely one multistem tree". L0/188 looks like a comparatively stable juniper watch case.

Suggested action: do not handle H2/188 as an isolated duplicate only. Review tags 185-191 as a cluster. The May 2024 duplicate itself is probably not a real new stem, but the note suggests a deeper tag/plant-boundary issue.

Process lesson: duplicate-stem rules need a "cluster-note escape hatch" that sends the case to identity/plant-boundary review.

### Tag 192

Cases: H2/192 and L0/192.

H2/192 is a marginal low-DBH Nyssa with subthreshold second/third stems and a May 2024 exact duplicate 53/53. Health declines toward dead/near-dead. L0/192 is a juniper that is mostly below threshold, with one 50 mm observation.

Suggested action: strike subthreshold DBH values. Treat the H2/192 May 2024 duplicate as a probable duplicate-entry stem. L0/192 should probably be treated as a threshold-edge tree: keep the 50 mm observation only if we accept it as qualifying; otherwise keep it out of canonical live-tree evidence.

Process lesson: "first qualifying DBH" should be threshold-based, but the UI should distinguish true threshold crossing from years of below-threshold sapling evidence.

### Tag 257

Cases: H0/257 and L4/257.

H0/257 is a multi-stem Nyssa with a May 2024 exact duplicate around 155/155. L4/257 looks stable and is likely only present because bare-tag grouping pulls it in.

Suggested action: suppress or review the May 2024 duplicate stem on H0/257. No action suggested for L4/257 from this pass.

Process lesson: bare tag grouping is valuable context, but decisions should land on H0/257 only.

### Tag 281

Cases: H0/281 and L3/281.

H0/281 is a marginal multi-stem Nyssa with subthreshold stems, a 2019 duplicate 60/60, and a May 2024 duplicate 54/54 plus 50. L3/281 is a dead-tree DBH gap case.

Suggested action: strike subthreshold DBH values. Review duplicate 54/54 if it affects the canonical profile, likely as a duplicate-entry stem. Downgrade the L3/281 dead DBH gap.

Process lesson: duplicate profile values near the threshold may mostly be cleanup noise unless they change whether the plant qualifies.

### Tag 151

Cases: H4/151 and L0/151.

H4/151 has taxon inconsistency, Acer rubrum versus unidentified, and a strange DBH profile: 2019 has about 102/67, 2020 has only 102, 2021 has about 56, then later years stabilize around a two-stem 90/60-ish profile. This is not a clean exact-duplicate case. L0/151 looks like a separate stable juniper watch case.

Suggested action: inspect original sheets for H4/151 around 2019-2021. This may be an early measurement/tag artifact or an omitted stem, not something to auto-correct.

Process lesson: large early profile discontinuities without exact duplication should stay human-review.

### Tag 227

Case: L2/227.

L2/227 has two stems around 114/104 in 2019-2020, then it is dead or missing for years, then April 2025 has one dead DBH measurement around 112. This looks like a dead tree where one stem or one DBH was not found later.

Suggested action: downgrade from high-priority review unless there is a mortality contradiction elsewhere. Keep dead status/health logic separate from DBH-gap logic.

Process lesson: dead trees should tolerate incomplete DBH/stem profiles.

### Tag 2425

Case: M2/2425.

M2/2425 is a stable three-stem Nyssa. The suspicious point is a rank-3 DBH jump around May 2024, roughly 174 -> 217 -> 176. This looks like a one-survey measurement or transcription problem, possibly measuring a different spot or wrong stem.

Suggested action: review the May 2024 third-stem DBH. Do not split identity.

Process lesson: rank-specific one-survey jumps should be flagged even when stem count is stable.

### Tag 275

Case: H0/275.

H0/275 is near H0/274 and has a similar small multi-stem pattern. It starts with several stems around 63/54/53, later has one qualifying stem around 75/76, and May 2024 has duplicate 76/76. The small stems are often subthreshold.

Suggested action: review together with H0/274. Strike subthreshold DBH values. Treat May 2024 76/76 as likely duplicate-entry stem unless notes support a second stem.

Process lesson: adjacent low-DBH cluster cases should be reviewed as a group.

### Tag 140

Cases: H4/140 and L1/140.

H4/140 is Acer rubrum. It has 2019 duplicate 91/91, 2020 single 91, then 2021 onward a large stem around 194-219 plus a smaller stem around 78-80. That is too large to treat as normal growth. L1/140 is a dead juniper with intermittent DBH measurement.

Suggested action: inspect H4/140 original sheets around 2019-2021. It may need early correction or blank back-history for a large missed stem. Downgrade L1/140 dead-tree DBH gaps.

Process lesson: exact duplicate DBH plus later large persistent stem can indicate a deeper measurement/entry problem, not just a duplicate row.

### Tag 119

Cases: H4/119 and L1/119.

H4/119 is Acer rubrum with a main stem around 240 and a second stem around 114 in 2019. The second stem is absent in 2020-2021, then reappears around 98-109 later, sometimes with dead/low health. L1/119 has a possible zombie-style mortality/status issue.

Suggested action: H4/119 probably needs blank/missing second-stem rows for the absent years rather than treating it as a new stem. L1/119 belongs in mortality/zombie review.

Process lesson: stem disappearance/reappearance should become a blank interpolation candidate when the tree identity is otherwise stable.

### Tag 242

Case: H1/242.

H1/242 is Nyssa with one stem in 2019-2021, then a second stem appears around 66 mm in 2022 and persists. Since 66 mm is above the survey threshold, this probably was previously unmeasured rather than a newly qualifying stem.

Suggested action: add or propose blank back-history for the second stem before 2022, pending original-sheet review.

Process lesson: persistent new stems above 60 mm should trigger back-history review.

### Tag 105

Cases: H1/105 and L6/105.

H1/105 is an unidentified dead tree with a subthreshold second stem around 41 mm. L6/105 is a separate juniper watch case with mortality contradiction context.

Suggested action: for H1/105, strike the subthreshold second-stem DBH from the canonical DBH profile. Route L6/105 through mortality/zombie review if it appears in that queue.

Process lesson: a subthreshold second stem on a dead tree should not force heavy review.

### Tag 131

Cases: H4/131 and L1/131.

H4/131 is a dead Acer rubrum where a second stem around 123 appears in 2019 and is gone later. L1/131 is a separate juniper watch/zombie context.

Suggested action: downgrade H4/131 stem disappearance if the tree is dead and no later alive evidence exists. Review L1/131 under mortality rules, not stem rules.

Process lesson: dead/inferred-dead context should soften stem disappearance diagnostics.

### Tag 249

Cases: H1/249 and L4/249.

H1/249 is a pine watch case with possible alive-after-dead context. L4/249 is a dead unidentified two-stem tree where the second stem disappears after 2019.

Suggested action: H1/249 should go through mortality/zombie review if needed. L4/249 can probably be downgraded as dead-tree stem disappearance.

Process lesson: same bare tag can combine two totally different review categories.

### Tag 208

Cases: H2/208 and L2/208.

H2/208 is a large Pinus taeda. It is mostly a single large stem around 468-480, but May 2024 has exact duplicate 480/480. Oct 2025 then shows two large stems around 475/471, which may mean there really is another large stem that was previously omitted. L2/208 is a dead pine with intermittent DBH measurement.

Suggested action: do not blindly auto-suppress all second-stem evidence for H2/208. The May 2024 duplicate is suspicious, but Oct 2025 needs review as possible real second stem. Downgrade L2/208 dead DBH gaps.

Process lesson: duplicate DBH plus later plausible second stem should remain human-review, not auto-fix.

### Tag 297

Case: L3/297.

L3/297 is a dead juniper around the threshold, with DBH 56 in 2019-2020, gaps, then DBH 57 in Oct 2024. Health/status are dead.

Suggested action: downgrade dead-tree DBH gap. No identity action suggested from this pass.

Process lesson: dead trees can have sparse DBH evidence without implying a canonical inconsistency.

### Tag 102

Cases: H2/102 and L6/102.

H2/102 is a dead pine with intermittent DBH measurement, including a later 136 mm DBH after gaps. L6/102 is a separate juniper watch case.

Suggested action: downgrade H2/102 dead-tree rank gap. No stem correction suggested unless a mortality contradiction appears elsewhere.

Process lesson: same as other dead-tree DBH gaps.

### Tag 175

Cases: H2/175 and L0/175.

H2/175 has the strong May 2024 transient exact duplicate pattern: one stem around 184 becomes 184/184, then returns to one stem. L0/175 is a dead-tree DBH gap case.

Suggested action: mark H2/175 May 2024 extra stem as probable duplicate-entry stem. Downgrade L0/175 dead DBH gap.

Process lesson: this is a clean example of the transient exact duplicate rule.

### Tag 176

Case: H2/176.

H2/176 has May 2024 344/344, then returns to a single large pine stem. This is a clean duplicate-entry signature.

Suggested action: suppress or review-strike the May 2024 extra duplicate stem.

Process lesson: use as a positive training/example case for the duplicate DBH + stem-count increase rule.

### Tag 178

Case: H2/178.

H2/178 has May 2024 65/65, then returns to one stem. This is another clean transient duplicate pattern.

Suggested action: suppress or review-strike the May 2024 extra duplicate stem.

Process lesson: exact duplicate transients happen on small trees too, not just large pines.

### Tag 179

Case: H2/179.

H2/179 has May 2024 56/56, then returns to one stem. This is likely a duplicate-entry stem.

Suggested action: suppress or review-strike the May 2024 extra duplicate stem.

Process lesson: near-threshold duplicate transients should not inflate stem count or qualification evidence.

### Tag 180

Case: H2/180.

H2/180 has May 2024 251/251, then returns to one stem. This matches the same May 2024 duplicate-entry pattern.

Suggested action: suppress or review-strike the May 2024 extra duplicate stem.

Process lesson: enough H2 May 2024 tags show this that we should add a batch-level diagnostic note for May 2024 duplicate stem rows.

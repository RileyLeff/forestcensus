# Third 25 needs-review tags

Date: 2026-05-10

Scope: bare tags 51-75 in the current `Tags -> needs_review` UI ordering. As before, bare tags are used for discovery, but suggested actions should be applied at UUID/tag-plot scope.

The tags in this pass are: 264, 265, 268, 269, 270, 271, 273, 276, 277, 278, 279, 280, 282, 283, 286, 287, 288, 289, 293, 103, 104, 106, 108, 110, and 111.

## Additional process rules suggested by this pass

### 1. The May 2024 duplicate-stem artifact extends strongly into H0

This pass is dominated by H0 trees with the same May 2024 exact-duplicate stem signature already seen in H2:

- one stable measured stem before May 2024
- May 2024 has an extra stem with exactly duplicated DBH
- the extra stem disappears by October 2024
- October 2025 often has alive/health evidence but missing DBH, which is expected under the protocol transition away from DBH collection

Examples: H0/264, H0/265, H0/268, H0/269, H0/270, H0/271, H0/273, H0/276, H0/279, H0/280, H0/282, H0/283, H0/287, H0/288, H0/289.

Suggested handling: same as the prior batch. Pre-classify these as probable duplicate-entry stems, suppress the duplicate from canonical DBH/stem count, and preserve the real survey evidence.

### 2. One-off DBH typos need a separate rule from duplicate stems

Two cases show sharp one-survey DBH changes that are not duplicate-stem artifacts:

- H0/286: 315 -> 155 -> 307 on a living pine
- L1/110: 332 -> 132 -> 330 on a dead pine

Suggested handling: flag these as `single_survey_dbh_outlier` or similar. The likely action is to correct or strike the one offending DBH, but the duplicate-stem rule should not be asked to handle these.

### 3. Broken/snapped/dead context can explain real DBH drops

Several dead or damaged trees show substantial DBH decreases after breakage or years of being dead. Examples include L4/264, L6/103, H4/108, and possibly L3/280. These are not all typos.

Suggested handling: if a note says broken, snapped, standing but broken, fallen, hidden tag, vine in DBH, or similar, the DBH jump diagnostic should surface the note and lower the confidence of an automatic typo call.

### 4. Missing October 2025 DBH with health is protocol-valid

Many H0 trees in this batch have October 2025 health/alive evidence but no DBH. We later clarified that DBH collection stopped during the October 2025 survey, so this should be treated as an intentional protocol transition, not a source artifact and not a stem disappearance.

Suggested handling: canonical row should remain present with missing DBH and observed health/alive status.

### 5. Missing rows should not inflate stem count

Several dead-tree cases have two October 2025 rows with no DBH. These should not count as two measured stems. The stem-count diagnostics should count measured qualifying stems, not blank/missing placeholder rows.

Examples: L2/220 from the prior batch, plus H2/103, H2/104, L6/106.

## Tag-by-tag notes

### Tag 264

Cases: H0/264 and L4/264.

H0/264 is a pine with the standard May 2024 duplicate pattern: 255/255 in May, then back to one stem. October 2025 has health 2/alive but missing DBH. L4/264 is a dead pine with DBH 410 in 2019-2020, missing for years, then around 343-348 from 2024 onward, with a "leaning! tag hidden" note.

Suggested action: suppress/review-strike H0/264's May duplicate and keep October 2025 as alive evidence with missing DBH. L4/264 should be reviewed as a dead-tree structural/measurement change, but not treated as an identity issue by default.

Process lesson: dead large-DBH drops need note context before typo assumptions.

### Tag 265

Cases: H0/265 and L4/265.

H0/265 is Nyssa. It dies by June 2023, then May 2024 has duplicate 132/132 while dead. L4/265 is a living juniper watch case with "vine in DBH" and "couldn't find" notes but otherwise stable.

Suggested action: suppress/review-strike the H0/265 May duplicate. Downgrade the DBH gap because the tree is dead after 2023. No action on L4/265 from this pass.

Process lesson: the duplicate-stem artifact also appears on dead trees.

### Tag 268

Cases: H0/268 and L4/268.

H0/268 is a stable Nyssa with May 2024 183/183 and otherwise one stem. October 2025 has alive/health 4 but missing DBH. L4/268 is stable watch context.

Suggested action: suppress/review-strike H0/268's May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: classic H0 duplicate artifact.

### Tag 269

Cases: H0/269 and L4/269.

H0/269 is a very large pine with May 2024 562/562 and otherwise one stem. October 2025 has alive/health 6 but missing DBH. L4/269 is a dead juniper with DBH gaps and later dead measurements.

Suggested action: suppress/review-strike H0/269's May duplicate. Downgrade L4/269 dead-tree DBH gap.

Process lesson: the duplicate pattern includes very large pines, so size alone does not protect a row from being an entry artifact.

### Tag 270

Cases: H0/270 and L4/270.

H0/270 is a pine with May 2024 325/325 and otherwise one stem. L4/270 is a dead pine with intermittent DBH and a later "LOST TAG" note.

Suggested action: suppress/review-strike H0/270's May duplicate. Treat L4/270 as dead-tree missing/tag-context rather than identity review unless other evidence conflicts.

Process lesson: lost-tag notes should be surfaced but not automatically imply a tag swap.

### Tag 271

Cases: H0/271 and L4/271.

H0/271 is a stable Nyssa with May 2024 207/207 and otherwise one stem. L4/271 is a living juniper watch case with leaning/half-dead notes but no invariant issue.

Suggested action: suppress/review-strike H0/271's May duplicate. No action suggested for L4/271.

Process lesson: bare tag grouping is useful context but should not pull a clean watch case into the correction decision.

### Tag 273

Cases: H0/273 and L4/273.

H0/273 is Nyssa with May 2024 148/148 and otherwise one stem. L4/273 is a pine with normal history and October 2025 missing/dead-ish note "potentially fallen".

Suggested action: suppress/review-strike H0/273's May duplicate. L4/273 may need ordinary recent-missing/fallen follow-up, not DBH cleanup.

Process lesson: recent fallen/missing notes should feed mortality/absence logic, not duplicate-stem logic.

### Tag 276

Case: H0/276.

H0/276 is a very large pine with May 2024 549/549 and otherwise one stem. October 2025 has alive/health 8 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: classic H0 duplicate artifact plus missing-recent-DBH evidence.

### Tag 277

Cases: H0/277 and L3/277.

H0/277 appears as a nonqualifying excluded identity with no canonical DBH/stem profile. L3/277 is a dead Nyssa with early DBH 84, years of missing/dead rows, then April 2025 DBH 77 and fallen/dead context.

Suggested action: no action on H0/277 unless evidence review shows a missing qualifying tree. Downgrade L3/277 dead-tree DBH gap.

Process lesson: nonqualifying excluded identities need a clearer UI label so they do not look like broken canonical records.

### Tag 278

Case: H0/278.

H0/278 is a threshold-edge Nyssa. It starts at 60, then drops below threshold for several years, May 2024 has duplicate 50/50, then 48, then dead/missing. This is both a subthreshold cleanup case and a May duplicate case.

Suggested action: preserve early qualifying evidence, strike subthreshold DBH values from the canonical DBH profile, and suppress/review-strike the May 2024 duplicate 50. Treat the later death as real unless contradicted elsewhere.

Process lesson: threshold-edge trees need a rule that distinguishes "tree qualified historically" from "below-threshold measurements should not count as canonical stems."

### Tag 279

Cases: H0/279 and L3/279.

H0/279 is a very large pine with May 2024 543/543 and otherwise one stem. L3/279 is a dead pine with early DBH 457.5, gaps, then later dead DBH around 400-412.

Suggested action: suppress/review-strike H0/279's May duplicate. Downgrade L3/279 dead-tree DBH gap and treat the DBH decrease as dead-tree structural/measurement change unless there is conflicting evidence.

Process lesson: old 0.5 mm values are legacy precision and should not imply special certainty.

### Tag 280

Cases: H0/280 and L3/280.

H0/280 is a pine with May 2024 350/350 and otherwise one stem. L3/280 is a living juniper with 145 in 2019-2020, then 176 in 2021 and stable around 166-175 afterward, with a vine note in October 2024.

Suggested action: suppress/review-strike H0/280's May duplicate. L3/280 needs human DBH review: either early 145 was measured differently, or 2021 onward reflects a different measurement condition. Do not auto-correct without original sheets.

Process lesson: sustained post-jump DBH levels are different from one-off typos.

### Tag 282

Case: H0/282.

H0/282 is a stable Nyssa with May 2024 157/157 and otherwise one stem. October 2025 has alive/health 8 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: classic H0 duplicate artifact.

### Tag 283

Case: H0/283.

H0/283 is Acer rubrum with May 2024 235/235 and otherwise one stem. October 2025 has alive/health 7 but missing DBH.

Suggested action: suppress/review-strike the May duplicate. Keep October 2025 alive evidence with missing DBH.

Process lesson: the duplicate artifact is not taxon-specific.

### Tag 286

Case: H0/286.

H0/286 is a pine with a very likely one-off DBH problem: 315 in 2019-2020, then 155 in 2021, then 307+ afterward. It also has the May 2024 duplicate 310/310.

Suggested action: suppress/review-strike the May duplicate. Separately review the 2021 DBH 155 as a likely typo or bad measurement; probably correct/strike that DBH after checking source evidence.

Process lesson: single-survey DBH outliers need their own action path.

### Tag 287

Cases: H0/287 and L3/287.

H0/287 is Nyssa with May 2024 216/216 and otherwise one stem. L3/287 is a dead pine with intermittent dead DBH measurements.

Suggested action: suppress/review-strike H0/287's May duplicate. Downgrade L3/287 dead-tree DBH gap.

Process lesson: classic duplicate plus dead-gap pairing under one bare tag.

### Tag 288

Cases: H0/288 and L3/288.

H0/288 is Nyssa with May 2024 179/179 and otherwise one stem. L3/288 is a dead pine with intermittent dead DBH measurements.

Suggested action: suppress/review-strike H0/288's May duplicate. Downgrade L3/288 dead-tree DBH gap.

Process lesson: same as tag 287.

### Tag 289

Cases: H0/289 and L3/289.

H0/289 is a very large pine with May 2024 547/547 and otherwise one stem. L3/289 is a dead juniper at the threshold: 50 early, later 48/47, then missing.

Suggested action: suppress/review-strike H0/289's May duplicate. For L3/289, keep early 50 as qualifying if threshold-inclusive, but strike later subthreshold DBH values from the canonical profile; dead status remains.

Process lesson: threshold-inclusive 50 mm needs to be explicit, because 50 is qualitatively different from 47/48 under our rules.

### Tag 293

Case: H0/293.

H0/293 is Liquidambar with a different pattern. May 2024 has two stems, 147 and 131, while the surrounding years are basically one stem around 130-140. It is not an exact duplicate. A configured correction is already recorded.

Suggested action: do not apply the duplicate-DBH rule. Review the existing correction context and decide whether 147 is a real second stem, a mis-entered duplicate, or a corrected one-off value.

Process lesson: stem-count increase without duplicate DBH is a separate review category.

### Tag 103

Cases: H2/103 and L6/103.

H2/103 is a dead pine already inferred dead through repeated missing rows. L6/103 is a dead unidentified tree/pine-like case with DBH 290 early, missing while dead, then around 213 later, with notes "standing but broken" and "Brok of BH".

Suggested action: no correction for H2/103 from this pass. For L6/103, treat the DBH drop as likely related to breakage/dead structure unless original sheets suggest a typo.

Process lesson: broken-at-BH notes are high-value context for DBH drop diagnostics.

### Tag 104

Cases: H2/104 and L6/104.

H2/104 is a dead unidentified tree with repeated inferred-dead missing rows. L6/104 is a dead juniper with early DBH 60.5, missing for years, then 62 in October 2024.

Suggested action: no major correction. Downgrade L6/104 as dead-tree DBH gap.

Process lesson: dead-tree gap overflagging continues.

### Tag 106

Cases: H1/106 and L6/106.

H1/106 is a small dead unidentified tree around 51 mm, then unfound/missing. L6/106 is a pine with early alive DBH 337.5, then dead/standing/no bark, later dead DBH around 311-315, and October 2025 has two missing rows. Several configured corrections are already recorded.

Suggested action: treat H1/106 as a low-threshold dead tree with no extra action. For L6/106, preserve configured corrections and downgrade dead-tree DBH gaps. The two missing October 2025 rows should not count as measured stems.

Process lesson: configured corrections should be displayed as prior decisions so we do not repeatedly relitigate them.

### Tag 108

Cases: H4/108 and L1/108.

H4/108 is a living Liquidambar with horizontal growth/top broken notes. It has a May 2024 missing DBH but alive/health evidence, then DBH returns. L1/108 is a pine with dead -> alive health 1 -> dead behavior, which is a zombie/mortality-review case.

Suggested action: H4/108 should be treated as a missing DBH on a living damaged tree, not death. L1/108 belongs in mortality/zombie review.

Process lesson: alive missing-DBH rows are valid, and zombie cases need their own queue.

### Tag 110

Cases: H4/110 and L1/110.

H4/110 is a nonqualifying excluded identity. L1/110 is a pine with a clear one-off DBH problem: 332 in May 2024, 132 in October 2024, then 330 in April 2025. The tree is dead by then, but a 200 mm drop and rebound is not plausible.

Suggested action: review October 2024 DBH 132 as a likely typo, probably 332 or missing, depending on source evidence. Keep H4/110 as nonqualifying excluded unless evidence says otherwise.

Process lesson: rebound-shaped one-off DBH drops are high-confidence typo candidates even on dead trees.

### Tag 111

Case: L1/111.

L1/111 is a dead pine with DBH 262 in 2019-2020, missing for years, then 260/255 later, then missing. Dead throughout.

Suggested action: downgrade dead-tree DBH gap. No identity action suggested.

Process lesson: ordinary dead-tree intermittent DBH case.

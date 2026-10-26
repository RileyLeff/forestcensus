# Ninth 25 rebuilt needs-review cases

Date: 2026-05-10

Scope: next 25 rebuilt `needs_review` plot/tag cases not already mentioned in first- or second-review notes. This pass is a saturation check before consolidation.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| M6/5869 | Dead/no DBH, then dead DBH 72, then inferred dead. | Dead-tree first-measured pattern. | Downgrade to watch. |
| M7/915 | Dead/no DBH, then dead DBH 100. | Dead-tree first-measured pattern. | Downgrade to watch. |
| M7/979 | Dead/no DBH, later dead DBH 118 with poison ivy. | Dead-tree first-measured pattern with measurement note. | Downgrade to watch. |
| R1/942 | May 2024 two near-identical stems 175/173, then one stem later; knot note in Oct 2024. | Likely May 2024 double-measurement/slot artifact, with knot measurement context. | Rule-assisted review: suppress extra May 2024 near-duplicate unless source confirms two stems. |
| R1/951 | May 2024 two near-identical stems 209/208, then one stem later. | Likely May 2024 double-measurement artifact. | Rule-assisted review/suppress extra near-duplicate. |
| R1/956 | May 2024 two near-identical pine stems 454/451, then one stem later. | Likely May 2024 double-measurement artifact, but high-DBH pine deserves source caution. | Source/field review before suppressing extra May 2024 stem. |
| R1/961 | May 2024 duplicate 156/156; Oct 2025 DBH drops 157 -> 127 while tree remains healthy. | May duplicate is obvious. Oct 2025 DBH 127 is a separate suspicious outlier. | Suppress May duplicate; review/correct Oct 2025 DBH 127. |
| R2/605 | Dead/no DBH, then dead two-stem Prunus with note `merge Pru.ser.60`. | Dead-tree first-measured plus explicit merge clue. | Identity/merge review, not generic stem review. |
| R2/614 | Dead/no DBH, later dead Prunus DBH ~101-109 with merge notes. | Dead-tree first-measured plus merge clue. | Identity/merge watch/review. |
| R2/622 | Live Ilex 64-69, then Oct 2025 DBH 7 with health 9. | Obvious decimal/digit error or bad entry; 7 mm cannot be canonical DBH. | High-confidence correction candidate: strike/correct Oct 2025 DBH 7, likely 70-ish only if source supports. |
| R2/626 | Two-stem Ilex; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024; no identity review. |
| R2/628 | Dead/no DBH, then dead Pinus DBH 56-60. | Dead-tree first-measured pattern. | Downgrade to watch. |
| R2/632 | Morella gains dead second stem from Oct 2024 onward. | Real stem-level mortality. | Route to stem-level review/watch; preserve dead second stem. |
| R2/634 | Two-stem Ilex; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024. |
| R2/965 | Dead/no DBH, then dead DBH 81-82; note `broken dead below dbh?`. | Dead-tree first-measured with structural note. | Downgrade to watch. |
| R3/641 | Two-stem Acer; May 2024 records only main stem, second dead stem returns. | Bounded rank-2 gap and stem-level dead status. | Add blank rank-2 gap for May 2024. |
| R3/677 | Threshold second stem, knot note, then girdled/dead. | Mostly threshold/stem-level context. Sharp drop to dead looks like real girdling. | Downgrade mortality; suppress subthreshold DBHs. |
| R3/684 | Two-stem Ilex; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024. |
| R4/5205 | Large pine gains dead second stem; note says `2nd dead stem, left untagged`. | Real dead second stem, not identity weirdness. | Preserve second-stem evidence; blank rank-2 gap where DBH missing. |
| R4/5213 | Two-stem Ilex; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024. |
| R4/5220 | Two-stem Acer; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024. |
| R4/5224 | Two-stem Ilex; May 2024 records only main stem, second stem returns. | Bounded rank-2 gap. | Add blank rank-2 gap for May 2024. |
| R4/5227 | Two-stem Acer; May 2024 records only main stem, second dead stem returns. | Bounded rank-2 gap and stem-level dead status. | Add blank rank-2 gap for May 2024. |
| R4/5243 | Two-stem Acer; rank-2 absent April 2025 then returns. | Bounded rank-2 gap. | Add blank rank-2 gap for April 2025. |
| H1/236 | Dead pine drops 400 -> ~180, then Oct 2025 jumps 168 -> 232. | Dead-tree DBH loss can be real, but the later increase is suspicious after several lower values. | Source/field review for Oct 2025 DBH 232; do not auto-correct earlier dead-tree loss. |

## What this pass teaches

This pass mostly confirms saturation. The main rule classes are repeating:

- prior-dead/no-DBH followed by later dead DBH should be watch;
- bounded rank-2 gaps should become blank stem rows, not review alarms;
- May 2024 often under-recorded or double-recorded stems;
- stem-level dead/live states need separate treatment from tree-level mortality.

One small refinement: exact duplicate DBH is not the only duplicate artifact. R1/942, R1/951, and R1/956 show near-duplicate May 2024 stems that appear once and vanish. We should probably add a near-duplicate rule with stricter guardrails than exact duplicate suppression.

## Suggested rule changes

- Add `near_duplicate_stem_artifact` for one-survey extra stems with DBHs within a small tolerance, especially in May 2024.
- Keep near-duplicate suppression review-gated for large pines or known multi-stem trees.
- Add a merge-note route for notes like `merge Pru.ser.60`.
- Treat dead-tree DBH increases, not losses, as the suspicious direction unless notes explain structural remeasurement.

## Consolidation recommendation

This batch did not surface a major new class. It mainly reinforced the rule set from passes 7-8. I think we have enough signal to consolidate and implement the refined diagnostics before reviewing another tranche.

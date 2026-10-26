# Eighth 25 rebuilt needs-review cases

Date: 2026-05-10

Scope: next 25 rebuilt `needs_review` plot/tag cases not already mentioned in first- or second-review notes. This pass is mostly stem-profile and first-qualifying cases.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| H2/5859 | Dead in 2021, alive thereafter; May 2024 duplicate 341/341. | May 2024 is a classic duplicate-stem artifact. The 2021 dead row is suspicious because later health/DBH are strong and stable. | Suppress extra May 2024 duplicate; review/likely convert 2021 dead row to uncertain/missing. |
| H3/5842 | Dead/no DBH in 2023, then dead DBH ~193 afterward. | Dead-tree first-measured pattern. | Downgrade to watch. |
| H4/508 | Alive in 2021 with no DBH, then stable DBH ~350. | Prior-live missing DBH. This is a real blank-history/backfill case, but not suspicious. | Insert/retain blank DBH for 2021; no correction. |
| H6/521 | Known two-trunk Ilex; June 2020 records only one stem, second stem returns. | Real multi-stem tree with one missing survey for rank 2. | Add blank missing rank-2 stem for June 2020; do not treat as identity problem. |
| H6/529 | Two-stem pine; June 2020 records only one stem, second stem returns. | Same pattern as H6/521. | Add blank missing rank-2 stem for June 2020. |
| H7/891 | Large pine gets dead second stem 91 in Oct 2024; later second stem has health 0 but no DBH. | Likely real dead secondary stem/trunk; not tree-level identity problem. | Stem-level review/watch; preserve dead second stem evidence, blank later DBH. |
| H7/906 | Dead/no DBH, later dead DBH 275. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L0/5064 | Dead/no DBH, later dead DBH ~90-104 and species clarified to Nyssa. | Dead-tree first-measured pattern plus species note. | Downgrade to watch; preserve species clarification. |
| L3/5877 | Dead/no DBH, later dead DBH 111-113 and species change. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L4/5876 | Dead/no DBH, later dead DBH ~72-77. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L6/5022 | Dead/no DBH, later dead DBH 134-136; note `Only one stem visible`. | Dead-tree first-measured pattern with stem visibility note. | Watch; no correction. |
| L6/5027 | Dead/no DBH, one dead DBH 67 in Oct 2024. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L6/74 | Dead/no DBH in 2023, dead DBH 397 in Oct 2024, then inferred dead. | This one is not generic: we already suspected L6/74 and the 397 DBH may be a different tree/tag. | Keep in human DBH/identity review. |
| L6/990 | Dead/no DBH, then dead DBH 66. | Dead-tree first-measured pattern. | Downgrade to watch. |
| L7/5039 | October 2025 adds a second qualifying stem 73 next to 76. | New large stem appears at latest survey; could be real second stem or duplicate/slot issue. | Human stem/source review unless source clearly shows two stems. |
| M0/803 | Known two-trunk Nyssa; secondary stem absent in 2021-2022 then returns; mixed live/dead stem notes. | Real multi-stem/stem-level mortality case. | Add blank rank-2 gap for 2021-2022; route mortality at stem level. |
| M0/817 | Note says two trunks; second stem appears from 2020 onward and persists. | Real previously unrecorded second stem, probably should have blank 2019 history. | Insert blank rank-2 history for 2019; no review needed after rule exists. |
| M1/702 | Morella gains third qualifying stem and it persists. | Real multi-stem shrub, newly noticed/grew over threshold. | Accept; consider blank history only if prior survey exists and stem likely >60 before first record. |
| M1/834 | Threshold-edge Nyssa: 56 in 2019-2020, then 45-49 alive. | Live tree fell below threshold after qualifying; DBH should be suppressed when <50 but live evidence preserved. | Downgrade to threshold watch. |
| M1/870 | Known two-trunk Nyssa; poison ivy causes missing second-stem DBHs in May 2024/Apr 2025. | Measurement-access problem, not identity. | Add blank rank-2 gaps for poison-ivy surveys; route to measurement context/watch. |
| M3/347 | Known two-trunk Juniperus with one dead stem; rank-2 missing for 2022-2023 then returns. | Stem-level mortality/measurement gap. | Add blank rank-2 gap; preserve dead stem evidence. |
| M3/5826 | Dead/no DBH then dead DBH 73/71, then not found/inferred dead. | Dead-tree first-measured pattern. | Downgrade to watch. |
| M4/2459 | Known two-trunk Nyssa; one-stem rows in 2019/2022 and stem-level dead/alive transitions. | Real multi-stem/stem-level mortality case. | Add blank rank-2 gaps where missing; do not treat as generic new stem. |
| M6/505 | Morella note `Added`; second stem appears in May 2024 and persists to Oct 2024, then tree not found. | Real new/noticed stem. | Accept second stem from May 2024; blank earlier history optional if policy says >60 on entry implies earlier blank. |
| M6/5831 | Dead/no DBH, then dead DBH 173-183. | Dead-tree first-measured pattern. | Downgrade to watch. |

## What this pass teaches

Multi-stem continuity needs a first-class rule. If a tree has evidence of two trunks/stems before and after a missing rank-2 survey, the right canonical behavior is usually an explicit blank for the missing stem in that survey, not a new/disappearing-stem review case.

The phrase `Added` is useful. For cases like M6/505, it probably means a newly noticed stem, not an identity error.

The prior-dead first-qualifying pattern repeated again. This should be downgraded strongly once prior-dead and later-dead are both true.

## Suggested rule changes

- Add `bounded_stem_rank_gap` for multi-stem trees where rank N is present, absent, then present again.
- Downgrade bounded stem gaps to watch when the surrounding profile/taxon is stable.
- Treat notes `two trunks`, `dead second stem`, `one dbh dead`, `Added`, and `Only one stem visible` as stem-continuity evidence.
- Downgrade prior-dead/no-DBH -> later-dead/DBH first-qualifying cases.
- Keep latest-survey new large stems as review only when they lack notes or prior stem context.

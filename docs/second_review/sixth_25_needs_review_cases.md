# Sixth 25 rebuilt needs-review cases

Date: 2026-05-10

Scope: next 25 rebuilt `needs_review` plot/tag cases not already mentioned in the first- or second-review notes. This pass continues the mortality-heavy tranche but adds several DBH/identity cases.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| L7/5032 | One dead/0 row in June 2022 between healthy alive observations. | Classic one-survey death-label outlier. DBH returns to stable ~105-115 afterward. | High-confidence source/correction candidate: convert June 2022 dead/0 to uncertain/missing unless source proves death. |
| M0/486 | Nyssa gains a dead second stem in October 2024; later rows mix live/dead stems. | Looks like true stem-level mortality, not tree-level zombie. Notes explicitly say dead second stem. | Preserve as multi-stem/stem-status case; route away from generic mortality. |
| M0/581 | Early dead DBH 52, then alive subthreshold 40-44 for years with note `not dead`. | Threshold-edge tree with likely early mortality-label error. Later live DBHs should not qualify. | Human policy/source review: preserve alive evidence, suppress subthreshold DBHs, decide whether early dead rows should be uncertain. |
| M1/839 | Dead 2019-2021, alive low health 3 in 2022 with note `marked dead last year`, then dead. | Low-health zombie; plausible marginal live tissue or wrong alive label. | Human call on June 2022 alive/health 3. |
| M1/850 | Dead 2019-2021, alive health 3 in 2022, dead, then poison-ivy alive health 2 in Oct 2024. | Low-health zombie plus poison ivy context. | Human/source review; likely uncertain/marginal-live handling rather than DBH work. |
| M2/2408 | Alive 2019-2020, dead 2021, alive health 1 in 2022, dead afterward. | June 2022 may be marginal live tissue; note says marked dead last year. | Human mortality call; health 1 alive could remain alive if source confirms tissue. |
| M3/356 | Mostly dead in 2021, dead 2022-2023, alive low health later; notes say `alive !!!!`. | Field notes strongly support marginal live tissue after earlier death calls. | Keep for human mortality interpretation; do not auto-zero later low-health alive rows. |
| M3/5189 | Dead 2022-2023, alive from May 2024 onward; Oct 2024 note says `alive !!!!!`. | Similar to M3/356: later field notes assert live status. | Human review, likely older dead rows become uncertain/missing rather than later alive erased. |
| M3/605 | New second stem appears at 50 mm; health max jumps because a new stem has health 7. | Not a mortality contradiction. The health-rebound rule is incorrectly using tree-level max health across changing stem profiles. | Rule fix: do not classify health rebound as mortality when driven by a new stem appearance. |
| M4/2451 | One dead/0 row in June 2022 between healthy alive observations. | Clear one-survey death-label outlier. | High-confidence correction candidate: June 2022 dead/0 -> uncertain/missing. |
| M4/2452 | Early dead rows, then low-health alive from 2022 onward; later Quercus/willow oak notes. | Identity/taxon and mortality are entangled. Later repeated live evidence is credible. | Human/source review; probably early dead rows or early identity are wrong/uncertain. |
| M4/2461 | Dead 2019-2021, alive DBH 389/health 6 in 2022, then confirmed killed/dead later. | June 2022 is suspicious but not impossible; later `Confirmed Kill` supports death after that. | Human/source review of June 2022 row and tag identity. |
| M5/487 | Three-stem Morella with one dead stem, then later all alive/mixed missing. | Stem-level status issue; tree-level zombie logic is too blunt. | Route to multi-stem mortality review; preserve evidence. |
| M5/5870 | Dead 2021, alive low health 3 in 2022, then missing/dead. | Low-health zombie; similar to M1/839. | Human call on June 2022 alive/health 3 and whether first dead row should be uncertain. |
| M7/323 | Alive, missing, alive, one dead row in June 2023, then alive again. | June 2023 is likely one-survey death-label outlier. | Correction candidate: June 2023 dead/0 -> uncertain/missing unless source proves death. |
| M7/5834 | Dead 2023-2024, then October 2025 alive health 8. | Suspicious latest-survey revival, or older rows describe a dead stem/tag while October found live tree. | Source/field review. |
| M7/5835 | Dead pine through April 2025, then October 2025 has health 9 and 0; note says `mis ID should be Pin 5835`. | Identity/stem confusion in latest survey; not simple mortality. | Human source review, preserve note; decide whether live row belongs to this UUID. |
| R4/5206 | Dead May 2024 between alive June 2023/Oct 2024, then dead again from April 2025. | May 2024 is likely a one-survey death-label outlier; April 2025 may be real later death. | Review/correct May 2024 separately from later death. |
| M0/816 | Dead pine with stable ~100 DBH, one October 2024 DBH 196, then 97; October 2025 alive health 6. | DBH 196 is a clear source/entry problem. October 2025 alive health is also suspicious after years dead. | Human/source review; likely strike October 2024 DBH and review October 2025 health/alive. |
| L2/239 | June 2023 DBH 110 noted estimated due poison ivy; low-health alive/dead oscillation later. | DBH outlier has an explanatory note. Mortality is low-health marginal behavior, not a clean error. | Downgrade DBH to measurement context; keep low-health mortality watch/review. |
| L3/5886 | June 2022 DBH 319/dead between ~168/170 alive rows; later stable ~170. | Obvious wrong row/DBH/source error plus one-year death contradiction. | High-confidence correction/source candidate: strike or move June 2022 DBH/dead row. |
| L6/101 | Early dead rows followed by strong live tree; May 2024 DBH 101 outlier in ~140-165 series; Oct 2025 dead. | Multiple issues: early death labels probably wrong, May 2024 DBH likely bad, Oct 2025 may be real later death. | Human/source review; likely strike/correct May 2024 DBH and revisit early dead labels. |
| L6/76 | DBH regime shift 114 -> persistent ~228; April 2025 dead then Oct 2025 alive health 8. | Early DBH likely wrong tag/source; later mortality blip may be a field/status mistake or stem/bole ambiguity. | Human/source review for DBH regime and April/October 2025 status. |
| L7/14 | Small Juniperus with noisy DBH and one dead row in 2021, otherwise alive. | One-year death label likely wrong; DBH noise may be threshold/small-stem measurement variation. | Review June 2021 dead/0; likely uncertain/missing. DBH needs lower-severity small-tree treatment. |
| M0/580 | DBH regime shift 214 -> persistent ~76; health rebound flagged but all rows are alive. | Not a mortality issue. The real problem is old-source/identity DBH regime shift. | Route to DBH/identity review; downgrade health rebound when status remains observed alive. |

## What this pass teaches

The mortality rule needs another refinement: a health rebound should not automatically mean mortality review if both observations are `observed_alive`, as in M0/580. That belongs in health-change watch at most.

Health transitions also need to account for stem count changes. M3/605 gets flagged because the maximum health jumps when a new second stem appears. That is not a tree-level recovery event.

The one-survey death-label pattern is now very clear: L7/5032, M4/2451, M7/323, R4/5206, and probably L7/14. These are good candidates for a `single_survey_death_label_outlier` diagnostic.

Several cases show October 2025 suspicious live revivals after repeated dead rows: M7/5834, M7/5835, and M0/816. These should stay human/source review cases because October 2025 is newer and often more trustworthy, but the contradiction is too strong to auto-resolve.

## Suggested rule changes

- Add `single_survey_death_label_outlier` for alive -> observed_dead/health 0 -> alive sequences.
- Downgrade `sharp_health_rebound` when both previous and current rows are `observed_alive`.
- Suppress tree-level health rebound diagnostics when the rebound is caused by a new stem appearing in a multi-stem profile.
- Route notes like `dead second stem`, `1 dead trunk`, and mixed live/dead same-survey rows to stem-level mortality review.
- Add small-tree DBH tolerance/watch handling for near-threshold Juniperus/Morella cases where measurement noise is large relative to DBH.

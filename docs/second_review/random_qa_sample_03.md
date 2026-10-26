# Random QA sample 03

Date: 2026-05-10

Scope: deterministic random sample of 25 plot/tag labels already mentioned in review docs, excluding labels from `random_qa_sample_01.md` and `random_qa_sample_02.md`.

Sampling seed: `20260512`

## Sampled cases

| Case | Current route | QA verdict | Notes |
|---|---|---|---|
| R2/605 | `watch_context`; dead-tree stem context and prior-dead first DBH | Mostly right | Dead multi-stem Prunus/unidentified merge context is watch-level, but merge notes should stay visible as identity context. |
| L7/20 | `dbh_review`; `stable_incompatible_dbh_era` | Looks right | Pine 307/307 then stable 468-473; clear source-era/tag-alignment review. |
| L2/222 | `mortality_review`; low-health one-survey death | Looks right | May 2024 health 2, October 2024 dead/0, then alive health 1/6. Human mortality call is appropriate. |
| L6/105 | `mortality_review`; early dead then live | Looks right | Early dead labels followed by strong live Juniperus; human mortality/source review is right. |
| L7/39 | `candidate_identity_link` | Looks right | Dead/missing pine link endpoint; candidate link review is appropriate. |
| R4/5222 | `stem_profile_review`; threshold/subthreshold plus stem-gap behavior | Too loud | Multi-stem Ilex has one May 2024 missing rank-2 and a persistent subthreshold third stem. Likely bounded-gap/threshold context, not urgent new-stem review. |
| M0/816 | `mortality_review`; zombie plus dead-tree DBH outlier/increase | Looks right | October 2024 DBH 196 and October 2025 alive health 6 both need human/source review. |
| H5/559 | `candidate_identity_link`; dead-tree stem context | Looks right | Candidate link plus old two-trunk dead Acer case; link review is appropriate. |
| L0/477 | `mortality_review`; low-health one-survey death | Looks right | April 2025 dead/0 with poison ivy between low-health alive rows; human/source call is appropriate. |
| R4/5236 | `dbh_review`; `single_survey_dbh_outlier` | Looks right | October 2024 DBH 58 inside stable 93-94 Nyssa trajectory. |
| R4/5211 | `watch_context`; dead-tree gap and prior-dead first DBH | Looks right | Dead unidentified tree with later dead DBHs 141/139; watch/context is fine. |
| L4/613 | `rule_assisted_cleanup`; stem mortality plus subthreshold DBH | Looks right | Morella second stem has April 2025 dead DBH 11 and October 2025 dead DBH 65 with `?`; rule-assisted/watch is okay, source note remains important. |
| M1/831 | `dbh_review`; `stable_incompatible_dbh_era` | Looks right | Middle-era 315/315 between 390-ish eras; clear source-era review. |
| L2/214 | `dbh_review`; `single_survey_dbh_outlier` | Looks right | June 2021 DBH 123 is isolated against ~101-115 Juniperus sequence. |
| L1/110 | `dbh_review`; dead-tree isolated DBH outlier | Looks right | October 2024 DBH 132 inside ~330 pine trajectory; source/correction review is right. |
| L7/973 | `candidate_identity_link` | Looks right | Dead/no-DBH candidate-link endpoint. |
| M5/972 | `candidate_identity_link` | Looks right | Dead/no-DBH candidate-link endpoint. |
| L5/433 | `missing_from_october_2025` | Maybe too loud | Long-dead pine missing from October 2025 is probably normal. Recent missing was deemed acceptable; missing-from-October bucket may still be over-prioritizing dead trees. |
| L1/5060 | `watch_context`; `structural_measurement_dbh_context` | Too soft | Later `leaning` note is being used to explain June 2022 DBH 130 isolated between 96 and 101. Structural context should be temporally local. |
| R4/5205 | `watch_context`; dead second-stem context | Looks right | Large pine with explicit `2nd dead stem, left untagged`; watch/context is good. |
| H1/199 | `dbh_review`; dead-tree loss then increase | Looks right | Dead Nyssa 95 -> 66 -> 86/83/87; May 2024 66 may be an isolated low dead-tree measurement, so review is reasonable. |
| L2/207 | `watch_context`; `dead_tree_stable_dbh_loss_context` | Looks right | All-dead stable lower DBH era; new rule is behaving correctly here. |
| H1/250 | `dbh_review`; exact-threshold/dead-tree DBH jump | Too loud | Live 70/70, then dead with DBH 58/57/61. This resembles dead-tree/threshold context more than urgent DBH review. |
| L6/5027 | `watch_context`; prior-dead first DBH | Looks right | Dead/standing tree with later Juniperus DBH; watch/context is okay. |
| H3/155 | `dbh_review`; source-era plus May 2024 outlier | Looks right | Early 280/280, stable ~209-218, and May 2024 270 outlier. Human source review is appropriate. |

## Summary

This third QA sample again supports the main classifier shape. Most review cases still look genuinely review-worthy: source-era DBH blocks, isolated DBH outliers, mortality contradictions, and candidate links are landing where they should.

It also reinforces the same small set of targeted fixes:

- Structural notes must be temporally local. L1/5060 repeats the L6/83 problem: a later `leaning` note should not explain an earlier isolated DBH spike.
- Exact-threshold and dead-tree near-threshold cases are still too loud. H1/250 and prior samples H6/530/H0/278 all point the same way.
- Multi-stem bounded gaps with threshold/subthreshold stems are too loud. R4/5222 should probably be watch/context rather than urgent stem-profile review.
- Missing-from-October may be over-prioritizing long-dead trees. L5/433 is dead for years and absent from October 2025; that should probably be quiet/watch, not high priority.
- Merge/species notes on dead multistem trees should remain visible as identity context, even when not urgent.

## Candidate follow-up rules reinforced

| Candidate rule | Evidence from this sample |
|---|---|
| Make structural DBH context survey-local or adjacent-window-only. | L1/5060. |
| Expand threshold-edge/dead-tree context to exact 50 and nearby dead DBH drops. | H1/250. |
| Downgrade bounded secondary-stem gaps when subthreshold/threshold context explains the extra stem. | R4/5222. |
| Do not prioritize missing-from-October for trees already long dead before October 2025. | L5/433. |
| Keep merge/species notes surfaced as identity context even in watch cases. | R2/605. |

# Random QA sample 02

Date: 2026-05-10

Scope: deterministic random sample of 25 plot/tag labels already mentioned in review docs, excluding the 25 labels from `random_qa_sample_01.md`.

Sampling seed: `20260511`

## Sampled cases

| Case | Current route | QA verdict | Notes |
|---|---|---|---|
| M7/325 | `dbh_review`; isolated DBH outlier plus explicit mortality note | Looks right | June 2021 DBH 150 is isolated against ~110-116; June 2022 death is bracketed by alive evidence and note says marked dead last year. |
| L6/5022 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Long-dead/standing tree first measured later; watch/context is fine. |
| L0/905 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead/fallen tree first measured later; watch/context is fine. |
| M5/2500 | `mortality_review`; low-health one-survey death | Looks right | October 2024 dead/0 is bracketed by low-health alive; October 2025 may be a later real death. |
| M7/318 | `mortality_review`; zombie/dead-then-live sequence | Looks right | Early dead labels followed by low-health alive sequence, then later death. Human mortality call is appropriate. |
| L0/170 | `mortality_review`; dead/no-DBH then low-health alive then dead | Looks right | Needs human call on whether 2022 dead row is uncertain versus 2023 marginal live tissue. |
| M0/817 | `watch_context`; `stem_mortality_context` | Looks right | Two-trunk Nyssa gains persistent second stem after 2019; watch/blank-history context is fine. |
| L7/5040 | `watch_context`; dead-tree gap and prior-dead first DBH | Looks right | Dead tree with delayed dead DBH and species specificity changes; watch/context is okay. |
| R2/614 | `watch_context`; prior-dead first DBH | Mostly right | Dead tree with merge/species notes. Watch is okay, but merge notes should remain surfaced for identity context. |
| L7/5039 | `stem_profile_review`; `new_persistent_large_stem` | Looks right | October 2025 adds a second qualifying stem near the existing stem; this needs stem/source review. |
| L3/5881 | `mortality_review`; identity/mortality mess | Looks right | Known weird new-tree/dead/large-pine case. Human review is appropriate. |
| H6/523 | `dbh_review`; `stable_incompatible_dbh_era` | Looks right | Dead pine 136/136 then dead 501/498 is too extreme for dead-tree shrinkage; source/identity review is right. |
| H4/145 | `dbh_review`; `stable_incompatible_dbh_era` | Looks right | H4 early source-era pattern: 372/372 then stable ~97-110. |
| H7/459 | `mortality_review`; explicit note plus mortality contradiction | Looks right | Dead row followed by `marked as dead last year`; still fine to keep in human mortality review. |
| H6/530 | `dbh_review`; max/ranked DBH jump and rank gap | Too loud | Dead/standing Nyssa 64, later dead DBH 50/53. This is threshold-edge/dead-tree context and should likely downgrade once exact-50 logic is fixed. |
| M6/505 | `rule_assisted_cleanup`; `near_duplicate_stem_artifact` | Too aggressive | Source explicitly says `Added`, and the second Morella stem persists into October 2024. This should be new-noticed/persistent stem context, not probable duplicate cleanup. |
| L1/927 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead pine first measured later; watch/context is fine. |
| L1/122 | `dbh_review`; max/ranked DBH jump | Acceptable | Small low-health Juniperus drops 85 -> 71 and stays 71. No explanatory note, so human review is reasonable even if this may be real decline/measurement variation. |
| M5/5870 | `mortality_review`; early dead then low-health alive | Looks right | Human call needed on whether early dead or 2022 low-health alive is the bad label. |
| H7/880 | `mortality_review`; low-health death-label outlier plus rebound | Looks right | Failing/girdled Nyssa with dead/low-live oscillation; human mortality review is appropriate. |
| M7/5832 | `candidate_identity_link` | Looks right | Dead/no-DBH link endpoint; candidate link review is appropriate. |
| H4/140 | `dbh_review`; stable-era plus duplicate/stem context | Mostly right, one noisy code | Source-era review is right, but `probable_duplicate_stem_artifact` is too aggressive because notes explicitly say `two trunks` and equal 91/91 may be real. |
| L5/985 | `candidate_identity_link` | Looks right | Dead/no-DBH link endpoint; candidate link review is appropriate. |
| R2/628 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead pine first measured later; watch/context is fine. |
| M1/5860 | `mortality_review`; single-survey death-label outlier | Looks right | October 2024 dead/fallen row is bracketed by live rows; human mortality/source review is right. |

## Summary

This second QA sample again says the broad classifier shape is good. The current review stream is mostly made of genuinely human-needed DBH source-era cases, mortality contradictions, stem-profile review, and candidate links.

It also repeats several refinements from QA sample 01:

- Exact-threshold DBH cases are still too loud. H6/530 is the clearest repeat: dead/standing 64 -> dead 50/53 should probably be threshold/dead-tree context, not generic DBH review.
- Near-duplicate cleanup is too aggressive when there is an explicit added/new-stem note and the stem persists into another survey. M6/505 mirrors M7/454 from QA sample 01.
- Duplicate-stem artifact logic should respect explicit multistem notes. H4/140 has `two trunks`, so early equal DBHs should not be treated as probable duplicate artifacts.
- Merge/species notes on dead trees, like R2/614, are okay as watch but should remain visible in the UI as identity context.

## Candidate follow-up rules reinforced

| Candidate rule | Evidence from this sample |
|---|---|
| Expand threshold-edge DBH jump test to include exactly 50 mm and dead-tree context. | H6/530. |
| Let explicit `added` / `new stem` override near-duplicate artifact, especially when the extra stem persists. | M6/505. |
| Prevent duplicate-artifact routing when notes explicitly say `two trunks`, `three trunks`, or similar. | H4/140. |
| Keep merge/species notes visible as identity context even when the case is otherwise watch-level. | R2/614. |

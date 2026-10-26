# Random QA sample 01

Date: 2026-05-10

Scope: deterministic random sample of 25 plot/tag labels already mentioned in the second-review notes or human-attention queue, after the fourteenth-batch consolidation.

Sampling seed: `20260510`

## Sampled cases

| Case | Current route | QA verdict | Notes |
|---|---|---|---|
| L3/918 | `candidate_identity_link`; `prior_dead_first_qualifying_dbh` | Looks right | Dead tree with delayed DBH and candidate link. Human/link review is appropriate. |
| M7/326 | `dbh_review`; `single_survey_dbh_outlier`, explicit mortality note | Looks right | June 2023 alive/DBH 116 is isolated against dead ~73-75 sequence and note says marked dead last year. Keep in review. |
| L7/33 | `rule_assisted_link` | Looks right | Long-dead pine with no current invariant pressure; rule-assisted link bucket is fine. |
| R2/622 | `dbh_review`; `max_dbh_jump`, `subthreshold_dbh_present` | Looks right | October 2025 DBH 7 in a stable 64-69 live Ilex is a clean correction/source-review case. |
| L2/928 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead tree first measured after death; watch/context is appropriate. |
| L6/83 | `watch_context`; `structural_measurement_dbh_context` | Too soft | Later `fell due to girdling` note is being allowed to explain earlier 98.5 -> 201 -> 281 -> 206 DBH jumps. This should remain source-era/outlier review, or structural notes should only apply when temporally local. |
| H3/5842 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead tree with later dead DBH; watch/context is fine. |
| L0/171 | `rule_assisted_link` | Looks right | Long-dead/missing pine link case; no urgent invariant. |
| H3/160 | `dbh_review`; `single_survey_dbh_outlier` | Looks right | May 2024 DBH 407 inside stable ~493-501 pine trajectory. |
| H0/278 | `dbh_review`; threshold/subthreshold/duplicate/ranked jump mix | Slightly too loud | This is a threshold-edge Nyssa around 43-60 mm plus May 2024 duplicate 50/50. The remaining `ranked_dbh_jump` keeps it urgent; threshold-edge logic should probably include exactly 50 mm. |
| H5/567 | `dbh_review`; `persistent_dbh_regime_shift` | Looks right | Outside-plot notes plus 203 -> 169-195 regime. Human review is reasonable. |
| H7/906 | `watch_context`; `prior_dead_first_qualifying_dbh` | Looks right | Dead Quercus first measured after death; odd note is preserved, not urgent by itself. |
| H4/136 | `candidate_identity_link`; `stable_incompatible_dbh_era` | Looks right | H4 source-era/tag-alignment pattern and candidate link. |
| R1/956 | `rule_assisted_cleanup`; `near_duplicate_stem_artifact` | Looks right | May 2024 near-duplicate 454/451 appears once and disappears. |
| L6/91 | `mortality_review`; `mortality_contradiction` | Looks right | Long-dead Juniperus with October 2025 alive health 1 and old note about possible new tags. Human review is appropriate. |
| L6/101 | `mortality_review`; mortality contradiction plus May 2024 DBH outlier | Looks right | Early dead labels conflict with later live tree, plus May 2024 isolated DBH 101. Human review is appropriate. |
| R4/5227 | `stem_profile_review`; second-stem gap and stem mortality context | Maybe too loud | This looks like a dead secondary stem missing in May 2024 and then returning. It likely wants blank rank-2 gap/watch rather than urgent `new_persistent_large_stem`/`blank_missing_stem_backfill_candidate`. |
| M2/2408 | `mortality_review`; explicit note plus one-survey death | Looks right | June 2021 dead followed by 2022 health 1 with `marked dead last year`; keep human mortality/source review. |
| M0/909 | `candidate_identity_link`; `nonqualifying_tree_excluded` | Looks right | Evidence-only/nonqualifying endpoint with a link; human link review is appropriate. |
| H4/130 | `watch_context`; dead-tree gap/stem/structural context | Maybe too soft | October 2025 adds two large dead stems 211/209 after a one-stem dead history. Watch is understandable, but source/field review may still be wanted for late large dead second stem. |
| L1/5052 | `watch_context`; measurement/stem context | Too soft | Notes say `to 5051` and `NO second stem`; this is tag/stem-scope ambiguity, not just measurement/stem mortality context. Should stay in human review. |
| R3/641 | `stem_profile_review`; second-stem gap and stem mortality context | Maybe too loud | Similar to R4/5227: missing secondary dead stem in May 2024, present before/after. Candidate for blank rank-2 gap/watch. |
| L6/61 | `dbh_review`; `stable_incompatible_dbh_era` | Looks right | Pine 181/181 then stable 339-369; source-era review is appropriate. |
| M7/454 | `rule_assisted_cleanup`; `near_duplicate_stem_artifact` | Too aggressive | Third Morella stem persists into April 2025 and has `new stem added`; this should be newly noticed/persistent stem context, not probable duplicate cleanup. |
| L7/12 | `dbh_review`; single-survey dead-tree DBH outlier | Looks right | October 2024 DBH 126 between dead DBH 158 values; source/correction review is appropriate. |

## Summary

The new buckets are mostly behaving well. The sample supports the broad direction: isolated DBH outliers, source-era blocks, candidate links, and mortality contradictions are staying in review; dead-tree delayed DBH and prior-dead first measurements are mostly downgraded appropriately.

The QA sample did find a few actionable rule refinements:

- Structural notes should be temporally local. A later `fell due to girdling` note should not automatically downgrade older source-era DBH jumps.
- Threshold-edge DBH logic should treat exactly 50 mm as threshold context, not only values below 50.
- Secondary-stem bounded gaps with dead/mixed stem context should probably suppress `new_persistent_large_stem` / `blank_missing_stem_backfill_candidate` when the same rank is present before and after.
- Tag-change/no-second-stem notes such as `to 5051` and `NO second stem` should keep a case in human tag/stem-scope review.
- Near-duplicate stem cleanup should not fire when the extra stem persists into later surveys or has an explicit `new stem added` note.

## Candidate follow-up rules

| Candidate rule | Expected effect |
|---|---|
| Make structural DBH context survey-local or adjacent-window-only. | Prevent later fall/girdle notes from hiding older source-era/outlier problems. |
| Expand threshold-edge DBH jump test to include `min <= 50 <= max <= 60`. | Downgrade H0/278-style exact-threshold cases. |
| Add `tag_scope_note_review` for `to <tag>`, `NO second stem`, `could be one of the new tags`, and similar notes. | Keep tag/stem-scope ambiguity in human review. |
| Suppress new/disappearing-stem review when a bounded rank gap plus stem mortality context explains the pattern. | Reduce noisy urgent stem-profile review for dead secondary stems. |
| Require near-duplicate artifact to be non-persistent, and let explicit `new stem added` override it. | Avoid false duplicate cleanup for M7/454-style real new Morella stems. |

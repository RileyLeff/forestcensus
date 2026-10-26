# Targeted QA after consolidation

Date: 2026-05-11

Scope: stratified QA sample from the current `needs_review` stream after the random-QA consolidation rebuild. I sampled across the remaining major buckets/codes rather than drawing another broad random sample.

Current UI-facing `needs_review` stream: 225 cases.

| Bucket | Cases |
|---|---:|
| `dbh_review` | 86 |
| `mortality_review` | 79 |
| `candidate_identity_link` | 35 |
| `stem_profile_review` | 18 |
| `taxon_or_identity_conflict` | 6 |
| `new_in_october_2025` | 1 |

## Sampled cases

| Case | Current route | QA verdict | Notes |
|---|---|---|---|
| L6/87 | `taxon_or_identity_conflict`; `tag_scope_note_review` | Right issue, misleading bucket | Dead/live/missing history with `could be one of the new tags`; human identity review is right. UI summary says taxon conflict even though this is tag-scope ambiguity, not taxon conflict. |
| R2/631 | `taxon_or_identity_conflict`; `taxon_conflict` | Looks right | Ilex threshold-edge tree plus October 2025 note-row/taxon artifact: `should be Pin 93 no Pin 6 in p`. Needs human call; likely not a real second stem. |
| L6/91 | `taxon_or_identity_conflict`; `tag_scope_note_review` | Right issue, misleading bucket | Long-dead Juniperus with `could be one of the new tags` and October 2025 health 1. Human review is right; bucket/summary should say tag-scope, not taxon conflict. |
| M4/2444 | `taxon_or_identity_conflict`; `taxon_conflict` | Looks right | Old unidentified dead tree, later `Confirmed Kill Pin tae`, `change to pine`, and October 2025 `mixup` with Quercus/unidentified rows. Needs source/identity decision. |
| L1/5052 | `taxon_or_identity_conflict`; `tag_scope_note_review` | Looks right | April 2025 says `to 5051`; October 2025 says `NO second stem`. This is exactly the kind of stem/tag-scope ambiguity that should stay in review. |
| M7/5274 | `taxon_or_identity_conflict`; `tag_scope_note_review` | Looks right | New Morella with `tag on trunk 2` and `new tag 795`; October 2025 DBH profile changes sharply. Human tag/stem-scope review is right. |
| L7/5029 | `candidate_identity_link`; mortality contradictions | Looks right | Linked to 982; repeated alive/dead/low-health sequence. This belongs in link plus mortality review. |
| H4/992 | `candidate_identity_link`; source-note DBH conflict | Looks right | Linked from 136; May 2024 note says `might be 136`, and DBH goes 187 -> 111 -> 194. Human link/source review is right. |
| M2/5863 | `candidate_identity_link`; single-survey DBH outlier | Looks right | Linked from 5883; May 2024 DBH 163 is isolated between ~127 and ~125, with species wobble. Human review is right. |
| L3/918 | `candidate_identity_link`; prior-dead first DBH | Looks right | Link from 301 has too-large DBH mismatch. Even though this endpoint alone is watch-like, the link itself needs human review. |
| H5/912 | `candidate_identity_link`; dead first qualifying DBH | Looks right | Link from 559 has too-large DBH mismatch; dead Acer evidence remains link-review material. |
| M0/585 | `dbh_review`; DBH regime/identity chaos | Looks right | 68 dead/dead/dead -> 235 alive -> 56/53/57 dead. This is not a normal threshold case; likely source/identity or row alignment issue. |
| M7/325 | `dbh_review`; single-survey outlier plus mortality weirdness | Looks right | June 2021 DBH 150 is isolated inside a 110-ish Juniperus sequence, with one-year dead row and `Marked dead last year`. Human review is right. |
| M3/5188 | `dbh_review`; outlier/regime plus new stems | Looks right | Morella 134 -> 160/164, May 2024 isolated 104, then later multistem. Still review-worthy because DBH and stem profile are both changing. |
| M7/320 | `dbh_review`; source-note DBH conflict | Looks right | Notes explicitly say `dbh approx. 200 not 450` / `200 range, not 450`; June 2022 DBH 451 should stay in human source review. |
| L1/145 | `dbh_review`; stable incompatible era | Looks right | 161.5/161.5, missing, then stable 284-300. This is exactly source-era/tag-alignment review. |
| L6/49 | `mortality_review`; death label outlier and final mortality | Looks right | June 2022 dead row is contradicted by 2023 `Marked dead last year`, but October 2025 is dead again after several alive surveys. Needs human decision because there may be two mortality events/corrections. |
| H7/895 | `mortality_review`; zombie/low-health death row | Looks right | Nyssa alive through low health, June 2023 dead/0, later alive with poison ivy/girdle notes. Human mortality/source call is right. |
| L1/5050 | `mortality_review`; low-health zombie sequence | Looks right | Low-health alive rows, June 2023 dead/0, May 2024 `zombie?`, then October 2025 dead/0. Needs human mortality interpretation. |
| M2/2408 | `mortality_review`; death label outlier then true dead era | Looks right | June 2021 dead/standing, June 2022 `marked dead last year` alive health 1, then persistent dead from 2023 onward. Needs a split decision: early death label correction plus later true mortality. |
| M3/356 | `mortality_review`; zombie/field-boundary weirdness | Looks right | Alive/mostly dead, dead rows, then alive rows with `alive !!!!`, April 2025 dead `out of plot`, October 2025 alive health 3. Human review is right. |
| H2/208 | `stem_profile_review`; duplicate plus later second stem | Looks right | May 2024 exact duplicate 480/480 is suspicious, but October 2025 has two similar large stems 475/471. This should not be auto-dropped; it needs a stem-history decision. |
| L6/503 | `stem_profile_review`; small new Morella stems | Maybe too loud | Second stem enters at 54 mm and third is subthreshold; Morella cluster context plus threshold-edge size makes this feel more watch/context than urgent review. |
| R1/960 | `stem_profile_review`; duplicate plus persistent second stem | Looks right | May 2024 has duplicate-like 182/182 plus 170, but later surveys persist as two stems around 180/170. Human review/blank-backfill decision is right. |
| R2/5303 | `new_in_october_2025` | Looks right | New October 2025 Ilex DBH 65 health 6. Needs complementary-search/new-tree review before canonical acceptance. |

## QA synthesis

The remaining `needs_review` stream is mostly high signal. The DBH cases left in review are dominated by stable but incompatible DBH eras, isolated outliers, explicit source-note conflicts, and dead-tree DBH increases. The mortality cases are mostly real decision-layer cases where one row should be corrected or interpreted differently, not broad classifier noise.

The two clearest improvements:

1. `tag_scope_note_review` needs its own bucket/summary language.

   Currently these are routed through `taxon_or_identity_conflict`, so cases like L6/87 and L6/91 say "conflicting taxon evidence" even when the actual problem is a note like `could be one of the new tags`. The review priority is right, but the UI/user-facing label is wrong.

   Follow-up: implemented as the `tag_or_stem_scope_review` bucket.

2. Newly appearing small secondary stems near threshold should probably have a watch/context route.

   L6/503 is the clearest example: Morella has a second stem entering at 54 mm and a third subthreshold stem. This is compatible with threshold crossing/newly noticed small stems, not necessarily a high-priority identity problem. We already handle small bounded gaps; we may want a sibling code like `threshold_new_stem_context` for new qualifying stems entering at roughly 50-60 mm.

   Follow-up: implemented as `threshold_new_stem_context`, currently scoped to small newly recorded secondary stems in clustered taxa such as Morella.

## Decision-layer implications

This QA pass reinforces that the next system piece should be a durable manual decision layer rather than more broad diagnostics. The cases above need decisions such as:

- mark a source row as note-only / not a real stem observation;
- strike or correct a DBH for a specific survey/stem;
- accept a candidate tag link or reject it;
- split one tag into multiple UUID histories;
- correct a single death label while preserving later true mortality;
- insert blank DBH/health rows for newly recognized large stems.

The classifier is now doing its job: it is surfacing the places where these decisions need to be made.

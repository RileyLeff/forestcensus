# Second review: next 25 needs-review cases

Date: 2026-05-10

Input ordering: cases 26-50 from the rebuilt UI-like `needs_review` queue in `output/canonical_review/tree_cases.csv`.

## Quick synthesis

This batch reinforces the split from the first 25:

- Candidate links remain common, especially dead-tree retags where the source and target should be reviewed as one link.
- A smaller subset are genuine DBH/stem cases. These are richer than the old raw-jump list: threshold-edge shrubs, old-source regime shifts, poison ivy / fallen-tree measurement gaps, and May 2024 duplicate-stem artifacts.
- Some cases are not actually “bad data” so much as “canonical policy needed”: whether subthreshold-but-observed living trees stay as evidence, how threshold-edge trees qualify, and how to represent a tree whose old tag has no current DBH but an explicit retag exists.

## Cases

### 26. M4/2444

Bucket: `taxon_or_identity_conflict`

History: dead unidentifiable tree at 194 mm in 2019-2020, dead/no DBH through 2023, May 2024 not-found row labeled Pinus with note `Confirmed Kill Pin tae`, April 2025 unidentifiable at 182 mm with note `change to pine`, October 2025 introduces Quercus phellos with note `mixup`.

Impression: likely dead Pinus/unidentifiable tree with October 2025 mixup noise. The Quercus label should not become canonical taxon evidence without original-source confirmation.

Suggested action: likely call this Pinus taeda or Unidentifiable with pine note support; suppress/ignore the October 2025 Quercus `mixup` row as taxon evidence unless source review says otherwise.

Teaches us: note text like `mixup` should down-rank a source row as taxon evidence.

### 27. L4/615

Bucket: `dbh_review`

History: living Morella. One stem at 62 mm in May 2024, two stems at 74/51 in October 2024, two stems at 64/53 in April 2025, October 2025 has 73 plus a subthreshold 42 with note `?`.

Impression: likely a real two-stem threshold-edge shrub, not a duplicate artifact. The 51/53 second stem qualifies in 2024-2025; the October 2025 42 should not count as qualifying DBH but may be the same second stem measured differently.

Suggested action: keep as two-stem when both stems are >=50; suppress October 2025 42 from qualifying profile but preserve health/status. Consider a stem-backfill blank for May 2024 second stem rather than treating it as absent.

Teaches us: October 2025 protocol rule should not say “missing DBH” when the row has subthreshold DBH; that is threshold-edge measurement, not DBH omission.

### 28. H0/278

Bucket: `dbh_review`

History: Nyssa. 60 mm alive in 2019-2020, then 48/43/45 alive, May 2024 two duplicate 50 mm live stems, October 2024 48 alive, October 2025 dead/no DBH.

Impression: threshold-edge tree with May 2024 duplicate-stem artifact. The DBH values hover around qualification; no evidence of a true second stem.

Suggested action: treat May 2024 second 50 mm row as duplicate artifact; suppress subthreshold DBHs from qualifying profile but preserve the alive/dead status. Mortality in October 2025 may be real and separate.

Teaches us: threshold-edge trees can legitimately cross in/out of qualification; duplicate-stem cleanup should be separate from threshold suppression.

### 29. H1/224

Bucket: `dbh_review`

History: Nyssa. 46/46 alive in 2019-2020, 54 in 2021, 39/45 in 2022-2023, then 55/50/59 alive in 2024-2025. Health declines from 8 to 1 by October 2025.

Impression: real threshold-edge living tree. No obvious typo; values are small and variable.

Suggested action: preserve all status/health evidence, suppress subthreshold DBHs from qualifying profile. This may not need human `needs_review` unless the first qualifying/backfill policy is unresolved.

Teaches us: threshold-edge live trees with repeated observations should probably be `watch`, not `needs_review`, unless there is a 10x/digit error or mortality contradiction.

### 30. H1/230

Bucket: `dbh_review`

History: Ilex. 58 alive in 2019-2020, 49 alive in 2021, dead/no DBH in 2022-2023, missing in May 2024, 45 alive in October 2024, 54 dead in October 2025 with note `half gone`.

Impression: mortality contradiction / zombie-ish threshold-edge tree. The 2022-2023 dead labels are followed by alive evidence; October 2025 dead with `half gone` may be real later mortality.

Suggested action: route as mortality review, not DBH review. Likely convert 2022-2023 dead/no-DBH to missing/uncertain if later alive evidence is trusted, then keep October 2025 as dead if field context supports it.

Teaches us: zombie/mortality contradiction should outrank `dbh_review` when both are present.

### 31. H1/231

Bucket: `dbh_review`

History: Ilex growing horizontally. 59 alive in 2019-2020, 46 alive in 2021, DNF in 2022, 50 alive in 2023, May 2024 missing, 53/51 alive in 2024-2025.

Impression: threshold-edge/hard-to-find live tree, not obviously erroneous.

Suggested action: suppress subthreshold DBH from qualifying profile and treat missing surveys as missing, not death. Likely downgrade from `needs_review` after threshold-edge policy is encoded.

### 32. H3/153

Bucket: `dbh_review`

History: multi-stem Nyssa. 2019 note `Two trunks` with one recorded 139 mm stem; from 2021 onward a stable three-stem-ish profile appears around 236/130/130, with a May 2024 duplicate 131/131 and October 2024 only 130/129 DBH recorded while health rows imply three stems.

Impression: real multi-stem tree where early data missed stems and later surveys inconsistently measured/report DBH. May 2024 duplicate 131 may be real close-valued stems, not necessarily an artifact, because this is a known multi-stem individual.

Suggested action: do not auto-drop duplicate values here. Add blank/backfill for missing early stems if we model stem-profile completeness; preserve later three-stem health evidence even when DBH is missing.

Teaches us: duplicate-DBH artifact rule needs a guardrail for documented multi-trunk trees.

### 33. H4/140

Bucket: `dbh_review`

History: Acer rubrum. June 2019 note `two trunks` with duplicate 91/91; June 2020 only one 91; from 2021 onward stable two stems around 200+ and 80+.

Impression: early source under-recording / stem identity problem. The 2021 jump to 194/78 is persistent and likely reflects the true two-stem tree finally being recorded correctly, not growth.

Suggested action: keep modern two-stem profile. Review original 2019-2020 sheets; likely strike or reinterpret early 91/91/91 values rather than treating them as continuous with the 200 mm stem.

Teaches us: persistent regime shift plus explicit `two trunks` note usually means early stem measurement/entry problem.

### 34. H6/540

Bucket: `dbh_review`

History: Ilex. Mostly subthreshold 38-49 mm, one 51 mm in June 2021, alive throughout, October 2025 alive/no DBH.

Impression: live tree that barely qualified once. It may be below threshold for most of the record and probably should not be a high-priority review case.

Suggested action: suppress subthreshold DBHs. Decide policy: if a tree has one qualifying measurement but otherwise lives below threshold, keep the UUID with qualifying evidence or exclude from canonical census until sustained qualification?

Teaches us: “ever qualified once” vs “convincingly qualified” is a canonical policy question.

### 35. L5/413

Bucket: `candidate_identity_link`

Link: `L5/413 -> L5/985`, explicit tag-change assertion.

History: dead Juniperus, 85 mm in 2019-2020, 83 mm in 2024, with dead/no DBH in between.

Impression: clean dead-tree retag candidate.

Suggested action: likely accept link if L5/985 target has compatible no-conflict evidence.

### 36. L7/982

Bucket: `candidate_identity_link`

Link: `L7/5029 -> L7/982`, explicit tag-change assertion.

History: target L7/982 is excluded from canonical output because it has no qualifying DBH; evidence includes a 0 DBH/fell note. Source L7/5029 has zombie/mortality issues from case 21.

Impression: not enough target evidence to accept as a simple retag; source mortality conflict must be resolved first.

Suggested action: review with L7/5029 as one link/mortality case. Do not auto-accept while source has zombie behavior.

### 37. M0/909

Bucket: `candidate_identity_link`

Link: `M0/813 -> M0/909`, explicit tag-change assertion.

History: target excluded as nonqualifying; values 33/35 mm, dead, notes `species change` and `leaning`. Source max 57 mm.

Impression: likely a tiny dead/leaning Ilex/Juniperus-ish retag, but target is below threshold. This is probably an alias for historical context, not a canonical qualifying tree.

Suggested action: accept link only as identity/provenance if source is compatible; keep target DBHs nonqualifying.

### 38. M2/2420

Bucket: `dbh_review`

History: Pinus. 38 mm in 2019-2020, 245 in 2021, then stable 360-ish from 2022-2024, October 2025 dead/no DBH.

Impression: clear old data error or tag/source mixup. A Pinus cannot go 38 -> 245 -> 362 by growth; 2019-2020 probably missing a digit or wrong tree, and 2021 may also be suspect relative to later stable 360s.

Suggested action: original-source review. If handwriting supports it, 38 could be 380-ish, but then 245 remains odd. Do not auto-correct yet; this is a serious persistent regime case.

### 39. M3/358

Bucket: `dbh_review`

History: reviewed Nyssa multi-stem. Stable around 190 and 100-110, with June 2023 duplicate 193/193 during poison ivy estimate, then October 2024 poison ivy/no DBH, April 2025 partial fallen with only 105 DBH.

Impression: this is a real multi-stem tree affected by poison ivy and partial fall. June 2023 second 193 likely an estimated/duplicate DBH replacing the smaller stem; April 2025 may reflect only remaining/measurable small stem after partial fall.

Suggested action: keep as manual review. Likely strike or flag June 2023 second 193 as duplicate/estimate error; treat October 2024 no DBH as poison ivy measurement gap; treat April 2025 partial-fallen single 105 as structural change, not automatic DBH typo.

Teaches us: poison ivy and partial-fallen notes should explain DBH gaps/jumps and alter severity.

### 40. M3/359

Bucket: `candidate_identity_link`

Link: `M3/359 -> M3/911`, explicit tag-change assertion.

History: Juniperus 159 alive/health 2 in 2019, dead in 2020-2022, dead 161 in May 2024, then October 2024 alive health 6, October 2025 dead.

Impression: mortality contradiction is more important than the candidate link. October 2024 alive health 6 in a long-dead sequence is suspicious.

Suggested action: route to mortality review; likely October 2024 alive/health 6 is wrong or belongs elsewhere, unless field notes support rediscovery/live status.

### 41. R1/938

Bucket: `dbh_review`

History: Ilex, stable three-stem profile around 219/216/53 in 2023, 219/212/55 in 2025, and October 2024 217/210/52. May 2024 has five stems: 218/218/212/212/52.

Impression: textbook May 2024 duplicate-stem artifact: the two large stems each duplicated once, inflating stem count from 3 to 5.

Suggested action: suppress May 2024 duplicate 218 and duplicate 212 DBH rows from canonical stem profile, preserving evidence rows.

Teaches us: duplicate artifact rule should handle paired duplicates within a known multi-stem profile, not only one-stem-to-two-stem cases.

### 42. R1/963

Bucket: `dbh_review`

History: dead/unidentified in 2023; May 2024 has Ilex alive 156 plus two dead/unidentified 71/71 duplicate rows; October 2024 returns to dead/unidentified 73 with note `knot @ dbh`; April 2025 dead 70.

Impression: May 2024 likely mixed two identities or accidental insertion of a live Ilex row into a dead unidentified tree history. The duplicate 71/71 is artifact-like, but the live 156 Ilex row is a bigger identity problem.

Suggested action: source/identity review. Likely move or strike the May 2024 156 Ilex row; collapse duplicate 71 only after resolving whether it belongs to the dead tree.

Teaches us: duplicate-stem artifact with conflicting taxon/status should escalate to identity review, not batch cleanup.

### 43. L0/153

Bucket: `candidate_identity_link`

Link: `L0/153 -> L0/921`, explicit tag-change assertion.

History: old dead Pinus 298 mm in 2019-2020, then not found/dead no GPS/inferred dead.

Impression: plausible old side of a dead-tree retag, but target L0/921 has no DBH.

Suggested action: review as a link pair; likely accept as alias if target is non-overlapping dead/no-DBH evidence.

### 44. L0/157

Bucket: `candidate_identity_link`

Link: `L0/157 -> L0/922`, explicit tag-change assertion.

History: old dead Pinus 299 mm in 2019-2020, then dead/no GPS. Target L0/922 is dead/no DBH with `fallen` note.

Impression: plausible dead/fallen retag.

Suggested action: likely accept link.

### 45. L0/171

Bucket: `candidate_identity_link`

Link: `L0/171 -> L0/905`, explicit tag-change assertion.

History: old dead Pinus 268 mm in 2019-2020, then dead/not found/inferred dead. Target L0/905 was reviewed in first 25 and has 200 mm partially fallen in April 2025.

Impression: same link as prior case 12, old endpoint. Plausible dead/fallen retag with DBH loss.

Suggested action: review once as link; likely accept.

### 46. L0/177

Bucket: `candidate_identity_link`

Link: `L0/177 -> L0/989`, explicit tag-change assertion.

History: old dead Pinus 210 mm in 2019-2020, then dead/no DBH. Target L0/989 is stable dead Pinus around 196-200.

Impression: clean retag.

Suggested action: likely accept.

### 47. L0/921

Bucket: `candidate_identity_link`

Link: `L0/153 -> L0/921`, explicit tag-change assertion.

History: target dead/no DBH from 2023 onward, including April 2025 DNF/inferred dead.

Impression: target side of case 43.

Suggested action: review once with L0/153; likely accept as dead-tree alias if no overlap conflict.

### 48. L0/922

Bucket: `candidate_identity_link`

Link: `L0/157 -> L0/922`, explicit tag-change assertion.

History: target dead/no DBH, April 2025 note `fallen`.

Impression: target side of case 44. Plausible fallen retag.

Suggested action: likely accept.

### 49. L1/130

Bucket: `candidate_identity_link`

Link: `L1/130 -> L1/927`, explicit tag-change assertion.

History: old dead Pinus 293 mm in 2019-2020, then dead/not found/no GPS/inferred dead. Target L1/927 is dead Pinus 274/260 in 2024.

Impression: clean dead-tree retag with plausible DBH loss.

Suggested action: likely accept.

### 50. L1/144

Bucket: `candidate_identity_link`

Link: `L1/144 -> L1/924`, explicit tag-change assertion.

History: old dead Nyssa 64 mm in 2019, then dead/not-found/no DBH. Target L1/924 is dead Nyssa 74/79 in 2024.

Impression: plausible small dead-tree retag with threshold/measurement variation.

Suggested action: likely accept.

## Rules learned or reinforced

1. Candidate links with both endpoints in `needs_review` should collapse into one link-review task.
2. Dead-tree explicit retags with same taxon and plausible DBH are often safe to downgrade from `needs_review`.
3. Multi-stem trees with exact duplicate DBHs should not all be batch-corrected; known multi-trunk notes require a stricter guardrail.
4. May 2024 can duplicate multiple stems at once, as in R1/938.
5. Threshold-edge live trees are overrepresented in `dbh_review`; many should become watch/policy cases rather than manual review.
6. Mortality/zombie contradictions should take precedence over DBH or candidate-link bucket labels.
7. Notes like `poison ivy`, `partial fallen`, `knot @ dbh`, `fallen`, `mixup`, and `dangerous to DBH` are strong diagnostic context and should alter severity/routing.

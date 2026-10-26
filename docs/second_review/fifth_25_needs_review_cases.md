# Fifth 25 rebuilt needs-review cases

Date: 2026-05-10

Scope: next 25 `needs_review` plot/tag cases from the rebuilt review artifacts, excluding plot/tag labels already mentioned in the first- and second-review notes. This pass is dominated by mortality diagnostics, especially the new health-transition rules.

## Cases reviewed

| Case | Main signal | Impression | Proposed action |
|---|---|---|---|
| L3/285 | Health 7 alive in 2019-2020, then dead/fallen from 2021 onward. | Looks like a real mortality event. The `sharp_health_drop_to_observed_dead` rule is over-alerting when there is no later alive rebound. | Downgrade this pattern to watch if no later alive evidence. No per-case correction. |
| M1/842 | Two-trunk Nyssa with early equal DBHs, one-stem/two-status years, dead/alive oscillation in 2024-2025. | Real multi-stem/stem-level mortality confusion. Early 75/75 is supported by `2 trunks`, so duplicate cleanup would be dangerous here. | Human stem-level review. Add guard: duplicate DBH must see notes before calling artifact. |
| M6/374 | 50.5 alive in 2019-2020, dead from 2021 onward; May 2024 DBH 49, April 2025 DBH 52. | Looks like real death of a threshold-edge Nyssa. The 49 should not contribute to qualifying DBH, but the mortality sequence is plausible. | Suppress subthreshold 49 from canonical DBH; downgrade sharp drop with no rebound. |
| L5/419 | Pine dead health 0 from 2019 through April 2025, then October 2025 DBH 301 health 6 alive. | October 2025 row is suspicious: stable dead pine suddenly alive with health 6. | Source/field review. Likely October 2025 health/alive should be dead/0 unless source supports live tissue. |
| L7/25 | Dead 2019-2022, alive health 1 in 2023, then dead; May 2024 note says `zombie`. | A low-health zombie. Could be field workers saw marginal live tissue in 2023, but sequence mostly reads dead. | Human call: likely convert 2023 alive/health 1 to dead/0 or uncertain if source is ambiguous. |
| M1/838 | Alive 2019-2020, dead 2021-May 2024, alive health 5 in October 2024, dead afterward. | October 2024 is the only strong contradiction. DBH is stable, so this is probably label/health interpretation, not identity. | Source review for October 2024; likely set that row to dead/0 or uncertain. |
| H7/895 | Alive through 2022, dead June 2023, poison-ivy missing/context in 2024, alive from October 2024 onward. | June 2023 death label is probably wrong or should become uncertain/missing; poison ivy plausibly explains missed/uncertain observation. | Convert June 2023 dead/0 to uncertain/missing if source gives no death evidence. |
| L1/474 | Alive 2021, dead from 2022 onward; October 2024 has Morella DBH 70, later notes `delta to Mor` and `no Nyssa`. | Mortality itself looks plausible. The more interesting bit is taxonomy/identity notes, but no later alive rebound. | Downgrade mortality. Keep as watch/taxon-note context unless source shows wrong tag. |
| L1/5050 | Alive low health 3 in 2021-2022, dead in 2023, alive low/moderate 2024-2025, dead October 2025. | A genuine zombie-pattern review case. Health stays low enough that field interpretation could have wobbled. | Human/source call on June 2023 dead row; likely uncertain rather than canonical death. |
| L1/5063 | Dead/fallen 2021-2023, then `Fallen still live` in October 2024 and alive health 2 in October 2025. | This is probably a fallen/live-stem case, not a simple tree-level death. | Human review; preserve live evidence from 2024 onward and revisit older dead labels. |
| L2/238 | Dead 2019-2021, alive health 6/DBH 121 in 2022, dead afterward with poison ivy notes. | June 2022 is the only high-health live rebound and is suspicious. | Source review; likely strike/move/uncertain the June 2022 live row unless source is clear. |
| L3/300 | Alive through 2021, dead in June 2022, alive 2023 onward; notes say pushed/fallen on by tree. | June 2022 death looks like a one-year label error or overcall. Later live DBH is consistent. | Convert June 2022 dead/0 to uncertain/missing unless source clearly says dead tissue. |
| L3/5881 | New/unidentified in 2022, dead in 2023, huge Pinus DBH in May 2024, dead/error notes afterward. | Already known weird identity/source problem; this is not a normal mortality issue. | Keep in human queue for source/identity review. Do not solve with generic mortality rules. |
| L5/420 | Large pine alive through 2022, dead 2023-April 2025, then October 2025 alive health 6 with stable DBH. | October 2025 alive/health is suspicious after repeated dead observations. | Source/field review; likely October 2025 health/alive should be dead/0 unless confirmed. |
| L5/425 | Pine alive for years, dead only in May 2024, then alive health 8-9 afterward. | Clear one-survey death-label problem. | High-confidence correction candidate: May 2024 dead/0 should become uncertain/missing or alive status removed. |
| L5/435 | Alive 2019-2020, dead 2021-April 2025, then October 2025 alive health 6 with DBH 317. | Similar to L5/419 and L5/420: suspicious October 2025 live rebound after long dead sequence. | Source/field review; likely correct October 2025 to dead/0 unless source supports live tissue. |
| L6/49 | Alive through 2021, dead in 2022, alive high-health 2023-April 2025, dead October 2025. | June 2022 dead is probably wrong; June 2023 note says marked dead last year. October 2025 may be a real later death. | Correct/review June 2022 dead row; keep October 2025 as potentially real death. |
| L6/504 | Morella alive 2021-2022, dead from 2023 onward. | Looks like straightforward mortality. The sharp-drop rule is too noisy here. | Downgrade if no later alive rebound. No per-case correction. |
| L6/54 | Dead 2019-2022, alive health 6 in 2023, dead from 2024 onward; April 2025 note says `new death`. | Either early dead labels are wrong or 2023 alive is wrong. The `new death` note suggests 2023 may have been alive. | Human/source review; likely older dead rows need uncertainty rather than 2023 being erased. |
| L6/67 | Dead 2019-2020, alive 2021-April 2025, dead October 2025. | Early dead labels are likely wrong for this tag/identity. | Human/source review; likely convert 2019-2020 dead to uncertain/missing or wrong-label correction. |
| L6/78 | Pine alive 2019-2020, dead from 2021 onward. | Looks like real mortality. | Downgrade sharp-drop-without-rebound. No per-case correction. |
| L6/86 | Juniper alive through 2021, missing 2022-2023 with `could be one of the new tags`, alive 2024-April 2025, dead/fallen October 2025. | This is plausible missing/refound plus latest real death. The tag-note is worth context but not a correction by itself. | Downgrade mortality; keep identity/tag-change watch context. |
| L6/87 | Dead 2019-2020, alive 2021, missing until alive low-health April 2025. | Early dead labels look suspect, or this is an identity carry-forward issue. | Human/source review; do not infer stable death from early rows. |
| L7/23 | Dead 2019-2021, alive 2022-2023, dead 2024-2025. | Similar pattern: older dead labels conflict with later plausible live measurements. | Human/source review; likely early dead rows should be uncertain/missing or wrong-label corrections. |
| L7/498 | Morella cluster: alive 2021, dead 2022-2023, alive May 2024 with note `1 dead trunk`, then dead/fallen. | This teaches a rule: alive/dead may be stem-level in multi-stem/cluster cases. Tree-level zombie logic is too blunt. | Human stem-level review; add cluster/stem note guard for mortality contradictions. |

## What this pass teaches

The new mortality diagnostics are directionally useful but too broad. A sharp high-health-to-dead transition is not suspicious by itself. It should become human review only when there is later observed-alive evidence, a strong health rebound, a source note contradicting the death, or an implausible single-survey pattern.

Several October 2025 rows now stand out as suspicious because they revive trees that had been repeatedly dead for years: L5/419, L5/420, and L5/435. Those should be source/field review cases rather than generic zombie cases.

Multi-stem and cluster cases need a mortality guard similar to the duplicate-stem guard. L7/498 and M1/842 show that `observed_dead` and `observed_alive` may be describing different stems or trunks within the same tagged plant.

## Suggested rule changes

- Downgrade `sharp_health_drop_to_observed_dead` to watch when there is no later observed-alive evidence.
- Keep `sharp_health_rebound` and observed-dead-then-observed-alive zombie sequences as human review.
- Add a `single_survey_death_label_outlier` subtype for alive -> dead/0/no DBH -> alive cases like L5/425 and L3/300.
- Add a multi-stem/cluster mortality context subtype when notes include `trunk`, `stem`, `cluster`, or similar wording.
- Make duplicate-DBH artifact detection note-aware at the survey level, not just tree level, so cases like M1/842 are not mislabeled as duplicate artifacts when `2 trunks` is explicitly recorded.

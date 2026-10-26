# Handoff Open Questions and Work Register

Audited October 26, 2026. This register is current orientation; old review logs
remain evidence and should not be deleted. Closing an item requires an accepted
decision or implementation plus verification, not merely mentioning it here.

## Immediate Operational Work

| Item | State / next action | Needs Riley? |
| --- | --- | --- |
| Kevin access | Write invitation sent to `kevindonnellyy`; acceptance still required. This is a personal-account repo, not access to Riley's billing or credentials. | Kevin accepts |
| October full OCR | Five-page pilot only, 81 rows. Finish all 78 pages in fresh run directories and explicitly preserve pilot edits. | Approve paid run and choose preserve-pilot vs re-extract strategy |
| Pilot review | R4 overwritten health 5224, scribbled standing 5229, 5163/5243 stem-count/out-of-plot annotation; M3 5826/5827 identity note and approximate DBH for 360. See the October transcription note. | Field/source judgment where ambiguous |
| Shared editing/publication | These are local apps with file logs, not a concurrent multi-user database. A release is a snapshot, not live synchronization. | Who owns the current master logs and approves publication while both researchers work? |
| Public permissions | Riley explicitly approved public data/scans; credentials excluded. Public availability is not itself an explicit reuse license. | Choose code/data license and citation/authorship wording |

## Implementation Gaps Found During Handoff

### 1. Diagnostic Thresholds Lag the Scientific Policy

Assembly, field eligibility, and basic small-DBH validation use inclusive
20 mm generally / 50 mm for Morella cerifera. However `invariants.py`, several
rank-profile helpers in `validate.py`, and candidate matching in
`canonical_review.py` still use `MIN_MEASURED_DBH_MM = 50`. Some explanations
also say all stems below 50 are nonqualifying. This can create both false
positives and missed smaller-stem cases. Do not globally replace 50 with 20:
distinguish historical collection practice from current taxon eligibility.

Next: route eligibility-sensitive comparisons through the taxon policy, add
20/50 boundary tests and mixed-stem cases, and compare changed review cohorts
before rebuilding the UI's queue. This should precede another exhaustive
round of per-tag review. No automatic scientific corrections were made here.

### 2. Review Artifacts Are Not Guaranteed to Share a Build

The canonical UI loads fixed CSV directories independently. Its historical
diagnostics/evidence may predate May reconciliation. Older queue totals in
`docs/decision_layer.md` and review batches are not current. The published
manifest also predates two October-related config edits. A fresh isolated build
matches the publication cell-for-cell and has zero hard errors, but the old
manifest was not falsified to remove its detectable drift.

Next: generate raw findings, accepted-decision ledger, post findings, evidence,
and cases together with input/config fingerprints; switch the UI to that
consistent snapshot. Prefer a run selector/manifest to independently stale
fixed files. Decide separately whether to promote the byte-equivalent fresh
candidate to refresh publication provenance.

### 3. Missingness Does Not Yet Fill the Whole Survey Calendar

Assembly iterates surveys with rows for a tree. It does not synthesize every
absent tree/survey or persistent stem channel. Thus two explicit not-found
events separated by an entirely absent survey can be treated as a run, and
an entirely omitted tree may lack a canonical not-found event. UI missing-row
placeholders do not fix this. Do not assume a complete tree x survey panel.

Next: define whether absent rows mean not reported or searched-not-found;
define which surveys/plots were actually visited; test gap/reappearance
behavior before changing mortality inference. A model must not invent search
effort from an empty cell.

### 4. Candidate Acceptance Is Not End-to-End

Accepted config operations run in one phase, but canonical-UI decision logs
are not replayed into that phase. Generated candidates and marked reviews
do not automatically change canonical data. Existing configured IDs are based
on operation-list position, so they are not durable IDs under reordering.

Next: explicit accept/reject/defer translation with source fingerprints,
unique guarded selectors, stable decision IDs, reviewer/rationale, and a
raw -> decisions -> verify comparison. Preserve existing TOML decisions;
do not add a parallel hidden correction pathway or silently auto-apply all
suggestions. Duplicate cleanup precedes rank-dependent interpretation.

### 5. Import/Publication Gates Need Stronger Completeness Checks

October 2025 and May reviewed inputs are configured `required=false`, so a
code-only clone can omit them; strict source-row decisions may fail later,
but the loader itself does not require full vintage coverage. Review
materialization accepts non-edit decisions as audit entries and does not
require every row confirmed or reject the entire run just because some pages
failed. Bare `build` writes the primary publication directly.

Next: preflight expected source fingerprints, plots/surveys/pages and review
coverage; fail closed for a publication candidate. Continue fresh destinations
and approval-only promotion. Do not overwrite reviewed imports just to fix
setup. Page-level question/feedback editing also needs an audited path; it is
currently read-only in the transcription UI.

### 6. Final Output Contract Is Not Yet Lean

The current Parquet still contains observed/interpreted alive/status fields;
health-only public interpretation remains an intent. Poison ivy and difficulty
are preserved outside the Parquet and joined from exact source coordinates
for field-sheet context. Blank standing is not universally fallen, and
deciduous autumn health zero is not automatically reliable death evidence.

Next: agree on observed vs inferred public columns, contextual side tables,
and seasonal interpretation before removing columns or recalculating mortality.
The October roster's two-survey omission rule is already agreed and separate.

### UI Dependency Security Before Network Hosting

The October 26 clean-install audit reports 10 vulnerable dependency packages
in each UI (5 high, 3 moderate, 2 low; no critical). This includes the Svelte /
SvelteKit / Vite toolchain and CSV parsing dependencies. Package audit counts
are not proof that each advisory is exploitable in this application, but must
not be represented as a clean security audit. Keep these unauthenticated,
file-editing review apps bound to `127.0.0.1`; public source/data permission
does not authorize exposing a running reviewer to the network.

Next: update dependencies in a separate tested change, inspect advisory
applicability, and rerun both app checks/builds and review-save browser tests.
Do not run `npm audit fix --force` blindly during an active review session.
Some fixes require major-version migration. No dependency upgrades were mixed
into this handoff or the live demo.

## Scientific Cases Still Open

- **Source-era/tag-alignment blocks:** H4 roughly 136-152; H1 233/235/239/241;
  possible H3 analogues; L6/L7 and other groups in the historical queue.
  Stable incompatible early/late or middle-era DBH patterns suggest record
  alignment, not instantaneous growth. Compare neighboring tags and source
  sheets together. A similar DBH is a candidate, not proof of a swap.
- **May histories intentionally left unmatched:** L1/891, L5/509, L5/786,
  L6/574. Keep the observations without inventing earlier identities. Later
  accepted May decisions supersede speculative earlier entries in May docs.
- **October field answers:** the packet has 31 questions covering 32 trees.
  These may resolve old fallen/standing and identity questions, but only five
  pages have been extracted so far. Do not carry the old questions forward
  without reading the completed answers.
- **H4/149 and other duplicate/stem cases:** preserve the approved ordering
  principle (duplicate first, profile analysis second), but do not adopt a
  global near-duplicate rejecter. The previous proposal to average a small
  third stem must be reconsidered under the newer 20/50 policy.
- **Historical health=1 placeholders:** some accepted alive/health-zero
  contradictions were set to 1 because exact health was unknown. Keep the
  notes and revisit only with source support, not health interpolation.
- **Original 2019 and 2021 records:** still not located in the searched lab
  archive. Derived all-years spreadsheets are secondary evidence.

Detailed queues: `docs/second_review/human_attention_queue.md`,
`docs/third_review/synthesis.md`, and its ten shard reports. These contain
proposals, some since superseded, and older universal-50-mm assumptions.
Reconcile them against accepted config and current sources before acting.

## Closed or Verified in This Handoff

- Reviewer's stale-process EPERM resolved by a scoped restart; HTTP 200,
  loaded scan image, and no browser runtime errors verified.
- Both UI manifests now explicitly include Node TypeScript definitions;
  clean-install checks no longer depend on packages above the checkout.
- Current publication reproduced exactly in a separate candidate; raw data,
  published Parquet, and live review decisions were not rewritten.
- Current counts and 214 accepted config decisions documented; historical
  decision-layer counts explicitly labeled as a historical snapshot.
- Git/data-bundle separation and safe restore documented; ignored outputs
  are no longer treated as disposable caches in the handoff instructions.
- Credential ignore rules cover both apps' build/dependency folders and common
  credential files. Secret scanning is required before publishing snapshots.

# Forest Census: Researcher and Agent Handoff

Verified: **October 26, 2026**. Incoming researcher: GitHub `kevindonnellyy`.
Repository: <https://github.com/RileyLeff/forestcensus>.

This document is the starting context for Kevin and his agent. It is not a
claim that the historical census is fully reconciled. Preserve the distinction
between source evidence, accepted decisions, proposed fixes, and published data.

## 1. Where We Are

| Item | Verified state |
| --- | --- |
| Canonical publication | `output/forest_census.parquet`: 12,266 rows, 1,385 tree UIDs, ten surveys, June 2019 through May 2026 |
| May 2026 | Reviewed and published; 1,341 canonical rows / 1,241 UIDs; reviewed source has 1,349 rows and 33 saved edits |
| Accepted canonical decisions | 214 operations from corrections/identity config, not 214 necessarily distinct trees |
| October 2026 printed packet | v8, 28 plots, 78 pages, 1,279 Main rows / 1,184 trees; 12 Newly Tracked slots per plot |
| October completed scans | All 78 pages assembled and audited, ordered R -> H -> M -> L |
| October OCR | Only five-page Gemini 3.8 Flash pilot, global pages 9-12 and 43: 81 rows, zero rejected pages, zero unmapped rows |
| October publication | **Not incorporated**; no full extraction or accepted October canonical source yet |
| Historical review | Significant unresolved identity/source-era cases remain; older queue counts are snapshots |

Publication SHA-256:
`b7532e7bf56ac03cc810141a8b99683e26989b40f5bbada923f4b803a04dfa99`.

A fresh build under `output/handoff_audit_2026_10_26/` was compared with the
publication: every value and dtype matched; zero hard errors. Its validation
has 1,081 warnings and 1,427 informational findings. These are finding counts,
not numbers of erroneous trees. Do not mistake an info-level correction audit
or biological context note for another unresolved error.

The existing publication's config hashes differ for `surveys.toml` and
`datasheets_october_2026.toml`, which were subsequently edited for October.
Its input files still match. We did not rewrite the publication's old manifest
to conceal this; a newly built candidate has current fingerprints.

## 2. The Scientific Model

There are 28 densely vegetated 20 x 20 m plots at Brownsville (`BRNV`): R1-R4
are the highest reference zone; H0-H7, M0-M7, and L0-L7 are high, middle, and
low forest. Trees can be difficult to relocate. Not finding a tree is not the
same as seeing it dead, and absence from a future search sheet does not erase
its historical data.

- **Tree identity:** biological individual, resolved as `tree_uid`. The code
  uses the first 16 hex characters of SHA-1 of `site/plot/identity_tag`, not a
  random RFC UUID. Changing resolved identity can therefore change the UID.
- **Tags:** `public_tag` is the written/recording label; `identity_tag` groups
  records; `identity_label` makes synthetic splits legible. A tag can be reused
  across plots and can accidentally refer to multiple trees in one plot.
  One tree can have multiple historical tags.
- **Stems:** only trees are tagged. Datasheet trunk/slot numbers are writing
  positions. `stem_rank` sorts each survey by DBH, then health and provenance
  for ties/missing DBH. Rank 1 this year need not be the same stem as last year.
  Rank comparisons are profile diagnostics, not proof of persistent tracks.
- **Health:** observed 0 means dead, positive values mean living tissue, blank
  means unknown. Legacy alive/dead columns remain in adaptation/provenance and
  currently also in the output; a lean health-only publication is unfinished.
- **Presence:** any nonmissing DBH, health, or standing input means found,
  including `health=0` and `standing=false`. With none, the event is not found.
  A found record with indeterminate health is `observed_unknown`.
- **Missingness:** threshold is two survey events in `config/pipeline.toml`.
  Eligible missing runs become retrospectively inferred dead unless a later
  observed-alive event disproves that inference. Inferred death remains an
  interpretation, not a fabricated observed health 0. See the calendar-gap
  implementation caveat in the open register.
- **Zombies:** require observed dead followed by observed alive. NA-only gaps
  cannot establish a zombie. Multi-stem mortality needs extra care.
- **Size:** inclusive 20 mm for non-Morella-cerifera, 50 mm for Morella cerifera.
  Entire measured histories that never qualify are excluded; no-DBH histories
  are not automatically removed. Mixed histories retain evidence. A broken or
  decomposing formerly qualifying tree may become smaller without being bogus.
- **Protocol change:** routine DBH collection stopped midway through October
  2025. Later missing DBH is legitimate. Historical DBH still matters for
  identity, roster size eligibility, and retrospective science.
- **Taxonomy:** aim for one canonical taxon per tree. Vaccinium is deliberately
  `Vaccinium spp.`. Notes and historical taxon guesses remain evidence.

Common non-error explanations include poison ivy covering the measurement
point or preventing measurement, knots, split trunks, falling/decomposing wood,
seasonal leaf loss, and a previously missed secondary stem. Equal DBHs alone
do not justify deleting a stem. Later strong fieldwork can inform a decision,
but never silently overwrites an earlier record.

## 3. Architecture and Ownership

```text
Historical CSVs / reviewed recent-survey imports
    -> adapters: normalized, provenance-bearing observations
    -> raw diagnostic branch (no accepted corrections/identity overrides)
    -> apply_decisions(): accepted source-row edits/exclusions,
       identity operations, then canonical taxon overrides
    -> TreeDataset: tree -> surveys -> observed stem profiles
    -> assembly: ranks, eligibility, missingness, zombie interpretation
    -> candidate Parquet + manifest + post-decision diagnostics
    -> approved publication

Historical workbooks + raw observations + notes/tag-change assertions
    -> evidence ledger -> canonical review proposals/UI (not auto-applied)

Completed PDF + exact printed packet manifest
    -> Gemini OCR -> transcription UI decisions -> reviewed import
    -> the same canonical pathway above
```

| Location | Responsibility |
| --- | --- |
| `src/forestcensus/adapters.py` | Source-specific normalization, source coordinates, presence classification |
| `decisions.py`, `corrections.py`, `identity.py`, `taxonomy.py` | Unified accepted-decision phase and guarded operations |
| `tree_ir.py`, `assembly.py`, `domain.py`, `schema.py` | Tree IR, interpretation, shared rules, current column contracts |
| `validate.py`, `invariants.py` | Basic findings and context-sensitive tree-history review |
| `evidence.py` | Non-collapsing source/workbook evidence, notes, explicit tag-change assertions |
| `canonical_review.py` | Tree cases, possible links, candidate decisions, human worklist |
| `llm_transcribe.py`, `transcription_packet.py`, `review_layout.py` | OCR contracts, packet validation, materialization, scan geometry |
| `field_packet.py`, `datasheets.py` | Current audited field packet; older generator retained for reproduction |
| `publish.py` | Build manifests, validation output, guarded promotion and publication backup |
| `config/sources.toml` | Exactly which adapted inputs enter the build |
| `config/corrections.toml`, `identity.toml` | Accepted scientific calls, with reasons and guarded selectors |
| `config/resolutions.toml` | Acknowledged review contexts; not measurement edits |
| `config/may_2026_transcription_additions.json` | Source-guarded handwritten observations OCR omitted |
| `config/may_2026_review_layout.json` | Display geometry only, not scientific corrections |
| `review-ui/` | Recent-survey transcription correction app, Svelte 5/SvelteKit |
| `canonical-ui/` | Historical identity/evidence investigation app, intentionally separate |
| `prototypes/datasheets/portrait_prototype.typ` | Typst field-sheet template actually used by the generator |
| `docs/first_review/`, `second_review/`, `third_review/` | Historical investigation logs, not a second accepted-decision engine |

The old GitHub `forcen` implementation is not this pipeline. It remains in
Git history at commit `638b4d5bc54e1e489a3eb63ce96d7fc188994dfa`.
Do not mix its transaction DSL or planning specifications into current commands.

## 4. Install and Restore

Requirements: Git, `uv`, Python >=3.13.7 (uv can provide it), Node >=22.12 with
npm, Poppler (`pdftoppm`, `pdftotext`, `pdfinfo`), and Typst for PDF generation.
On macOS, `brew install uv node poppler typst` supplies the external tools.
Gemini credentials are needed only for new paid extraction, not review/build.

```sh
git clone https://github.com/RileyLeff/forestcensus.git
cd forestcensus
uv sync --locked
cd review-ui
npm ci
cd ../canonical-ui
npm ci
cd ..
```

Download the public data bundle from the repository's `handoff-2026-10-26`
release. With GitHub CLI:

```sh
gh release download handoff-2026-10-26 \
  --repo RileyLeff/forestcensus \
  --pattern 'forestcensus-data-2026-10-26.tar.gz' --dir .handoff
uv run python scripts/handoff_bundle.py verify \
  .handoff/forestcensus-data-2026-10-26.tar.gz --extract-to .
```

The utility validates member hashes, rejects unsafe paths/links, and refuses
to overwrite differing local files. Identical existing files are left alone.
The release also provides a whole-archive SHA-256. The archive's own manifest
is an integrity check, not a cryptographic signature of its publisher.

The bundle includes data archives, all saved output snapshots (except handoff
builds and synthetic dev fixtures), review logs, crops, original model JSON,
printed packet manifests, and available source scans. It deliberately excludes
credentials, virtual environments, node_modules, browser profiles, and scratch
UI screenshots/scripts. Large data live in a release asset rather than bloating
Git history. A dated bundle is a checkpoint: later edits need a new snapshot.

**Run commands from the repository root**, except npm commands from the
specific app directory. Paths and source guards rely on this convention.

For new OCR, put a separately provisioned key in a local `.env`:
`GEMINI_API_KEY=...`. `.env.example` contains an empty placeholder. Never send
keys through Git, issue text, logs, or the handoff archive. Kevin needs his own
authorized billing/key setup; repository access does not confer API access.

## 5. Demonstrate the Two Reviewers

### Recent OCR Review

```sh
cd review-ui
REVIEW_RUN_DIR=output/llm_transcription/october_2026_pilot_gemini38_v1 \
  npm run dev -- --port 5176 --strictPort
```

Open <http://127.0.0.1:5176/>. Choose a row in the left queue, inspect the scan
and overlay in the center, and confirm or edit the transcription on the right.
Use All rows for a completeness pass, not just model-flagged rows. Page notes
contain separate recheck answers and field-note annotations. Those metadata
are currently read-only; fixing a row does not resolve plot-level prose.

Edits are recorded in the run's `review_decisions.jsonl`; refresh preserves
them. Save/confirm is not canonical publication. The normal save path appends;
the UI's removal/undo path can rewrite that log, so back it up before reviewing.
The materializer uses the latest edit per row-key/field and rejects unmatched
edits or duplicate row keys. It does not demand that every row was confirmed.

May demonstration: use
`output/llm_transcription/may_2026_all_gemini37_printed_manifest` on another
port. Do not overwrite or re-extract this reviewed run. Explicitly pinning
`REVIEW_RUN_DIR` avoids accidentally selecting a failed run, a fixture, or the
partial selection in `output/llm_transcription/review_selection.json`.

If a long-lived dev process returns EPERM on macOS, check the process/cwd and
restart that specific server from an authorized terminal. Do not chmod the
repository broadly or delete data. The October server was restarted and
browser-tested successfully during this handoff.

### Historical Evidence Review

```sh
cd canonical-ui
npm run dev -- --port 5174 --strictPort
```

This reads `output/canonical_review`, `output/evidence`, and raw/current
diagnostics. Browse Tags to expose cross-tree noise, Tag x Plot for field
context, or Tree UID for biological identity. Default compact stem columns
align survey rows. Together view includes stem rank as a column. Missing-view
placeholders are not necessarily real canonical rows or evidence of death.
Linked/all evidence includes possible old-tag/note connections; direct evidence
is narrower. Deduplicated display rows retain origins/counts: display grouping
does not delete source observations.

Investigate the provenance of a suspicious value before correcting it. The
reviewer writes a separate `output/canonical_review/review_decisions.jsonl`,
but that log is **not yet automatically consumed by `apply_decisions()`**.
Accepted scientific changes still need reviewed config operations. Candidate
links and suggested fixes are proposals, not already-applied merges.

Both apps are local, unauthenticated tools, not a safe multi-user service.
Do not expose them on `0.0.0.0` or let two researchers independently edit the
same dataset without reconciling their logs and assigning one publisher.

## 6. Accepted Decision Workflow

1. Inspect the tag across plots/UIDs and related sources; identify the exact
   observation or identity window. Look for complementary missing trees before
   proposing a swap, split, or new identity.
2. Run raw diagnostics before new decisions. "Raw" here means normalized
   selected inputs before canonical config decisions, not unreviewed OCR or
   every historical workbook. Raw assembly still applies shared eligibility
   and interpretation rules.
3. Record Riley/field-expert approval, evidence, and rationale. Correct an exact
   value only when supported; otherwise suppress that field while retaining
   the observation where appropriate. Excluding a duplicate observation is a
   different operation from blanking its DBH.
4. Add guarded operations to corrections/identity config. Source rows are
   original adapter coordinates (normally CSV line including header), not
   current dataframe indices. Pair row coordinates with source file and
   expected contextual values. The helpers require unique matches and forbid
   rewriting provenance coordinates. Earlier edits can change a later guard's
   value, so decision ordering still matters; exclusions do not renumber source
   coordinates.
5. The normal path applies row corrections, row exclusions, identity
   reassignments/aliases/splits, then tree/genus taxon overrides. Duplicates
   must be dealt with before interpreting ranked profiles. Do not call the old
   `apply_corrections()` helper in a second phase on top of `apply_decisions()`.
6. Rebuild to a new candidate directory; compare changed source keys/UIDs,
   rows, taxonomy, health, missingness, and validation against the publication.
   Run focused regression tests plus the suite for shared changes.
7. Promote only an approved candidate with `publish-candidate`; keep its
   manifest and provenance. Never hand-edit published Parquet.

Useful commands (choose fresh destinations for each review cycle):

```sh
uv run forestcensus diagnose-raw --out-dir output/my_review/raw
uv run forestcensus decisions --out-dir output/my_review/decisions
uv run forestcensus build --out output/my_review/forest_census.parquet
uv run forestcensus validate output/my_review/forest_census.parquet \
  --out-dir output/my_review/diagnostics
uv run forestcensus invariants --decision-stage post \
  --out output/my_review/invariants.csv
uv run forestcensus evidence --out-dir output/my_review/evidence
uv run forestcensus canonical-review \
  --parquet output/my_review/forest_census.parquet \
  --evidence-dir output/my_review/evidence \
  --invariants output/my_review/invariants.csv \
  --issues output/my_review/diagnostics/issues.csv \
  --out-dir output/my_review/canonical_review
```

The canonical UI still reads fixed output directories. Review those candidate
artifacts separately before replacing UI inputs together as a consistent
snapshot. A raw/post comparison must use the same input vintage and config.
Invariants read configured source events, not the Parquet argument to another
command. Bare `build` overwrites the primary publication; avoid it during QA.

## 7. Ingest the Rest of October

Read `docs/october_2026_transcription.md` first. The completed scan is
`output/pdf/BRNV_October_2026_completed_all_plots_R_H_M_L.pdf`; its adjacent
`.manifest.json` binds the audited page map and SHA to printed packet v8.

The default is `gemini-3.8-flash`, 300 DPI, HIGH media resolution and HIGH
thinking. Five pilot pages cost approximately $0.37 at October 2026 rates;
$6-10 was the full-packet estimate including some retries, not a guarantee.
Per-response `usage/page_NNN.json` includes model version and thinking tokens.

After approval for the paid full run:

```sh
uv run forestcensus transcribe-pdf \
  output/pdf/BRNV_October_2026_completed_all_plots_R_H_M_L.pdf \
  --survey-id October_2026 \
  --datasheet-manifest-dir output/datasheets_october_2026/v8/json \
  --pages all --out-dir output/llm_transcription/october_2026_full_v1
```

Never regenerate/replace v8 before parsing the sheets collected with it.
Use a fresh extraction directory. Check rejected pages, complete 78-page/28-plot
coverage, row labels, question coverage, all recruit slots, and layout coverage.
An omitted handwritten note observation may need a source-guarded addition,
not a fabricated blank-slot position. Preserve original model output.

The pilot already has human edits. Do not lose them by switching to a new
full-run directory: carry them forward only after matching scan/page/row/ID
and verifying the edited field context, or retain the pilot for its five pages
and extract only the other 73. Do not combine overlapping pilot/full pages in
a materialization manifest. Choose and document one strategy first.

After transcription review, make a complete tracked run manifest (a `dirs`
array), then materialize to a **fresh** reviewed destination:

```sh
uv run forestcensus materialize-llm-review \
  --selection docs/october_2026_reviewed_run_manifest.json \
  --out-dir output/llm_transcription/october_2026_reviewed_candidate
```

That October full-review manifest does not exist yet. Create it only when
coverage is known. Verify rejected/missing pages, unmatched edits, row counts,
and page metadata explicitly; materialization itself is not an approval gate.
Then add an approved source to `config/sources.toml`, resolve targeted identity
questions through the same decision layer, build/compare a candidate, and
promote only when approved. Do not load the pilot as an entire census.

For October 2025, always use `docs/oct_2025_reviewed_run_manifest.json`, not
the UI subset. It covers 58 pages and all 47 deduplicated field edits. For May,
use `docs/may_2026_reviewed_run_manifest.json`; additions and image guards are
documented in `docs/may_2026_review_layout.md`.

## 8. Generate Future Search Sheets

Use `field-packet`, not the older `datasheet-prep`/`datasheets` workflow.
Update a new policy for the next survey and its two latest context surveys;
do not keep copying an October 2026 label or stale roster selection.

Rules accepted for v8: include recently found eligible trees, including dead
standing trees; omit trees missing in both latest surveys and confirmed
dead/fallen entries. Rediscovered trees return through Newly Tracked under
their original tag and receive a renewed search window. Newly Tracked does
not mean biological recruitment. Genuine unresolved conflicts may remain
starred in Main with a specific question and answer space.

Roster membership is separate from canonical mortality inference. Repeated
zero health alone is not the omission rule. Evergreen/deciduous bins exist,
but a new seasonal mortality rule has not been implemented. HSP context must
stay tied to the correct survey, with `/p` only for recorded poison ivy. Blank
current-input cells stay blank. Field notes are concise context, not confusing
internal diagnostic language. `*` means question; `+` means field-note mention.

Generation requires a matching canonical manifest, all expected plots, and an
explicit recording label for multi-tag identities. It refuses an existing
destination and records coverage/exclusions and generator/input hashes. Inspect
PDFs visually, especially crowded multi-page plots and notes/questions.

## 9. Sources, Tests, and Next Work

The four historical input CSVs are themselves imperfect integrations, especially
`2023_and_prior.csv`. Archive workbooks are evidence, not additional canonical
inputs to concatenate. Prefer dated 2023 field-entry files, then RAW/QAQC trail;
2020 and 2022 have useful source records. Original tree-specific 2019/2021
sheets were not found. See `data/raw/forest_census/original_drive_records/MINI_REPORT.md`.
DBH and circumference columns must not be conflated; preserve source units.

```sh
uv run pytest -q
cd review-ui
npm test
npm run check
npm run build
cd ../canonical-ui
npm run check
npm run build
```

No test/setup command should call Gemini or need a paid key. An intact bundle
is needed for data-dependent regression tests. The handoff audit does not
certify every historical identity, every OCR character, or diagnostic freshness.

Next priorities are in `handoff_open_questions.md`: finish October without
losing pilot edits; align diagnostic thresholds with the accepted policy;
refresh coherent review snapshots; investigate source-era blocks as groups;
and finish explicit candidate-decision acceptance. Preserve the detailed
human queues rather than converting all their proposed calls into bulk fixes.

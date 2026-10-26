# Forest Census

Clean canonical forest census pipeline.

## Researcher Handoff

Start with [the researcher and agent handoff](docs/researcher_handoff.md), then
[the open-questions register](docs/handoff_open_questions.md). These describe
the verified October 26, 2026 state, installation, both review apps, data
restoration, decision workflows, and important unfinished work.

Code, configuration, source archives, and documentation live in Git. Large
scans, reviewed imports, saved review decisions, and publication snapshots are
provided separately as the public `handoff-2026-10-26` release data bundle.
**A code-only clone is not the complete dataset.** Restore the bundle before
building; optional configured inputs can otherwise be absent. Never commit
`.env`, API keys, service-account credentials, or local authentication files.

## Current Canonical Intent

The published dataset should be a single tabular output, currently written as
`output/forest_census.parquet`. Long term, health is the authoritative observed
state: `health = 0` means dead, and `health > 0` means alive. Legacy
`alive/dead` fields are adaptation/provenance scaffolding used to resolve older
input formats before the canonical output is finalized.

Corrections live in `config/corrections.toml`. Raw diagnostics run on normalized
observations before accepted decisions. The normal build then applies all
accepted decisions through `apply_decisions()` after adaptation and before
assembly, followed by post-decision diagnostics. Row corrections touch specific source rows;
taxon overrides apply one canonical genus/species to a resolved tree identity.
An explicit `scope = "genus"` resolution may instead retain a genus while
setting its species to `spp.`; Vaccinium uses this policy. Written source
identifications remain available before the unified decision phase.
Raw data files should remain unchanged.

Identity operations live in `config/identity.toml`. The raw field tag remains
visible as `public_tag`; biological individuals are resolved with
`identity_tag`, and `identity_label` gives a human-readable filter label for
synthetic split identities such as old dead trees that were later confused with
a new visible tag.

Assembly now builds a tree-level intermediate representation before publishing.
The IR groups rows by resolved `tree_uid`, then by survey, and treats stems as
survey-local ranked DBH observations rather than persistent stem identities.
Trees whose observed DBHs never meet the inclusive taxon-specific threshold
(20 mm generally, 50 mm for *Morella cerifera*) are excluded from the canonical
output; mixed histories remain so fallen/decomposing formerly qualifying trees
keep their evidence.

Presence and health are separate: any recorded DBH, health, or standing value
means found, including health 0 and standing false. With all three missing,
the adapted event is `not_found`. Found observations without enough evidence
to determine alive/dead use `observed_unknown`; they break an absence run
without inventing a health score or a zombie event. `alive_interpreted` is
nullable for unknown health and pending absence, not false by default.
Missing/not-found prose alongside direct inputs produces a
`W_FOUND_NOTE_CONFLICT` review finding instead of overriding measurements.
Accepted manual decisions still run in their single explicit phase after
adaptation. Approved May decisions extract unambiguous standing/fallen notes
and resolve seven contradictory absence entries; they are guarded source-row
decisions, not a rule that unchecked boxes imply fallen. Uncertain notes,
partial breakage, and plot-level descriptions remain unresolved. Seasonal
foliage interpretation remains separate from the implemented field-roster
rules in `docs/october_2026_datasheet_requirements.md`.

## October 2026 Field Packet

The primary `output/forest_census.parquet` now includes the reviewed May 2026
survey. The current verified packet is `output/datasheets_october_2026/v8/`:
28 per-plot PDFs, their JSON manifests, coverage and exclusion ledgers, and a
ZIP containing only those PDFs. Its 78 pages contain 1,279 recording rows for
1,184 trees, with 20-point writing rows and 12 Newly Tracked slots. Claude's revised
field notes are context-only, with independent Helpful / Confusing / Incorrect
checkboxes. Headers include the historical average difficulty (NA if unrated).
There are 31 targeted recheck questions covering 32 trees, marked with an
asterisk in the main roster and followed by ruled answer space.
Tags mentioned in Field Notes carry `+`; both markers can appear together.
The header explains `* = open question below | + = appears in field note`
beside the HSP guide. Note references are explicit and plot-scoped, not
inferred from numbers such as DBH measurements in the note text.
The combined PDF is `output/pdf/BRNV_October_2026_all_plots_R_H_M_L.pdf`,
ordered R1-R4, H0-H7, M0-M7, L0-L7. Internal packet IDs remain in the manifest,
not on the printed sheets.

```sh
uv run forestcensus field-packet \
  --parquet output/forest_census.parquet \
  --policy config/datasheets_october_2026.toml \
  --out-dir output/datasheets_october_2026/v9
```

Use a new destination for each revision. Generation refuses existing output
directories and requires the latest two context surveys, all expected plots,
an explicit recording tag for multi-tag identities, and a matching canonical
manifest. It records dataset, policy, template, and generator hashes and checks
the ZIP against the generated PDFs. Old `datasheet-prep` / `datasheets` commands
remain available for historical reproduction; they are not the October workflow.

Roster grouping is by UUID, not written tag. HSP.1 is May 2026; HSP.2 is
October 2025. Trees absent from both surveys are omitted from the printed
search list, as are dead/fallen entries. Dead standing trees remain eligible;
a rediscovery resets the two-survey window. None of these omissions deletes
canonical history. Genuine unresolved questions stay with starred main rows,
not a separate blanket recheck roster. Historical split identities receive explicit guidance rather than
duplicate rows under the same tag. Notes-only extra ranks with no direct
observation are audited but do not manufacture additional stems. All new-input
cells stay blank. Seasonal bins are recorded, but repeated zero health alone
does not trigger roster removal, and canonical mortality inference is unchanged.

HSP prints health/standing, with `/p` only for recorded poison ivy; blank ivy
does not become an absence observation. Because the current Parquet omits ivy,
the packet recovers this context by survey/source-file/source-row from the
exact hashed reviewed imports used by that publication, not by tag or rank.
Difficulty uses one rating per plot/survey: easy=1, medium=2, hard=3, brutal=4.
Its mean and rated-survey count come from the configured page metadata; 18
plots have May ratings and ten have no ratings. These source files are included
in the packet fingerprint. Neither feature rewrites the canonical dataset.

Approved candidates can be promoted with `forestcensus publish-candidate
output/october_2026_roster_fixes/forest_census.parquet`; this checks source/config
fingerprints and preserves the preceding publication under
`output/publication_history/`. Promotion does not rewrite source data or UI edits.

## Experimental LLM Transcription

Scanned recent datasheets can be rendered and transcribed with Gemini:

```bash
forestcensus transcribe-pdf /path/to/oct_2025_forest_census.pdf --pages 1
```

The command reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the environment or a
local `.env` file. It defaults to `gemini-3.8-flash`, a 300-DPI render, and page
1 so test runs stay small. Use `--pages all` only after checking a few page
outputs.

The May 2026 portrait datasheets use a separate typed contract:

```bash
forestcensus transcribe-pdf tmp/pdfs/spring_2026_BRNV_May26_scans.pdf \
  --survey-id May_2026 \
  --datasheet-format portrait_2026 \
  --datasheet-manifest-dir output/datasheets_2026/json \
  --pages 1-2
```

For Main rows, the printed per-plot JSON manifest is authoritative for tag,
taxon, and stem slot. Only handwritten health, standing, poison ivy, species
update, and notes are current observations; printed DBH and HSP columns remain
context and are never imported as May 2026 DBH. Newly Tracked rows have their
own schema and may contain a current handwritten DBH. Plot-level date, crew,
Problems/Info, and difficulty are retained in `page_metadata.csv`.
Saved portrait responses can be rematerialized against the exact manifest used
to print a field package without another model call:

```bash
forestcensus rematerialize-llm-run output/llm_transcription/may_2026_all_gemini37 \
  --datasheet-manifest-dir output/datasheets_2026_printed_manifest/json \
  --out-dir output/llm_transcription/may_2026_all_gemini37_printed_manifest
```

The completed October 2026 v8 sheets use the same portrait handler with the
exact v8 manifest, 12 Newly Tracked slots, and separate recheck/field-note
evidence. See [October 2026 transcription](docs/october_2026_transcription.md)
for source verification, pilot commands, and the latest extraction status.

Named handwriting calibration profiles can be included conditionally:

```bash
forestcensus transcribe-pdf /path/to/oct_2025_forest_census.pdf \
  --pages 3 \
  --handwriting-profile juan
```

Profiles live in `config/handwriting_profiles.toml` and point to calibration
images under `assets/handwriting/`. The Juan profile currently labels an example
where the left digits are 7s and the right digits are 1s.

Outputs are written under `output/llm_transcription/<pdf_stem>/`, including page
renders, review crops, strict raw JSON, rejected page errors, page metadata, run
metadata, a full transcription CSV, and an import-shaped CSV. The legacy LLM
schema intentionally excludes `dhas.1` and `dhas.2`; those columns are
field-worker context, not import data. The `p`/`pi` column is parsed as
`poison_ivy` for later review but is not part of canonical tree status logic.

## Revisit

- Future data collection guidance: alive/dead evidence should be recorded for
  each stem/measurement slot, not just for the plant as a whole. A multi-stem
  plant can have one dead stem and one living stem.
- Final output columns: decide whether `alive_observed`, `field_status`, and
  `interpreted_status` stay in the published parquet or move to diagnostics /
  internal provenance only.
- Canonical taxonomy: each tree identity should resolve to one canonical taxon.
  Rows that disagree within a tree should become taxonomy corrections or
  identity fixes, not mixed species values in the final dataset.
- Duplicate handling: keep manual `row_exclusions` for now. Do not add an
  automatic duplicate rejecter until we have a safer design, because repeated
  field mistakes and delayed stem additions can look duplicate-like.
- Minimum live health rule: for some `alive = true` and `health = 0` conflicts
  where context supports a living tree but not an exact health value, we are
  temporarily setting health to `1`. Revisit these after checking source sheets.
- Date parsing: mixed May 2024 formats such as `05/22/24` and `5/20/2024`
  are covered by adapter tests. Keep this coverage when adding future raw
  formats.

# Forest Census

Clean canonical forest census pipeline.

## Current Canonical Intent

The published dataset should be a single tabular output, currently written as
`output/forest_census.parquet`. Long term, health is the authoritative observed
state: `health = 0` means dead, and `health > 0` means alive. Legacy
`alive/dead` fields are adaptation/provenance scaffolding used to resolve older
input formats before the canonical output is finalized.

Corrections live in `config/corrections.toml` and are applied after raw input
adaptation, before assembly. Row corrections touch specific source rows;
taxon overrides apply one canonical genus/species to a resolved tree identity.
Raw data files should remain unchanged.

Identity operations live in `config/identity.toml`. The raw field tag remains
visible as `public_tag`; biological individuals are resolved with
`identity_tag`, and `identity_label` gives a human-readable filter label for
synthetic split identities such as old dead trees that were later confused with
a new visible tag.

## Experimental LLM Transcription

Scanned recent datasheets can be rendered and transcribed with Gemini:

```bash
forestcensus transcribe-pdf /path/to/oct_2025_forest_census.pdf --pages 1
```

The command reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the environment or a
local `.env` file. It defaults to `gemini-3.1-flash-lite-preview` and page 1 so
test runs stay small. Use `--pages all` only after checking a few page outputs.

Outputs are written under `output/llm_transcription/<pdf_stem>/`, including page
renders, review crops, strict raw JSON, rejected page errors, a full transcription
CSV, and an import-shaped CSV. The LLM schema intentionally excludes `dhas.1` and
`dhas.2`; those columns are field-worker context, not import data. The `p` column
is parsed as `poison_ivy` for later review but is not part of canonical tree
status logic.

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

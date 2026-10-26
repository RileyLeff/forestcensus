# LLM Transcription Handoff

This note describes the October 2025 scanned datasheet transcription workflow and the proposed handoff into the main forest census data pipeline.

## Current Status

The scanned PDF is `/Users/rileyleff/Desktop/oct_2025_forest_census.pdf`.

All 58 sheets have been rendered, transcribed, loaded into the review UI, and reviewed by Riley. Empty or blank sheets are represented in the layout manifests even when they produce no data rows.

Observed review result:

- Sheets represented in layout metadata: 58 / 58
- Extracted data rows: 1,413
- Editable fields reviewed per row: `dbh_mm`, `health`, `standing`, `poison_ivy`, `notes`
- Editable field count: 7,065
- Raw append-only review decisions: 51
- Deduped final field edits: 47
- Deduped edited rows: 42
- Observed editable-field accuracy after manual review: 7,018 / 7,065 = 99.33%

Deduped edits by field:

- `standing`: 23
- `health`: 16
- `dbh_mm`: 4
- `poison_ivy`: 4
- `notes`: 0

This is an empirical correction rate from the review pass. It should be described as "observed reviewed-field accuracy" rather than absolute accuracy unless a second independent audit is performed.

## Code Locations

Core transcription code:

- `src/forestcensus/llm_transcribe.py`
- CLI registration in `src/forestcensus/cli.py`
- Tests in `tests/test_llm_transcribe.py`

Reviewer app:

- `review-ui/src/routes/+page.svelte`
- `review-ui/src/routes/+page.server.ts`
- `review-ui/src/lib/server/review-data.ts`
- `review-ui/src/lib/types.ts`

Handwriting profile scaffolding:

- `config/handwriting_profiles.toml`
- `assets/handwriting/`

Current combined review selection:

- `output/llm_transcription/review_selection.json`

The `review-ui/` app is a SvelteKit/Svelte 5 tool. It reads transcription outputs and appends review decisions; it does not directly mutate the LLM transcription CSVs.

Important: `review_selection.json` is a mutable UI convenience file. During review it was changed to show different page ranges, and it currently may point only at the later 26-58 page set. Do not rely on that file alone as the final October 2025 reviewed-run manifest unless it is first updated to include the full reviewed run set below.

## How To Run Transcription

Use `uv` for project commands.

Example:

```bash
uv run forestcensus transcribe-pdf /Users/rileyleff/Desktop/oct_2025_forest_census.pdf \
  --pages 1-5 \
  --model gemini-3.1-pro-preview \
  --out-dir output/llm_transcription/oct_2025_pages_1_5_gemini_3_1_pro_column_guardrails \
  --save-cell-crops
```

The command reads `GEMINI_API_KEY` or `GOOGLE_API_KEY` from the environment or a local `.env` file.

The default model in code is currently `gemini-3.1-flash-lite-preview`, but the reviewed production batches mostly used `gemini-3.1-pro-preview`. Page 32 failed structured JSON parsing under Pro and was recovered with `gemini-3.1-flash-lite-preview`.

## Transcription Output Shape

Each run directory under `output/llm_transcription/` contains some or all of:

- `pages/page_###.png`: rendered full-page images
- `raw_json/page_###.json`: strict provider JSON for each successfully parsed page
- `layout_manifest.json`: page dimensions, table bounding boxes, column boxes, row boxes, crop paths
- `crops/page_###/table.png`: table crop
- `crops/page_###/rows/row_###.png`: row crops
- `crops/page_###/cells/...`: optional cell crops when `--save-cell-crops` is used
- `transcription.csv`: full internal transcription output with provenance and review flags
- `import_recent_format.csv`: recent-datasheet-shaped import CSV
- `review_rows.csv`: subset of rows with transcription or review flags
- `review_decisions.jsonl`: append-only human review decisions
- `rejected_pages.json`: rejected page errors, usually malformed JSON or schema failures

`transcription.csv` columns:

```text
survey_id,date,site,zone,plot,tree_number,tree_code,trunk_number,genus,spp,
dbh_mm,health,standing,poison_ivy,notes,
source_page,source_row,source_row_label,source_id_text,source_page_title,
source_image,source_json,transcription_flags,review_flags
```

`import_recent_format.csv` columns:

```text
survey_id,date,site,zone,plot,tree_number,tree_code,trunk_number,genus,spp,
dbh_mm,health,alive,old_tag,standing,notes,poison_ivy
```

Notes on semantics:

- `site` is hard-coded to `BRNV`; the forest census currently only occurs at Brownsville.
- `plot` is parsed from the sheet title.
- `id_text` is extracted from the printed sheet text and parsed into `genus`, `spp`, `tree_number`, and `trunk_number`.
- `health` is canonical. `0` means dead; `1-10` means alive. `alive` remains blank in LLM import output.
- `standing` is the `stnd` column, encoded as `1`, `0`, or blank.
- `poison_ivy` is the `p` column, encoded as `1`, `0`, or blank. It is extracted but not currently used in tree status logic.
- `dhas.1` and `dhas.2` are context only. They are intentionally forbidden in structured LLM output and are not import fields.
- Slash/dash marks in typed value cells are treated as missing values. Prose punctuation in notes can remain.

## Review Decision Output Shape

The review UI writes append-only JSON lines to `review_decisions.jsonl` in the source run directory.

Type shape:

```ts
type ReviewDecision = {
  key: string;
  source_run_dir?: string;
  action: 'accept' | 'edit' | 'skip';
  chosen_field?: string;
  chosen_value?: string;
  note?: string;
  decided_at: string;
};
```

Typical edit:

```json
{"key":"28:16:Pin.tae.838.1","source_run_dir":"/Users/rileyleff/Documents/dev/forestcensus/output/llm_transcription/oct_2025_pages_26_30_gemini_3_1_pro_column_guardrails","action":"edit","chosen_field":"dbh_mm","chosen_value":"219","note":"","decided_at":"2026-05-06T12:37:51.774Z"}
```

Decision keys are currently:

```text
source_page:source_row:source_id_text
```

The log is append-only. For integration, dedupe by `(key, chosen_field)` for `edit` actions and keep the latest `decided_at`. This preserves self-corrections without rewriting history.

`accept` and `skip` are useful review-progress signals. They should not change extracted data values.

## Current Reviewed Run Set

The 58-page review uses these run directories:

```text
output/llm_transcription/oct_2025_pages_1_5_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_6_10_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_11_15_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_16_20_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_21_25_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_26_30_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_31_35_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_page_32_retry_gemini_3_1_flash_lite_preview_column_guardrails
output/llm_transcription/oct_2025_pages_36_40_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_41_45_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_46_50_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_51_55_gemini_3_1_pro_column_guardrails
output/llm_transcription/oct_2025_pages_56_58_gemini_3_1_pro_column_guardrails
```

Page 32 should come from the flash-lite retry directory, not from the rejected Pro attempt.

Pages 1-25 have their own decision logs and must be included in final materialization:

- Pages 1-5: 0 review edits
- Pages 6-10: 11 raw decision entries, 10 deduped edits
- Pages 11-15: 18 raw decision entries, 16 deduped edits
- Pages 16-20: 1 raw decision entry, 1 deduped edit
- Pages 21-25: 5 raw decision entries, 5 deduped edits

Together, pages 1-25 contain 35 raw append-only decision entries and 32 deduped final field edits. Pages 26-58 contain 16 raw decision entries and 15 deduped final field edits. The full October 2025 reviewed total is therefore 51 raw decision entries and 47 deduped final field edits.

## Recommended Integration Move

Add a materialization step between review and the canonical build:

1. Load the selected run directories.
2. Concatenate `transcription.csv` rows.
3. For each row, build the key `source_page:source_row:source_id_text`.
4. Load all `review_decisions.jsonl` files.
5. Keep the latest edit for each `(key, chosen_field)`.
6. Apply those edited values to a copy of the transcription rows.
7. Write:
   - `output/llm_transcription/oct_2025_reviewed/transcription_reviewed.csv`
   - `output/llm_transcription/oct_2025_reviewed/import_recent_format_reviewed.csv`
   - `output/llm_transcription/oct_2025_reviewed/review_application_summary.json`
8. Feed the reviewed import CSV into the existing raw-data adaptation path for recent datasheets.
9. Run the normal build and validation pipeline.

This keeps the provenance clean:

- Raw scans remain unchanged.
- Raw LLM output remains unchanged.
- Human review remains append-only and auditable.
- The reviewed import CSV is a deterministic derived artifact.
- Existing `config/corrections.toml` can still handle downstream biological/data-model corrections after import.

The materializer should fail loudly if a decision key does not match exactly one transcription row. That prevents silent off-by-one errors, which were the main concern behind extracting printed `id_text` from the sheet instead of aligning rows by prior data order.

## Suggested Materializer CLI

Suggested command:

```bash
uv run forestcensus materialize-llm-review \
  --selection docs/oct_2025_reviewed_run_manifest.json \
  --out-dir output/llm_transcription/oct_2025_reviewed
```

The final materialization manifest is `docs/oct_2025_reviewed_run_manifest.json`. It includes all run directories listed in "Current Reviewed Run Set", not just the current UI subset.

Suggested summary output:

```json
{
  "rows_loaded": 1413,
  "decisions_loaded": 51,
  "edits_applied": 47,
  "edited_rows": 42,
  "unmatched_decisions": 0,
  "outputs": {
    "transcription": "output/llm_transcription/oct_2025_reviewed/transcription_reviewed.csv",
    "import": "output/llm_transcription/oct_2025_reviewed/import_recent_format_reviewed.csv"
  }
}
```

## Open Questions For The Data Agent

- Where should the reviewed October 2025 import CSV live before canonical build: under `output/llm_transcription/` as a derived artifact, or copied into `data/raw/forest_census/` as an accepted input?
- Should poison ivy remain in the recent import file only, or should it get a canonical/provenance column downstream?
- Should reviewer `accept` and `skip` decisions be preserved in a diagnostics table, or only the edit application summary?
- Should page-level rejected-run metadata be retained with the final reviewed artifact, especially the page 32 Pro failure and flash-lite recovery?

# October 2026 Transcription

The October parser and review UI support the completed v8 sheets. Billing was
restored on October 12, 2026, and the new default `gemini-3.8-flash` completed
`output/llm_transcription/october_2026_pilot_gemini38_v1`: five pages, 81 rows,
no rejected pages, and no unmapped rows. The run is `transcribed_pending_review`;
the full 78-page extraction has not started. No October data have been published
to the canonical dataset, and existing May review decisions are unchanged.

Each successful API response now records its actual model version and token
usage, including thinking tokens, in `usage/page_NNN.json`. High thinking and
high image resolution remain enabled. These logs support cost estimates rather
than billing reconciliation; they do not include failed provider attempts.

## Source Packet

- Completed scan: `output/pdf/BRNV_October_2026_completed_all_plots_R_H_M_L.pdf`
- Audited page map: the adjacent `.manifest.json` file.
- Printed packet: `output/datasheets_october_2026/v8/`, ID `5865feed3c3222e1`.
- Coverage: 78 pages, 28 plots, 1,279 Main rows, 12 Newly Tracked slots per plot.
- Scan SHA256: `e1af80122706e9fea9fec80254d06b636d8b3c046cd92a2bc8f62442ecd692a4`.

The adapter checks the scan hash, printed packet ID, survey, and complete page
map before making model requests. It reads the blank packet PDFs to establish
which row labels and questions belong on each scanned page, and verifies Main
row coverage against the flat per-plot JSON manifests. It does not use previous
health scores to supply current observations.

## Contract

The existing `portrait_2026` handler supports both May and October. May's
`row_pages` manifests and six recruit slots remain supported. October uses
flat `rows`, 20-point rows, updated column widths, and N1-N12.

- Main identity comes from the exact printed manifest. `*` and `+` are context
  markers, not parts of tag identity. Stem numbers remain survey slots.
- Main health, standing, poison ivy, species updates, and notes are handwritten
  current inputs. Printed previous DBH and HSP values are never current inputs.
- Newly Tracked entries retain their physical N label, including N7-N12, and
  may contain current DBH. The section does not imply biological recruitment.
- Blank or handwritten NA numeric/boolean inputs are missing. Blank standing
  is not automatically converted to fallen during transcription.
- Recheck answers retain their question number, printed question ID, target
  tags/UUIDs, and handwritten answer. Unanswered questions remain explicit.
- Field-note feedback retains independent Helpful, Confusing, and Incorrect
  checkbox values and handwritten annotations. Unmarked boxes are null.
- Roles, handwritten date, Problems and Info, and other margin handwriting are
  retained as page evidence. Current difficulty comes only from the final
  difficulty checkboxes, never the historical average in the header.

Question answers and page prose are evidence, not automatically generated
stem rows or canonical corrections. Review them before making identity,
stem-count, or standing decisions. Page evidence is present in raw JSON and
`page_metadata.csv`, is shown under **Page notes** in the transcription UI,
and survives `materialize-llm-review` as a separate provenance-bearing table.
The row editor still handles stem fields; the new page evidence is read-only.

## Validation and Safety

The model must account for every printed Main row, question, and field-note
bullet on the page. Wrong plots, missing/duplicate rows, invalid recruit slot
labels, and invented difficulty ratings fail validation. Saved structured
responses that fail packet checks remain available for diagnosis but do not
enter the import CSV. Rematerialization repeats packet validation and rejects
a changed printed manifest.

Use a fresh output directory for each model run. The command refuses to
overwrite an existing transcription, saved model response, or review log.
Incomplete runs return a nonzero CLI exit status and record rejected pages.
Authentication/billing failures stop further model requests in that run.

Local geometry QA checked all 78 actual scanned pages against all 1,615 printed
table slots, including blank recruit slots, with none unmapped. Representative
overlays were visually inspected. The detector searches additional strips to
avoid mistaking M7's crossed-out notes for table lines. Automated Python tests,
Svelte checks/build, and browser checks cover compatibility and the new metadata.
These checks establish coverage and alignment, not perfect OCR accuracy. The
real pilot below still needs human review before publication. All 197 Python
tests passed after the model upgrade and token-usage logging change.

## Gemini 3.8 Pilot Results

| Global page | Plot page | Extracted observations | Additional evidence |
| --- | --- | ---: | --- |
| 9 | R4 1/4 | 30 Main | Date, roles, row notes |
| 10 | R4 2/4 | 33 Main | Ambiguous standing checkbox flagged |
| 11 | R4 3/4 | 10 Main | Three recheck answers and one annotated field note |
| 12 | R4 4/4 | 0 | Easy difficulty; blank recruit slots remained empty |
| 43 | M3 2/2 | 6 Main + 2 Newly Tracked | Plot prose and medium difficulty |

Visual spot checks found the expected main-row health patterns, question
answers, and handwritten recruits. Review attention remains warranted for:

- R4 row 33 (5224): overwritten health numeral, transcribed as 8.
- R4 row 40 (5229): scribbled standing checkbox; returned null with a flag.
- R4's 5163 field-note annotation: overwritten stem count and the 5243/out-of-plot
  remarks remain evidence, not an automatic stem or identity change.
- M3 N1 (transcribed as 5826): the note itself questions its relationship to
  5827. Both rows are preserved; no identity merge has been made.
- M3 N2 (360): approximate DBH was transcribed as 400 mm with a flag retaining
  the approximation. The note about its absence from the sheet is preserved.

The five successful responses report 13,939 input tokens, 7,108 answer tokens,
and 88,980 thinking tokens. At Google's October 2026 standard rates of $0.75
per million input tokens and $3.75 per million output/thinking tokens, the
estimated pilot cost is **$0.3708**. A simple 78-page extrapolation is **$5.78**;
budget roughly $6-10 for the full extraction and some retries, not a guaranteed
quote. Complexity and thinking usage vary substantially by page. See
[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).

## Pilot and Full Run

The current pilot command uses a fresh output directory:

```bash
uv run forestcensus transcribe-pdf \
  output/pdf/BRNV_October_2026_completed_all_plots_R_H_M_L.pdf \
  --survey-id October_2026 \
  --datasheet-manifest-dir output/datasheets_october_2026/v8/json \
  --pages 9-12,43 \
  --out-dir output/llm_transcription/october_2026_pilot_gemini38_v1
```

R4 pages 9-12 cover recheck answers and annotated field notes; M3 page 43 adds
handwritten Newly Tracked rows and plot-level prose. Verify raw output, packet
validation, `layout_report.json`, and scans in the review UI before `--pages all`
in a separate full-run directory. Do not add an unreviewed run to canonical
sources or overwrite the May review selection.

```bash
cd review-ui
REVIEW_RUN_DIR=output/llm_transcription/october_2026_pilot_gemini38_v1 npm run dev -- --port 5176 --strictPort
```

The first attempt, `october_2026_pilot_v1`, failed because the local Tailscale
DNS resolver returned NXDOMAIN for `generativelanguage.googleapis.com`.
Google's HTTPS DNS service resolved the endpoint successfully; the
process-local helper (now tracked as `scripts/transcribe_with_https_dns.py`) reached Gemini,
which returned the billing error in `october_2026_pilot_v2`. The helper leaves
system DNS settings, the request hostname, and TLS verification unchanged.
If ordinary DNS remains broken, substitute
`uv run python scripts/transcribe_with_https_dns.py transcribe-pdf` for
`uv run forestcensus transcribe-pdf` in the pilot command.

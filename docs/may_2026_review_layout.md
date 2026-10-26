# May 2026 Review Overlays

## Current Reconciliation Status

Riley approved the final tag, taxonomy, absence, and note-standing decisions
on 2026-10-03; the October 4 follow-up below recovers two additional stem
observations and corrects M5/2479's standing value. The current publication
contains 1,341 May observations for 1,241 identities
across 28 plots, with no hard validation errors and no May row-scoped warnings.
This does not certify every historical identity or close the broader review
queue. Four May tags retain explicitly unresolved histories. The reviewed
input has 1,349 source rows and all 33 saved transcription edits. Every cell
of the preceding 1,347 reviewed rows was verified unchanged by source key.
The verified candidate has now been promoted to `output/forest_census.parquet`;
its original remains in `output/october_2026_roster_fixes/forest_census.parquet`.
The preceding publication and replaced diagnostics/decision files are backed
up under `output/publication_history/`. Before promotion, all 33 saved edits
were rematerialized into a temporary directory and both reviewed tables were
compared cell-for-cell; neither source evidence nor review logs were changed.
Fresh validation again found no hard errors. The current October roster packet
is `output/datasheets_october_2026/v8/`; Claude's context-only field-note rewrite
is incorporated, with Helpful / Confusing / Incorrect feedback columns. The
roster now omits trees absent from both recent surveys and dead/fallen entries,
with targeted questions linked to starred main rows for genuine conflicts.
See `docs/october_2026_datasheet_requirements.md`
for the final format, HSP source links, and historical difficulty averages.

The dated sections below retain earlier counts and proposed calls as a work
log; later accepted decisions supersede those earlier snapshots.

Before the October 4 follow-up, the reviewed-manifest run contained 1,347
observation rows: 1,292 Main rows and 55 Newly Tracked rows. Before the
approved R4 recovery below, the 44
Newly Tracked rows included 37 entries in printed N1-N6 slots,
six handwritten additions below Main on pages 19, 21, and 23, and the approved
L6/100 overflow observation in page 57's Problems and Info.

The original viewer assumed one table per page. On pages with both sections,
it omitted some newly tracked overlays or assigned the wrong table's columns.
The layout rebuild separates the sections, matches physical slot labels
(including gaps), and follows the scan's tilt. Main has health before the
historical printed DBH column; Newly Tracked has measured DBH before health.
Handwritten additions below Main retain Main's column order.

## Rebuild

```sh
uv run forestcensus rematerialize-llm-run \
  output/llm_transcription/may_2026_all_gemini37 \
  --out-dir output/llm_transcription/may_2026_all_gemini37_printed_manifest \
  --datasheet-manifest-dir output/datasheets_2026_printed_manifest/json \
  --page-additions config/may_2026_transcription_additions.json

uv run forestcensus rebuild-review-layout \
  output/llm_transcription/may_2026_all_gemini37_printed_manifest \
  --overrides config/may_2026_review_layout.json
```

The second command changes only `layout_manifest.json`, preserving its original as
`layout_manifest.before_tables.json`. It does not modify transcription CSVs,
model responses, source scans, row keys, or review decisions, and makes no LLM
calls. New portrait transcription runs generate section-aware geometry
automatically. Unlocated handwritten additions need a visually checked geometry
override, not an invented grid position.

`config/may_2026_review_layout.json` records twenty off-grid rectangles.
Each override checks the source image SHA-256 and exact source row label/ID
before it can apply. These are display annotations, not data corrections.

## Verification

- All saved Newly Tracked/recovered rows have overlays, including R4's eleven note
  observations, page 57's N6, and L6/100.
- All 1,349 saved rows have overlays after the October 4 rebuild, including
  both newly recovered parent-note stem observations.
- Blank N slots are preserved in geometry; they do not become observations.
- Page 2 has no extracted observations and its Newly Tracked grid is blank.
- Tests cover mixed six-row tables, blank N slots, tilted scans, unchanged
  CSVs/decisions, repeatable rebuilding, and invalid override rejection.

This verifies display coverage of the saved extractions, not an independent
OCR completeness audit. Model readings still require review. For example,
page 4 N2 (R2/980) was extracted as DBH 4.7. Riley subsequently approved
assuming 47 mm on 2026-10-03; this is now an explicit review decision, not
a silent change to the source extraction.

## Roster Follow-Up, 2026-10-04

Two visually verified parent-row notes contained observations missing from
the extracted data:

| Case | Source | Recovered observation |
| --- | --- | --- |
| R3/677 | Scan page 5, Main row 21: `2nd stem 0/10 stand` | Second stem, health 0, standing true |
| H0/274 | Scan page 9, Main row 21: `3rd stem also dead stand` | Third stem, health 0, standing true |

`config/may_2026_transcription_additions.json` records these additions using
stable labels `row-21-stem-2` and `row-21-stem-3`. The shared materializer
now optionally selects an exact parent `source_row_label`, requiring a unique
parent, matching plot, expected note text, and the unchanged raw JSON SHA-256.
No DBH or poison-ivy values were invented. The original parent notes, scans,
and model JSON remain intact. Geometry overrides point to those written notes
so the recovered rows are reviewable in the transcription UI.

M5/2479's Main row 13 on scan page 35 has health 0, an unchecked standing
box, and the explicit note `Fallen`. The model had incorrectly supplied
standing=true. A guarded `config/corrections.toml` decision sets it false
in the unified canonical decision phase, preserving the raw reviewed source.
This is not a new unchecked-box default. Its current dead/fallen context
excludes it from the October search list.

Preservation and publication checks:

- All 33 saved edits applied, with zero unmatched edits; the decision log
  is byte-identical. All prior 1,347 reviewed rows match cell-for-cell by
  `(source_page, source_row_label, source_id_text)`.
- Review layout rebuilt for 49 observation-bearing pages with zero unmapped
  rows. Blank pages remain part of the original complete scan/run.
- Compared with the prior canonical dataset, exactly two observations were
  added and none removed. The only existing observation-value change is
  M5/2479's May standing correction. Source-row coordinates shifted where
  the extra input rows were inserted; this is provenance, not a retag.
- The current canonical publication has 12,266 observations for 1,385 UUIDs,
  including 1,341 May observations. Validation has no hard errors; existing
  historical review findings are not asserted resolved.
- Previous reviewed files and layout/log metadata are retained under
  `output/llm_transcription/may_2026_before_roster_fixes/`. The preceding
  canonical publication is in `output/publication_history/eb16b0b5f5e2060/`.
- Full suite: 175 passed; the final focused packet/reconciliation check
  passed 42 tests, including rendered asterisks and question text.

Of the initial 29 single-rank standing/fallen candidates, M5/2479 is corrected
above and three have intervening live evidence. The remaining 25 have targeted
questions in the October packet, as approved by Riley. Missing both recent
surveys does not itself create a recheck question or restore an omitted tree.

## Reviewed Input Materialization, 2026-10-03

Riley reported that the UI corrections were entered. The saved log contains
28 field edits across 27 rows (20 edits since the previous eight-entry check):
21 health, three species, two stem-slot, one genus, and one standing edit.
All 28 applied to exactly one matching transcription row; none were skipped
or unmatched. The R3 taxonomy and R4 standing decisions are included.

Use the fixed full-run manifest, not a mutable UI page selection:

```sh
uv run forestcensus materialize-llm-review \
  --selection docs/may_2026_reviewed_run_manifest.json \
  --out-dir output/llm_transcription/may_2026_reviewed
```

The reviewed transcription and recent-format import contain all 1,347 rows
from 28 plots: 1,292 Main and 55 Newly Tracked/recovered rows. The source run
materialized all 62 pages, including blank pages; no pages were rejected.
Verification reconstructed the expected edited table and compared every
transcription cell. Source transcriptions, raw model JSON, layout, decision
log, and the published canonical Parquet were unchanged.

An in-memory adaptation and unified-decision check loaded 1,346 May events.
One untagged M2 page-30 row (`|JUNVIR|1`, source row 12) has no health or
notes and is not assigned a tree by the numeric-tag adapter; it remains
in both reviewed CSVs. No other May rows were removed by adaptation or
manual decisions. The R4 merge yields three May observations under the
5163 UUID, with health 9, 8, and 0 and both original public tags retained.

`config/sources.toml` already points at this reviewed import, so subsequent
pipeline builds will include it. Materializing this input does not itself
rebuild or publish the canonical dataset or regenerate field sheets. The
application summary is `output/llm_transcription/may_2026_reviewed/review_application_summary.json`.

Riley then approved assuming 47 mm for R2/980 rather than 4.7. That decision
was appended through the review server's normal action, with the assumption
recorded in its rationale. The rematerialized input now contains 29 edits
across 28 rows, including that DBH edit; all 29 edited fields and all
otherwise unchanged transcription cells were verified. The earlier history
(47 mm in June 2023, then 46 mm in October 2024, April and October 2025)
supports the approved value. The original model value remains available.

Forty focused transcription, identity, and assembly tests passed before this
additional data-only decision.

## Initial Integration Preflight, 2026-10-03

An in-memory build after the 47 mm correction returned no hard validation
errors and retained all 1,346 tagged May input rows after whole-tree size
filtering. This is structural validation, not a clean bill of health for
identities, stem counts, taxonomy, or field-status interpretation. No updated
canonical Parquet, diagnostic bundle, or datasheets were published.

| Category | Current evidence / effect | Required next action |
| --- | --- | --- |
| Repeated entries | L6/88 appears on Main and in the write-ins, both dead and standing. L6/991 and its accepted alias 57 likewise appear in both places. | Resolved by the approved case-specific consolidation below: one May observation per identity, both sources retained. No general automatic deduplication rule. |
| Incomplete or cancelled slots | R2/933 and M5/1201 have crossed-out, unmeasured extra entries on the scans. | Resolved below: retain one measured stem for R2/933 and two for M5/1201; exclude the cancelled rows only from the canonical projection. Ordinary not-found observations are unchanged. |
| Remaining readings | M2 was extracted as 1264; the scan looks like 1204, with no history under either number. M4/1205 was `Mor lbr`. | Both resolved after Riley's confirmation: M2/1204 and M4/1205 MORCER. |
| Historical identity collisions | L5/443 is a live Juniperus in May but a dead Pinus in the existing history. M6/5154 could be a transposition of 5145. L2/733 explicitly mentions 5038, but neither has a same-plot archived match. | Resolve or retain explicitly uncertain identities; do not manufacture resurrection, recruitment, or cross-plot links. The omissions audit lists the other unmatched write-ins. |
| Found versus health status | Nine standing-only rows and seven note/input contradictions exposed a conflation of unknown health with absence. | Presence rule fixed below. Preserve the seven note/input contradictions as explicit review findings; do not silently change measurements. |
| R4 partial evidence | 5262 has one May score for a historical two-stem plant; 5263 says "sta"; 5238/5163 have complementary histories. | Riley accepted one score for 5262, confirmed standing for 5263, and approved the 5238/5163 alias. See the subsequent decisions below. |

The nine standing-only rows are M3/5188, L0/191, L0/192, L1/115,
L1/5058, L3/297, L4/268, L5/509, and L7/5039. The seven note/input
contradictions are H1/96, H4/130, M0/585, M0/586, M4/2444, M7/319,
and M7/329. This preflight records concerns; it does not approve extra
corrections or implement new rules. For October generation, also complete
the roster, alias, seasonal, and packaging safeguards in
`docs/october_2026_datasheet_requirements.md`.

## Final Reconciliation Approved, 2026-10-03

These are canonical decisions, not rewritten transcription cells: Riley
checked the source PDFs and found the handwritten tags correctly transcribed.
The reviewed CSVs, all 33 UI edits, original scans, and model outputs remain
unchanged. The existing unified decision phase applies the following calls:

| Case | Accepted interpretation |
| --- | --- |
| Vaccinium | Canonical genus-level identification only: Vaccinium spp. An explicit `scope = "genus"` taxon-resolution decision applies after tree-level taxon calls. The legacy `cor -> cerifera` abbreviation is restricted to Morella; raw Vaccinium `cor` is preserved until the decision phase. |
| M1/5952 | Exclude this measurement-free, taxon-free `(fallen)` write-in from the canonical projection. Preserve source evidence; no new plant or death event is asserted. |
| M6/5154 | Associate the written tag with identity 5145. Historical Juniperus 5145 was dead standing at 40 mm and omitted by the old threshold. The May note supplies standing=true; established identity supplies canonical Juniperus virginiana. |
| L2/616 | Associate with identity 816, the declining 59 mm Morella with complementary missing entries. Suppress the blank Main 816 placeholder, retain the dead-standing 616 observation and original public tag. |
| L2/733 | Associate with identity 5380. The written `5038` note is interpreted as a digit-order mistake. Preserve both May health-3 observations: Main 5380 and handwritten slot-2 733. This is an additional observation, not a duplicate or proof of permanent stem identity. |
| L5/509 | Extract health=0 from `0 - previously tagged`, retain standing=true and written tag 509, and leave historical identity unresolved. |

The three new identity interpretations are survey-scoped row reassignments,
not global aliases or claims that the archived tag-change sheet supplied
these links. They preserve `public_tag` and `tree_number`, change only
`identity_tag`, and record the rationale in `correction_notes`.

### Unlinked History Queue

Do not force these retained observations into the suggested alternatives or
infer recruitment/threshold crossing from their first documented appearance.

| Written tag | Current call and field-check context |
| --- | --- |
| L1/891 | Retain dead standing Morella. No convincing number variant; 727 is missing but numerically unrelated, and 456 was already fallen. |
| L5/786 | Retain dead standing Juniperus. Omitted dead-standing 987 (30-31 mm) is a weak candidate, not an accepted link; 986 is a pine already recorded in May. |
| L5/509 | Retain dead standing Morella with the approved health correction. No L5 historical match. The archive's H3/509 pine is not evidence of a cross-plot link. |
| L6/574 | Retain living Morella, health 8. Missing 724 (62 mm, health 5 in April 2025) and omitted 782 (56 mm, health 6 in October 2024) remain weak candidates, not approved links. |

### Absence And Standing Decisions

The seven contradictory May entries are now `not_found`: H1/96, H4/130
slot 2, M0/585, M0/586, M4/2444, M7/319, and M7/329. Their canonical current
health, standing, and legacy alive inputs are missing, while original values
and notes remain in source evidence. Historical observed death is retained.
In particular, M7/329's earlier fallen observations are not replaced with a
May standing sighting. H4/130's separate standing slot-1 observation remains.
An absence run may still affect interpreted mortality; it is not a new
observed death or a claim that the fallen stem was located in May.

Standing guidance is implemented as guarded decisions for unambiguous May
source contents, not a global keyword parser or an unchecked-box default:

- 32 explicit fallen notes supply standing=false. Health is unchanged; three
  entries with no health remain unknown-health observations, not invented
  health zeroes (H2/102, M1/829, L0/174).
- M6/5154's `dead standing` and R4/5211's `upright but leaning on another
  tree` supply standing=true despite blank checkboxes.
- `fallen most likely` (L1/148), `lots of fallen junipers` (L6/50), and
  partial breakage `fallen above girdle` (L2/228) do not establish a new
  standing/fallen measurement. Blank boxes without corroboration stay unknown,
  including on health-zero or positive-health rows.
- Explicit missing/not-found entries are not converted into observed fallen
  rows. No irreversible status is imposed on a changing stem-rank channel or
  on all stems of a multi-stem tree.

Every selector includes survey/source/plot/tag and expected observation
contents, without row-number dependence. Changed evidence fails the guarded
correction rather than silently adopting a different observation. These
rules stay in the existing configured-decision ledger.

The below-threshold row diagnostic now uses inclusive 20 mm generally and
50 mm for Morella cerifera, consistent with current eligibility; the six
valid May measurements no longer receive the stale blanket-50 warning.
Other historical stem-profile diagnostics are not redefined by this change.

The separately built candidate and its manifest, diagnostics, and decision
ledger are in `output/may_2026_prepublication/`. May statuses are 818 observed
alive, 385 observed dead, 125 not found, and 11 observed with unknown health.
All approved group counts and seven absence corrections were checked against
the actual rebuilt candidate. Source/review and published-file hashes were
verified unchanged. October sheets have not been regenerated.

Verification: the full suite passed 140 tests. After the final refinement
that applies genus-resolution policies after tree taxon calls, all 80 focused
decision, identity, taxonomy, observation-status, and validation tests passed,
including the new ordering regression. Candidate event values were compared
with the final configured decisions. Tests cover preserved source inputs,
two-versus-one stem counts, absence without resurrecting fallen trees,
unknown checkboxes, changed-evidence guard failures, and row-number independence.

## Approved Stem Consolidation and Taxon Call, 2026-10-03

Riley authorized merging likely duplicates after checking for historical
second stems and asked for the historical context of blank extra entries.
The history and original page images support four specific suppressions:

- L6/88: one stem in the historical records, 92 mm in 2019/2020 and 96 mm
  in October 2024. May Main page 53 row 38 and page 57 N5 both say dead,
  standing, stem 1. Retain Main, carrying forward "previously tagged".
- L6/57 and 991: accepted old/new tags for one identity, historically
  56 mm under 57 and 54-55 mm under 991. The October 2024 extra row under
  57 is entirely blank, not evidence of a second stem. May Main page 55
  row 64 and page 57 N6 repeat dead/standing stem 1. Retain Main tag 991
  resolving to identity 57, and carry forward "previously tagged".
- R2/933: one historical stem with DBHs 24, 29, 20, 28 mm. May page 4 N1
  visibly crosses out the tag/taxon without measurements; N3 records
  23 mm, health 4, standing. Retain N3, not a fictitious second stem.
- M5/1201: no historical entry for this plot/tag. May page 36 N1/N2 have
  62/58 mm and health 3/8, both standing; Riley corrected their slots to
  1/2. N3 crosses out the tag with no measurements. Retain two stems, not
  three. Their ranks are still survey-local, not permanent stem identities.

These decisions are in `config/corrections.toml` and execute only within
the unified decision phase. They are scoped by source filename, survey,
site, plot, tag, slot, and recorded contents, not shifting row indices.
Numeric `nan` selectors now explicitly match missing values, allowing the
cancelled-row decisions to fail rather than suppress a newly supplied DBH
or health measurement. Standing false and health zero are not missing.
Each L6 retained row has a correction rationale linking the supporting
write-in review key; all original rows remain in reviewed source evidence.

M4/1205's species suffix was corrected from `lbr` to `cer` through the
review server after Riley confirmed MORCER. The current reviewed export
contains 30 field edits across 29 rows, with all 1,347 source rows retained.
Its 1,346 tagged adapted events become 1,342 May observations after these
four exclusions. Focused verification confirmed the 1/1/1/2 stem counts
above, retained notes and measurements, and 56 passing tests. The published
canonical Parquet has not been regenerated.

### Findings Presented to Riley

This is the evidence presented before the subsequent approvals below; it
does not supersede the current accepted-decision section.

- M2/1204 versus 1264: neither occurs in the archived evidence ledger's
  public/old tags, tree codes or notes, or in explicit tag-change assertions.
  May page 30 N2 looks like 1204 and records Morella cerifera, 50 mm,
  health 6, standing. Recommend 1204 from the handwriting, not from a
  claimed historical match. The reviewed tag remains 1264 pending a call.
- L5/443: historical Pinus taeda is dead from June 2019 through October
  2024, with 420 mm DBH recorded in 2019, 2020, and 2022. April 2025 says
  DNF; October 2025 has no direct inputs. May 2026 page 52 N1 says
  Juniperus, health 7, standing, no DBH, "previously tagged". Do not assume
  this is resurrection or overwrite the historical species. Also preserve
  the contradictory May 2024 source: DBH cell says "confirmed fallen"
  while standing is 1. No identity/status call has been made here.
- Found status still conflates unknown health with not found in nine
  standing-only May observations, and explicit not-found notes override
  populated measurements in seven others. Proposed handling is separate
  found evidence (any recorded DBH, health, or standing, including 0/false)
  from health (which can remain unknown); flag note/input contradictions
  without silently discarding recorded measurements. No status code changed.
- R4/5262: the smaller historical stem is health 0 in October 2024,
  April 2025, and October 2025, while the larger stem has health 7/7/4.
  May's single health 5 likely concerns the living stem, but does not
  justify assigning a second score or proving permanent stem continuity.
- R4/5263: May note reads "5263 - vacc 7, sta"; standing is plausible,
  but remains unspecified until the abbreviation is accepted.
- R4/5238 versus 5163: same Acer rubrum and complementary 316/317 mm
  histories strongly suggest a tag correction; no explicit assertion
  confirms it. This remains separate from the accepted 5243/5163 merge.

## Subsequent Accepted Decisions, 2026-10-03

Riley accepted the recommendations other than the unresolved L5 tag reading:

- M2/1264 -> 1204 and R4/5263 standing -> true were appended as ordinary
  review edits and rematerialized. The export now contains 32 field edits
  across 31 rows. Original source IDs still point to the original readings.
- R4/5238 -> 5163 is an additional alias in the unified identity-decision
  phase. June 2023 now has the three distinct maple observations under one
  UUID (316 mm, 133 mm, and a dead stem without DBH), preserving all source
  public tags. No fourth stem or extra observation was invented.
- R4/5262 keeps its one actual May health-5 observation, with no fabricated
  score for its smaller historical dead stem and no claimed stem identity.

### Found-Status Implementation

Adapters now determine presence from DBH, health, or standing, including
zero and false. All three absent means `not_found`; presence with unknown
health means `observed_unknown`, distinct from pending absence. Legacy
alive/dead fields can help classify health only after direct found evidence
exists. Existing manual decisions still apply in their one explicit phase.

`observed_unknown` breaks absence runs and does not establish either a
death or a later living observation for zombie detection. A dead stem plus
a found stem with unknown health does not assert whole-tree death.
`alive_interpreted` is now nullable for unknown health and pending absence.
The source health and standing fields are unchanged.

Notes mentioning missing/not found alongside direct observations now produce
`W_FOUND_NOTE_CONFLICT` / `found_note_conflict` in diagnostics and the review
queue instead of overriding the inputs. The seven May contradictions listed
above remain flagged. May's 1,342 post-decision observations classify as
819 observed alive, 389 observed dead, 123 not found, and 11 observed with
unknown health. The last group includes the original nine standing-only
rows plus two standing-only rows formerly overridden by a missing note.
Season-aware foliage and October retirement policies are not changed here.
Missing tags and broken/missing treetops alone are not treated as missing-tree
contradictions. Tests cover those wording exclusions and preserve mixed notes
that separately say the tree was not found.

Verification: the full suite's 105 other tests passed; its existing evidence
integration test was updated for the newly available May source and its
untagged cancelled slot, then passed on rerun. After the final note-pattern
refinement, all 72 focused status, identity, correction, assembly, validation,
review, IR, and datasheet tests passed. All 32 saved field edits were compared
against the reviewed transcription; all other cells and 1,347 source rows
were retained. The published Parquet remains pre-May.

### L5/943 Counterfactual, Not Yet Applied

Riley suggested the May page 52 N1 tag may be 943 rather than 443. There is
no L5/943 history in the canonical inputs, archived public/old tags, tree
codes, notes, or explicit tag-change assertions. The archive's occurrences
of 943 are R1 Ilex, not a basis for linking this L5 Juniperus.

An in-memory test changing only this May observation to 943 separates a
living Juniperus (health 7, standing, DBH missing, "previously tagged") from
the long-dead L5/443 Pinus. It removes that taxon/zombie collision but does
not recover earlier history or prove biological recruitment. Keep the
previously-tagged note and treat history as unlinked, not newly grown.

There is also an existing L5/913 Juniperus with 232/227/230/230/235 mm
history from June 2023 through October 2025, and May health 7/standing
already recorded on Main. That is a comparison candidate only: matching
taxon and health do not prove the write-in is its duplicate. No 443 -> 943
edit or 913 merge has been applied pending Riley's tag confirmation.

### Accepted L5/913 Reading And Duplicate Merge

Subsequently on 2026-10-03 Riley read page 52 N1's scratched-out tag as
913 and explicitly approved treating it as the same observation as the
printed main row 48. Both record one Juniperus stem, health 7, standing,
and no newly measured DBH. Historical L5/913 has one measured stem,
227-235 mm and health 6-7, from June 2023 through October 2025.

The append-only transcription review decision changes only N1's tag to
913, preserving its original review key `52:15:443|JUN|1`. The unified
decision configuration retains the main row, carries `previously tagged`
onto it, and suppresses the repeated write-in from the canonical projection.
Both source rows remain available. These are guarded, May-only decisions;
there is no global 443-to-913 alias, no change to the historical dead pine
L5/443, no new L5/943 identity, and no inferred extra stem.

The same-plot omission check found no healthy Juniperus excluded from the
printed May roster in the available histories. Omitted tags 427 and 985
had dead/unknown histories and failed the two-survey presence rule; 987
was a dead 30-31 mm tree excluded by the old blanket 50 mm threshold.
Previously live 403 (April 2025: 174 mm, health 5), 405 (October 2025:
96 mm, health 6), and 5045 (October 2025: 117 mm, health 4) lack May
observations but were all printed. None establishes a competing link to N1.

Verification: 50 focused decision, identity, and transcription tests passed.
All 33 saved transcription edits apply; all 1,347 source rows remain, and
only the approved tag cell changed in this rematerialization. May now has
1,341 post-decision observations from 1,346 tagged inputs. L5/913 assembles
to one May stem (health 7, standing, DBH missing); all other resolved rows
are unchanged. The published pre-May Parquet was not overwritten.

## Approved L6/100 Addition

Riley approved capturing `100-JUN-1-NA-0-std-previously tagged` from page 57 as
a normal Newly Tracked observation. It is now stem 1, genus Juniperus, species
unspecified, DBH missing, health 0, standing true, poison ivy unspecified, and
notes `previously tagged`. The source label `notes-1` identifies the actual
overflow location, not an invented printed N slot.

`config/may_2026_transcription_additions.json` stores this reviewed transcription,
the evidence text, rationale, and source JSON hash. The rematerializer validates
that source, appends the row through the normal portrait row conversion, and
records its provenance as `reviewed_page_note`. Its `source_json` points to the
addition file. The original model JSON, scan, and page note are unchanged.
The run metadata remembers the additions file for later rebuilds; rebuilding
does not duplicate the row. All 1,335 pre-existing rows and their review keys
were compared against the rebuilt run and remained unchanged.

## Approved R4 Recovery, 2026-10-03

Riley approved recovering ten existing-tag observations from page 8's Problems
and Info and lower margin: 5218, 735, 5253, 5250, 5251, 5264, 5246, 5263, 5262,
and 5260. Main row 52's note also supplies a second observation for 5247:
health 4, standing true, poison ivy false, DBH missing. These eleven additions
use the same source-hash-guarded configuration as L6/100, not an untracked CSV
patch. The main 5247 observation remains health 8.

The ten page-note observations have no explicit stem slot, so that field stays
blank. In particular, 5262's one health score does not create two observations
or assert continuity with a historical stem. Species not actually specified
are not borrowed from history: 5253's taxon remains blank; Nyssa and Ilex
notes retain genus-only identification. Unreported standing/poison ivy remain
blank, including 5263's uncertain standing abbreviation. All eleven DBHs
remain missing. The crossed-out note and abbreviated margin numbers are not
additional observations. Riley subsequently approved the 5163/5243 identity
merge on 2026-10-03: one Acer rubrum plant, three recent stems, primary
identity 5163. The alias is recorded in `config/identity.toml` for the unified
decision phase; all transcription rows and original tags remain intact.
The possible 5238 connection was initially left unresolved and subsequently
approved in the accepted-decision section above. See the October requirements
for the current calls and physical-alias field guidance.

R4/5202's checked standing box was saved as an ordinary review decision. The
existing 5235 health-8 decision, R3 taxonomy decisions, and any concurrent user
edits are retained. The materializer now treats literal NA/N/A species updates
as no update without altering free-text notes. This clears 61 spurious R4
species-update flags while preserving the saved model JSON.

Verification compared all 1,336 previous row keys and values: only species
update NA normalization and its associated flag removal changed existing
base rows. The eleven additions have unique keys, all 1,347 rows have geometry,
and note rectangles correspond to the actual prose, not fabricated table
columns. Review UI navigation was checked against the new 5247 stem values.

The reload check also exposed a decision-history rendering bug when batch edits
share a timestamp. History entries now use record identity, and undo includes
the chosen field so undoing one field does not erase another simultaneous
edit on the same row. Existing decision logs were not rewritten.

These changes update the May transcription/review input, not the published
canonical Parquet. Complete note/margin coverage still needs checking across
the other plots before May integration is considered complete. October roster
and seasonal mortality work is tracked in
`docs/october_2026_datasheet_requirements.md`.

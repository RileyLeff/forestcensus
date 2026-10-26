# October 2026 Datasheet Requirements

Agreed with Riley on 2026-10-03 and clarified on 2026-10-04. Publication,
two-survey roster omission, dead/fallen omission, and targeted rechecks are
implemented. Seasonal interpretation of recorded health remains separate.

## Current Packet

`output/datasheets_october_2026/v8/` is the verified roster/layout packet,
ID `5865feed3c3222e1`: 28 per-plot PDFs, 78 pages, 1,279 recording rows for
1,184 trees. The ZIP contains those 28 PDFs only. Directories `v1` through
`v7` are superseded iterations, not the current distribution; v5 retained
too many missing and dead/fallen trees. The main canonical Parquet now includes
May 2026; previous publication files are retained in `output/publication_history/`.

- 1,184 UUIDs remain in the main roster. There is no separate recheck roster.
- 165 UUIDs absent from both October 2025 and May 2026 are omitted, along
  with 31 additional dead/fallen UUIDs. Their canonical histories remain intact.
- Five approved historical split/orphan identities appear in field guidance,
  not as misleading duplicate current-tag rows. All 1,385 canonical UUIDs
  have a disposition in `coverage.csv`.
- The 216-row reduction from v5 consists of 173 rows on the 165 absent
  trees, 38 dead/fallen stem rows (31 whole plants plus seven stems on
  retained plants), and five other rank slots absent from both surveys on
  retained plants. Notes-only/blank placeholders do not become extra stems.
  Each omission is recorded in `exclusions.csv`; `coverage.csv` accounts
  for every canonical UUID.
- 31 targeted questions cover 32 trees: six configured questions plus
  25 unresolved standing/fallen conflicts. Each target is starred in Main;
  each question has two ruled answer lines. `rechecks.json` records the
  UUIDs, printed tags, evidence references, and exact question text.
- Historical size-ranked channels do not assert permanent stem identities.
  Unmeasured recent observations stay eligible for checking rather than being
  rejected using an unrelated small historical rank.
- Full suite: 175 passed. PDF extraction matched every recording row, tag,
  taxon, stem label, DBH reference, and fixed HSP slot to its JSON manifest;
  new input cells were blank. All 78 pages were rendered and visually inspected
  on contact sheets, with full-size H1 and L2 question checks. All 3,323 blank observation and
  feedback checkboxes were verified, with no out-of-page text.
  QA output: `tmp/pdfs/october_v6_QA/report.json`.

The header-only revision (v7) removed the printed bottom-left packet ID
and changes the legend to `hsp = health / standing / poison ivy (only if applicable)`.
The ID remains in the manifest and JSON provenance. Roster, context, questions,
and all 78 page-body renders are unchanged from v6; 37 focused tests passed.
Verification: `tmp/pdfs/october_v7_QA/report.json`. The combined PDF is
`output/pdf/BRNV_October_2026_all_plots_R_H_M_L.pdf`, in R1-R4, H0-H7,
M0-M7, L0-L7 order with per-plot bookmarks.

The final marker revision (v8) adds `+` after recording tags explicitly
referenced in the plot's Field Notes. `*` still identifies an open question;
both appear as `*+` where applicable. The guide alongside the HSP explanation
on every page reads `* = open question below | + = appears in field note`.
The old question-only legend beside Main is removed. There are 36 note-marked
trees, including two with both markers. All 1,279 rows, existing note/question
text, and 78-page pagination are unchanged; 40 focused tests passed.
Each note stores explicit `tags`, and each roster row records its linked
`field_note_numbers`. Matching stays within a plot; measurement/year numbers
are not interpreted as tags, and marker links do not merge tree identities.
Every printed marker and header was checked against its JSON payload.
QA output: `tmp/pdfs/october_v8_QA/report.json`.

The October 4 formatting pass retains 20-point recording rows and provides
12 Newly Tracked slots, one enlarged eight-digit date field per plot, and
Observer / Recorder / Bonus person lines. The heading is October 2026 Survey.
The NA=unknown caption and instruction line below the date are removed.
Field Notes contain plot context only, not instructions or a generic recheck
blurb. Empty note sections are omitted. The corrected finite search list
replaces the earlier blanket recheck list. Two May stem observations recovered
from handwritten parent-row notes and the M5/2479 standing correction are
now published; all 33 saved UI edits and all prior reviewed cells were preserved.

Claude's context-only rewrite was incorporated after checking its factual
claims against the accepted identities. CLI route, configured default resolved
to `claude-opus-5-5`; persistent session
`01f45e50-9920-4d79-8aeb-ca354064120a`. Prompts/results remain outside the repo at
`/tmp/forest-field-notes.QwpbU2/`. Claude drafted prose only; it did not edit
the data or make new identity decisions. Unlinked histories are described as
not yet matched, rather than asserting no matching historical tree exists.

### Historical Header and HSP

- Difficulty is the arithmetic mean of ordinal scores: easy=1, medium=2,
  hard=3, brutal=4, accompanied by the number of rated surveys. Missing ratings
  are excluded; a plot with none prints NA. Identical repeated page ratings
  count once per plot/survey; contradictory ratings stop generation.
- The approved May run's `page_metadata.csv` supplies 18 rated plots; the other
  ten are unrated. The policy explicitly lists these metadata sources, and
  their hashes are part of the packet fingerprint. No rating is inferred from
  missing trees, stem count, or field-note text.
- HSP prints `health/standing`, appending the literal `/p` only when ivy was
  recorded present. False or unreported ivy adds no suffix; unknown health or
  standing still prints NA. An entirely unobserved context slot remains blank.
- The current canonical Parquet omits poison ivy. The packet therefore joins
  this display context from the exact reviewed imports, guarded by their
  published hashes and keyed by survey/source-file/source-row, never tag/rank.
  This is not a new canonical correction phase or a changed presence rule.

## Workflow

1. Finish review of the completed May 2026 survey, including observations in
   page notes, margins, and parent-stem notes, not just extracted table rows.
2. Reconcile handwritten entries with existing UUIDs and accepted tag aliases;
   a "Newly Tracked" section does not prove biological recruitment. Resolve
   uncertain identities with Riley and retain original source evidence.
3. Integrate the reviewed May input through the existing unified decision
   pipeline, verify the result, and publish the updated canonical Parquet.
4. Generate October 2026 sheets with the corrected data and roster rules.
5. Make the requested minor formatting improvements after the data is ready.

## Roster and Delivery Safeguards

- Inclusive minimum DBH: 20 mm for non-Morella cerifera, 50 mm for Morella
  cerifera. Do not discard a qualifying history because later DBH is blank.
- Recent context for October 2026 is October 2025 and May 2026, not the old
  April/October 2025 window. Keep historical columns in the correct order.
- Keep a tree found in either of the last two surveys. DBH, health, or
  standing establishes found, including health 0 and standing false. Notes
  alone and an inferred mortality label do not establish a new sighting.
- Omit a tree absent from both surveys from the next printed search list,
  not from canonical history. A rediscovery under its original tag in Newly
  Tracked reconnects to that UUID and resets the two-survey window.
- Omit dead/fallen rank slots using the latest explicit health and standing
  evidence, without carrying those values into canonical observations.
  Dead standing, unknown standing, and living fallen observations are not
  interchangeable with dead/fallen. Blank standing boxes remain unknown.
  One dead/fallen stem does not remove its live siblings.
- A recent standing report following an older dead/fallen record can be a
  genuine conflict, not automatic evidence to omit the plant. Riley approved
  retaining these with targeted questions. The automatic check uses only
  single-rank histories; it does not claim persistent identities for ranked
  stems, and intervening positive health clears that historical conflict.
- A genuine recheck is a UUID-scoped question on an asterisked Main entry,
  with short supporting context and open answer space. Configured questions
  must resolve to known UUIDs in the stated plot. They cannot silently revive
  an off-roster plant: an explicit `retain_on_roster = true` exception is
  required. This packet needs no such override.
- Show accepted old-tag aliases and catch repeated entries across main rows,
  handwritten additions, and aliases without treating stem rank as identity.
- Publish PDFs, manifest JSON, and ZIP from the same immutable dataset and
  policy version. Verify matching contents; do not leave stale distribution
  files masquerading as the current packet.
- New observation and notes fields stay blank. Historical context must not
  be imported as current measurements.

## Plot-Level Field Notes

Requested by Riley on 2026-10-03 for the October rebuild; layout implemented
and subsequently compacted at Riley's request. Give each plot an area of preprinted bullet
notes containing useful identity and survey context, without instructions. Keep this context
separate from the blank cells where collectors write new observation notes.

- Explain both the primary recording tag and any physical alias tags that
  may still be attached. A database merge does not remove a physical tag;
  otherwise a collector may reasonably re-enter the alias as a new plant.
- For R4, describe 5163 as one red maple with three stems, including the
  ~70 mm stem recorded dead in October 2025 and May 2026, and its earlier
  recorded tags 5243 and 5238. Do not add procedural instructions.
- Beside each bullet provide unmarked Helpful / Confusing / Incorrect
  checkboxes in three right-hand columns. These are independent signals: a
  note may be both helpful and confusing. No response must not be treated as
  a negative rating. The next survey's ingestion adapter must preserve all
  three tracks independently; this PDF pass does not implement that adapter.
- Derive notes from approved decisions and retain the decision reference
  in the sheet manifest so future packets can revise or retire stale advice.
  Unresolved hypotheses must be labeled as uncertain, not printed as facts.
- Verify the roster itself groups aliases into one plant with all its stems;
  a warning bullet alone is not a substitute for fixing duplicate roster
  entries. Test physical-alias guidance and roster grouping together.

## Approved R4 Identity Decision

Riley approved 5243 -> 5163 on 2026-10-03: one Acer rubrum plant, three
recently observed stems, including the dead stem. The two explicit "same
tree as 5163" notes on May scan page 8 support the merge. The larger stem
under 5163 and the two smaller stems under 5243 are distinct observations,
not duplicates to delete.

`config/identity.toml` records the alias from the June 2023 start of 5243's
history, using the existing unified decision phase. Keep the 5163 UUID
(`b1559c5076c63b50`) as the merged identity and preserve original public tags,
source rows, measurements, and notes. Stems remain survey-local ranks, not
permanent identities. The May transcription UI should continue to show the
tags actually written on the scan; the canonical merge is a separate layer.
This merge was subsequently included in the approved May publication.

Riley subsequently approved the complementary 5238 -> 5163 history on
2026-10-03. The June 2023 Acer rubrum observation (316 mm, health 6) now
resolves to the same UUID as 5163 (317 mm in October 2024 and April 2025,
314 mm in October 2025). Preserve 5238 as the historical public tag. This
is a human-approved interpretation, not a claimed explicit archive assertion.

Presence handling is now implemented separately from seasonal inference:
any recorded DBH, health, or standing input establishes found. A found row
with unknown health cannot contribute to an absence run. Conflicting
not-found notes remain visible as review findings. This does not implement
the seasonal retirement policy below.

## Season-Aware Health Interpretation

Riley flagged the H1 May 2026 note on scan page 12. Its model transcription
reads: "nyssa fall sampling creating issues where plants that had not leafed
out were falsely marked dead". The original scan and text are retained in
`output/llm_transcription/may_2026_all_gemini37/`. The awkward "not leafed out"
wording is source wording, not a conclusion about when senescence occurs.

Riley's proposed operational bins:

- Evergreen: conifers, Morella, and Ilex.
- Deciduous: other identified taxa.
- Unknown taxonomy: unresolved, not automatically assigned an informative
  evergreen/deciduous expectation.

For future mortality inference, consider counting informative opportunities
to observe a living canopy, not simply N zero-health records regardless of
taxon and season. Under Riley's proposed policy, evergreen observations can
be informative in both May and October. For deciduous trees, an October
leaflessness-based zero should not combine with one missed spring observation
to declare an otherwise potentially living tree dead. Under the implemented
sheet rule, that fall-zero observation establishes found; one missed spring
therefore leaves the tree eligible. Two zero-health observations alone do
not remove a standing tree.

Keep these distinctions explicit:

- An observed health score of zero, absence of foliage, explicit structural
  evidence of death, and "not found" are not interchangeable evidence.
- Preserve what was actually recorded. Do not silently change historical
  zeroes to positive health or conflate them with a missing observation.
- Distinguish observed health from inferred mortality and from field-roster
  membership. Existing missingness inference counts not-found/unknown surveys;
  existing datasheet selection uses recent direct inputs. Neither should be
  inaccurately described as an implemented N-zero retirement rule.
- Specify whether seasonally uninformative rounds pause or break a consecutive
  run, what explicit death evidence overrides seasonal ambiguity, and which
  sample dates indicate expected foliage before implementing the rule.
- Test a deciduous fall-zero + missed-spring sequence, repeated informative
  spring observations, evergreen observations in both seasons, rediscovery,
  and explicit death evidence. Unknown phenology should remain conservative.

These remain proposals for a separate mortality-interpretation change, not
a new universal taxonomic classification or an already-applied mortality
algorithm. They do not delay the explicit two-absence/dead-fallen sheet rules.

## R4 Observation Limits

- 5262: Riley accepted retaining one May health-5 observation for the
  historically two-stem plant. Do not manufacture a second score or silently
  assert permanent stem continuity. Its previously dead smaller stem is
  historical context, not a new May observation.
- 5263: Riley confirmed "sta" means standing; the reviewed May input now
  has health 7 and standing true, with the original note retained.
- Crossed-out R4 bottom annotation and bare margin numbers remain source
  evidence, not additional observations or automatic retags.

## Final May Calls To Carry Forward

Approved 2026-10-03 and implemented in the unified canonical decision phase:

- Vaccinium is always printed/canonicalized as VACSPP, retaining more specific
  written source text only as evidence.
- M6 primary recording tag 5145 includes the May observation written 5154.
- L2 primary recording tag 816 includes the May observation written 616;
  its blank Main placeholder must not become an additional stem.
- L2 primary recording tag 5380 has two May observations, including the
  write-in under 733 whose note says `same as 5038`. Keep both stems; do not
  repeat 733 as an independent plant or silently print 5038 as the primary.
- These are accepted field-tag interpretations, not proof of physical alias
  tags. Field guidance should ask collectors to confirm the labels while
  preventing repeat entries. Roster generation must group by identity and
  choose primary recording tags deliberately, not blindly use the latest
  `public_tag` from a preserved source observation.
- Exclude M1/5952's unsupported fallen-only write-in. Retain L1/891, L5/786,
  L5/509, and L6/574 with unresolved historical links in field-check context;
  do not label their first recorded appearance as biological recruitment.
- Seven May absence conflicts are now not-found observations, not new
  confirmed dead/standing sightings. Preserve their historical death/fallen
  context when deciding roster membership or a genuine targeted question.
- An unchecked standing box alone remains unknown. Prefer explicit standing
  or fallen evidence and keep uncertainty distinct; specify a clearer field
  convention in the upcoming format rather than retrospectively treating
  every blank as fallen.

The current candidate is `output/october_2026_roster_fixes/forest_census.parquet`;
the same data is published at `output/forest_census.parquet`. It includes
12,266 observations for 1,385 UUIDs, including 1,341 May observations. Primary-tag,
roster, and packaging safeguards are implemented by `field-packet` with
`config/datasheets_october_2026.toml` (policy version `october-2026-v4`).
Operational omission applies to all seasonal bins; canonical observed zeroes
and inferred mortality are not rewritten by the packet generator.

The May follow-up recovered R3/677's second dead-standing stem and H0/274's
third dead-standing stem from their parent-row notes. M5/2479's scan explicitly
says fallen; a guarded decision corrects its standing value to false. See
`docs/may_2026_review_layout.md` for provenance and preservation checks.

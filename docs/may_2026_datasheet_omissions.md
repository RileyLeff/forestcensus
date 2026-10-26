# May 2026 Datasheet Omission Audit

Investigation date: 2026-10-03. Omission findings are an audit, not applied
corrections. No source observations, canonical output, or datasheet-selection
code were changed. During the audit Riley separately approved three R3
taxonomy calls; these were saved through the existing review UI decision
mechanism, as documented below.

**Subsequent R4 review:** ten additional tree observations in page 8's prose
and one extra stem in Main row 52's note were not materialized when this audit
was written. They have since been recovered with Riley's approval; see
`docs/may_2026_review_layout.md`. The counts and hashes below intentionally
describe the original 44-row extracted-addition snapshot, not a complete
inventory of all handwriting. Page-note/margin coverage needs auditing across
the other plots too. The confirmed printed-roster and threshold findings
remain valid.

## Conclusion

The field crew's report is substantiated. Most handwritten additions were
already tagged, not newly qualifying plants. Two distinct mechanisms explain
most omissions:

1. **The printed roster uses the old blanket 50 mm threshold.** Nineteen
   handwritten plot/tag identifiers already had qualifying histories under the
   revised inclusive 20 mm rule for non-Morella cerifera. All nineteen are in
   the newer generated sheets but absent from the printed version.
2. **The two-survey lookback removes previously tagged trees after two rounds
   without DBH, health, or standing input.** Eight handwritten identifiers
   match histories excluded this way, even from the newer sheets. One of
   these, L5/443, has a substantial species/health conflict, so matching the
   tag does not establish matching the biological tree.

There are also alias/duplicate and unresolved identity cases. "Newly Tracked"
is a location on the form, not reliable evidence that a plant is new.

## Scope and Counts

Examined all 44 extracted Newly Tracked rows, including additions below the
main grids and the approved L6/100 overflow observation. These contain 40
distinct nonblank plot/tag identifiers, plus one untagged cancelled entry.
Counts are extraction-level working identifiers, not 40 independently
confirmed biological identities. Crossed-out and repeated entries remain
represented here; they are not automatically treated as real extra stems.

| Explanation | Nonblank plot/tag identifiers | Extracted rows |
| --- | ---: | ---: |
| Old 50 mm roster; included in newer 20 mm roster | 19 | 20 |
| No direct input in either 2025 census | 8 | 8 |
| Unresolved tag/history match | 8 | 8 |
| Plausibly newly tagged plants | 3 | 5 |
| Already on main sheet under same tag | 1 | 1 |
| Already represented under configured replacement tag | 1 | 1 |
| Untagged cancelled entry | 0 | 1 |
| **Total** | **40** | **44** |

The audit uses the saved transcription, not an assumption that its OCR is
fully reviewed. At inspection the only saved UI decision changed R4/5235
health, outside this set. Additional review edits may change particular
identifiers without changing the demonstrated roster-version problem.

## 1. Printed Version Versus Revised Threshold

| Artifact | Stem rows | Tree identities |
| --- | ---: | ---: |
| `output/datasheets_2026_printed_manifest/json/` | 1,292 | 1,198 |
| `output/datasheets_2026/json/` | 1,350 | 1,246 |

The revised sheets add 58 stem rows across 48 additional trees. The nineteen
write-in identifiers below are a subset of those additions.

Verification:

- All 28 printed-manifest JSON files equal the JSON files in
  `output/BRNV_May_2026_datasheets_package.zip`.
- The ZIP's L6 PDF is byte-identical to
  `output/BRNV_May_2026_per_plot_pdfs/BRNV_L6.pdf`, but differs from
  `output/datasheets_2026/pdf/BRNV_L6.pdf`.
- An in-memory simulation using the current canonical snapshot, a blanket
  inclusive 50 mm threshold, the assembly whole-tree eligibility filter, and
  normal datasheet preparation reproduces **all 1,292 printed row dictionaries
  exactly**, not merely their count or tags. Nothing was regenerated on disk.
- The original package dates to May 11; the newer per-plot manifests date to
  May 12. File dates support the version distinction but do not establish
  when the crew printed a packet or who distributed it.

The generation function `write_plot_datasheets` writes JSON, Typst, per-plot
PDFs, a combined PDF, and summaries. It does **not** rebuild the separate ZIP
or the external per-plot PDF copy directory. Those distribution artifacts
can therefore remain stale after a threshold update.

Historical maxima below are from the current corrected canonical snapshot.
They explain the threshold outcome; they are not proposed replacement May
2026 measurements. Historical taxonomy is not a new species decision.

| Plot/tag | Scan page/slot | Historical taxon | Maximum DBH, mm | Relevant earlier evidence |
| --- | --- | --- | ---: | --- |
| R2/933 | 4/N1 and N3 | VACSPP | 29 | April 2025: 20; October: 28. One May entry is incomplete/cancelled. |
| R2/980 | 4/N2 | ILEOPA | 47 | Both 2025 rounds: 46. May OCR reads 4.7; handwriting appears 47, still for review. |
| R3/687 | 6/N1 | VACSPP | 43 | April: 42, health 7; October: health 8, standing. |
| R3/682 | 6/N2 | NYSSYL | 37 | April: 33, health 0; October: health 0, standing. Riley confirmed leaving this as Nyssa. |
| R3/665 | 6/N3 | VACSPP | 37 | April: two stems, 35 and 27; both health 0. |
| R3/650 | 6/N4 | VACSPP | 29 | April: 29, health 0; October: health 0, standing. |
| H0/277 | 10/N1 | NYSSYL | 45 | April: 28, health 0; October: health 0, standing. |
| H1/5142 | 12/N1 | PINTAE | 31 | April: 28; October: 31. May explicitly says tagged previous year. |
| H4/110 | 18/N1 | ILEOPA | 36 | Both 2025 rounds: 26. May says tagged last year. |
| H4/109 | 18/N2 | ILEOPA | 31 | Both 2025 rounds: 22. May says tagged last year. |
| H5/551 | 19/26, handwritten | ILEOPA | 42 | April: 33; October: 42. |
| H6/451 | 21/N1 | NYSSYL | 34 | April: 34; October: 31. May note says VACCOR; separate taxonomy issue. |
| H6/5307 | 21/N2 | PINTAE | 25 | October 2024: 20; April 2025: 21; October: 25. |
| H6/5381 | 21/N3 | ILEOPA | 22 | April: 22, newly tagged; October: 21. |
| H7/882 | 23/N1 | JUNVIR | 45 | April: 31, health 0; October: health 0, standing. |
| M1/875 | 28/N1 | NYSSYL | 49 | April: 39; October: 41. |
| L6/82 | 57/N3 | JUNVIR | 44 | Health 0 and standing recorded in both 2025 rounds. |
| L6/81 | 57/N4 | JUNVIR | 38.5 | April: health 0, standing; October: health 8. Health conflict is not the omission cause. |
| L6/100 | 57/notes-1 | JUNVIR | 46 | Health 0 and standing recorded in both 2025 rounds. |

These are not nineteen plants that first crossed the revised threshold in
May 2026: they already passed it historically.

## 2. Two-Survey Exclusions

`build_datasheet_prep` defaults to April and October 2025. Its found test is:

```python
dbh_mm.notna() | health_observed.notna() | standing_observed.notna()
```

Health zero and standing false count as found. This is **not** a truthiness
bug that drops dead or fallen trees. Conversely, a missing October row and
an October row with all three inputs blank both fail the test. April blanks
were checked against accepted input evidence, and October rows against the
reviewed transcription evidence where present.

| Plot/tag | May page/slot | Last direct recorded input | Why excluded / caution |
| --- | --- | --- | --- |
| H7/903 | 23/N2 | October 2024: health 0, fallen | April has "girdle couldn't find" with inputs blank; no October row. No DBH history to establish size independently. |
| M1/829 | 28/N2 | October 2024: health 0, fallen | April inputs blank; no October row. May only says "(fallen)"; not a new measured stem. |
| M6/505 | 38/N1 | October 2024: 71/55 mm, health 7, standing | Both April stems not found; two fully blank October records. This is the clearest formerly live, qualifying-tree example. |
| L1/137 | 44/N1 | October 2024: health 0, fallen | April not found; no October row. Historical maximum 408 mm. |
| L2/216 | 46/N1 | October 2024: fallen | April inputs blank; no October row. Historical maximum 314.5 mm. |
| L5/443 | 52/N1 | October 2024: health 0, standing | April not found; October inputs blank. Historical tree is a dead pine, maximum 420 mm; May says Juniperus, health 7. **Identity unresolved.** |
| L5/985 | 52/N3 | May 2024: standing | October 2024 inputs blank, April 2025 not found, no October 2025 row. No DBH history. |
| L6/74 | 57/N2 | October 2024: pine, 397 mm, health 0, standing | April not found; October inputs blank. Use the pine identity, not the older split juniper. |

Useful source locators: `data/raw/forest_census/2025_spring.csv` rows 967,
1157, 1339/1352, 92, 146, 338, 342, and 387 respectively. The October blank
entries for M6/505, L5/443, and L6/74 are rows 867/868, 1248, and 1296 in
`output/llm_transcription/oct_2025_reviewed/import_recent_format_reviewed.csv`.
These are source locators, not new correction selectors.

The implementation follows the agreed recent-found rule. The operational
problem is using that rule to remove an existing tag from the next search
roster entirely. An unlocated tree can then be absent from the next form,
making another missed observation more likely. Mortality inference does not
itself decide whether field workers should still have its tag on their list.

## 3. Already Represented on the Main Sheet

| Write-in | Existing main entry | Interpretation |
| --- | --- | --- |
| L6/88, page 57/N5 | Printed L6 row 38, scan page 53/row 38 | Same tag and Juniperus; main and write-in both have health 0, standing. Candidate duplicate, **not an omitted tag**. Do not invent an extra stem or delete without review. |
| L6/57, page 57/N6 | Printed L6 row 64, tag 991; scan page 55/row 24 | Configured 57-to-991 alias since 2023 in `config/identity.toml`. Both records have health 0, standing. Old tag was not displayed as an alias, making field recognition harder. Confirm identity before merging. |

## 4. Unresolved Historical Tags

These eight extracted plot/tag combinations have no same-plot match in the
current canonical snapshot or adapted uncorrected inputs. Searches of the
59,762-row evidence ledger also considered public tags, old tags, tree codes,
and explicit numeric mentions in notes. A matching number in a different plot
does not establish a link. Missing archive evidence is not proof of a new
plant.

| Plot/tag | Page/slot | May evidence | Next question |
| --- | --- | --- | --- |
| M1/5952 | 28/N3 | "(fallen)", other inputs blank | Is the handwritten tag correct, and is there an unrecorded old alias? |
| M6/5154 | 38/N2 | Health 0; "dead standing, previously tagged" | M6/5145 is a plausible digit transposition: Juniperus, historical 40 mm, April 2025 dead standing, absent October. It was also excluded by the old threshold. **Candidate only.** |
| L1/891 | 44/N2 | Morella, health 0, standing; previously tagged | No same-plot history. H7/891 is not a justified substitute. |
| L2/616 | 46/N2 | Morella, health 0, standing; previously tagged | No same-plot history. R2/616 is not a justified substitute. |
| L2/733 | 46/N3 | Morella, health 3; "double stem, same as 5038" | Neither L2/733 nor L2/5038 has matching history. There is an L7/5038 history, but that alone does not justify a cross-plot merge. |
| L5/786 | 52/N2 | Juniperus, health 0, standing; previously tagged | Inspect old tag/handwriting evidence; nearby numbers alone are insufficient. |
| L5/509 | 52/N4 | Morella, standing; "0 - previously tagged" | Review the tag and whether the overflow note supplies health 0. No automatic edit. |
| L6/574 | 57/N1 | Morella, health 8, standing; previously tagged | No matching same-plot history; do not force onto a similar number. |

## 5. Plausibly New Entries and Cancelled Slots

| Working identifier | Page/slots | Evidence | Interpretation |
| --- | --- | --- | --- |
| M2/1264 in OCR; appears 1204 on scan | 30/N2 | Morella, 50 mm, health 6, standing | No archived match for either number. Compatible with entering at the inclusive 50 mm boundary; prior growth across it is not demonstrated. Review tag first. |
| M4/1205 | 34/N1 | 62 mm, health 8, standing | Newly tagged candidate. OCR species suffix is `lbr`; handwriting appears MORCER. No archived identity found; cannot distinguish recruitment from a previously overlooked plant. |
| M5/1201 | 36/N1-N3 | 62 and 58 mm; health 3 and 8; another crossed-out/incomplete entry | Likely one newly tagged two-stem plant, not three plants. Confirm cancelled-slot handling. |
| M2/no tag | 30/N1 | Crossed-out Juniperus entry, no measurements | Incomplete/cancelled slot, not evidence for another omitted tree. |

## Recommended Changes, Not Yet Applied

1. **Package from one immutable roster version.** Build PDFs, JSON manifests,
   the per-plot ZIP, and summaries together; include threshold policy and
   input/version hashes. Verify all packaged rosters match. Do not leave a
   separately named old packet looking current after regenerating sheets.
2. **Separate search-roster membership from recent-found status.** Keep the
   recent-found main list, but retain previously tagged candidates in an
   explicit "previously tagged / recheck" section or roster. Decide retirement
   deliberately instead of making two blanks silently erase a tag. Agree
   how to handle dead/fallen trees and trees with no DBH evidence before
   reinstating anything in bulk.
3. **Print accepted old-tag aliases next to the current tag.** Flag a write-in
   matching a main entry or its alias for review before adding a new stem.
4. **Keep new, rediscovered, and uncertain-identity entries distinct.** Their
   form section alone must not create new biological identities or imply a
   threshold-crossing date. Preserve per-case provenance and manual calls.
5. **Retain all observations, even when excluding them from a field roster.**
   Analytical size eligibility, stem counts, inferred mortality, and operational
   retirement are different decisions. Avoid treating rank as permanent stem
   identity when reasoning about missing or reappearing branches.

## Concurrent Review Notes

Riley clarified that R3/687, R3/665, and R3/650 should be VACSPP, while R3/682
stays Nyssa. Four field edits were saved through the review server's normal
`decideBatch` action: species suffix `spp` for the three Vaccinium entries,
and genus `Vac` instead of `Va` for 650. They are appended, with rationale,
to the active run's `review_decisions.jsonl`. Existing decisions were
preserved. No decision was added for 682, and raw transcription and canonical
data remain unchanged. The review view will apply these decisions on reload.

Riley also confirmed that handwritten "NA" should be missing, not zero. All
four R3 write-ins retain blank DBH; health values were not altered by the
taxonomy decisions.

## Reproducibility and Inputs

Primary code: `src/forestcensus/datasheets.py` (`build_datasheet_prep`,
`_filter_nonqualifying_active_stems`, `write_plot_datasheets`),
`src/forestcensus/assembly.py` (`_is_nonqualifying_below_threshold_tree`),
and `src/forestcensus/domain.py` (`passes_size_filter`).

The exact roster comparison can be reproduced without writing outputs:

```python
import json
from pathlib import Path
from unittest.mock import patch
import pandas as pd
from forestcensus import domain
from forestcensus.assembly import _is_nonqualifying_below_threshold_tree
from forestcensus.datasheets import build_datasheet_prep, build_plot_datasheets

census = pd.read_parquet("output/forest_census.parquet")
with patch.object(domain, "NON_MORELLA_CERIFERA_MIN_DBH_MM", 50):
    excluded = {
        uid for uid, rows in census.groupby("tree_uid")
        if _is_nonqualifying_below_threshold_tree(rows)
    }
    prep = build_datasheet_prep(census.loc[~census.tree_uid.isin(excluded)])
    rebuilt = build_plot_datasheets(prep["active_stems_found_last2"])
for path in Path("output/datasheets_2026_printed_manifest/json").glob("*.json"):
    plot = path.stem.removeprefix("BRNV_")
    assert rebuilt[plot]["rows"] == json.loads(path.read_text())["rows"]
```

Snapshot SHA-256 values:

| Input | SHA-256 |
| --- | --- |
| `output/forest_census.parquet` | `1c8cbd9cf4827732dd0a4a9738a1fc90e7ff66b7dd5320f36a98a71cc35c7f73` |
| `output/llm_transcription/may_2026_all_gemini37_printed_manifest/transcription.csv` | `5c7533fa7111e970321036191c465e09438d8cc36e2286768348b1bd94e64a32` |
| `output/BRNV_May_2026_datasheets_package.zip` | `4640c759cc2655b4c9608d87fe49a91626a39f8d5aa1991309f714ed3604f527` |

Other evidence: `output/evidence/evidence_observations.parquet`, raw historical
adapter output from configured sources, original May model JSON and page PNGs
under `output/llm_transcription/may_2026_all_gemini37/`, and the preserved
printed/revised JSON manifests. No live materialization or UI restart was
needed for this audit.

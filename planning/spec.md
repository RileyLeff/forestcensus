File: planning/spec.md

Title: forcen specification (single source of truth)

Core definitions and invariants
Tree: a conceptual organism observed over time. No stored first_seen/last_seen. Properties (genus, species, code, site, plot) are determined “as-of” a date from UPDATE commands.
Stem: not tracked individually. Within a survey, stems are unranked in storage; any ranking is computed on demand by dbh descending, ties broken by health descending, then input order.
Survey: a dated window (start, end) with an ordered id. Windows are non-overlapping and ordered in surveys.toml.
Alive at tree level (in a survey): any stem with health > 0.
Zombie at tree level (ever): the tree is observed dead (alive=false) in some survey t and later observed alive (alive=true) in a survey u > t. Implied rows do not create zombies if later removed by rediscovery.
Datasheet inclusion for target survey S_next: include a tree only if it has real observations in S_next-1 or S_next-2 (the previous two surveys). Implied rows do not count as presence.
Implied dead: if absent for two consecutive surveys Sk and Sk+1, insert one synthetic row at Sk with health=0, standing=false, dbh_mm=NA, origin="implied". If later rediscovered after Sk, remove that implied row on rebuild. If a later ≥2 gap occurs, insert a new implied row at the first missing survey of that later gap.
Aliases are time-aware bindings from (site, plot, tag) to a tree identity. A tag cannot bind to two trees for the same instant. Public name (display tag) is designated by PRIMARY and is time-aware.
Idempotency: applying the same DSL lines or submitting the same transaction twice has no effect; rebuild from ledger reproduces identical artifacts and manifest.
2. Storage model (persisted files and schemas)

observations.parquet (and observations.csv mirror)
Purpose: append-only storage of raw/normalized rows accepted via transactions. Tree resolution is deferred to assembly.
Columns:
obs_id: string UUID
survey_id: string (must exist in surveys.toml)
date: YYYY-MM-DD (must lie within survey window)
site: string (from sites.toml)
plot: string (explicit list in sites.toml)
tag: string (field tag recorded on sheet)
dbh_mm: integer ≥ 0, or NA only when origin == "implied"
health: integer in [0..10] or NA
standing: boolean or NA
notes: string (free text, may be empty)
origin: string in {"field","ai","implied"}
source_tx: string (transaction id that contributed this row)
Not stored: tree_uid, stem ids, ranks, derived flags.
updates_log.tdl
Purpose: append-only concatenation of accepted metadata DSL lines in acceptance order. This is the only source of alias and property updates.
Lines must conform to DSL (section 4). Idempotent operations are allowed to repeat.
trees_index.jsonl
Purpose: append-only existence index of tree identities created implicitly or explicitly.
Fields per line:
tree_uid: string UUID
created_by_tx: string
note: optional string
transactions.jsonl
Purpose: append-only ledger of accepted transactions.
Fields per line (minimum):
tx_id: string (SHA256 of normalized tx files)
accepted_at: ISO timestamp (UTC)
code_version: string (e.g., git commit or semver)
config_hashes: map of filename → SHA256
input_checksums: map of tx file → SHA256
rows_added: integer
dsl_lines_added: integer
validation_summary: {errors: int, warnings: int}
3. Configuration (TOML files)

taxonomy.toml
species: array of tables [{genus, species, code}]
genus: string (e.g., "Pinus")
species: string (e.g., "taeda")
code: string (e.g., "PINTAE") must equal upper(genus[0:3] + species[0:3]).
enforce_no_synonyms: boolean (true)
sites.toml
[sites.<SITE>]
zone_order: array of zone names in ascending order (e.g., ["Low Forest","Mid Forest","High Forest","Reference Forest"])
plots: explicit array of plot codes (e.g., ["H0","H1",...,"R4"])
girdling: table mapping plot → YYYY-MM-DD (optional)
surveys.toml
surveys: array of tables [{id, start, end}]
id: string (ordered label, unique)
start, end: YYYY-MM-DD (inclusive)
Constraints: non-overlapping, strictly increasing by start date.
validation.toml
rounding: "half_up"
dbh_pct_warn: float (0.08)
dbh_pct_error: float (0.16)
dbh_abs_floor_warn_mm: int (3)
dbh_abs_floor_error_mm: int (6)
retag_delta_pct: float (0.10)
new_tree_flag_min_dbh_mm: int (60)
drop_after_absent_surveys: int (2)
datasheets.toml
show_previous_surveys: int (2)
sort: string ("public_tag_numeric_asc")
show_zombie_asterisk: boolean (true)
Loading rules
All TOML files are required except ai-related config (optional).
Fail closed on missing keys, wrong types, or invalid constraints.
4. Metadata DSL (only three verbs)

Tokens/refs
site/plot/tag: e.g., BRNV/H4/112
date: YYYY-MM-DD
tree_ref: tree_uid (UUID) or site/plot/tag@date (date disambiguates historical alias states). If @date omitted and a bare PRIMARY tag is used, resolve “as of now” during submit (discouraged for reproducibility; allowed for convenience).
Common clauses
EFFECTIVE <date>: change takes effect from this date forward (as-of semantics).
PRIMARY: marks the public/display tag for the tree from EFFECTIVE forward (until overridden).
NOTE "...": free text.
Commands
ALIAS <site>/<plot>/<tag> TO <tree_ref> [PRIMARY] [EFFECTIVE <date>] [NOTE "..."]
Binds or rebinds a tag to a tree identity from EFFECTIVE forward.
Overlapping bindings for the same tag across time are invalid.
PRIMARY sets the public name from EFFECTIVE forward.
Idempotent: reapplying the same binding is a no-op.
UPDATE <tree_ref> SET [genus=...], [species=...], [code=...], [site=...], [plot=...] [EFFECTIVE <date>] [NOTE "..."]
Changes properties of a tree from EFFECTIVE forward.
Last-writer-wins per field at a given date.
Moving site/plot is allowed but rare; warn loudly.
SPLIT <tree_ref> INTO <site>/<plot>/<new_tag> [PRIMARY] [EFFECTIVE <date>] [SELECT <selector>] [NOTE "..."]
Forward-only if SELECT omitted.
With SELECT, reassigns historical rows from source to the new target tree based on selection:
Selector grammar (combinable):
ALL | LARGEST | SMALLEST | RANKS n[,m...]
BEFORE <date> | AFTER <date> | BETWEEN <date> AND <date>
Ranks for selection are computed per survey on demand (dbh desc; tie-break health desc; then input order).
Idempotent: once rows move, selector finds nothing further on reapplication.
Conflicts and uniqueness
For any (site, plot, tag), alias bindings must not overlap in time; reject the DSL file if detected.
At any instant, each tree has at most one PRIMARY tag; newest PRIMARY at or before the instant wins; warn if PRIMARY flips often.
Examples
ALIAS BRNV/H4/508 TO BRNV/H4/112 PRIMARY EFFECTIVE 2020-06-15 NOTE "Retag"
UPDATE BRNV/H4/112 SET genus=Pinus, species=taeda, code=PINTAE EFFECTIVE 2021-06-15
SPLIT BRNV/H4/112 INTO BRNV/H4/900 PRIMARY EFFECTIVE 2020-06-15 SELECT LARGEST BEFORE 2020-01-01 NOTE "Largest was separate"
SPLIT BRNV/H4/112 INTO BRNV/H4/901 EFFECTIVE 2020-06-15 SELECT RANKS 2,3 BETWEEN 2019-01-01 AND 2019-12-31
5. Transactions

Layout (directory)
survey_meta.toml
survey_id: string (must exist in surveys.toml or define here with start/end)
sites: array of sites included in this tx
plots: array of plots included in this tx
Optional: new survey declaration {id, start, end} if introducing a new survey
updates.tdl (optional)
measurements.csv (required)
Required headers: site, plot, tag, date, dbh_mm, health, standing, notes
Optional headers: genus, species (allowed for new trees; must match taxonomy if provided)
attachments/ (optional; used by ai prepare scaffold)
tx_id
SHA256 over normalized contents (UTF-8, LF line endings, trimmed trailing whitespace, deterministic key ordering when serializing TOML).
Processing order
Parse updates.tdl → apply on a dry “as-of” state
Load and normalize measurements.csv
Validate row-level → alias/update constraints → per-tree across surveys → dataset-level
Assemble with the new tx applied → final validation pass
Accept or reject atomically
Acceptance effects (on accept)
Append updates to updates_log.tdl
Append rows to observations.(parquet/csv)
Add any new tree_uids to trees_index.jsonl
Append entry to transactions.jsonl
Write new version artifacts under versions/<seq> (manifest + outputs)
Rejection
Write a tx report with:
errors: list of {code, message, location}, where location is "measurements.csv:row X,col Y" or "updates.tdl:line Z"
warnings: list of {code, message, location}
retag_suggestions: list of suggested ALIAS lines with rationale
No files are modified
6. Normalization (applied to measurements.csv rows before validation)

Health
Coerce to numeric; round half-up to integer; clamp to [0..10]; reject if not coercible.
Legacy alive override
If alive column exists and alive==TRUE and health==0, set health=1; record normalization="alive_override" in the validator report (not stored).
Standing
Coerce to {true,false,NA}; reject any other tokens.
Taxonomy
If genus/species provided, must match an entry in taxonomy.toml; code must equal upper(genus[0:3] + species[0:3]).
For existing trees, raw rows cannot change genus/species/code without an UPDATE; otherwise reject.
For new trees, genus/species may be omitted or set to a placeholder allowed in taxonomy.
Dates
date must lie within survey_id start/end; otherwise reject (or accept only if survey_meta declares this survey with matching dates).
7. Validation (rules and error codes)

Row-level
E_ROW_DBH_NEG: dbh_mm < 0
E_ROW_DBH_NA_NOT_IMPLIED: dbh_mm is NA but origin != "implied"
E_ROW_HEALTH_RANGE: health not in [0..10] (after normalization)
E_ROW_STANDING_TOKEN: standing not in {true,false,NA}
E_ROW_DATE_OUTSIDE_SURVEY: date outside survey window
E_ROW_SITE_OR_PLOT_UNKNOWN: site/plot not in sites.toml
E_ROW_TAXONOMY_MISMATCH: code != upper(gen[0:3]+spp[0:3]) or unknown species
Alias and updates
E_ALIAS_OVERLAP: same site/plot/tag bound to different trees over overlapping intervals
E_PRIMARY_DUPLICATE_AT_DATE: more than one PRIMARY for a tree at a given instant
W_PRIMARY_FLIP: frequent PRIMARY changes for a tree (warning)
Per-tree across surveys
W_DBH_GROWTH_WARN: abs(d1-d0)/max(d0,d1) > dbh_pct_warn and abs change ≥ dbh_abs_floor_warn_mm (computed on max dbh between adjacent surveys where tree is present)
E_DBH_GROWTH_ERROR: abs(d1-d0)/max(d0,d1) > dbh_pct_error and abs change ≥ dbh_abs_floor_error_mm
E_SPECIES_CHANGED_WITHOUT_UPDATE: observed genus/species/code diverges from update-derived metadata
Implied dead
Implement as assembly rule (no row-level checks needed), but ensure implied rows never count for presence
Retag candidates (warning-only output)
For survey S: Lost = trees in S-1 not present in S; New = first-seen trees in S with max dbh ≥ new_tree_flag_min_dbh_mm
If |dbh_lost - dbh_new| ≤ retag_delta_pct × max(dbh_lost, dbh_new) and same plot, emit suggestion
Dataset-level
E_SURVEYS_OVERLAP: overlapping survey windows
E_CONFIG_INVALID: invalid/missing config key (reported during config load)
8. Assembly (per-tree algorithm; pure and deterministic)

Inputs: observations.*, updates_log.tdl, config TOMLs, survey order, accepted transactions
Steps per tree_uid
Resolve aliases “as-of” for each date; build the mapping from tags to tree_uids over time
Resolve properties via UPDATE “as-of” (genus, species, code, site, plot, public name via PRIMARY)
Apply SPLIT retroactive selectors:
For each survey in selector window: compute ranks (dbh desc; tie-break as defined) and move matched rows to the new tree_uid
Forward-only SPLIT (no SELECT) creates a new identity from EFFECTIVE forward (future measurements with the new tag should map there)
Build presence vector across ordered surveys (real observations only)
Insert implied dead:
Find gaps where there are two consecutive absences at Sk and Sk+1; insert a synthetic row at Sk with health=0, standing=false, dbh=NA, origin="implied"
If any later real observation exists after Sk, remove the implied row at Sk
Compute alive per survey: any health>0 on that survey
Compute zombie_ever: exists t with alive=false and a later u with alive=true (ignore implied rows removed by rediscovery)
Produce per-survey stem “views” for display by sorting stems by dbh desc with tie-breaks; ranks are not stored
Dataset fold
Concatenate all per-tree outputs; run final validators; sort outputs deterministically (by site, plot, public tag, survey, dbh desc, obs_id) before writing
9. CLI contract (commands, arguments, exit codes)

forcen ai prepare <pdf-or-dir> --out <dir>
Purpose: scaffold; produce draft measurements.csv and updates.tdl from scanned sheets; never auto-submit
Exit codes: 0 success; 4 IO error
forcen tx new --out <dir>
Purpose: scaffold a transaction folder with empty updates.tdl and a measurements.csv header
Exit codes: 0 success; 4 IO error
forcen tx lint <txdir>
Purpose: parse DSL, normalize measurements, dry-run assembly/validation; no writes
Output: JSON report to stdout and a report file in <txdir>/lint-report.json
Exit codes: 0 clean (warnings allowed); 2 validation error; 3 DSL parse error; 4 IO error; 5 config error
forcen tx submit <txdir>
Purpose: full pipeline; accept or reject atomically
Effects on accept: append updates, append observations, update trees_index and transactions.jsonl, write a new version
Exit codes: 0 accepted; 2 validation error; 3 DSL parse error; 4 IO error; 5 config error
forcen build
Purpose: rebuild latest version from ledger and config; useful after code or config changes
Exit codes: 0 success; 5 config error; 4 IO error
forcen datasheets generate --survey <id> --site <site> --plot <plot> --out <dir>
Purpose: produce context JSON; optionally call Typst if installed
Exit codes: 0 success; 4 IO error; 5 config error
forcen versions list|show <seq>|diff <seqA> <seqB>
Purpose: inspect manifests and differences between versions
Exit codes: 0 success; 4 IO error
10. Outputs and manifest (versions/<seq>/)

Artifacts
observations_long.parquet and observations_long.csv (post-updates/splits; includes origin and source_tx)
trees_view.csv (per survey: tree_uid, public tag, genus, species, code, site, plot)
retag_suggestions.csv (survey_id, plot, lost_tree_uid, lost_public_tag, lost_max_dbh_mm, new_tree_uid, new_public_tag, new_max_dbh_mm, delta_mm, delta_pct, suggested_alias_line)
updates_log.tdl (concatenated accepted DSL)
validation_report.json (summary of warnings/errors for this version)
manifest.json
manifest.json fields (minimum)
version_seq: integer (monotonic)
created_at: ISO timestamp (UTC)
code_version: string
config_hashes: map file → SHA256
tx_ids: array of tx ids included since previous version
input_checksums: map of source paths → SHA256 (for tx files)
artifact_checksums: map of artifact file → SHA256
row_counts: {total, by_origin: {field, ai, implied}}
validation_summary: {errors: int, warnings: int}
Deterministic writes
Write to a temp directory; fsync; atomic rename to versions/<seq>
11. Datasheets scaffold (context contract)

Selection
For target survey S_next: include trees with real observations in S_next-1 or S_next-2; exclude others
Sorting/grouping
Group by tree (public tag as of S_next), sort groups by numeric public tag ascending; within a group, order stems by dbh desc with display-only ranks 1..n
Columns per row
id: site/plot/public-tag.rank
dbh, health, standing, notes
DHS1 and DHS2: strings “dbh/health/standing” from S_next-1 and S_next-2 for that tree; append “*” if tree_zombie_ever
Context JSON (written alongside, consumed by Typst)
survey_id, site, plot
tags_used: array of tag strings already used in that plot
trees: array of { tree_uid, public_tag, zombie_ever: bool, stems_next: [{rank, dbh_mm, health, standing, notes}], dhs1: [{rank, dbh_mm, health, standing}], dhs1_marked: bool, dhs2: [{rank, dbh_mm, health, standing}], dhs2_marked: bool }
12. AI prepare scaffold

Input: PDFs (datasheets), optional model settings
Output: draft measurements.csv (with required headers), draft updates.tdl, saved under a staging directory; never touches accepted storage
Behavior:
May call an external API (Gemini 2.5 Flash) to extract rows; or run in “mock” mode and just write headers
Always validate drafts locally (basic schema) and warn on obvious issues
Human-in-the-loop: the user must review/edit before tx lint/submit
13. Glossary

Alias: a time-aware mapping from (site, plot, tag) to a tree identity
Public name: the display tag for a tree at a date, designated by PRIMARY
Implied row: a synthetic observation inserted at the first missing survey after two consecutive absences (health=0, standing=false, dbh=NA, origin="implied")
Zombie: tree-level status; dead at some survey and later alive at a later survey
SPLIT selector: a rule describing which historical rows move to a new tree during a split (ALL, LARGEST, SMALLEST, RANKS, with optional date windows)
Retag candidate: a potential alias correction suggested by similar dbh between a lost tree and a new tree in the same plot
14. Non-goals (for this phase)

No persistent stem identifiers
No smoothing/interpolation beyond the implied-dead rule
No database server; flat files only
No salinity or other datasets
No web UI
15. Notes on extensibility

SQLite-backed ledger: the ledger/alias abstraction permits moving transactions.jsonl and updates_log.tdl into SQLite later for concurrency/ACID without changing CLI contracts.
Multiple sites: sites.toml already supports multiple [sites.<SITE>] tables.
Additional validators: add in validate/ with error codes; keep fail-closed behavior.
More DSL verbs: avoid unless indispensable; prefer expressing operations in ALIAS/UPDATE/SPLIT.
End of spec.md.
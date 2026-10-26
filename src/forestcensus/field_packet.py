"""Identity-based field rosters and immutable, audited PDF packets."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pandas as pd

from .datasheets import (
    _clean_stem,
    _clean_tag,
    _dhs_for_survey,
    _hsp_for_survey,
    _latest_dbh_by_stem,
    _natural_key,
    _typst_with_data_path,
    build_plot_datasheets,
)
from .domain import passes_size_filter
from .publish import _sha256


def _attach_poison_ivy_context(census: pd.DataFrame, sources: dict[str, str], manifest: dict) -> pd.DataFrame:
    """Recover omitted context by immutable source coordinates, never by tag/rank."""
    result = census.copy()
    if "poison_ivy_observed" not in result:
        result["poison_ivy_observed"] = pd.Series(pd.NA, index=result.index, dtype="boolean")
    for survey, name in sources.items():
        path = Path(name)
        if _sha256(path) != manifest.get("inputs", {}).get(str(path)):
            raise ValueError(f"HSP source differs from the published canonical input: {path}")
        source = pd.read_csv(path, dtype=str, keep_default_na=False)
        if not source.survey_id.eq(survey).all():
            raise ValueError(f"HSP source contains a different survey: {path}")
        values = source.poison_ivy.str.strip().str.lower()
        allowed = {"": pd.NA, "na": pd.NA, "true": True, "1": True, "1.0": True,
                   "false": False, "0": False, "0.0": False}
        if not values.isin(allowed).all():
            raise ValueError(f"Unrecognized poison ivy value in {path}")
        lookup = pd.Series(values.map(allowed).array, index=source.index + 2, dtype="boolean")
        mask = result.survey_id.eq(survey)
        if not result.loc[mask, "source_file"].eq(path.name).all() or not result.loc[mask, "source_row"].isin(lookup.index).all():
            raise ValueError(f"Canonical HSP source coordinates do not match {path}")
        context = result.loc[mask, "source_row"].map(lookup)
        existing = result.loc[mask, "poison_ivy_observed"]
        if (existing.notna() & context.notna() & existing.ne(context)).any():
            raise ValueError(f"Poison ivy context conflicts with canonical data: {path}")
        result.loc[mask, "poison_ivy_observed"] = existing.combine_first(context)
    return result


def _historical_difficulty(metadata: pd.DataFrame) -> dict[str, dict]:
    """Average the ordinal scale once per plot/survey, not per repeated page."""
    if metadata.empty:
        return {}
    ratings = metadata.loc[metadata.difficulty.str.strip().ne("")].copy()
    ratings["score"] = ratings.difficulty.str.strip().str.lower().map({"easy": 1, "medium": 2, "hard": 3, "brutal": 4})
    if ratings.score.isna().any() or ratings["plot"].eq("").any() or ratings.survey_id.eq("").any():
        raise ValueError("Difficulty ratings require a known category, plot, and survey")
    if ratings.groupby(["plot", "survey_id"]).score.nunique().gt(1).any():
        raise ValueError("Conflicting difficulty ratings for the same plot/survey")
    ratings = ratings.drop_duplicates(["plot", "survey_id"])
    return {str(plot): {"mean": float(group.score.mean()), "count": len(group)}
            for plot, group in ratings.groupby("plot")}


def _dead_fallen_context(channel: pd.DataFrame) -> bool:
    """Use the latest explicit health and standing evidence, not inferred death.

    This selects a printed rank slot; it does not assert permanent stem identity
    or write a carried-forward measurement into the canonical observations.
    """
    health = channel.loc[channel.health_observed.notna()]
    standing = channel.loc[channel.standing_observed.notna()]
    return (not health.empty and not standing.empty and
            health.iloc[-1].health_observed == 0 and standing.iloc[-1].standing_observed == False)


def _standing_conflict_question(tree: pd.DataFrame, record: dict) -> dict | None:
    # Rank changes cannot establish that a physical stem got back up. Limit this
    # check to one-rank histories and clear any old conflict after live evidence.
    if tree._stem.nunique() != 1:
        return None
    observed = tree.loc[tree._found_signal]
    fallen = observed.loc[observed.health_observed.eq(0) & observed.standing_observed.eq(False)]
    standing = observed.loc[observed.standing_observed.notna()]
    if fallen.empty or standing.empty or standing.iloc[-1].standing_observed != True:
        return None
    earlier = fallen.iloc[-1]
    later = standing.iloc[-1]
    if later.date <= earlier.date or observed.loc[observed.date.gt(earlier.date), "health_observed"].gt(0).any():
        return None
    return dict(id=f"standing-conflict-{record['tree_uid']}", plot=record["plot"],
                tree_uids=[record["tree_uid"]],
                context=f"Tag {record['tag']} was recorded dead and fallen in {earlier.survey_id.replace('_', ' ')}, but standing in {later.survey_id.replace('_', ' ')}.",
                question="Is the tagged trunk standing, supported by another tree, or lying on the ground?",
                reference=f"{earlier.source_file}:{earlier.source_row}; {later.source_file}:{later.source_row}",
                reason="conflicting observed standing history")


def build_field_roster(census: pd.DataFrame, policy: dict) -> dict:
    """Build a finite search list; retirement never deletes canonical history.

    Rank is only a survey-local display channel. Historical DBH is a locating
    aid, never proof of stem continuity or a new observation.
    """
    surveys = policy["recent_surveys"]
    if len(surveys) != 2 or len(set(surveys)) != 2:
        raise ValueError("Exactly two distinct, chronological context surveys are required")
    if policy.get("missing_surveys_to_omit") != 2 or policy.get("omit_dead_fallen") is not True:
        raise ValueError("Field policy requires two-survey absence and dead/fallen omission")
    if set(surveys) - set(census.survey_id):
        raise ValueError("Requested context survey is absent from this dataset")
    survey_dates = census.groupby("survey_id")["date"].min().sort_values()
    if list(survey_dates.index[-2:]) != surveys:
        raise ValueError("Context must be the latest two surveys, oldest first")
    if set(census["plot"]) != set(policy["expected_plots"]):
        raise ValueError("Canonical plot coverage differs from the packet policy")
    history = census.sort_values(["date", "survey_id", "source_file", "source_row"]).copy()
    history["_found_signal"] = history[["dbh_mm", "health_observed", "standing_observed"]].notna().any(axis=1)
    history["_stem"] = history.stem_rank.map(_clean_stem)
    if history.duplicated(["tree_uid", "survey_id", "_stem"]).any():
        raise ValueError("Canonical tree/survey/rank rows must be unique before roster selection")
    references = _latest_dbh_by_stem(history)
    notes = {plot: [] for plot in policy["expected_plots"]}
    questions = {plot: [] for plot in notes}
    configured_questions = policy.get("rechecks", [])
    known_uids = set(history.tree_uid.astype(str))
    ids = set()
    exception_uids = set()
    for question in configured_questions:
        if question["id"] in ids or not question["question"].endswith("?"):
            raise ValueError("Rechecks require unique IDs and an actual question")
        ids.add(question["id"])
        if not question["tree_uids"] or set(question["tree_uids"]) - known_uids:
            raise ValueError(f"Unknown recheck UUID: {question['id']}")
        target = history.loc[history.tree_uid.isin(question["tree_uids"])]
        if not target['plot'].eq(question["plot"]).all():
            raise ValueError(f"Recheck plot/UUID mismatch: {question['id']}")
        questions[question["plot"]].append(dict(question))
        if question.get("retain_on_roster", False):
            exception_uids.update(question["tree_uids"])
    for note in policy.get("field_notes", []):
        notes[note["plot"]].append({"text": note["text"], "reference": note["reference"],
                                    "tags": [_clean_tag(tag) for tag in note.get("tags", [])]})
    rows, coverage, exclusions = [], [], []
    unknown_size_tags = {plot: [] for plot in notes}
    seen_policy_keys = set()
    for uid, tree in history.groupby("tree_uid", sort=False):
        latest = tree.iloc[-1]
        plot, identity = str(latest["plot"]), _clean_tag(latest["identity_tag"])
        key = f"{plot}/{identity}"
        seen_policy_keys.add(key)
        source_tags = sorted(set(tree.public_tag.map(_clean_tag)), key=_natural_key)
        primary = policy.get("primary_tags", {}).get(key)
        if primary is None:
            if len(source_tags) != 1:
                raise ValueError(f"Choose a primary recording tag explicitly for {key}: {source_tags}")
            primary = source_tags[0]
        if primary not in source_tags:
            raise ValueError(f"Primary recording tag for {key} is absent from its evidence")
        genus = str(latest["genus"])
        phenology = ("evergreen" if genus in policy["evergreen_genera"] else
                     "unknown" if genus in {"Unidentifiable", "", "nan", "None"} else "deciduous")
        record = dict(tree_uid=str(uid), plot=plot, identity_tag=identity, tag=primary,
                      source_tags="|".join(source_tags), phenology=phenology,
                      latest_recorded_survey=str(latest.survey_id))
        recent = tree.loc[tree.survey_id.isin(surveys)]
        found = recent.loc[recent._found_signal]
        all_found = tree.loc[tree._found_signal]
        exception = str(uid) in exception_uids
        historical_note = policy.get("historical_identity_checks", {}).get(key)
        if historical_note:
            if tree.loc[tree.survey_id.isin(surveys), "_found_signal"].any():
                raise ValueError(f"Historical-only policy is stale; {key} has recent evidence")
            notes[plot].append(dict(text=historical_note, reference=policy["decision_reference"], tree_uid=str(uid), tags=[primary]))
            coverage.append({**record, "disposition": "historical_identity_guidance", "row_count": 0})
            continue
        if found.empty and not exception:
            coverage.append({**record, "disposition": "omitted_absent_two_surveys", "row_count": 0})
            exclusions.append({**record, "stem": "*", "reason": "no direct input in either recent survey"})
            continue
        if len(source_tags) > 1 and key not in {"L2/816", "L2/5380", "M6/5145", "R4/5163"}:
            aliases = ", ".join(tag for tag in source_tags if tag != primary)
            notes[plot].append(dict(
                text=f"{primary} was previously recorded under tag(s) {aliases}; these are the same plant.",
                reference=policy["decision_reference"], tree_uid=str(uid), tags=source_tags))
        # Only an explicit question can restore a long-missing search entry.
        if found.empty:
            anchor_survey = all_found.iloc[-1].survey_id if not all_found.empty else latest.survey_id
            anchor = tree.loc[tree.survey_id.eq(anchor_survey)]
            slots = set(anchor._stem) | set(recent._stem)
        else:
            slots = set(recent._stem)
        tree_rows, excluded_slots = [], []
        retired_dead_fallen = 0
        for stem in sorted(slots, key=_natural_key):
            channel = tree.loc[tree._stem.eq(stem)]
            channel_recent = recent.loc[recent._stem.eq(stem)]
            channel_found = channel_recent.loc[channel_recent._found_signal]
            if not channel._found_signal.any() and (not all_found.empty or stem != min(slots, key=_natural_key)):
                exclusions.append({**record, "stem": stem, "reason": "extra rank has no direct observation in any survey"})
                continue
            if channel_found.empty and not exception:
                exclusions.append({**record, "stem": stem, "reason": "rank has no direct input in either recent survey"})
                continue
            if _dead_fallen_context(channel) and not exception:
                exclusions.append({**record, "stem": stem, "reason": "dead and fallen; no later live or standing evidence"})
                retired_dead_fallen += 1
                continue
            qualifying = any(passes_size_filter(r.dbh_mm, r.genus, r.species, r.taxon_code)
                             for r in channel.itertuples())
            measured = channel.loc[channel.dbh_mm.notna()]
            # An unmeasured recent entry could be a different stem in this rank.
            # Do not reject it on a small, unrelated historical measurement.
            unknown_recent_size = channel_found.dbh_mm.isna().any()
            if not measured.empty and not qualifying and not unknown_recent_size:
                exclusions.append({**record, "stem": stem, "reason": "all recorded DBH below taxon threshold"})
                excluded_slots.append(stem)
                continue
            last_found = channel.loc[channel._found_signal]
            context = last_found.iloc[-1] if not last_found.empty else channel.iloc[-1]
            qualification = "qualifying_history" if qualifying else "size_unknown"
            tree_rows.append({
                **record, "stem": stem, "spp_latest": str(latest.taxon_code),
                "latest_survey": str(context.survey_id), "latest_health": context.health_observed,
                "latest_standing": context.standing_observed, "reference_dbh_mm": references.get((str(uid), stem)),
                "dhs_1": _dhs_for_survey(channel_recent, surveys[1]),
                "dhs_2": _dhs_for_survey(channel_recent, surveys[0]),
                "hsp_1": _hsp_for_survey(channel_recent, surveys[1]),
                "hsp_2": _hsp_for_survey(channel_recent, surveys[0]),
                "roster_section": "main", "qualification": qualification,
                "reason": "explicit field-question exception" if exception else "direct input in recent context",
                "latest_source_file": str(context.source_file), "latest_source_row": int(context.source_row),
            })
        if any(r["qualification"] == "size_unknown" for r in tree_rows):
            unknown_size_tags[plot].append(primary)
        if excluded_slots:
            notes[plot].append(dict(text=f"Small {primary} stems that were never recorded at or above the survey minimum (20 mm; wax myrtle 50 mm) are not printed.", reference="packet policy: inclusive 20 mm / Morella 50 mm", tree_uid=str(uid), tags=[primary]))
        rows.extend(tree_rows)
        if tree_rows and policy.get("recheck_standing_conflicts", True):
            if question := _standing_conflict_question(tree, record):
                questions[plot].append(question)
        disposition = "main" if tree_rows else "omitted_dead_fallen" if retired_dead_fallen else "below_threshold_guidance"
        coverage.append({**record, "disposition": disposition, "row_count": len(tree_rows)})
    configured = set(policy.get("primary_tags", {})) | set(policy.get("historical_identity_checks", {}))
    if configured - seen_policy_keys:
        raise ValueError(f"Unmatched roster policy identities: {sorted(configured - seen_policy_keys)}")
    roster = pd.DataFrame(rows)
    if roster.empty:
        roster = pd.DataFrame(columns=["tree_uid", "plot", "tag", "stem"])
    collisions = roster.groupby(["plot", "tag"]).tree_uid.nunique()
    if collisions.gt(1).any():
        raise ValueError("Distinct UUIDs share a recording tag; resolve or explicitly label historical identities")
    # Display slots are contiguous after eligibility filtering; preserve the
    # source rank separately so 1/2 and 2/2 do not imply physical tracking.
    roster["source_rank"] = roster["stem"]
    for _, group in roster.groupby("tree_uid", sort=False):
        for position, index in enumerate(group.index, start=1):
            roster.at[index, "stem"] = str(position)
    for plot in notes:
        if unknown_size_tags[plot]:
            tags = ", ".join(sorted(unknown_size_tags[plot], key=_natural_key))
            notes[plot].append(dict(text=f"Some stems under {tags} have no confirmed measurement at or above the survey minimum (20 mm; wax myrtle 50 mm).", reference="packet policy: uncertain size retained", tags=sorted(unknown_size_tags[plot], key=_natural_key)))
    active_uids = set(roster.tree_uid)
    historical_uids = {r["tree_uid"] for r in coverage if r["disposition"] == "historical_identity_guidance"}
    question_ids = {uid: [] for uid in active_uids}
    for plot, checks in questions.items():
        for number, check in enumerate(checks, 1):
            if set(check["tree_uids"]) - active_uids:
                raise ValueError(f"Recheck targets are off roster; review or explicitly retain them: {check['id']}")
            check["number"] = number
            check["tags"] = sorted(set(roster.loc[roster.tree_uid.isin(check["tree_uids"]), "tag"]), key=_natural_key)
            for uid in check["tree_uids"]:
                question_ids[uid].append(check["id"])
        notes[plot] = [n for n in notes[plot] if "tree_uid" not in n or n["tree_uid"] in active_uids | historical_uids]
    roster["recheck_ids"] = roster.tree_uid.map(lambda uid: "|".join(question_ids[uid]))
    # Link explicit tag references within a plot, not arbitrary numbers in prose.
    # A historical split note can mention the current tag without merging UUIDs.
    note_numbers = {}
    for plot, plot_notes in notes.items():
        for number, note in enumerate(plot_notes, 1):
            for tag in set(note.get("tags", [])):
                note_numbers.setdefault((plot, tag), []).append(str(number))
    roster["field_note_numbers"] = ["|".join(note_numbers.get((r.plot, r.tag), []))
                                    for r in roster.itertuples()]
    return {"roster": roster, "coverage": pd.DataFrame(coverage), "exclusions": pd.DataFrame(exclusions), "field_notes": notes, "rechecks": questions}


def write_field_packet(
    parquet: str | Path, policy_path: str | Path, out_dir: str | Path,
    *, template: str | Path = "prototypes/datasheets/portrait_prototype.typ",
) -> dict:
    """Publish a fresh directory only after PDF, roster, and ZIP checks pass."""
    parquet, policy_path, template, out = map(Path, (parquet, policy_path, template, out_dir))
    if out.exists():
        raise FileExistsError(f"Use a new packet directory; refusing to overwrite {out}")
    for executable in ("typst", "pdfinfo", "pdftotext"):
        if not shutil.which(executable):
            raise RuntimeError(f"Required packet verification tool is missing: {executable}")
    census_manifest = json.loads(parquet.with_name("manifest.json").read_text())
    if _sha256(parquet) != census_manifest["artifact_sha256"]:
        raise ValueError("Canonical Parquet does not match its publication manifest")
    if census_manifest["diagnostics"]["by_severity"].get("error", 0):
        raise ValueError("Cannot generate field packet from a build with validation errors")
    policy = tomllib.loads(policy_path.read_text())
    context_paths = [Path(p) for p in policy.get("hsp_sources", {}).values()]
    difficulty_paths = [Path(p) for p in policy.get("difficulty_sources", [])]
    provenance = {str(p): _sha256(p) for p in (parquet, parquet.with_name("manifest.json"), policy_path, template, Path(__file__), Path(__file__).with_name("datasheets.py"), *context_paths, *difficulty_paths)}
    census = pd.read_parquet(parquet)
    census = _attach_poison_ivy_context(census, policy.get("hsp_sources", {}), census_manifest)
    metadata = pd.concat([pd.read_csv(p, dtype=str, keep_default_na=False) for p in difficulty_paths], ignore_index=True) if difficulty_paths else pd.DataFrame()
    if not metadata.empty and (not metadata.survey_id.isin(census.survey_id).all() or
                              not metadata.loc[metadata.difficulty.ne(""), "plot"].isin(policy["expected_plots"]).all()):
        raise ValueError("Difficulty metadata contains an unknown survey or rated plot")
    difficulty = _historical_difficulty(metadata)
    frames = build_field_roster(census, policy)
    packet_id = hashlib.sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()[:16]
    payloads = build_plot_datasheets(frames["roster"], survey_id=policy["survey_id"], field_notes=frames["field_notes"], recent_surveys=policy["recent_surveys"], packet_id=packet_id, historical_difficulty=difficulty, rechecks=frames["rechecks"])
    if set(payloads) != set(policy["expected_plots"]):
        raise ValueError("Not every expected plot has a printable roster")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".packet-", dir=out.parent) as tmp:
        stage = Path(tmp)
        for name in ("json", "typ", "pdf"):
            (stage / name).mkdir()
        for key in ("roster", "coverage", "exclusions"):
            frames[key].to_csv(stage / f"{key}.csv", index=False)
        (stage / "rechecks.json").write_text(json.dumps(frames["rechecks"], indent=2, sort_keys=True) + "\n")
        (stage / "policy.toml").write_bytes(policy_path.read_bytes())
        (stage / "canonical_manifest.json").write_text(json.dumps(census_manifest, indent=2, sort_keys=True) + "\n")
        plots = {}
        for plot, payload in payloads.items():
            stem = f"BRNV_{plot}"
            data, typ, pdf = stage / "json" / f"{stem}.json", stage / "typ" / f"{stem}.typ", stage / "pdf" / f"{stem}.pdf"
            data.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            typ.write_text(_typst_with_data_path(template.read_text(), f"../json/{data.name}"))
            subprocess.run(["typst", "compile", "--root", str(stage), str(typ), str(pdf)], check=True, capture_output=True)
            info = subprocess.check_output(["pdfinfo", str(pdf)], text=True)
            pages = int(next(line.split(":", 1)[1] for line in info.splitlines() if line.startswith("Pages:")))
            payload["total_pages"] = pages
            data.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
            content = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
            for needle in (f"BRNV {plot}", payload["survey_title"], "Newly Tracked",
                           "hsp = health / standing / poison ivy (only if applicable)",
                           "* = open question below", "+ = appears in field note"):
                if needle not in content:
                    raise ValueError(f"{plot}: required content missing from PDF: {needle}")
            if packet_id in content:
                raise ValueError(f"{plot}: internal packet ID should not be printed")
            if payload["field_notes"]:
                if any(label not in content for label in ("Field Notes", "Helpful", "Confusing", "Incorrect")):
                    raise ValueError(f"{plot}: field-note feedback columns missing from PDF")
            elif "Field Notes" in content:
                raise ValueError(f"{plot}: empty field-note section should not be printed")
            if "Recheck - no direct input" in content:
                raise ValueError(f"{plot}: obsolete missing-tree search section")
            if bool(payload["rechecks"]) != ("Recheck Questions" in content):
                raise ValueError(f"{plot}: recheck questions missing from PDF")
            if len(re.findall(r"\bDate\b", content)) != payload["date_fields"]:
                raise ValueError(f"{plot}: date field count differs from packet layout")
            for role in payload["crew_roles"]:
                if content.count(role) != 1:
                    raise ValueError(f"{plot}: expected one {role} line")
            new_slots = re.findall(r"(?m)^\s*N(\d+)\s", content)
            if new_slots != [str(i) for i in range(1, payload["newly_tracked_slots"] + 1)]:
                raise ValueError(f"{plot}: Newly Tracked slots do not match the manifest")
            for number in range(1, pages + 1):
                if f"page {number}/{pages}" not in content:
                    raise ValueError(f"{plot}: page numbering differs from rendered page count")
            plots[plot] = dict(rows=len(payload["rows"]), trees=payload["tree_count"], pages=pages,
                               pdf=f"pdf/{pdf.name}", pdf_sha256=_sha256(pdf), json_sha256=_sha256(data))
        zip_name = f"BRNV_{policy['survey_id']}_per_plot_pdfs.zip"
        with ZipFile(stage / zip_name, "w", ZIP_DEFLATED) as archive:
            for plot in plots.values():
                file = stage / plot["pdf"]
                archive.write(file, file.name)
        with ZipFile(stage / zip_name) as archive:
            if set(archive.namelist()) != {Path(p["pdf"]).name for p in plots.values()}:
                raise ValueError("ZIP members do not match plot manifest")
            for p in plots.values():
                if hashlib.sha256(archive.read(Path(p["pdf"]).name)).hexdigest() != p["pdf_sha256"]:
                    raise ValueError("ZIP PDF differs from generated PDF")
        if any(_sha256(Path(name)) != digest for name, digest in provenance.items()):
            raise ValueError("Packet inputs changed during generation; rebuild from one stable version")
        coverage = frames["coverage"]
        manifest = dict(packet_id=packet_id, policy_version=policy["version"], survey_id=policy["survey_id"],
                        provenance=provenance, recent_surveys=policy["recent_surveys"], automatic_retirement=True,
                        missing_surveys_to_omit=policy["missing_surveys_to_omit"], omit_dead_fallen=policy["omit_dead_fallen"],
                        recheck_questions=sum(map(len, frames["rechecks"].values())),
                        recheck_trees=int(frames["roster"].loc[frames["roster"].recheck_ids.ne(""), "tree_uid"].nunique()),
                        canonical_trees=int(census.tree_uid.nunique()), roster_rows=len(frames["roster"]),
                        coverage=coverage.disposition.value_counts().to_dict(), plots=plots, zip=zip_name,
                        zip_sha256=_sha256(stage / zip_name),
                        files={str(p.relative_to(stage)): _sha256(p) for p in stage.rglob("*") if p.is_file()})
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        # Move the verified packet into its final name in one filesystem operation.
        stage.rename(out)
    return manifest

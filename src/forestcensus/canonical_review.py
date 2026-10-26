"""Non-destructive canonical identity review artifacts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .assembly import _tree_uid
from .config import Config
from .domain import MIN_MEASURED_DBH_MM


TREE_CASE_COLUMNS = [
    "tree_uid",
    "site",
    "plot",
    "identity_tag",
    "identity_label",
    "public_tags",
    "first_survey",
    "last_survey",
    "present_in_october_2025",
    "first_seen_in_october_2025",
    "missing_from_october_2025",
    "last_pre_october_status",
    "primary_taxon_code",
    "taxon_codes",
    "max_dbh_mm",
    "october_max_dbh_mm",
    "max_stem_count",
    "invariant_codes",
    "invariant_actions",
    "diagnostic_codes",
    "evidence_rows",
    "primary_evidence_rows",
    "accepted_input_evidence_rows",
    "note_flags",
    "candidate_link_count",
    "best_candidate_link_score",
    "review_bucket",
    "priority_score",
    "summary",
]

TAXON_REVIEW_CODES = {"taxon_conflict"}
TAG_SCOPE_REVIEW_CODES = {"tag_scope_note_review"}
MORTALITY_REVIEW_CODES = {
    "found_note_conflict",
    "mortality_contradiction",
    "alive_health_conflict",
    "dead_health_conflict",
    "single_survey_death_label_outlier",
}
DBH_REVIEW_CODES = {
    "max_dbh_jump",
    "ranked_dbh_jump",
    "single_survey_dbh_outlier",
    "short_run_dbh_outlier",
    "persistent_dbh_regime_shift",
    "stable_incompatible_dbh_era",
    "early_low_dbh_source_era_candidate",
    "source_note_dbh_conflict",
    "dead_tree_dbh_increase",
}
STEM_REVIEW_CODES = {
    "stem_count_change",
    "large_stem_appearance",
    "large_stem_disappearance",
    "new_persistent_large_stem",
    "blank_missing_stem_backfill_candidate",
    "qualifying_rank_gap",
    "first_qualifying_after_prior_observation",
}
RULE_ASSISTED_CODES = {
    "probable_duplicate_stem_artifact",
    "subthreshold_dbh_present",
    "duplicate_stem_conflicting_fields",
    "dead_low_health_to_zero_candidate",
    "dead_label_low_health_later_alive",
    "near_duplicate_stem_artifact",
    "single_survey_low_health_death_label_outlier",
    "explicit_note_mortality_correction_candidate",
}
WATCH_INVARIANT_CODES = {
    "bounded_stem_rank_gap",
    "cluster_measurement_dbh_context",
    "dead_tree_stable_dbh_loss_context",
    "dead_tree_stem_context",
    "dead_tree_dbh_gap",
    "dead_tree_dbh_loss",
    "health_rebound_alive_context",
    "health_rebound_new_stem_context",
    "measurement_note_dbh_context",
    "merge_note_context",
    "morella_cluster_rank_jump_context",
    "new_noticed_stem_context",
    "observed_mortality_event",
    "oct_2025_protocol_missing_dbh",
    "nonqualifying_tree_excluded",
    "prior_dead_first_qualifying_dbh",
    "prior_live_blank_dbh_history",
    "stem_mortality_context",
    "structural_measurement_dbh_context",
    "threshold_edge_dbh_context",
    "dead_tree_threshold_dbh_context",
    "threshold_multistem_gap_context",
    "threshold_new_stem_context",
}

CANDIDATE_LINK_COLUMNS = [
    "link_id",
    "link_type",
    "score",
    "site",
    "plot",
    "source_tree_uid",
    "source_identity_tag",
    "source_public_tag",
    "target_tree_uid",
    "target_identity_tag",
    "target_public_tag",
    "source_max_dbh_mm",
    "target_max_dbh_mm",
    "dbh_delta_mm",
    "dbh_delta_pct",
    "taxon_match",
    "review_status",
    "review_reason",
    "evidence_source",
    "evidence_source_row",
    "details",
]

CASE_EVIDENCE_COLUMNS = [
    "case_tree_uid",
    "case_priority_score",
    "case_review_bucket",
    "candidate_link_id",
    "candidate_role",
    "evidence_id",
    "source_path",
    "source_sheet",
    "source_row",
    "source_kind",
    "evidence_rank",
    "canonical_role",
    "observation_role",
    "survey_id",
    "date",
    "plot",
    "public_tag_raw",
    "datasheet_slot_raw",
    "genus_raw",
    "species_raw",
    "taxon_raw",
    "dbh_mm_raw",
    "health_raw",
    "alive_raw",
    "standing_raw",
    "notes_raw",
    "note_flags",
]

CANONICAL_HISTORY_COLUMNS = [
    "survey_id",
    "date",
    "site",
    "zone",
    "plot",
    "tree_uid",
    "public_tag",
    "identity_tag",
    "identity_label",
    "tree_number",
    "stem_rank",
    "datasheet_slot",
    "genus",
    "species",
    "taxon_code",
    "dbh_mm",
    "health_observed",
    "alive_observed",
    "standing_observed",
    "field_status",
    "interpreted_status",
    "alive_interpreted",
    "zombie_ever",
    "origin",
    "source_file",
    "source_row",
    "notes",
    "correction_notes",
]

DECISION_CANDIDATE_COLUMNS = [
    "candidate_id",
    "lane",
    "generator",
    "operation",
    "priority",
    "status",
    "confidence",
    "decision_scope",
    "site",
    "plot",
    "tree_uid",
    "identity_tag",
    "public_tag",
    "survey_id",
    "stem_rank",
    "source_file",
    "source_row",
    "selector",
    "parameters",
    "reason",
    "guardrail_notes",
    "source_code",
    "source_summary",
    "details",
]

REVIEW_WORKLIST_COLUMNS = [
    "item_id",
    "lane",
    "work_type",
    "priority",
    "status",
    "site",
    "plot",
    "tree_uid",
    "related_tree_uids",
    "identity_tag",
    "identity_label",
    "public_tags",
    "review_bucket",
    "review_status",
    "current_codes",
    "diagnostic_codes",
    "candidate_decision_ids",
    "summary",
    "recommended_action",
    "decision_scope",
    "confidence",
    "needs_riley_call",
    "source_rows_to_check",
    "guardrail_notes",
]

NUMERIC_COLUMNS = {
    "source_row",
    "score",
    "source_max_dbh_mm",
    "target_max_dbh_mm",
    "dbh_delta_mm",
    "dbh_delta_pct",
    "max_dbh_mm",
    "october_max_dbh_mm",
    "max_stem_count",
    "evidence_rows",
    "primary_evidence_rows",
    "accepted_input_evidence_rows",
    "candidate_link_count",
    "best_candidate_link_score",
    "priority_score",
    "case_priority_score",
    "priority",
    "confidence",
}

BOOLEAN_COLUMNS = {
    "present_in_october_2025",
    "first_seen_in_october_2025",
    "missing_from_october_2025",
}


@dataclass(frozen=True)
class CanonicalReviewFrames:
    tree_cases: pd.DataFrame
    candidate_links: pd.DataFrame
    priority_case_evidence: pd.DataFrame
    canonical_history: pd.DataFrame
    decision_candidates: pd.DataFrame
    review_worklist: pd.DataFrame


def build_canonical_review(
    census: pd.DataFrame,
    evidence_observations: pd.DataFrame,
    tag_change_assertions: pd.DataFrame,
    invariants: pd.DataFrame,
    issues: pd.DataFrame,
    config: Config,
    *,
    priority_case_limit: int = 200,
) -> CanonicalReviewFrames:
    """Build non-destructive review/proposal tables for canonical identity work."""

    summaries = _tree_summaries(census, evidence_observations, invariants, issues, config)
    links = _candidate_links(summaries, tag_change_assertions, config)
    cases = _tree_cases(summaries, links)
    case_evidence = _priority_case_evidence(cases, links, evidence_observations, priority_case_limit)
    decision_candidates = _decision_candidates(cases, links, invariants)
    review_worklist = _review_worklist(cases, links, decision_candidates)
    return CanonicalReviewFrames(
        tree_cases=_frame(cases, TREE_CASE_COLUMNS),
        candidate_links=_frame(links, CANDIDATE_LINK_COLUMNS),
        priority_case_evidence=_frame(case_evidence, CASE_EVIDENCE_COLUMNS),
        canonical_history=_canonical_history(census),
        decision_candidates=_frame(decision_candidates, DECISION_CANDIDATE_COLUMNS),
        review_worklist=_frame(review_worklist, REVIEW_WORKLIST_COLUMNS),
    )


def write_canonical_review(frames: CanonicalReviewFrames, out_dir: str | Path) -> dict[str, object]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    for name, frame in [
        ("tree_cases", frames.tree_cases),
        ("candidate_links", frames.candidate_links),
        ("priority_case_evidence", frames.priority_case_evidence),
        ("canonical_history", frames.canonical_history),
        ("decision_candidates", frames.decision_candidates),
        ("review_worklist", frames.review_worklist),
    ]:
        parquet_path = out_dir / f"{name}.parquet"
        csv_path = out_dir / f"{name}.csv"
        frame.to_parquet(parquet_path, index=False)
        frame.to_csv(csv_path, index=False)
        outputs[name] = str(parquet_path)
    summary = canonical_review_summary(frames)
    summary["outputs"] = outputs
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary["summary"] = str(summary_path)
    return summary


def canonical_review_summary(frames: CanonicalReviewFrames) -> dict[str, object]:
    cases = frames.tree_cases
    links = frames.candidate_links
    return {
        "tree_cases": int(len(cases)),
        "candidate_links": int(len(links)),
        "priority_case_evidence_rows": int(len(frames.priority_case_evidence)),
        "canonical_history_rows": int(len(frames.canonical_history)),
        "decision_candidates": int(len(frames.decision_candidates)),
        "review_worklist_items": int(len(frames.review_worklist)),
        "review_buckets": _value_counts(cases, "review_bucket"),
        "candidate_link_types": _value_counts(links, "link_type"),
        "decision_candidate_generators": _value_counts(frames.decision_candidates, "generator"),
        "worklist_lanes": _value_counts(frames.review_worklist, "lane"),
        "worklist_types": _value_counts(frames.review_worklist, "work_type"),
        "high_priority_cases": int(cases["priority_score"].ge(100).sum()) if not cases.empty else 0,
    }


def _tree_summaries(
    census: pd.DataFrame,
    evidence: pd.DataFrame,
    invariants: pd.DataFrame,
    issues: pd.DataFrame,
    config: Config,
) -> dict[str, dict[str, Any]]:
    census = census.copy()
    census["_survey_index"] = census["survey_id"].map(config.survey_index)
    october_index = _survey_index_or_none(config, "October_2025")
    summaries: dict[str, dict[str, Any]] = {}
    for tree_uid, rows in census.groupby("tree_uid", sort=False):
        ordered = rows.sort_values(["_survey_index", "stem_rank", "source_file", "source_row"])
        first = ordered.iloc[0]
        survey_indices = ordered["_survey_index"].dropna().astype(int)
        pre_october = ordered.loc[ordered["_survey_index"].lt(october_index)] if october_index is not None else ordered.iloc[0:0]
        last_pre_october = pre_october.sort_values(["_survey_index", "stem_rank"]).tail(1)
        public_tags = sorted(str(value) for value in ordered["public_tag"].dropna().astype(str).unique())
        dbhs = pd.to_numeric(ordered["dbh_mm"], errors="coerce").dropna()
        october_rows = ordered.loc[ordered["survey_id"].eq("October_2025")]
        october_dbhs = pd.to_numeric(october_rows["dbh_mm"], errors="coerce").dropna()
        stem_counts = ordered.groupby("survey_id")["stem_rank"].count()
        taxon_codes = sorted(str(value) for value in ordered["taxon_code"].dropna().astype(str).unique())
        summary = {
            "tree_uid": str(tree_uid),
            "site": str(first["site"]),
            "plot": str(first["plot"]),
            "identity_tag": str(first["identity_tag"]),
            "identity_label": str(first["identity_label"]),
            "public_tags": public_tags,
            "first_survey": str(ordered.iloc[0]["survey_id"]),
            "last_survey": str(ordered.iloc[-1]["survey_id"]),
            "first_survey_index": int(survey_indices.min()) if not survey_indices.empty else -1,
            "last_survey_index": int(survey_indices.max()) if not survey_indices.empty else -1,
            "present_in_october_2025": bool(not october_rows.empty),
            "first_seen_in_october_2025": bool(str(ordered.iloc[0]["survey_id"]) == "October_2025"),
            "missing_from_october_2025": bool(october_index is not None and october_rows.empty and not pre_october.empty),
            "last_pre_october_status": str(last_pre_october["interpreted_status"].iloc[0]) if not last_pre_october.empty else "",
            "last_pre_october_field_status": str(last_pre_october["field_status"].iloc[0]) if not last_pre_october.empty else "",
            "primary_taxon_code": _mode(ordered["taxon_code"]),
            "taxon_codes": taxon_codes,
            "max_dbh_mm": float(dbhs.max()) if not dbhs.empty else None,
            "october_max_dbh_mm": float(october_dbhs.max()) if not october_dbhs.empty else None,
            "max_stem_count": int(stem_counts.max()) if not stem_counts.empty else 0,
            "invariant_codes": [],
            "invariant_actions": [],
            "diagnostic_codes": [],
            "note_flags": [],
            "evidence_rows": 0,
            "primary_evidence_rows": 0,
            "accepted_input_evidence_rows": 0,
        }
        summaries[str(tree_uid)] = summary

    _merge_invariant_only_summaries(summaries, invariants)
    _attach_invariants(summaries, invariants)
    _attach_issues(summaries, issues)
    _attach_evidence_counts(summaries, evidence)
    return summaries


def _tree_cases(
    summaries: dict[str, dict[str, Any]],
    links: list[dict[str, object]],
) -> list[dict[str, object]]:
    link_scores: dict[str, list[float]] = {}
    human_link_scores: dict[str, list[float]] = {}
    for link in links:
        for key in ["source_tree_uid", "target_tree_uid"]:
            uid = str(link.get(key, ""))
            if uid:
                link_scores.setdefault(uid, []).append(float(link.get("score", 0) or 0))
                if str(link.get("review_status", "")) == "needs_human":
                    human_link_scores.setdefault(uid, []).append(float(link.get("score", 0) or 0))
    cases = []
    for tree_uid, summary in summaries.items():
        scores = link_scores.get(tree_uid, [])
        review_scores = human_link_scores.get(tree_uid, [])
        invariant_codes = set(summary.get("invariant_codes", []))
        diagnostic_codes = set(summary.get("diagnostic_codes", []))
        priority = _priority_score(summary, invariant_codes, diagnostic_codes, scores, review_scores)
        bucket = _review_bucket(summary, invariant_codes, diagnostic_codes, scores, review_scores)
        if priority <= 0 and bucket == "low_context":
            continue
        cases.append(
            {
                **summary,
                "public_tags": "|".join(summary.get("public_tags", [])),
                "taxon_codes": "|".join(summary.get("taxon_codes", [])),
                "invariant_codes": "|".join(summary.get("invariant_codes", [])),
                "invariant_actions": "|".join(summary.get("invariant_actions", [])),
                "diagnostic_codes": "|".join(summary.get("diagnostic_codes", [])),
                "note_flags": "|".join(summary.get("note_flags", [])),
                "candidate_link_count": len(scores),
                "best_candidate_link_score": max(scores) if scores else 0,
                "review_bucket": bucket,
                "priority_score": priority,
                "summary": _case_summary(summary, bucket),
            }
        )
    return sorted(cases, key=lambda row: (-float(row["priority_score"]), row["plot"], str(row["identity_tag"])))


def _candidate_links(
    summaries: dict[str, dict[str, Any]],
    tag_changes: pd.DataFrame,
    config: Config,
) -> list[dict[str, object]]:
    links = []
    links.extend(_tag_change_links(summaries, tag_changes, config))
    links.extend(_october_candidate_links(summaries, config))
    return sorted(links, key=lambda row: (-float(row["score"]), row["plot"], row["source_identity_tag"], row["target_identity_tag"]))


def _tag_change_links(
    summaries: dict[str, dict[str, Any]],
    tag_changes: pd.DataFrame,
    config: Config,
) -> list[dict[str, object]]:
    links = []
    for row in tag_changes.itertuples(index=False):
        old_uid = _tree_uid("BRNV", str(row.old_plot), str(row.old_tag))
        new_uid = _tree_uid("BRNV", str(row.new_plot), str(row.new_tag))
        old_summary = summaries.get(old_uid, {})
        new_summary = summaries.get(new_uid, {})
        source_max_dbh = old_summary.get("max_dbh_mm")
        target_max_dbh = new_summary.get("max_dbh_mm")
        taxon_match = _taxon_hint_match(str(row.old_taxon_hint), str(row.new_taxon_hint))
        review_status, review_reason = _link_review_status(
            "tag_change_assertion",
            old_summary,
            new_summary,
            source_max_dbh,
            target_max_dbh,
            taxon_match,
        )
        details = {
            "old_tree_code": row.old_tree_code,
            "new_tree_code": row.new_tree_code,
            "change_type": row.change_type,
            "year_changed": row.year_changed,
        }
        if _tag_change_has_configured_alias(row, config):
            review_status = "configured"
            review_reason = "accepted configured identity alias"
            details["accepted_configured_alias"] = True
        links.append(
            _link(
                link_type="tag_change_assertion",
                score=95,
                site="BRNV",
                plot=str(row.new_plot or row.old_plot),
                source_tree_uid=old_uid,
                source_identity_tag=str(row.old_tag),
                source_public_tag=str(row.old_tag),
                target_tree_uid=new_uid,
                target_identity_tag=str(row.new_tag),
                target_public_tag=str(row.new_tag),
                source_max_dbh_mm=source_max_dbh,
                target_max_dbh_mm=target_max_dbh,
                taxon_match=taxon_match,
                review_status=review_status,
                review_reason=review_reason,
                evidence_source=str(row.source_path),
                evidence_source_row=getattr(row, "source_row", ""),
                details=details,
            )
        )
    return links


def _tag_change_has_configured_alias(row: object, config: Config) -> bool:
    old_plot = str(getattr(row, "old_plot", ""))
    old_tag = str(getattr(row, "old_tag", ""))
    new_plot = str(getattr(row, "new_plot", ""))
    new_tag = str(getattr(row, "new_tag", ""))
    return any(
        alias.site == "BRNV"
        and alias.plot == new_plot
        and alias.tag == new_tag
        and alias.identity_tag == old_tag
        and new_plot == old_plot
        for alias in config.identity_aliases
    )


def _october_candidate_links(
    summaries: dict[str, dict[str, Any]],
    config: Config,
) -> list[dict[str, object]]:
    october_index = _survey_index_or_none(config, "October_2025")
    if october_index is None:
        return []
    october_first = [
        item for item in summaries.values()
        if item.get("first_seen_in_october_2025")
        and _safe_float(item.get("october_max_dbh_mm")) >= MIN_MEASURED_DBH_MM
    ]
    missing_prior = [
        item for item in summaries.values()
        if item.get("missing_from_october_2025")
        and item.get("last_pre_october_status") in {"alive", "missing_pending", "inferred_dead"}
        and _safe_float(item.get("max_dbh_mm")) >= MIN_MEASURED_DBH_MM
    ]
    by_plot: dict[str, list[dict[str, Any]]] = {}
    for item in missing_prior:
        by_plot.setdefault(str(item["plot"]), []).append(item)

    links = []
    for october in october_first:
        candidates = []
        for prior in by_plot.get(str(october["plot"]), []):
            score, details = _match_score(prior, october)
            if score >= 55:
                candidates.append((score, prior, details))
        for score, prior, details in sorted(candidates, key=lambda item: -item[0])[:5]:
            review_status, review_reason = _link_review_status(
                "october_new_matches_missing_prior_candidate",
                october,
                prior,
                october.get("october_max_dbh_mm"),
                prior.get("max_dbh_mm"),
                details["taxon_match"],
            )
            links.append(
                _link(
                    link_type="october_new_matches_missing_prior_candidate",
                    score=score,
                    site=str(october["site"]),
                    plot=str(october["plot"]),
                    source_tree_uid=str(october["tree_uid"]),
                    source_identity_tag=str(october["identity_tag"]),
                    source_public_tag=_first_tag(october),
                    target_tree_uid=str(prior["tree_uid"]),
                    target_identity_tag=str(prior["identity_tag"]),
                    target_public_tag=_first_tag(prior),
                    source_max_dbh_mm=october.get("october_max_dbh_mm"),
                    target_max_dbh_mm=prior.get("max_dbh_mm"),
                    taxon_match=details["taxon_match"],
                    review_status=review_status,
                    review_reason=review_reason,
                    evidence_source="canonical_october_vs_missing_prior",
                    evidence_source_row="",
                    details=details,
                )
            )
    return links


def _priority_case_evidence(
    cases: list[dict[str, object]],
    links: list[dict[str, object]],
    evidence: pd.DataFrame,
    priority_case_limit: int,
) -> list[dict[str, object]]:
    if evidence.empty or not cases:
        return []
    top_cases = cases[:priority_case_limit]
    links_by_tree: dict[str, list[dict[str, object]]] = {}
    for link in links:
        links_by_tree.setdefault(str(link["source_tree_uid"]), []).append(link)
        links_by_tree.setdefault(str(link["target_tree_uid"]), []).append(link)

    rows = []
    for case in top_cases:
        case_uid = str(case["tree_uid"])
        tags = set(str(case.get("public_tags", "")).split("|")) - {""}
        linked_tags: set[str] = set()
        for link in links_by_tree.get(case_uid, []):
            linked_tags.update(
                str(link.get(key, ""))
                for key in ["source_public_tag", "target_public_tag", "source_identity_tag", "target_identity_tag"]
            )
        linked_tags.discard("")
        all_tags = tags | linked_tags
        if not all_tags:
            continue
        evidence_rows = evidence.loc[
            evidence["plot"].eq(case["plot"])
            & evidence["public_tag_raw"].astype(str).isin(all_tags)
        ].copy()
        for evidence_row in evidence_rows.itertuples(index=False):
            role = "case_tag" if str(evidence_row.public_tag_raw) in tags else "linked_candidate_tag"
            matching_link = _first_matching_link(case_uid, str(evidence_row.public_tag_raw), links_by_tree.get(case_uid, []))
            rows.append(
                {
                    "case_tree_uid": case_uid,
                    "case_priority_score": case["priority_score"],
                    "case_review_bucket": case["review_bucket"],
                    "candidate_link_id": matching_link.get("link_id", "") if matching_link else "",
                    "candidate_role": role,
                    **{column: getattr(evidence_row, column, "") for column in CASE_EVIDENCE_COLUMNS if column not in {
                        "case_tree_uid",
                        "case_priority_score",
                        "case_review_bucket",
                        "candidate_link_id",
                        "candidate_role",
                    }},
                }
            )
    return rows


SUGGESTED_INVARIANT_DECISIONS: dict[str, dict[str, object]] = {
    "single_survey_death_label_outlier": {
        "generator": "bracketed_one_survey_death",
        "operation": "reinterpret_mortality_observation",
        "priority": 90,
        "confidence": 0.82,
        "parameters": {"field_status": "uncertain", "alive_observed": None, "health_observed": None},
        "guardrail_notes": "Candidate only when one observed-dead row is bracketed by observed-alive evidence.",
    },
    "single_survey_low_health_death_label_outlier": {
        "generator": "low_health_bracketed_one_survey_death",
        "operation": "reinterpret_mortality_observation",
        "priority": 85,
        "confidence": 0.78,
        "parameters": {"field_status": "uncertain", "alive_observed": None, "health_observed": None},
        "guardrail_notes": "Lower confidence because low health makes true mortality more plausible.",
    },
    "explicit_note_mortality_correction_candidate": {
        "generator": "explicit_note_contradicts_death",
        "operation": "reinterpret_mortality_observation",
        "priority": 92,
        "confidence": 0.88,
        "parameters": {"field_status": "uncertain", "alive_observed": None, "health_observed": None},
        "guardrail_notes": "Source notes explicitly indicate that an earlier death label was uncertain or wrong.",
    },
    "dead_low_health_to_zero_candidate": {
        "generator": "dead_low_health_normalization",
        "operation": "set_health_observed",
        "priority": 75,
        "confidence": 0.86,
        "parameters": {"health_observed": 0},
        "guardrail_notes": "Applies when the row is otherwise treated as dead and has no later alive evidence.",
    },
    "dead_label_low_health_later_alive": {
        "generator": "dead_label_later_alive",
        "operation": "reinterpret_mortality_observation",
        "priority": 82,
        "confidence": 0.8,
        "parameters": {"field_status": "observed_alive", "alive_observed": True},
        "guardrail_notes": "Candidate assumes the mortality label was wrong because later alive evidence exists.",
    },
    "single_survey_dbh_outlier": {
        "generator": "isolated_dbh_outlier",
        "operation": "suppress_dbh_observation",
        "priority": 80,
        "confidence": 0.76,
        "parameters": {"dbh_mm": None},
        "guardrail_notes": "Candidate only when neighboring measured surveys return to a comparable DBH baseline.",
    },
    "subthreshold_dbh_present": {
        "generator": "subthreshold_dbh_suppression",
        "operation": "suppress_dbh_observation",
        "priority": 70,
        "confidence": 0.82,
        "parameters": {"dbh_mm": None},
        "guardrail_notes": f"DBH below {MIN_MEASURED_DBH_MM} mm is not qualifying survey evidence.",
    },
    "probable_duplicate_stem_artifact": {
        "generator": "duplicate_stem_artifact",
        "operation": "suppress_duplicate_stem_observation",
        "priority": 78,
        "confidence": 0.74,
        "parameters": {"duplicate_stem": True},
        "guardrail_notes": "Candidate requires duplicate DBH values plus a stem-count increase pattern.",
    },
    "near_duplicate_stem_artifact": {
        "generator": "near_duplicate_stem_artifact",
        "operation": "suppress_duplicate_stem_observation",
        "priority": 68,
        "confidence": 0.62,
        "parameters": {"duplicate_stem": True},
        "guardrail_notes": "Near-duplicate stem candidates should be batch-reviewed more cautiously.",
    },
    "blank_missing_stem_backfill_candidate": {
        "generator": "missing_stem_blank_backfill",
        "operation": "insert_blank_stem_observation",
        "priority": 72,
        "confidence": 0.7,
        "parameters": {"dbh_mm": None, "health_observed": None, "field_status": "not_reported"},
        "guardrail_notes": "Adds explicit blank evidence for a missing ranked qualifying stem; does not infer stem mortality.",
    },
}

HUMAN_REVIEW_BUCKETS = {
    "candidate_identity_link",
    "taxon_or_identity_conflict",
    "tag_or_stem_scope_review",
    "mortality_review",
    "dbh_review",
    "stem_profile_review",
    "new_in_october_2025",
}


def _decision_candidates(
    cases: list[dict[str, object]],
    links: list[dict[str, object]],
    invariants: pd.DataFrame,
) -> list[dict[str, object]]:
    case_by_uid = {str(case["tree_uid"]): case for case in cases}
    candidates: list[dict[str, object]] = []
    seen_payloads: set[str] = set()

    if not invariants.empty:
        for row in invariants.itertuples(index=False):
            if _has_resolution(row):
                continue
            code = str(row.code)
            spec = SUGGESTED_INVARIANT_DECISIONS.get(code)
            if spec is None:
                continue
            details = _json_object(getattr(row, "details", ""))
            survey_id = str(details.get("survey_id") or details.get("current_survey") or "")
            stem_rank = _stem_rank_from_details(details)
            selector = _candidate_selector(row, details, survey_id, stem_rank)
            parameters = dict(spec["parameters"])
            _enrich_candidate_parameters(parameters, code, details, stem_rank)
            candidate = _candidate_record(
                generator=str(spec["generator"]),
                operation=str(spec["operation"]),
                priority=int(spec["priority"]),
                confidence=float(spec["confidence"]),
                site=str(row.site),
                plot=str(row.plot),
                tree_uid=str(row.tree_uid),
                identity_tag=str(row.identity_tag),
                public_tag=str(row.public_tag),
                survey_id=survey_id,
                stem_rank=stem_rank,
                source_file=str(details.get("source_file") or ""),
                source_row=details.get("source_row", ""),
                selector=selector,
                parameters=parameters,
                reason=str(getattr(row, "summary", "")) or str(details.get("classification_reason", "")),
                guardrail_notes=str(spec["guardrail_notes"]),
                source_code=code,
                source_summary=str(getattr(row, "summary", "")),
                details=details,
            )
            payload = _candidate_payload_key(candidate)
            if payload in seen_payloads:
                continue
            seen_payloads.add(payload)
            candidates.append(candidate)

    for link in links:
        if str(link.get("review_status", "")) != "rule_assisted":
            continue
        candidate = _candidate_record(
            generator="clean_tag_change_identity_link",
            operation="accept_identity_link",
            priority=88,
            confidence=0.84,
            site=str(link.get("site", "")),
            plot=str(link.get("plot", "")),
            tree_uid=str(link.get("target_tree_uid", "")),
            identity_tag=str(link.get("target_identity_tag", "")),
            public_tag=str(link.get("target_public_tag", "")),
            survey_id="",
            stem_rank="",
            source_file=str(link.get("evidence_source", "")),
            source_row=link.get("evidence_source_row", ""),
            selector={
                "link_id": str(link.get("link_id", "")),
                "source_tree_uid": str(link.get("source_tree_uid", "")),
                "target_tree_uid": str(link.get("target_tree_uid", "")),
                "plot": str(link.get("plot", "")),
            },
            parameters={
                "source_tree_uid": str(link.get("source_tree_uid", "")),
                "target_tree_uid": str(link.get("target_tree_uid", "")),
                "link_type": str(link.get("link_type", "")),
            },
            reason=str(link.get("review_reason", "")),
            guardrail_notes="Rule-assisted identity links still need batch approval before they change canonical UUID scope.",
            source_code=str(link.get("link_type", "")),
            source_summary=_link_summary(link, case_by_uid),
            details=_json_object(str(link.get("details", ""))),
        )
        candidates.append(candidate)

    return sorted(
        candidates,
        key=lambda row: (-int(row["priority"]), row["plot"], str(row["identity_tag"]), str(row["candidate_id"])),
    )


def _review_worklist(
    cases: list[dict[str, object]],
    links: list[dict[str, object]],
    candidates: list[dict[str, object]],
) -> list[dict[str, object]]:
    candidates_by_uid: dict[str, list[dict[str, object]]] = {}
    for candidate in candidates:
        candidates_by_uid.setdefault(str(candidate.get("tree_uid", "")), []).append(candidate)
        selector = _json_object(str(candidate.get("selector", "")))
        for uid_key in ["source_tree_uid", "target_tree_uid"]:
            uid = str(selector.get(uid_key, ""))
            if uid:
                candidates_by_uid.setdefault(uid, []).append(candidate)

    human_link_uids: set[str] = set()
    for link in links:
        if str(link.get("review_status", "")) == "needs_human":
            human_link_uids.update([str(link.get("source_tree_uid", "")), str(link.get("target_tree_uid", ""))])
    human_link_uids.discard("")

    worklist: list[dict[str, object]] = []
    for candidate in candidates:
        worklist.append(
            {
                "item_id": _stable_id("work_suggested", candidate["candidate_id"]),
                "lane": "suggested_fix",
                "work_type": str(candidate["generator"]),
                "priority": candidate["priority"],
                "status": "candidate",
                "site": candidate["site"],
                "plot": candidate["plot"],
                "tree_uid": candidate["tree_uid"],
                "related_tree_uids": _related_tree_uids(candidate),
                "identity_tag": candidate["identity_tag"],
                "identity_label": f"{candidate['plot']}/{candidate['identity_tag']}",
                "public_tags": candidate["public_tag"],
                "review_bucket": "",
                "review_status": "candidate",
                "current_codes": candidate["source_code"],
                "diagnostic_codes": "",
                "candidate_decision_ids": candidate["candidate_id"],
                "summary": candidate["reason"],
                "recommended_action": candidate["operation"],
                "decision_scope": candidate["decision_scope"],
                "confidence": candidate["confidence"],
                "needs_riley_call": False,
                "source_rows_to_check": _source_rows_to_check(candidate),
                "guardrail_notes": candidate["guardrail_notes"],
            }
        )

    for case in cases:
        codes = set(str(case.get("invariant_codes", "")).split("|")) - {""}
        diagnostics = set(str(case.get("diagnostic_codes", "")).split("|")) - {""}
        bucket = str(case.get("review_bucket", ""))
        if not _case_needs_human_work(case, codes, diagnostics, human_link_uids):
            continue
        uid = str(case["tree_uid"])
        candidate_ids = sorted({str(candidate["candidate_id"]) for candidate in candidates_by_uid.get(uid, [])})
        work_type = _human_work_type(bucket, codes, diagnostics, uid in human_link_uids)
        worklist.append(
            {
                "item_id": _stable_id("work_human", uid, work_type, "|".join(sorted(codes))),
                "lane": "needs_human_call",
                "work_type": work_type,
                "priority": int(case.get("priority_score", 0) or 0),
                "status": "open",
                "site": case.get("site", ""),
                "plot": case.get("plot", ""),
                "tree_uid": uid,
                "related_tree_uids": uid,
                "identity_tag": case.get("identity_tag", ""),
                "identity_label": case.get("identity_label", ""),
                "public_tags": case.get("public_tags", ""),
                "review_bucket": bucket,
                "review_status": "needs_review",
                "current_codes": "|".join(sorted(codes)),
                "diagnostic_codes": "|".join(sorted(diagnostics)),
                "candidate_decision_ids": "|".join(candidate_ids),
                "summary": case.get("summary", ""),
                "recommended_action": _human_recommended_action(work_type),
                "decision_scope": "uuid",
                "confidence": 0,
                "needs_riley_call": True,
                "source_rows_to_check": "",
                "guardrail_notes": _human_guardrail_notes(work_type),
            }
        )

    return sorted(
        worklist,
        key=lambda row: (0 if row["lane"] == "needs_human_call" else 1, -int(row["priority"]), row["plot"], str(row["identity_tag"])),
    )


def _candidate_record(**kwargs: object) -> dict[str, object]:
    selector = kwargs["selector"]
    parameters = kwargs["parameters"]
    candidate_id = _stable_id(
        "candidate",
        kwargs.get("operation", ""),
        kwargs.get("tree_uid", ""),
        kwargs.get("survey_id", ""),
        kwargs.get("stem_rank", ""),
        json.dumps(selector, sort_keys=True, default=str),
        json.dumps(parameters, sort_keys=True, default=str),
    )
    record = dict(kwargs)
    record.update({
        "candidate_id": candidate_id,
        "lane": "suggested_fix",
        "status": "candidate",
        "decision_scope": _decision_scope(str(kwargs.get("operation", ""))),
        "selector": json.dumps(selector, sort_keys=True, default=str),
        "parameters": json.dumps(parameters, sort_keys=True, default=str),
        "details": json.dumps(kwargs.get("details", {}), sort_keys=True, default=str),
    })
    return record


def _candidate_selector(row: object, details: dict[str, object], survey_id: str, stem_rank: object) -> dict[str, object]:
    selector = {
        "tree_uid": str(getattr(row, "tree_uid", "")),
        "plot": str(getattr(row, "plot", "")),
        "identity_tag": str(getattr(row, "identity_tag", "")),
        "public_tag": str(getattr(row, "public_tag", "")),
    }
    if survey_id:
        selector["survey_id"] = survey_id
    if stem_rank not in {"", None}:
        selector["stem_rank"] = stem_rank
    source_file = str(details.get("source_file") or "")
    if source_file:
        selector["source_file"] = source_file
    source_row = details.get("source_row")
    if source_row not in {"", None}:
        selector["source_row"] = source_row
    return selector


def _enrich_candidate_parameters(parameters: dict[str, object], code: str, details: dict[str, object], stem_rank: object) -> None:
    for source_key, target_key in [
        ("current_dbh", "original_dbh_mm"),
        ("dbh_mm", "original_dbh_mm"),
        ("current_health", "original_health_observed"),
        ("current_field_status", "original_field_status"),
    ]:
        if source_key in details and details[source_key] not in {"", None}:
            parameters[target_key] = details[source_key]
    if code == "blank_missing_stem_backfill_candidate":
        parameters["affected_ranks"] = details.get("affected_ranks", [])
        parameters["previous_survey"] = details.get("previous_survey", "")
    if stem_rank not in {"", None}:
        parameters["stem_rank"] = stem_rank


def _stem_rank_from_details(details: dict[str, object]) -> object:
    for key in ["stem_rank", "current_rank", "rank"]:
        value = details.get(key)
        if value not in {"", None}:
            return value
    affected = details.get("affected_ranks")
    if isinstance(affected, list) and len(affected) == 1:
        return affected[0]
    return ""


def _case_needs_human_work(
    case: dict[str, object],
    codes: set[str],
    diagnostics: set[str],
    human_link_uids: set[str],
) -> bool:
    if str(case.get("review_bucket", "")) in HUMAN_REVIEW_BUCKETS:
        return True
    if str(case.get("tree_uid", "")) in human_link_uids:
        return True
    human_codes = (
        TAXON_REVIEW_CODES
        | TAG_SCOPE_REVIEW_CODES
        | MORTALITY_REVIEW_CODES
        | DBH_REVIEW_CODES
        | (STEM_REVIEW_CODES - {"blank_missing_stem_backfill_candidate"})
    )
    return bool((codes & human_codes) or diagnostics)


def _human_work_type(bucket: str, codes: set[str], diagnostics: set[str], has_human_link: bool) -> str:
    if bucket == "taxon_or_identity_conflict" or codes & TAXON_REVIEW_CODES or "W_TAXON_CONFLICT" in diagnostics:
        return "taxon_identity_conflict"
    if bucket == "tag_or_stem_scope_review" or codes & TAG_SCOPE_REVIEW_CODES:
        return "tag_stem_scope_note"
    if has_human_link or bucket == "candidate_identity_link":
        return "candidate_identity_link_review"
    if codes & {"stable_incompatible_dbh_era", "early_low_dbh_source_era_candidate", "persistent_dbh_regime_shift", "source_note_dbh_conflict"}:
        return "source_era_dbh_block"
    if codes & MORTALITY_REVIEW_CODES:
        return "marginal_live_mortality"
    if codes & {
        "new_persistent_large_stem",
        "large_stem_appearance",
        "large_stem_disappearance",
        "stem_mortality_context",
        "threshold_multistem_gap_context",
        "probable_duplicate_stem_artifact",
        "bounded_stem_rank_gap",
    }:
        return "multistem_cluster_review"
    if "qualifying_rank_gap" in codes:
        return "single_stem_observation_gap"
    if codes & DBH_REVIEW_CODES:
        return "dbh_outlier_review"
    if bucket == "new_in_october_2025":
        return "new_october_identity_review"
    return "source_row_check"


def _human_recommended_action(work_type: str) -> str:
    return {
        "candidate_identity_link_review": "Inspect both UUID histories before accepting, rejecting, or splitting the identity link.",
        "taxon_identity_conflict": "Choose one tree-level taxon or mark the UUID as representing multiple identities.",
        "tag_stem_scope_note": "Decide whether the note belongs to the tree, one stem, or a different tag.",
        "source_era_dbh_block": "Check original source rows around the era boundary before proposing DBH edits.",
        "marginal_live_mortality": "Use field notes and later observations to choose mortality interpretation.",
        "multistem_cluster_review": "Inspect stem profile by survey and decide whether to blank, split, or retain stems.",
        "single_stem_observation_gap": "Decide whether to insert a blank/not-reported row for the missing survey.",
        "dbh_outlier_review": "Check whether the DBH is a typo, structural measurement issue, or real dead-tree decay.",
        "new_october_identity_review": "Search for complementary missing prior trees before assigning a fresh UUID.",
    }.get(work_type, "Inspect source evidence before adding a configured decision.")


def _human_guardrail_notes(work_type: str) -> str:
    if work_type == "dbh_outlier_review":
        return "Dead trees can legitimately lose DBH; October 2025 DBH can be missing by protocol."
    if work_type == "multistem_cluster_review":
        return "Stem ranks are derived within survey and are not durable stem identities across years."
    if work_type == "single_stem_observation_gap":
        return "A bounded gap is usually missing/not-reported evidence, not proof of mortality or a stem identity split."
    if work_type == "candidate_identity_link_review":
        return "Do not collapse UUIDs until tag-change evidence and DBH/taxon continuity agree."
    return "Manual call should become an explicit accepted decision if it changes canonical output."


def _decision_scope(operation: str) -> str:
    if operation in {"accept_identity_link"}:
        return "uuid"
    if operation in {"insert_blank_stem_observation", "suppress_duplicate_stem_observation"}:
        return "stem_observation"
    return "observation"


def _link_summary(link: dict[str, object], case_by_uid: dict[str, dict[str, object]]) -> str:
    source = case_by_uid.get(str(link.get("source_tree_uid", "")), {})
    target = case_by_uid.get(str(link.get("target_tree_uid", "")), {})
    source_label = source.get("identity_label") or f"{link.get('plot', '')}/{link.get('source_identity_tag', '')}"
    target_label = target.get("identity_label") or f"{link.get('plot', '')}/{link.get('target_identity_tag', '')}"
    return f"{source_label} -> {target_label}: {link.get('review_reason', '')}"


def _source_rows_to_check(candidate: dict[str, object]) -> str:
    source_file = str(candidate.get("source_file", ""))
    source_row = str(candidate.get("source_row", ""))
    if source_file and source_row:
        return f"{source_file}:{source_row}"
    if source_file:
        return source_file
    return ""


def _related_tree_uids(candidate: dict[str, object]) -> str:
    selector = _json_object(str(candidate.get("selector", "")))
    uids = [
        str(candidate.get("tree_uid", "")),
        str(selector.get("tree_uid", "")),
        str(selector.get("source_tree_uid", "")),
        str(selector.get("target_tree_uid", "")),
    ]
    return "|".join(sorted({uid for uid in uids if uid}))


def _candidate_payload_key(candidate: dict[str, object]) -> str:
    return "|".join(
        str(candidate.get(key, ""))
        for key in ["operation", "tree_uid", "survey_id", "stem_rank", "selector", "parameters"]
    )


def _json_object(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(str(value or "{}"))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _stable_id(prefix: str, *parts: object) -> str:
    payload = "|".join(str(part) for part in parts)
    return f"{prefix}_" + hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _attach_invariants(summaries: dict[str, dict[str, Any]], invariants: pd.DataFrame) -> None:
    if invariants.empty:
        return
    if "resolution_kind" in invariants.columns:
        invariants = invariants.loc[invariants["resolution_kind"].fillna("").eq("")]
    for tree_uid, rows in invariants.groupby("tree_uid", dropna=False):
        summary = summaries.get(str(tree_uid))
        if summary is None:
            continue
        summary["invariant_codes"] = sorted(set(rows["code"].dropna().astype(str)))
        summary["invariant_actions"] = sorted(set(rows["suggested_action"].dropna().astype(str)))


def _attach_issues(summaries: dict[str, dict[str, Any]], issues: pd.DataFrame) -> None:
    if issues.empty:
        return
    for tree_uid, rows in issues.groupby("tree_uid", dropna=False):
        summary = summaries.get(str(tree_uid))
        if summary is None:
            continue
        summary["diagnostic_codes"] = sorted(set(rows["code"].dropna().astype(str)))


def _has_resolution(row: object) -> bool:
    value = getattr(row, "resolution_kind", "")
    if pd.isna(value):
        return False
    return bool(str(value))


def _attach_evidence_counts(summaries: dict[str, dict[str, Any]], evidence: pd.DataFrame) -> None:
    if evidence.empty:
        return
    for summary in summaries.values():
        tags = set(summary.get("public_tags", [])) | {str(summary.get("identity_tag", ""))}
        rows = evidence.loc[
            evidence["plot"].eq(summary.get("plot", ""))
            & evidence["public_tag_raw"].astype(str).isin(tags)
        ]
        summary["evidence_rows"] = int(len(rows))
        summary["primary_evidence_rows"] = int(rows["evidence_rank"].eq("primary").sum()) if not rows.empty else 0
        summary["accepted_input_evidence_rows"] = int(rows["evidence_rank"].eq("accepted_input").sum()) if not rows.empty else 0
        flags = set()
        for value in rows.get("note_flags", pd.Series(dtype="string")).dropna().astype(str):
            flags.update(flag for flag in value.split("|") if flag)
        summary["note_flags"] = sorted(flags)


def _merge_invariant_only_summaries(
    summaries: dict[str, dict[str, Any]],
    invariants: pd.DataFrame,
) -> None:
    if invariants.empty:
        return
    if "resolution_kind" in invariants.columns:
        invariants = invariants.loc[invariants["resolution_kind"].fillna("").eq("")]
    for row in invariants.itertuples(index=False):
        uid = str(row.tree_uid)
        if uid in summaries:
            continue
        summaries[uid] = {
            "tree_uid": uid,
            "site": str(row.site),
            "plot": str(row.plot),
            "identity_tag": str(row.identity_tag),
            "identity_label": str(row.identity_label),
            "public_tags": [str(row.public_tag)] if str(row.public_tag) else [],
            "first_survey": "",
            "last_survey": "",
            "first_survey_index": -1,
            "last_survey_index": -1,
            "present_in_october_2025": False,
            "first_seen_in_october_2025": False,
            "missing_from_october_2025": False,
            "last_pre_october_status": "",
            "last_pre_october_field_status": "",
            "primary_taxon_code": "",
            "taxon_codes": [],
            "max_dbh_mm": None,
            "october_max_dbh_mm": None,
            "max_stem_count": 0,
            "invariant_codes": [],
            "invariant_actions": [],
            "diagnostic_codes": [],
            "note_flags": [],
            "evidence_rows": 0,
            "primary_evidence_rows": 0,
            "accepted_input_evidence_rows": 0,
        }


def _priority_score(
    summary: dict[str, Any],
    invariant_codes: set[str],
    diagnostic_codes: set[str],
    candidate_scores: list[float],
    human_candidate_scores: list[float],
) -> int:
    score = 0
    if invariant_codes & TAXON_REVIEW_CODES or "W_TAXON_CONFLICT" in diagnostic_codes:
        score += 120
    if invariant_codes & TAG_SCOPE_REVIEW_CODES:
        score += 120
    if summary.get("first_seen_in_october_2025") and _safe_float(summary.get("october_max_dbh_mm")) >= MIN_MEASURED_DBH_MM:
        score += 80
    if summary.get("missing_from_october_2025") and summary.get("last_pre_october_status") == "alive":
        score += 80
    if human_candidate_scores:
        score += min(100, round(max(human_candidate_scores)))
    elif candidate_scores:
        score += min(20, round(max(candidate_scores) / 5))
    if invariant_codes & STEM_REVIEW_CODES:
        score += 50
    if invariant_codes & DBH_REVIEW_CODES:
        score += 35
    if invariant_codes & MORTALITY_REVIEW_CODES:
        score += 35
    if invariant_codes & RULE_ASSISTED_CODES:
        score += 15
    if invariant_codes & WATCH_INVARIANT_CODES:
        score += 5
    return int(score)


def _review_bucket(
    summary: dict[str, Any],
    invariant_codes: set[str],
    diagnostic_codes: set[str],
    candidate_scores: list[float],
    human_candidate_scores: list[float],
) -> str:
    if invariant_codes & TAXON_REVIEW_CODES or "W_TAXON_CONFLICT" in diagnostic_codes:
        return "taxon_or_identity_conflict"
    if invariant_codes & TAG_SCOPE_REVIEW_CODES:
        return "tag_or_stem_scope_review"
    if human_candidate_scores:
        return "candidate_identity_link"
    if summary.get("first_seen_in_october_2025"):
        return "new_in_october_2025"
    if summary.get("missing_from_october_2025") and summary.get("last_pre_october_status") == "alive":
        return "missing_from_october_2025"
    if invariant_codes & MORTALITY_REVIEW_CODES:
        return "mortality_review"
    if invariant_codes & DBH_REVIEW_CODES:
        return "dbh_review"
    if invariant_codes & STEM_REVIEW_CODES:
        return "stem_profile_review"
    if invariant_codes & RULE_ASSISTED_CODES:
        return "rule_assisted_cleanup"
    if invariant_codes & WATCH_INVARIANT_CODES:
        return "watch_context"
    if candidate_scores:
        return "rule_assisted_link"
    if invariant_codes:
        return "invariant_review"
    if summary.get("note_flags"):
        return "note_context"
    return "low_context"


def _case_summary(summary: dict[str, Any], bucket: str) -> str:
    tag = _first_tag(summary)
    if bucket == "new_in_october_2025":
        return f"{summary['plot']}/{tag} first appears in October 2025 with max DBH {summary.get('october_max_dbh_mm')} mm."
    if bucket == "missing_from_october_2025":
        return f"{summary['plot']}/{tag} has prior status {summary.get('last_pre_october_status')} but no October 2025 row."
    if bucket == "candidate_identity_link":
        return f"{summary['plot']}/{tag} has one or more candidate identity/tag links."
    if bucket == "taxon_or_identity_conflict":
        return f"{summary['plot']}/{tag} has conflicting taxon evidence in canonical output."
    if bucket == "tag_or_stem_scope_review":
        return f"{summary['plot']}/{tag} has tag or stem-scope notes that need review."
    if bucket == "mortality_review":
        return f"{summary['plot']}/{tag} has mortality/health evidence that needs review."
    if bucket == "dbh_review":
        return f"{summary['plot']}/{tag} has DBH behavior that needs review."
    if bucket == "stem_profile_review":
        return f"{summary['plot']}/{tag} has stem-profile behavior that needs review."
    if bucket == "rule_assisted_cleanup":
        return f"{summary['plot']}/{tag} matches a common cleanup pattern: {', '.join(summary.get('invariant_codes', []))}."
    if bucket == "rule_assisted_link":
        return f"{summary['plot']}/{tag} has candidate identity/tag links that look rule-assisted rather than human-critical."
    if bucket == "watch_context":
        return f"{summary['plot']}/{tag} has contextual invariant findings: {', '.join(summary.get('invariant_codes', []))}."
    if bucket == "invariant_review":
        return f"{summary['plot']}/{tag} has invariant findings: {', '.join(summary.get('invariant_codes', []))}."
    return f"{summary['plot']}/{tag} has contextual evidence worth retaining."


def _match_score(prior: dict[str, Any], october: dict[str, Any]) -> tuple[float, dict[str, object]]:
    prior_dbh = _safe_float(prior.get("max_dbh_mm"))
    october_dbh = _safe_float(october.get("october_max_dbh_mm"))
    if prior_dbh <= 0 or october_dbh <= 0:
        return 0, {}
    delta = abs(prior_dbh - october_dbh)
    delta_pct = delta / max(prior_dbh, october_dbh)
    if delta_pct > 0.35:
        return 0, {}
    dbh_score = max(0, 60 * (1 - delta_pct / 0.35))
    taxon_match = _taxon_match(prior.get("primary_taxon_code", ""), october.get("primary_taxon_code", ""))
    taxon_score = {"exact": 30, "genus_hint": 18, "unknown": 8, "different": 0}[taxon_match]
    score = dbh_score + taxon_score
    details = {
        "dbh_delta_mm": round(delta, 3),
        "dbh_delta_pct": round(delta_pct, 4),
        "taxon_match": taxon_match,
        "prior_last_survey": prior.get("last_survey", ""),
        "prior_last_pre_october_status": prior.get("last_pre_october_status", ""),
        "october_first_survey": october.get("first_survey", ""),
    }
    return score, details


def _link_review_status(
    link_type: str,
    source: dict[str, Any],
    target: dict[str, Any],
    source_dbh: object,
    target_dbh: object,
    taxon_match: str,
) -> tuple[str, str]:
    source_codes = set(source.get("invariant_codes", []))
    target_codes = set(target.get("invariant_codes", []))
    codes = source_codes | target_codes
    source_value = _safe_float(source_dbh)
    target_value = _safe_float(target_dbh)
    if taxon_match == "different":
        return "needs_human", "taxon hints differ across the proposed link"
    if codes & (TAXON_REVIEW_CODES | MORTALITY_REVIEW_CODES | DBH_REVIEW_CODES):
        return "needs_human", "one endpoint has taxon, mortality, or DBH review findings"
    if source_value <= 0 or target_value <= 0:
        return "needs_human", "one endpoint lacks a comparable DBH profile"
    delta_pct = abs(source_value - target_value) / max(source_value, target_value)
    if delta_pct > 0.35:
        return "needs_human", "DBH profiles differ too much for a whole-tree link"
    if link_type == "october_new_matches_missing_prior_candidate":
        return "needs_human", "new October 2025 tree matched to a missing prior tree"
    if codes & STEM_REVIEW_CODES:
        return "watch", "link is plausible, but one endpoint has stem-profile context"
    return "rule_assisted", "tag-change assertion is taxon-compatible with similar DBH profiles"


def _link(**kwargs: object) -> dict[str, object]:
    source_dbh = _safe_float(kwargs.get("source_max_dbh_mm"))
    target_dbh = _safe_float(kwargs.get("target_max_dbh_mm"))
    delta = abs(source_dbh - target_dbh) if source_dbh and target_dbh else None
    delta_pct = delta / max(source_dbh, target_dbh) if delta is not None and max(source_dbh, target_dbh) else None
    details = kwargs.get("details", {})
    record = dict(kwargs)
    record["details"] = json.dumps(details, sort_keys=True, default=str)
    return {
        "link_id": _link_id(kwargs),
        "dbh_delta_mm": round(delta, 3) if delta is not None else "",
        "dbh_delta_pct": round(delta_pct, 4) if delta_pct is not None else "",
        **record,
    }


def _link_id(values: dict[str, object]) -> str:
    import hashlib

    payload = "|".join(
        str(values.get(key, ""))
        for key in ["link_type", "source_tree_uid", "target_tree_uid", "evidence_source", "evidence_source_row"]
    )
    return "link_" + hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _first_matching_link(case_uid: str, evidence_tag: str, links: list[dict[str, object]]) -> dict[str, object] | None:
    for link in links:
        if str(link.get("source_tree_uid", "")) != case_uid and str(link.get("target_tree_uid", "")) != case_uid:
            continue
        if evidence_tag in {
            str(link.get("source_public_tag", "")),
            str(link.get("target_public_tag", "")),
            str(link.get("source_identity_tag", "")),
            str(link.get("target_identity_tag", "")),
        }:
            return link
    return None


def _taxon_match(left: object, right: object) -> str:
    left_text = str(left or "")
    right_text = str(right or "")
    if not left_text or not right_text:
        return "unknown"
    if left_text == right_text:
        return "exact"
    if left_text[:3] and left_text[:3] == right_text[:3]:
        return "genus_hint"
    if "UNI" in {left_text[:3], right_text[:3]}:
        return "unknown"
    return "different"


def _taxon_hint_match(left: str, right: str) -> str:
    if not left or not right:
        return "unknown"
    if left.lower() == right.lower():
        return "exact"
    return "different"


def _survey_index_or_none(config: Config, survey_id: str) -> int | None:
    try:
        return config.survey_index(survey_id)
    except Exception:
        return None


def _mode(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return ""
    return str(values.mode().iloc[0])


def _safe_float(value: object) -> float:
    try:
        if pd.isna(value):
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _first_tag(summary: dict[str, Any]) -> str:
    tags = summary.get("public_tags", [])
    if isinstance(tags, str):
        return tags.split("|")[0] if tags else str(summary.get("identity_tag", ""))
    return str(tags[0]) if tags else str(summary.get("identity_tag", ""))


def _value_counts(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if frame.empty or column not in frame:
        return {}
    return {str(key): int(value) for key, value in frame[column].value_counts(dropna=False).items()}


def _frame(rows: list[dict[str, object]], columns: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    for column in columns:
        if column not in frame:
            frame[column] = pd.Series(dtype="string")
    frame = frame[columns]
    for column in frame.columns:
        if column in NUMERIC_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
        elif column in BOOLEAN_COLUMNS:
            frame[column] = frame[column].fillna(False).astype(bool)
        else:
            frame[column] = frame[column].fillna("").astype(str)
    return frame


def _canonical_history(census: pd.DataFrame) -> pd.DataFrame:
    frame = census.copy()
    for column in CANONICAL_HISTORY_COLUMNS:
        if column not in frame:
            frame[column] = ""
    return frame[CANONICAL_HISTORY_COLUMNS].sort_values(
        ["plot", "identity_tag", "date", "stem_rank", "source_file", "source_row"],
        kind="mergesort",
    )

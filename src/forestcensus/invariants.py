"""Tree-level invariant report for canonical census review."""

from __future__ import annotations

from dataclasses import dataclass, replace
import json
from pathlib import Path
import re
from typing import Any, Iterable

import pandas as pd

from .adapters import load_historical_events
from .assembly import _tree_uid, assemble_events
from .config import Config
from .domain import MIN_MEASURED_DBH_MM
from .tree_ir import TreeDataset, TreeRecord, TreeSurvey
from .validate import Issue, IssueCode, validate_census


@dataclass(frozen=True)
class InvariantFinding:
    code: str
    tree_uid: str
    site: str
    plot: str
    identity_tag: str
    identity_label: str
    public_tag: str
    severity: str
    suggested_action: str
    summary: str
    details: dict[str, Any]
    resolution_kind: str = ""
    resolution_note: str = ""

    def to_record(self) -> dict[str, object]:
        return {
            "code": self.code,
            "tree_uid": self.tree_uid,
            "site": self.site,
            "plot": self.plot,
            "identity_tag": self.identity_tag,
            "identity_label": self.identity_label,
            "public_tag": self.public_tag,
            "severity": self.severity,
            "suggested_action": self.suggested_action,
            "summary": self.summary,
            "resolution_kind": self.resolution_kind,
            "resolution_note": self.resolution_note,
            "details": json.dumps(_jsonable(self.details), sort_keys=True),
        }


def build_invariant_report(
    raw_dir: str | Path,
    config: Config,
    *,
    apply_configured_decisions: bool = True,
) -> pd.DataFrame:
    """Build a tree-level invariant report from raw or post-decision events."""

    events = load_historical_events(
        raw_dir,
        config,
        apply_configured_decisions=apply_configured_decisions,
    ).copy()
    events["tree_uid"] = [
        _tree_uid(site, plot, tag)
        for site, plot, tag in zip(events["site"], events["plot"], events["identity_tag"])
    ]
    events["_survey_index"] = events["survey_id"].map(config.survey_index)
    pre_dataset = TreeDataset.from_events(events)

    census = assemble_events(events.drop(columns=["tree_uid", "_survey_index"]), config)
    census["_survey_index"] = census["survey_id"].map(config.survey_index)
    post_dataset = TreeDataset.from_events(census)
    issues = validate_census(census, config)

    findings: list[InvariantFinding] = []
    findings.extend(_nonqualifying_tree_findings(events, census, pre_dataset))
    findings.extend(_validation_issue_findings(census, post_dataset, issues))
    findings.extend(_first_qualifying_findings(post_dataset))
    findings.extend(_qualifying_rank_gap_findings(post_dataset))
    findings.extend(_duplicate_profile_findings(post_dataset))
    findings.extend(_health_transition_findings(post_dataset))
    findings.extend(_single_survey_death_sequence_findings(post_dataset))

    findings = _classify_findings(findings, post_dataset)
    findings = _apply_tree_resolutions(findings, config)
    records = [finding.to_record() for finding in findings]
    if not records:
        return pd.DataFrame(columns=list(InvariantFinding.__dataclass_fields__))
    return pd.DataFrame(records).sort_values(
        ["resolution_kind", "severity", "plot", "identity_tag", "code"],
        kind="mergesort",
    )


def write_invariant_report(report: pd.DataFrame, output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)
    return output_path


def invariant_summary(report: pd.DataFrame) -> dict[str, object]:
    if report.empty:
        return {"total": 0, "by_code": {}, "by_action": {}, "trees": 0}
    unresolved = report.loc[report["resolution_kind"].fillna("").eq("")]
    return {
        "total": int(len(report)),
        "unresolved": int(len(unresolved)),
        "trees": int(report["tree_uid"].nunique()),
        "unresolved_trees": int(unresolved["tree_uid"].nunique()),
        "by_code": report.groupby("code").size().astype(int).to_dict(),
        "by_action": report.groupby("suggested_action").size().astype(int).to_dict(),
    }


def _nonqualifying_tree_findings(
    events: pd.DataFrame,
    census: pd.DataFrame,
    pre_dataset: TreeDataset,
) -> list[InvariantFinding]:
    published_uids = set(census["tree_uid"])
    findings = []
    for tree_uid, tree in pre_dataset.trees.items():
        if tree_uid in published_uids:
            continue
        rows = events.loc[events["tree_uid"].eq(tree_uid)]
        dbhs = rows["dbh_mm"].dropna().astype(float).tolist()
        if not dbhs:
            continue
        findings.append(
            _finding(
                code="nonqualifying_tree_excluded",
                tree=tree,
                public_tag=_first_public_tag(tree),
                severity="info",
                suggested_action="auto_excluded",
                summary="Tree identity has no qualifying DBH measurement and was excluded from canonical output.",
                details={
                    "max_dbh": max(dbhs),
                    "dbh_values": dbhs,
                    "surveys": rows["survey_id"].drop_duplicates().astype(str).tolist(),
                    "field_statuses": rows["field_status"].drop_duplicates().astype(str).tolist(),
                    "notes": _unique_notes(rows),
                },
            )
        )
    return findings


def _validation_issue_findings(
    census: pd.DataFrame,
    dataset: TreeDataset,
    issues: Iterable[Issue],
) -> list[InvariantFinding]:
    issue_map = {
        IssueCode.W_BELOW_THRESHOLD_DBH: ("subthreshold_measurement", "strike_dbh_or_correct"),
        IssueCode.W_DBH_JUMP: ("max_dbh_jump", "review_or_correct"),
        IssueCode.W_TREE_RANKED_DBH_JUMP: ("ranked_dbh_jump", "review_or_correct"),
        IssueCode.W_TREE_STEM_COUNT_CHANGE: ("stem_count_change", "review_profile"),
        IssueCode.W_TREE_LARGE_STEM_APPEARANCE: ("large_stem_appearance", "review_or_insert_blank_history"),
        IssueCode.W_TREE_LARGE_STEM_DISAPPEARANCE: ("large_stem_disappearance", "review_or_insert_blank_gap"),
        IssueCode.W_ALIVE_HEALTH_CONFLICT: ("alive_health_conflict", "review_or_correct_health"),
        IssueCode.W_DEAD_HEALTH_CONFLICT: ("dead_health_conflict", "review_or_correct_health"),
        IssueCode.W_FOUND_NOTE_CONFLICT: ("found_note_conflict", "review_note_and_observation"),
        IssueCode.I_ZOMBIE_TREE: ("zombie_observed_dead_then_alive", "review_mortality_sequence"),
        IssueCode.W_TAXON_CONFLICT: ("taxon_conflict", "resolve_taxon_or_identity"),
    }
    findings = []
    for issue in issues:
        if issue.code not in issue_map:
            continue
        code, action = issue_map[issue.code]
        tree = dataset.trees.get(issue.tree_uid)
        if tree is None:
            continue
        rows = census.loc[census["tree_uid"].eq(issue.tree_uid)]
        findings.append(
            _finding(
                code=code,
                tree=tree,
                public_tag=issue.public_tag,
                severity=str(issue.severity),
                suggested_action=action,
                summary=issue.message,
                details={
                    **issue.details,
                    "survey_id": issue.survey_id,
                    "source_file": issue.source_file,
                    "source_row": issue.source_row,
                    "taxon_codes": sorted(rows["taxon_code"].dropna().astype(str).unique().tolist()),
                    "notes": _unique_notes(rows),
                    "local_notes": _issue_local_notes(rows, issue),
                },
            )
        )
    return findings


def _first_qualifying_findings(dataset: TreeDataset) -> list[InvariantFinding]:
    findings = []
    for tree in dataset.trees.values():
        ordered = tree.ordered_surveys()
        first_qualifying = _first_survey_with_profile(ordered)
        if first_qualifying is None:
            continue
        prior = [survey for survey in ordered if survey.survey_index < first_qualifying.survey_index]
        if not prior:
            continue
        prior_observed = [
            survey
            for survey in prior
            if survey.field_status in {"observed_alive", "observed_dead", "observed_unknown"}
        ]
        if not prior_observed:
            continue
        findings.append(
            _finding(
                code="first_qualifying_after_prior_observation",
                tree=tree,
                public_tag=first_qualifying.public_tag,
                severity="warning",
                suggested_action="review_or_insert_blank_history",
                summary="Tree has earlier observed evidence before its first qualifying DBH profile.",
                details={
                    "first_qualifying_survey": first_qualifying.survey_id,
                    "first_qualifying_profile": list(first_qualifying.dbh_profile(MIN_MEASURED_DBH_MM)),
                    "prior_observed_surveys": [survey.survey_id for survey in prior_observed],
                    "prior_statuses": [survey.field_status for survey in prior_observed],
                },
            )
        )
    return findings


def _qualifying_rank_gap_findings(dataset: TreeDataset) -> list[InvariantFinding]:
    findings = []
    for tree in dataset.trees.values():
        profiles = [
            (survey, list(survey.dbh_profile(MIN_MEASURED_DBH_MM)))
            for survey in tree.ordered_surveys()
        ]
        max_rank = max((len(profile) for _, profile in profiles), default=0)
        for rank in range(1, max_rank + 1):
            for start, end, before, after in _bounded_absent_runs(profiles, rank):
                gap_surveys = [survey.survey_id for survey, _ in profiles[start : end + 1]]
                findings.append(
                    _finding(
                        code="qualifying_rank_gap",
                        tree=tree,
                        public_tag=after[0].public_tag,
                        severity="warning",
                        suggested_action="insert_blank_gap_or_review",
                        summary="Qualifying ranked DBH is present, absent, then present again.",
                        details={
                            "rank": rank,
                            "gap_surveys": gap_surveys,
                            "before_survey": before[0].survey_id,
                            "before_dbh": before[1][rank - 1],
                            "after_survey": after[0].survey_id,
                            "after_dbh": after[1][rank - 1],
                        },
                    )
                )
    return findings


def _duplicate_profile_findings(dataset: TreeDataset) -> list[InvariantFinding]:
    findings = []
    for tree in dataset.trees.values():
        for survey in tree.ordered_surveys():
            profile = list(survey.dbh_profile(MIN_MEASURED_DBH_MM))
            if len(profile) == len(set(profile)):
                continue
            findings.append(
                _finding(
                    code="duplicate_dbh_profile_values",
                    tree=tree,
                    public_tag=survey.public_tag,
                    severity="warning",
                    suggested_action="review_duplicate_or_true_equal_stems",
                    summary="Survey has repeated qualifying DBH values within one tree profile.",
                    details={
                        "survey_id": survey.survey_id,
                        "dbh_profile": profile,
                    },
                )
            )
    return findings


def _health_transition_findings(dataset: TreeDataset) -> list[InvariantFinding]:
    findings = []
    for tree in dataset.trees.values():
        series = [
            (survey, _survey_max_health(survey))
            for survey in tree.ordered_surveys()
            if _survey_max_health(survey) is not None
        ]
        previous: tuple[TreeSurvey, float] | None = None
        for current in series:
            if previous is None:
                previous = current
                continue
            previous_survey, previous_health = previous
            current_survey, current_health = current
            if (
                previous_health >= 7
                and current_health <= 0
                and current_survey.field_status == "observed_dead"
            ):
                findings.append(
                    _finding(
                        code="sharp_health_drop_to_observed_dead",
                        tree=tree,
                        public_tag=current_survey.public_tag,
                        severity="warning",
                        suggested_action="review_mortality_or_source_row",
                        summary="Tree moves from high health to observed dead in the next measured health observation.",
                        details={
                            "previous_survey": previous_survey.survey_id,
                            "previous_health": previous_health,
                            "current_survey": current_survey.survey_id,
                            "current_health": current_health,
                            "current_field_status": current_survey.field_status,
                        },
                    )
                )
            if previous_health <= 2 and current_health >= previous_health + 5:
                findings.append(
                    _finding(
                        code="sharp_health_rebound",
                        tree=tree,
                        public_tag=current_survey.public_tag,
                        severity="warning",
                        suggested_action="review_zombie_or_health_typo",
                        summary="Tree has a sharp upward health rebound after very low health.",
                        details={
                            "previous_survey": previous_survey.survey_id,
                            "previous_health": previous_health,
                            "previous_field_status": previous_survey.field_status,
                            "current_survey": current_survey.survey_id,
                            "current_health": current_health,
                            "current_field_status": current_survey.field_status,
                        },
                    )
                )
            previous = current
    return findings


def _single_survey_death_sequence_findings(dataset: TreeDataset) -> list[InvariantFinding]:
    findings = []
    for tree in dataset.trees.values():
        observed = [
            (survey, _survey_max_health(survey))
            for survey in tree.ordered_surveys()
            if survey.field_status in {"observed_alive", "observed_dead"}
        ]
        for previous, current, next_observed in zip(observed, observed[1:], observed[2:]):
            previous_survey, previous_health = previous
            current_survey, current_health = current
            next_survey, next_health = next_observed
            if (
                previous_survey.field_status != "observed_alive"
                or current_survey.field_status != "observed_dead"
                or next_survey.field_status != "observed_alive"
            ):
                continue
            if previous_health is not None and previous_health >= 7:
                continue
            findings.append(
                _finding(
                    code="single_survey_death_label_sequence",
                    tree=tree,
                    public_tag=current_survey.public_tag,
                    severity="warning",
                    suggested_action="review_or_correct_single_death_row",
                    summary="A single observed-dead row is bracketed by observed-alive evidence.",
                    details={
                        "previous_survey": previous_survey.survey_id,
                        "previous_health": previous_health,
                        "current_survey": current_survey.survey_id,
                        "current_health": current_health,
                        "next_survey": next_survey.survey_id,
                        "next_health": next_health,
                        "current_field_status": current_survey.field_status,
                    },
                )
            )
    return findings


def _classify_findings(
    findings: list[InvariantFinding],
    dataset: TreeDataset,
) -> list[InvariantFinding]:
    classified = []
    for finding in findings:
        tree = dataset.trees.get(finding.tree_uid)
        if tree is None:
            classified.append(finding)
            continue
        classified.append(_classify_finding(finding, tree))
    return classified


def _classify_finding(finding: InvariantFinding, tree: TreeRecord) -> InvariantFinding:
    if finding.code == "subthreshold_measurement":
        return _reclassified(
            finding,
            code="subthreshold_dbh_present",
            severity="info",
            suggested_action="suppress_or_correct_subthreshold_dbh",
            summary="DBH is below the 50 mm measurement threshold and should not contribute to a qualifying profile.",
            reason="Subthreshold DBHs are preserved as evidence but treated separately from qualifying stem profiles.",
        )

    if finding.code == "dead_health_conflict":
        health = _maybe_float(finding.details.get("health_observed"))
        survey = _survey_by_id(tree, str(finding.details.get("survey_id", "")))
        if health is not None and 0 < health < 4 and survey is not None:
            if _has_later_observed_alive(tree, survey.survey_index):
                return _reclassified(
                    finding,
                    code="dead_label_low_health_later_alive",
                    severity="info",
                    suggested_action="treat_dead_label_as_uncertain_or_alive",
                    summary="Observed-dead label has low positive health and later observed-alive evidence.",
                    reason="Low positive health plus later alive evidence is more consistent with a mortality label error than true death.",
                )
            return _reclassified(
                finding,
                code="dead_low_health_to_zero_candidate",
                severity="info",
                suggested_action="set_dead_health_to_zero",
                summary="Observed-dead label has low positive health and no later observed-alive evidence.",
                    reason="Low positive health on an otherwise dead sequence should become canonical health 0.",
                )

    if finding.code == "sharp_health_drop_to_observed_dead":
        if _single_survey_death_label_outlier(finding, tree):
            return _reclassified(
                finding,
                code="single_survey_death_label_outlier",
                severity="warning",
                suggested_action="review_or_correct_single_death_row",
                summary="A single observed-dead row is bracketed by observed-alive evidence.",
                reason="Alive -> observed-dead/zero-health -> alive is usually a row-level mortality label or health typo.",
            )
        if not _has_later_observed_alive(tree, _finding_current_survey_index(finding, tree)):
            return _reclassified(
                finding,
                code="observed_mortality_event",
                severity="info",
                suggested_action="preserve_observed_mortality_event",
                summary="High-health tree transitions to observed dead with no later observed-alive evidence.",
                reason="A sharp drop to observed dead can be real mortality when the tree is not seen alive afterward.",
            )

    if finding.code == "sharp_health_rebound":
        if _health_rebound_is_alive_context(finding, tree):
            return _reclassified(
                finding,
                code="health_rebound_alive_context",
                severity="info",
                suggested_action="preserve_alive_health_context",
                summary="Health rebounds while adjacent surveys are both observed alive.",
                reason="A low health score followed by recovery is not a mortality contradiction when the datasheets keep the tree alive.",
            )
        if _health_rebound_has_new_stem_context(finding, tree):
            return _reclassified(
                finding,
                code="health_rebound_new_stem_context",
                severity="info",
                suggested_action="preserve_stem_level_health_context",
                summary="Health rebound coincides with a changed stem profile.",
                reason="Tree-level max health can rebound when a different or newly recorded stem carries the later health score.",
            )

    if finding.code == "single_survey_death_label_sequence":
        return _reclassified(
            finding,
            code="single_survey_low_health_death_label_outlier",
            severity="info",
            suggested_action="treat_single_death_row_as_uncertain",
            summary="A low-health alive sequence has one observed-dead row bracketed by observed-alive evidence.",
            reason="Alive low-health -> observed-dead/zero-health -> alive is usually a mortality label uncertainty rather than confirmed whole-tree death.",
        )

    if finding.code in {"zombie_observed_dead_then_alive", "sharp_health_rebound"} and _has_note_flag(
        finding,
        {"explicit_not_dead", "marked_dead_last_year"},
    ):
        return _reclassified(
            finding,
            code="explicit_note_mortality_correction_candidate",
            severity="info",
            suggested_action="treat_earlier_dead_label_as_uncertain",
            summary="Source notes explicitly contradict an earlier observed-dead label.",
            reason="Notes such as 'not dead' or 'marked dead last year' are strong evidence that the earlier mortality label was uncertain or wrong.",
        )

    if finding.code in {
        "zombie_observed_dead_then_alive",
        "sharp_health_rebound",
        "max_dbh_jump",
        "ranked_dbh_jump",
        "stem_count_change",
        "large_stem_appearance",
        "large_stem_disappearance",
    } and _has_note_flag(finding, {"tag_scope_note"}):
        return _reclassified(
            finding,
            code="tag_scope_note_review",
            severity="warning",
            suggested_action="review_tag_or_stem_scope_note",
            summary="Source notes suggest tag or stem-scope ambiguity.",
            reason="Notes such as 'to 5051', 'NO second stem', or 'could be one of the new tags' should stay in human identity/stem-scope review.",
        )

    if finding.code in {"zombie_observed_dead_then_alive", "sharp_health_rebound"} and _stem_mortality_context(finding, tree):
        return _reclassified(
            finding,
            code="stem_mortality_context",
            severity="info",
            suggested_action="preserve_stem_level_mortality_context",
            summary="Mortality/health transition has notes or profile context suggesting stem-level behavior.",
            reason="Alive/dead is recorded at the stem row level in some sources; mixed stems should not always be treated as whole-tree mortality.",
        )

    if finding.code in {
        "alive_health_conflict",
        "dead_health_conflict",
        "zombie_observed_dead_then_alive",
        "sharp_health_drop_to_observed_dead",
        "sharp_health_rebound",
    }:
        return _reclassified(
            finding,
            code="mortality_contradiction",
            severity=finding.severity,
            suggested_action="review_or_correct_health_status",
            summary=finding.summary,
            reason="Alive/dead labels, health scores, or observed mortality transitions disagree.",
        )

    if finding.code == "first_qualifying_after_prior_observation":
        if _first_qualifying_is_prior_dead_context(finding, tree):
            return _reclassified(
                finding,
                code="prior_dead_first_qualifying_dbh",
                severity="info",
                suggested_action="preserve_late_dead_dbh_context",
                summary="First qualifying DBH appears after prior observed-dead evidence.",
                reason="Later DBH on an already dead tree is usually delayed dead-stem measurement context, not a missing live history.",
            )
        if _first_qualifying_is_threshold_edge(finding):
            return _reclassified(
                finding,
                code="threshold_edge_dbh_context",
                severity="info",
                suggested_action="preserve_threshold_edge_context",
                summary="First qualifying DBH is close to the 50 mm inclusion threshold.",
                reason="Trees entering around 50-60 mm may simply have crossed the census threshold.",
            )
        return _reclassified(
            finding,
            code="prior_live_blank_dbh_history",
            severity="info",
            suggested_action="watch_or_insert_blank_history",
            summary="Tree has prior live/observed evidence before its first qualifying DBH profile.",
            reason="Prior live evidence without DBH is a candidate for blank-history rows, but not necessarily a row-level error.",
        )

    if finding.code in {
        "duplicate_dbh_profile_values",
        "stem_count_change",
        "large_stem_appearance",
        "large_stem_disappearance",
    } and _looks_like_duplicate_stem_artifact(finding):
        return _reclassified(
            finding,
            code="probable_duplicate_stem_artifact",
            severity="info",
            suggested_action="review_probable_duplicate_stem",
            summary="Repeated DBH profile coincides with a stem-count change and may be an extra duplicated stem entry.",
            reason="The larger adjacent profile contains repeated DBH values, matching the duplicate-stem artifact pattern.",
        )

    if finding.code in {
        "stem_count_change",
        "large_stem_appearance",
        "large_stem_disappearance",
    } and _looks_like_near_duplicate_stem_artifact(finding):
        return _reclassified(
            finding,
            code="near_duplicate_stem_artifact",
            severity="info",
            suggested_action="review_probable_near_duplicate_stem",
            summary="A one-survey stem-count change has near-identical DBH values.",
            reason="A May 2024 one-stem increase with a near-matching DBH often reflects duplicate entry rather than a true new stem.",
        )

    if finding.code in {"stem_count_change", "large_stem_appearance", "large_stem_disappearance"}:
        if _stem_profile_is_dead_tree_context(finding, tree):
            return _reclassified(
                finding,
                code="dead_tree_stem_context",
                severity="info",
                suggested_action="preserve_dead_stem_profile_context",
                summary="Stem-profile change occurs in a dead-tree context.",
                reason="Dead/fallen stems can disappear, reappear, or be measured inconsistently as they decay or become hard to find.",
            )
        if _stem_profile_is_small_multistem_gap(finding):
            return _reclassified(
                finding,
                code="threshold_multistem_gap_context",
                severity="info",
                suggested_action="preserve_threshold_multistem_gap",
                summary="Small multistem profile change is near the measurement threshold.",
                reason="Bounded gaps among small qualifying or subthreshold stems are usually stem-accounting context rather than urgent identity review.",
            )
        if _stem_mortality_context(finding, tree):
            return _reclassified(
                finding,
                code="stem_mortality_context",
                severity="info",
                suggested_action="preserve_stem_level_mortality_context",
                summary="Stem-profile change has notes or health evidence suggesting stem-level mortality.",
                reason="A tree can contain live and dead stems; stem-count changes in that context should be surfaced without forcing a whole-tree correction.",
            )
        if _stem_profile_is_threshold_edge(finding):
            return _reclassified(
                finding,
                code="threshold_edge_dbh_context",
                severity="info",
                suggested_action="preserve_threshold_edge_context",
                summary="Stem-profile change is close to the 50 mm inclusion threshold.",
                reason="New or disappearing stems near 50 mm can be threshold-edge survey membership rather than a data error.",
            )
        if _new_stem_is_threshold_context(finding, tree):
            return _reclassified(
                finding,
                code="threshold_new_stem_context",
                severity="info",
                suggested_action="preserve_threshold_new_stem_context",
                summary="Newly recorded qualifying stem is close to the 50 mm inclusion threshold.",
                reason="A secondary stem first recorded around 50-60 mm may have crossed the census threshold or been newly noticed, especially in clustered taxa.",
            )
        if _has_note_flag(finding, {"added_stem"}):
            return _reclassified(
                finding,
                code="new_noticed_stem_context",
                severity="info",
                suggested_action="watch_newly_noticed_stem",
                summary="A qualifying stem appears with an explicit added/new-stem note.",
                reason="An 'Added' or similar note suggests a real newly noticed stem; it may need blanks, but is not automatically suspicious.",
            )
        if _has_note_flag(finding, {"merge_note"}):
            return _reclassified(
                finding,
                code="merge_note_context",
                severity="info",
                suggested_action="watch_merge_note_context",
                summary="Stem-profile change has an explicit merge/combine note.",
                reason="Merge notes usually explain unusual stem accounting and should be retained as review context.",
            )

    if finding.code in {"stem_count_change", "large_stem_appearance"}:
        return _reclassified(
            finding,
            code="new_persistent_large_stem",
            severity="warning",
            suggested_action="review_or_insert_blank_history",
            summary="A qualifying stem appears in the ranked tree profile.",
            reason="A new qualifying stem can be real, but may need retrospective blank history if it was previously unreported.",
        )

    if finding.code == "large_stem_disappearance":
        if _current_survey_is_october_2025_protocol_gap(finding):
            return _reclassified(
                finding,
                code="oct_2025_protocol_missing_dbh",
                severity="info",
                suggested_action="preserve_october_2025_no_dbh",
                summary="October 2025 and later surveys may omit DBH by protocol.",
                reason="DBH collection was discontinued during the October 2025 survey; missing DBH is not itself suspicious.",
            )
        return _reclassified(
            finding,
            code="blank_missing_stem_backfill_candidate",
            severity="warning",
            suggested_action="review_or_insert_blank_gap",
            summary="A qualifying stem disappears from the ranked tree profile.",
            reason="A missing qualifying stem may represent not-found/not-reported evidence or a real fallen stem.",
        )

    if finding.code == "qualifying_rank_gap" and _gap_is_dead_tree_context(finding, tree):
        return _reclassified(
            finding,
            code="dead_tree_dbh_gap",
            severity="info",
            suggested_action="preserve_dead_tree_gap",
            summary="A dead-tree DBH profile has a bounded measurement gap.",
            reason="Dead or fallen trees can be hard to measure consistently; gaps are useful context but not automatic errors.",
        )

    if finding.code == "qualifying_rank_gap" and _bounded_gap_is_stem_context(finding, tree):
        return _reclassified(
            finding,
            code="bounded_stem_rank_gap",
            severity="info",
            suggested_action="watch_or_insert_blank_stem_gap",
            summary="A non-primary ranked stem has a bounded measurement gap.",
            reason="Ranked stems are survey-local; bounded gaps for secondary stems are better treated as blank-stem history context than hard errors.",
        )

    if finding.code in {"max_dbh_jump", "ranked_dbh_jump"}:
        if _has_note_flag(finding, {"not_dbh", "source_uncertainty"}):
            return _reclassified(
                finding,
                code="source_note_dbh_conflict",
                severity="warning",
                suggested_action="review_source_note_and_dbh",
                summary="DBH jump has a source note that directly questions or qualifies the measurement.",
                reason="Notes such as 'not 450' or uncertainty marks should keep the case in human review.",
            )
        if _threshold_edge_dbh_jump(finding):
            return _reclassified(
                finding,
                code="threshold_edge_dbh_context",
                severity="info",
                suggested_action="preserve_threshold_edge_context",
                summary="DBH jump occurs at the 50 mm inclusion threshold.",
                reason="Small live stems around 50 mm can cross in and out of qualifying status without implying a serious error.",
            )
        if _near_threshold_dead_dbh_context(finding, tree):
            return _reclassified(
                finding,
                code="dead_tree_threshold_dbh_context",
                severity="info",
                suggested_action="preserve_dead_tree_threshold_context",
                summary="Dead or failing tree has a DBH change near the measurement threshold.",
                reason="Small dead or failing stems near the threshold can lose measurable DBH without implying source/identity confusion.",
            )
        if _morella_cluster_rank_context(finding):
            return _reclassified(
                finding,
                code="morella_cluster_rank_jump_context",
                severity="info",
                suggested_action="preserve_multistem_rank_context",
                summary="Ranked DBH jump occurs in a multistem Morella/cluster context.",
                reason="Survey-local stem ranks can wobble in Morella or clustered multistem trees, especially when similar-sized stems appear only in recent surveys.",
            )
        stable_era = _stable_incompatible_era_context(finding, tree)
        if stable_era is not None:
            if _stable_era_is_dead_tree_loss(stable_era, tree):
                return _reclassified(
                    finding,
                    code="dead_tree_stable_dbh_loss_context",
                    severity="info",
                    suggested_action="preserve_dead_tree_dbh_change",
                    summary="Dead-tree DBH settles into a lower stable measurement era.",
                    reason="All compared observations are deadish and the later DBH era is lower, which can reflect decay, breakage, or changed measurability.",
                    extra_details=stable_era,
                )
            if _stable_era_is_early_low_source_candidate(stable_era):
                return _reclassified(
                    finding,
                    code="early_low_dbh_source_era_candidate",
                    severity="warning",
                    suggested_action="review_early_low_dbh_source_era",
                    summary="Early repeated low DBH values precede a much larger stable modern era.",
                    reason="A repeated early low value followed by a much larger stable tree may be a missing-leading-digit carry-forward or source/tag alignment problem.",
                    extra_details=stable_era,
                )
            return _reclassified(
                finding,
                code="stable_incompatible_dbh_era",
                severity="warning",
                suggested_action="review_source_era_or_identity_alignment",
                summary="DBH has stable but biologically incompatible measurement eras.",
                reason="Multiple adjacent surveys agree within each era, but the eras disagree too much to treat as ordinary growth or decay.",
                extra_details=stable_era,
            )
        if _has_note_flag(finding, {"structural_measurement"}, local=True):
            return _reclassified(
                finding,
                code="structural_measurement_dbh_context",
                severity="info",
                suggested_action="preserve_structural_measurement_context",
                summary="DBH change has structural field-note context.",
                reason="Horizontal, falling, bent, broken, girdled, or similar stems can change where and how DBH is measured.",
            )
        if _has_note_flag(finding, {"cluster_or_clump"}):
            return _reclassified(
                finding,
                code="cluster_measurement_dbh_context",
                severity="info",
                suggested_action="preserve_cluster_measurement_context",
                summary="DBH change occurs in a cluster/clump context.",
                reason="Clustered or clumped stems can make tree-level DBH profiles inconsistent without implying a simple typo.",
            )
        if _has_note_flag(finding, {"poison_ivy", "vine_or_parasite", "knot", "split_or_multistem", "non_circular"}):
            return _reclassified(
                finding,
                code="measurement_note_dbh_context",
                severity="info",
                suggested_action="preserve_measurement_context",
                summary="DBH change has field-note context that plausibly explains measurement inconsistency.",
                reason="Poison ivy, vines, knots, split trunks, or non-circular stems can create real measurement variation.",
            )
        if _dead_tree_dbh_increase(finding, tree):
            return _reclassified(
                finding,
                code="dead_tree_dbh_increase",
                severity="warning",
                suggested_action="review_dead_tree_dbh_increase",
                summary="Dead-tree DBH increases between adjacent observations.",
                reason="Dead trees can lose measurable diameter, but a large increase while dead is more suspicious and may indicate tag or row confusion.",
            )
        outlier_survey = _outlier_survey_for_jump(finding, tree)
        if outlier_survey:
            return _reclassified(
                finding,
                code="single_survey_dbh_outlier",
                severity="warning",
                suggested_action="review_or_correct_isolated_dbh",
                summary=f"DBH jump appears to be an isolated outlier in {outlier_survey}.",
                reason="The neighboring measured surveys return to a similar DBH baseline.",
                extra_details={"outlier_survey": outlier_survey},
            )
        if _dead_tree_dbh_loss(finding, tree):
            return _reclassified(
                finding,
                code="dead_tree_dbh_loss",
                severity="info",
                suggested_action="preserve_dead_tree_dbh_change",
                summary="Dead-tree DBH decreases between adjacent observations.",
                reason="Dead trees can genuinely lose DBH through decay, breakage, or fallen chunks.",
            )
        if _persistent_dbh_regime_shift(finding, tree):
            return _reclassified(
                finding,
                code="persistent_dbh_regime_shift",
                severity="warning",
                suggested_action="review_identity_or_measurement_regime",
                summary="DBH shifts into a new persistent measurement regime.",
                reason="The profile appears stable before and after the jump but at different DBH levels.",
            )

    return finding


def _reclassified(
    finding: InvariantFinding,
    *,
    code: str,
    severity: str,
    suggested_action: str,
    summary: str,
    reason: str,
    extra_details: dict[str, Any] | None = None,
) -> InvariantFinding:
    details = {
        **finding.details,
        "classified_from": finding.code,
        "classification_reason": reason,
    }
    if extra_details:
        details.update(extra_details)
    return replace(
        finding,
        code=code,
        severity=severity,
        suggested_action=suggested_action,
        summary=summary,
        details=details,
    )


def _looks_like_duplicate_stem_artifact(finding: InvariantFinding) -> bool:
    details = finding.details
    if _has_note_flag(finding, {"split_or_multistem"}):
        return False
    if finding.code == "duplicate_dbh_profile_values":
        return _profile_has_repeated_dbh(details.get("dbh_profile", []))

    previous = _float_profile(details.get("previous_dbh_profile", []))
    current = _float_profile(details.get("current_dbh_profile", []))
    if not previous or not current:
        return False
    if abs(len(current) - len(previous)) != 1:
        return False
    larger = current if len(current) > len(previous) else previous
    return _profile_has_repeated_dbh(larger)


def _looks_like_near_duplicate_stem_artifact(finding: InvariantFinding) -> bool:
    if _has_note_flag(finding, {"added_stem"}):
        return False
    details = finding.details
    previous = _float_profile(details.get("previous_dbh_profile", []))
    current = _float_profile(details.get("current_dbh_profile", []))
    if not previous or not current:
        return False
    if abs(len(current) - len(previous)) != 1:
        return False
    if "May_2024" not in {str(details.get("previous_survey", "")), str(details.get("current_survey", ""))}:
        return False
    larger = current if len(current) > len(previous) else previous
    return _profile_has_near_repeated_dbh(larger)


def _single_survey_death_label_outlier(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    if previous is None or current is None:
        return False
    if previous.field_status != "observed_alive" or current.field_status != "observed_dead":
        return False
    next_observed = [
        survey
        for survey in tree.ordered_surveys()
        if survey.survey_index > current.survey_index and survey.field_status in {"observed_alive", "observed_dead"}
    ]
    return bool(next_observed and next_observed[0].field_status == "observed_alive")


def _finding_current_survey_index(finding: InvariantFinding, tree: TreeRecord) -> int:
    survey = _survey_by_id(tree, str(finding.details.get("current_survey", finding.details.get("survey_id", ""))))
    return survey.survey_index if survey is not None else -1


def _health_rebound_is_alive_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    return (
        previous is not None
        and current is not None
        and previous.field_status == "observed_alive"
        and current.field_status == "observed_alive"
    )


def _health_rebound_has_new_stem_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    if previous is None or current is None:
        return False
    return len(current.dbh_profile(MIN_MEASURED_DBH_MM)) > len(previous.dbh_profile(MIN_MEASURED_DBH_MM))


def _first_qualifying_is_prior_dead_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    first = _survey_by_id(tree, str(finding.details.get("first_qualifying_survey", "")))
    prior_statuses = [str(status) for status in finding.details.get("prior_statuses", [])]
    if first is None or not prior_statuses:
        return False
    return _survey_is_deadish(first) and all(status == "observed_dead" for status in prior_statuses)


def _first_qualifying_is_threshold_edge(finding: InvariantFinding) -> bool:
    profile = _float_profile(finding.details.get("first_qualifying_profile", []))
    return bool(profile) and max(profile) <= 60


def _stem_profile_is_dead_tree_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    surveys = [survey for survey in [previous, current] if survey is not None]
    return bool(surveys) and all(_survey_is_deadish(survey) for survey in surveys)


def _stem_mortality_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    if _has_note_flag(finding, {"stem_mortality", "split_or_multistem", "cluster_or_clump"}):
        return True
    survey_ids = [
        str(finding.details.get(key, ""))
        for key in ["previous_survey", "current_survey", "before_survey", "after_survey", "survey_id"]
    ]
    for survey_id in survey_ids:
        survey = _survey_by_id(tree, survey_id)
        if survey is not None and _survey_has_mixed_health(survey):
            return True
    return False


def _stem_profile_is_threshold_edge(finding: InvariantFinding) -> bool:
    profiles = [
        _float_profile(finding.details.get("previous_dbh_profile", [])),
        _float_profile(finding.details.get("current_dbh_profile", [])),
    ]
    values = [value for profile in profiles for value in profile]
    return bool(values) and min(values) <= MIN_MEASURED_DBH_MM <= max(values) <= 60


def _stem_profile_is_small_multistem_gap(finding: InvariantFinding) -> bool:
    profiles = [
        _float_profile(finding.details.get("previous_dbh_profile", [])),
        _float_profile(finding.details.get("current_dbh_profile", [])),
    ]
    previous, current = profiles
    if not previous or not current:
        return False
    if abs(len(previous) - len(current)) != 1:
        return False
    values = [value for profile in profiles for value in profile]
    return bool(values) and max(values) <= 75


def _new_stem_is_threshold_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    if finding.code not in {"stem_count_change", "large_stem_appearance"}:
        return False
    previous = _float_profile(finding.details.get("previous_dbh_profile", []))
    current = _float_profile(finding.details.get("current_dbh_profile", []))
    if not previous or not current or len(current) <= len(previous):
        return False
    unmatched_current = _profile_unmatched_values(current, previous)
    if not unmatched_current or max(unmatched_current) > 60:
        return False
    taxon_codes = {str(code) for code in finding.details.get("taxon_codes", [])}
    return bool(taxon_codes & {"MORCER"}) or _has_note_flag(finding, {"cluster_or_clump"})


def _profile_unmatched_values(current: list[float], previous: list[float]) -> list[float]:
    unmatched = sorted(current)
    for previous_value in sorted(previous):
        if not unmatched:
            break
        match_index = min(
            range(len(unmatched)),
            key=lambda index: abs(unmatched[index] - previous_value),
        )
        unmatched.pop(match_index)
    return unmatched


def _bounded_gap_is_stem_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    try:
        rank = int(finding.details.get("rank", 0) or 0)
    except (TypeError, ValueError):
        rank = 0
    if rank < 2:
        return False
    before = _survey_by_id(tree, str(finding.details.get("before_survey", "")))
    after = _survey_by_id(tree, str(finding.details.get("after_survey", "")))
    if before is None or after is None:
        return False
    return len(before.dbh_profile(MIN_MEASURED_DBH_MM)) >= rank and len(after.dbh_profile(MIN_MEASURED_DBH_MM)) >= rank


def _threshold_edge_dbh_jump(finding: InvariantFinding) -> bool:
    previous = _maybe_float(finding.details.get("previous_dbh"))
    current = _maybe_float(finding.details.get("current_dbh"))
    if previous is None or current is None:
        return False
    return min(previous, current) <= MIN_MEASURED_DBH_MM <= max(previous, current) <= 60


def _near_threshold_dead_dbh_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    previous_dbh = _maybe_float(finding.details.get("previous_dbh"))
    current_dbh = _maybe_float(finding.details.get("current_dbh"))
    if previous is None or current is None or previous_dbh is None or current_dbh is None:
        return False
    values = [previous_dbh, current_dbh]
    if max(values) > 75 or min(values) > 60:
        return False
    return _survey_is_deadish(current) or (
        current.field_status in {"observed_alive", "missing_pending"} and (_survey_max_health(current) or 99) <= 3
    )


def _morella_cluster_rank_context(finding: InvariantFinding) -> bool:
    if finding.code != "ranked_dbh_jump":
        return False
    try:
        rank = int(finding.details.get("rank", 0) or 0)
    except (TypeError, ValueError):
        rank = 0
    if rank < 2:
        return False
    profiles = [
        _float_profile(finding.details.get("previous_dbh_profile", [])),
        _float_profile(finding.details.get("current_dbh_profile", [])),
    ]
    max_stem_count = max((len(profile) for profile in profiles), default=0)
    taxon_codes = {str(code) for code in finding.details.get("taxon_codes", [])}
    return max_stem_count >= 3 and ("MORCER" in taxon_codes or _has_note_flag(finding, {"cluster_or_clump"}))


def _dead_tree_dbh_increase(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    previous_dbh = _maybe_float(finding.details.get("previous_dbh"))
    current_dbh = _maybe_float(finding.details.get("current_dbh"))
    if previous is None or current is None or previous_dbh is None or current_dbh is None:
        return False
    return current_dbh > previous_dbh and _survey_is_deadish(previous) and _survey_is_deadish(current)


def _survey_max_health(survey: TreeSurvey) -> float | None:
    values = [stem.health_observed for stem in survey.stems if stem.health_observed is not None]
    return max(values) if values else None


def _has_later_observed_alive(tree: TreeRecord, survey_index: int) -> bool:
    return any(
        survey.survey_index > survey_index and survey.field_status == "observed_alive"
        for survey in tree.ordered_surveys()
    )


def _has_note_flag(finding: InvariantFinding, flags: set[str], *, local: bool = False) -> bool:
    return bool(_note_flags_for_finding(finding, local=local) & flags)


def _note_flags_for_finding(finding: InvariantFinding, *, local: bool = False) -> set[str]:
    flags = set()
    notes = finding.details.get("local_notes" if local else "notes", [])
    if not isinstance(notes, list | tuple):
        notes = [notes]
    for note in notes:
        text = str(note).lower()
        if not text:
            continue
        if "poison" in text or "ivy" in text:
            flags.add("poison_ivy")
        if any(needle in text for needle in ["vine", "liana", "parasite"]):
            flags.add("vine_or_parasite")
        if "knot" in text:
            flags.add("knot")
        if any(needle in text for needle in ["split", "trunk", "stem", "multistem", "multi-stem"]):
            flags.add("split_or_multistem")
        if any(needle in text for needle in ["cluster", "clump"]):
            flags.add("cluster_or_clump")
        if any(needle in text for needle in ["dead second", "second stem dead", "one dbh dead", "dead stem", "dead trunk"]):
            flags.add("stem_mortality")
        if any(needle in text for needle in ["added", "new stem", "new trunk"]):
            flags.add("added_stem")
        if (
            "no second stem" in text
            or "could be one of the new tags" in text
            or "new tags" in text
            or "tag on trunk" in text
            or re.search(r"\bto\s+\d+\b", text)
        ):
            flags.add("tag_scope_note")
        if any(needle in text for needle in ["merge", "combine"]):
            flags.add("merge_note")
        if any(needle in text for needle in ["not circle", "non-circular", "non circular", "weird"]):
            flags.add("non_circular")
        if any(
            needle in text
            for needle in [
                "horizontal",
                "falling",
                "fallen",
                "bent",
                "elbow",
                "girdle",
                "girdled",
                "girdling",
                "snapped",
                "broken",
                "break",
                "leaning",
            ]
        ):
            flags.add("structural_measurement")
        if "marked dead last year" in text or "marked as dead last year" in text:
            flags.add("marked_dead_last_year")
        if "not dead" in text:
            flags.add("explicit_not_dead")
        if "not " in text and "dbh" in text:
            flags.add("not_dbh")
        if "?" in text or any(needle in text for needle in ["might be", "maybe", "approx", "check"]):
            flags.add("source_uncertainty")
    return flags


def _current_survey_is_october_2025_protocol_gap(finding: InvariantFinding) -> bool:
    return str(finding.details.get("current_survey", "")) == "October_2025"


def _gap_is_dead_tree_context(finding: InvariantFinding, tree: TreeRecord) -> bool:
    before = _survey_by_id(tree, str(finding.details.get("before_survey", "")))
    after = _survey_by_id(tree, str(finding.details.get("after_survey", "")))
    if before is None or after is None:
        return False
    return _survey_is_deadish(before) and _survey_is_deadish(after)


def _dead_tree_dbh_loss(finding: InvariantFinding, tree: TreeRecord) -> bool:
    previous = _survey_by_id(tree, str(finding.details.get("previous_survey", "")))
    current = _survey_by_id(tree, str(finding.details.get("current_survey", "")))
    previous_dbh = _maybe_float(finding.details.get("previous_dbh"))
    current_dbh = _maybe_float(finding.details.get("current_dbh"))
    if previous is None or current is None or previous_dbh is None or current_dbh is None:
        return False
    return current_dbh < previous_dbh and _survey_is_deadish(previous) and _survey_is_deadish(current)


def _outlier_survey_for_jump(finding: InvariantFinding, tree: TreeRecord) -> str:
    rank = int(finding.details.get("rank", 0) or 0) if finding.code == "ranked_dbh_jump" else 0
    series = _dbh_series(tree, rank=rank)
    if len(series) < 3:
        return ""

    current_id = str(finding.details.get("current_survey", ""))
    current_index = next((index for index, item in enumerate(series) if item[0].survey_id == current_id), None)
    if current_index is None:
        return ""

    current = series[current_index][1]
    previous = series[current_index - 1][1] if current_index >= 1 else None
    next_value = series[current_index + 1][1] if current_index + 1 < len(series) else None
    if previous is not None and next_value is not None and _similar_dbh(previous, next_value) and _large_dbh_difference(current, previous):
        return series[current_index][0].survey_id

    if current_index >= 2:
        previous_previous = series[current_index - 2][1]
        if _similar_dbh(previous_previous, current) and _large_dbh_difference(previous, current):
            return series[current_index - 1][0].survey_id
    return ""


def _persistent_dbh_regime_shift(finding: InvariantFinding, tree: TreeRecord) -> bool:
    rank = int(finding.details.get("rank", 0) or 0) if finding.code == "ranked_dbh_jump" else 0
    series = _dbh_series(tree, rank=rank)
    current_id = str(finding.details.get("current_survey", ""))
    current_index = next((index for index, item in enumerate(series) if item[0].survey_id == current_id), None)
    if current_index is None or current_index < 1 or current_index + 1 >= len(series):
        return False
    previous = series[current_index - 1][1]
    current = series[current_index][1]
    next_value = series[current_index + 1][1]
    return _similar_dbh(current, next_value) and _large_dbh_difference(previous, current)


def _stable_incompatible_era_context(finding: InvariantFinding, tree: TreeRecord) -> dict[str, object] | None:
    rank = int(finding.details.get("rank", 0) or 0) if finding.code == "ranked_dbh_jump" else 0
    series = _dbh_series(tree, rank=rank)
    current_id = str(finding.details.get("current_survey", ""))
    previous_id = str(finding.details.get("previous_survey", ""))
    if len(series) < 4 or not current_id:
        return None
    runs = _stable_dbh_runs(series)
    for left, right in zip(runs, runs[1:]):
        if len(left) < 2 or len(right) < 2:
            continue
        left_mean = _mean_dbh_run(left)
        right_mean = _mean_dbh_run(right)
        if not _large_dbh_difference(left_mean, right_mean):
            continue
        boundary_ids = {left[-1][0].survey_id, right[0][0].survey_id}
        if current_id not in boundary_ids and previous_id not in boundary_ids:
            continue
        return {
            "stable_era_left_surveys": [survey.survey_id for survey, _ in left],
            "stable_era_left_dbhs": [value for _, value in left],
            "stable_era_left_mean_dbh": left_mean,
            "stable_era_right_surveys": [survey.survey_id for survey, _ in right],
            "stable_era_right_dbhs": [value for _, value in right],
            "stable_era_right_mean_dbh": right_mean,
        }
    return None


def _stable_era_is_dead_tree_loss(stable_era: dict[str, object], tree: TreeRecord) -> bool:
    left_mean = _maybe_float(stable_era.get("stable_era_left_mean_dbh"))
    right_mean = _maybe_float(stable_era.get("stable_era_right_mean_dbh"))
    if left_mean is None or right_mean is None or right_mean >= left_mean:
        return False
    survey_ids = [
        str(survey_id)
        for key in ["stable_era_left_surveys", "stable_era_right_surveys"]
        for survey_id in stable_era.get(key, [])
    ]
    if not survey_ids:
        return False
    surveys = [_survey_by_id(tree, survey_id) for survey_id in survey_ids]
    return all(survey is not None and _survey_is_deadish(survey) for survey in surveys)


def _stable_era_is_early_low_source_candidate(stable_era: dict[str, object]) -> bool:
    left_mean = _maybe_float(stable_era.get("stable_era_left_mean_dbh"))
    right_mean = _maybe_float(stable_era.get("stable_era_right_mean_dbh"))
    if left_mean is None or right_mean is None:
        return False
    left_surveys = [str(survey_id) for survey_id in stable_era.get("stable_era_left_surveys", [])]
    if not left_surveys or not all(survey_id in {"June_2019", "June_2020"} for survey_id in left_surveys):
        return False
    return left_mean <= 80 and right_mean >= 120 and (right_mean - left_mean >= 80 or right_mean / left_mean >= 2)


def _stable_dbh_runs(series: list[tuple[TreeSurvey, float]]) -> list[list[tuple[TreeSurvey, float]]]:
    if not series:
        return []
    runs: list[list[tuple[TreeSurvey, float]]] = [[series[0]]]
    for item in series[1:]:
        if _similar_dbh(runs[-1][-1][1], item[1]):
            runs[-1].append(item)
        else:
            runs.append([item])
    return runs


def _mean_dbh_run(run: list[tuple[TreeSurvey, float]]) -> float:
    return sum(value for _, value in run) / len(run)


def _dbh_series(tree: TreeRecord, *, rank: int = 0) -> list[tuple[TreeSurvey, float]]:
    series = []
    for survey in tree.ordered_surveys():
        profile = list(survey.dbh_profile(MIN_MEASURED_DBH_MM))
        if not profile:
            continue
        if rank > 0:
            if len(profile) < rank:
                continue
            value = profile[rank - 1]
        else:
            value = max(profile)
        series.append((survey, float(value)))
    return series


def _survey_by_id(tree: TreeRecord, survey_id: str) -> TreeSurvey | None:
    for survey in tree.ordered_surveys():
        if survey.survey_id == survey_id:
            return survey
    return None


def _survey_is_deadish(survey: TreeSurvey) -> bool:
    if survey.field_status == "observed_unknown":
        return False
    if survey.field_status == "observed_dead":
        return True
    healths = [stem.health_observed for stem in survey.stems if stem.health_observed is not None]
    return bool(healths) and max(healths) <= 0


def _survey_has_mixed_health(survey: TreeSurvey) -> bool:
    healths = [stem.health_observed for stem in survey.stems if stem.health_observed is not None]
    return any(health <= 0 for health in healths) and any(health > 0 for health in healths)


def _profile_has_repeated_dbh(profile: object) -> bool:
    values = _float_profile(profile)
    return len(values) != len(set(values))


def _profile_has_near_repeated_dbh(profile: object) -> bool:
    values = sorted(_float_profile(profile))
    for left, right in zip(values, values[1:]):
        if abs(left - right) <= max(3.0, 0.015 * max(abs(left), abs(right))):
            return True
    return False


def _float_profile(profile: object) -> list[float]:
    if not isinstance(profile, list | tuple):
        return []
    values = []
    for value in profile:
        parsed = _maybe_float(value)
        if parsed is not None:
            values.append(parsed)
    return values


def _maybe_float(value: object) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _similar_dbh(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) <= max(8.0, 0.08 * max(abs(left), abs(right)))


def _large_dbh_difference(left: float | None, right: float | None) -> bool:
    if left is None or right is None:
        return False
    return abs(left - right) >= max(20.0, 0.16 * max(abs(left), abs(right)))


def _apply_tree_resolutions(
    findings: list[InvariantFinding],
    config: Config,
) -> list[InvariantFinding]:
    resolutions = list(config.tree_resolutions)
    if not resolutions:
        return findings
    resolved = []
    for finding in findings:
        resolution = next(
            (
                item
                for item in resolutions
                if _resolution_matches(item.tree, finding)
                and (not item.codes or finding.code in item.codes)
            ),
            None,
        )
        if resolution is None:
            resolved.append(finding)
            continue
        resolved.append(
            InvariantFinding(
                **{
                    **finding.__dict__,
                    "resolution_kind": resolution.kind,
                    "resolution_note": resolution.note,
                }
            )
        )
    return resolved


def _resolution_matches(selector: dict[str, object], finding: InvariantFinding) -> bool:
    for field, expected in selector.items():
        if str(getattr(finding, field)) != str(expected):
            return False
    return True


def _first_survey_with_profile(surveys: tuple[TreeSurvey, ...]) -> TreeSurvey | None:
    for survey in surveys:
        if survey.dbh_profile(MIN_MEASURED_DBH_MM):
            return survey
    return None


def _bounded_absent_runs(
    profiles: list[tuple[TreeSurvey, list[float]]],
    rank: int,
) -> list[tuple[int, int, tuple[TreeSurvey, list[float]], tuple[TreeSurvey, list[float]]]]:
    runs = []
    index = 0
    while index < len(profiles):
        if len(profiles[index][1]) >= rank:
            index += 1
            continue
        start = index
        while index < len(profiles) and len(profiles[index][1]) < rank:
            index += 1
        end = index - 1
        before = [item for item in profiles[:start] if len(item[1]) >= rank]
        after = [item for item in profiles[index:] if len(item[1]) >= rank]
        if before and after:
            runs.append((start, end, before[-1], after[0]))
    return runs


def _finding(
    code: str,
    tree: TreeRecord,
    public_tag: str,
    severity: str,
    suggested_action: str,
    summary: str,
    details: dict[str, Any],
) -> InvariantFinding:
    return InvariantFinding(
        code=code,
        tree_uid=tree.tree_uid,
        site=tree.site,
        plot=tree.plot,
        identity_tag=tree.identity_tag,
        identity_label=tree.identity_label,
        public_tag=public_tag,
        severity=severity,
        suggested_action=suggested_action,
        summary=summary,
        details=details,
    )


def _first_public_tag(tree: TreeRecord) -> str:
    for survey in tree.ordered_surveys():
        if survey.public_tag:
            return survey.public_tag
    return ""


def _unique_notes(rows: pd.DataFrame) -> list[str]:
    return [
        str(note)
        for note in rows["notes"].dropna().astype(str).drop_duplicates()
        if str(note).strip()
    ]


def _issue_local_notes(rows: pd.DataFrame, issue: Issue) -> list[str]:
    survey_ids = {str(issue.survey_id)}
    for key in [
        "previous_survey",
        "current_survey",
        "before_survey",
        "after_survey",
        "first_qualifying_survey",
    ]:
        value = issue.details.get(key)
        if value:
            survey_ids.add(str(value))
    if "survey_id" not in rows.columns or "notes" not in rows.columns:
        return []
    local = rows.loc[rows["survey_id"].astype(str).isin(survey_ids)]
    return _unique_notes(local)


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(v) for v in value]
    if pd.isna(value):
        return None
    return value

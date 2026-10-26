"""Command line interface for the forest census pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .adapters import load_historical_events
from .assembly import assemble_events
from .canonical_review import build_canonical_review, write_canonical_review
from .config import load_config
from .datasheets import (
    DEFAULT_DATASHEET_DIFFICULTY,
    DEFAULT_FIELD_SURVEY_ID,
    DEFAULT_RECENT_SURVEYS,
    build_datasheet_prep,
    write_datasheet_prep,
    write_plot_datasheets,
)
from .decisions import write_configured_decision_ledger
from .evidence import build_evidence_ledger, write_evidence_ledger
from .field_packet import write_field_packet
from .invariants import build_invariant_report, invariant_summary, write_invariant_report
from .llm_transcribe import (
    add_transcribe_parser,
    run_materialize_review_command,
    run_rematerialize_command,
    run_transcribe_command,
)
from .publish import build_census, promote_candidate
from .validate import validate_census, write_diagnostics, write_issue_context


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="forestcensus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build the canonical parquet dataset")
    build.add_argument("--raw-dir", default="data/raw/forest_census")
    build.add_argument("--config-dir", default="config")
    build.add_argument("--out", default=None)

    promote = subparsers.add_parser("publish-candidate", help="Promote an approved build after fingerprint checks")
    promote.add_argument("candidate")
    promote.add_argument("--out", default="output/forest_census.parquet")

    packet = subparsers.add_parser("field-packet", help="Generate an audited search roster with targeted recheck questions")
    packet.add_argument("--parquet", default="output/forest_census.parquet")
    packet.add_argument("--policy", required=True)
    packet.add_argument("--out-dir", required=True, help="New directory; existing packets cannot be overwritten")

    validate = subparsers.add_parser("validate", help="Validate an existing canonical parquet")
    validate.add_argument("parquet", nargs="?", default="output/forest_census.parquet")
    validate.add_argument("--config-dir", default="config")
    validate.add_argument("--out-dir", default="output/diagnostics")

    inspect = subparsers.add_parser("inspect", help="Write context rows for a diagnostic code")
    inspect.add_argument("code")
    inspect.add_argument("parquet", nargs="?", default="output/forest_census.parquet")
    inspect.add_argument("--config-dir", default="config")
    inspect.add_argument("--out", default=None)

    invariants = subparsers.add_parser("invariants", help="Write tree-level invariant review report")
    invariants.add_argument("--raw-dir", default="data/raw/forest_census")
    invariants.add_argument("--config-dir", default="config")
    invariants.add_argument("--out", default="output/diagnostics/invariants.csv")
    invariants.add_argument("--decision-stage", choices=["raw", "post"], default="post")

    raw_diagnostics = subparsers.add_parser(
        "diagnose-raw",
        help="Run validation and invariant diagnostics before accepted decisions are applied",
    )
    raw_diagnostics.add_argument("--raw-dir", default="data/raw/forest_census")
    raw_diagnostics.add_argument("--config-dir", default="config")
    raw_diagnostics.add_argument("--out-dir", default="output/raw_diagnostics")

    decisions = subparsers.add_parser("decisions", help="Write the unified configured decision ledger")
    decisions.add_argument("--config-dir", default="config")
    decisions.add_argument("--out-dir", default="output/decisions")

    evidence = subparsers.add_parser("evidence", help="Build queryable evidence ledger tables")
    evidence.add_argument("--raw-dir", default="data/raw/forest_census")
    evidence.add_argument(
        "--archive-dir",
        default="data/raw/forest_census/original_drive_records",
    )
    evidence.add_argument("--config-dir", default="config")
    evidence.add_argument("--out-dir", default="output/evidence")

    canonical_review = subparsers.add_parser(
        "canonical-review",
        help="Build non-destructive canonical identity review/proposal artifacts",
    )
    canonical_review.add_argument("--parquet", default="output/forest_census.parquet")
    canonical_review.add_argument("--evidence-dir", default="output/evidence")
    canonical_review.add_argument("--invariants", default="output/diagnostics/invariants.csv")
    canonical_review.add_argument("--issues", default="output/diagnostics/issues.csv")
    canonical_review.add_argument("--config-dir", default="config")
    canonical_review.add_argument("--out-dir", default="output/canonical_review")
    canonical_review.add_argument("--priority-case-limit", type=int, default=200)

    datasheet_prep = subparsers.add_parser(
        "datasheet-prep",
        help="Prepare active recent stem tables for upcoming census datasheets",
    )
    datasheet_prep.add_argument("--parquet", default="output/forest_census.parquet")
    datasheet_prep.add_argument("--out-dir", default="output/datasheet_prep")
    datasheet_prep.add_argument("--survey", action="append", dest="surveys", default=None)

    datasheets = subparsers.add_parser(
        "datasheets",
        help="Generate per-plot Typst/PDF field datasheets from datasheet prep output",
    )
    datasheets.add_argument("--active-stems", default="output/datasheet_prep/active_stems_found_last2.csv")
    datasheets.add_argument("--out-dir", default="output/datasheets_2026")
    datasheets.add_argument("--survey-id", default=DEFAULT_FIELD_SURVEY_ID)
    datasheets.add_argument("--difficulty", default=DEFAULT_DATASHEET_DIFFICULTY)
    datasheets.add_argument("--template", default="prototypes/datasheets/portrait_prototype.typ")
    datasheets.add_argument("--compile", action=argparse.BooleanOptionalAction, default=True)
    datasheets.add_argument("--rows-per-page", type=int, default=40)

    add_transcribe_parser(subparsers)

    args = parser.parse_args(argv)
    if args.command == "build":
        census = build_census(args.raw_dir, args.config_dir, args.out)
        output = Path(args.out) if args.out else Path("output/forest_census.parquet")
        print(json.dumps({"rows": len(census), "output": str(output)}, sort_keys=True))
    elif args.command == "publish-candidate":
        print(json.dumps(promote_candidate(args.candidate, args.out), sort_keys=True))
    elif args.command == "field-packet":
        print(json.dumps(write_field_packet(args.parquet, args.policy, args.out_dir), sort_keys=True))
    elif args.command == "validate":
        config = load_config(args.config_dir)
        census = pd.read_parquet(args.parquet)
        issues = validate_census(census, config)
        summary = write_diagnostics(issues, args.out_dir)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "inspect":
        config = load_config(args.config_dir)
        census = pd.read_parquet(args.parquet)
        issues = validate_census(census, config)
        output = Path(args.out) if args.out else Path("output/diagnostics") / f"{args.code.lower()}_context.csv"
        context = write_issue_context(census, issues, args.code, output)
        print(json.dumps({"rows": len(context), "output": str(output)}, sort_keys=True))
    elif args.command == "invariants":
        config = load_config(args.config_dir)
        report = build_invariant_report(
            args.raw_dir,
            config,
            apply_configured_decisions=args.decision_stage == "post",
        )
        output = write_invariant_report(report, args.out)
        print(json.dumps({**invariant_summary(report), "output": str(output)}, sort_keys=True))
    elif args.command == "diagnose-raw":
        config = load_config(args.config_dir)
        out_dir = Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        events = load_historical_events(args.raw_dir, config, apply_configured_decisions=False)
        census = assemble_events(events, config)
        raw_parquet = out_dir / "raw_forest_census.parquet"
        census.to_parquet(raw_parquet, index=False)
        issues = validate_census(census, config)
        issue_summary = write_diagnostics(issues, out_dir)
        report = build_invariant_report(args.raw_dir, config, apply_configured_decisions=False)
        invariant_path = write_invariant_report(report, out_dir / "invariants.csv")
        summary = {
            "raw_census": str(raw_parquet),
            "rows": int(len(census)),
            "diagnostics": issue_summary,
            "invariants": {**invariant_summary(report), "output": str(invariant_path)},
        }
        summary_path = out_dir / "summary.json"
        summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        summary["summary"] = str(summary_path)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "decisions":
        config = load_config(args.config_dir)
        summary = write_configured_decision_ledger(config, args.out_dir)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "evidence":
        config = load_config(args.config_dir)
        frames = build_evidence_ledger(args.raw_dir, args.archive_dir, config)
        summary = write_evidence_ledger(frames, args.out_dir)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "canonical-review":
        config = load_config(args.config_dir)
        census = pd.read_parquet(args.parquet)
        evidence_dir = Path(args.evidence_dir)
        evidence_observations = pd.read_parquet(evidence_dir / "evidence_observations.parquet")
        tag_change_assertions = pd.read_parquet(evidence_dir / "tag_change_assertions.parquet")
        invariants = pd.read_csv(args.invariants) if Path(args.invariants).exists() else pd.DataFrame()
        issues = pd.read_csv(args.issues) if Path(args.issues).exists() else pd.DataFrame()
        frames = build_canonical_review(
            census,
            evidence_observations,
            tag_change_assertions,
            invariants,
            issues,
            config,
            priority_case_limit=args.priority_case_limit,
        )
        summary = write_canonical_review(frames, args.out_dir)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "datasheet-prep":
        census = pd.read_parquet(args.parquet)
        surveys = args.surveys if args.surveys else DEFAULT_RECENT_SURVEYS
        frames = build_datasheet_prep(census, recent_surveys=surveys)
        summary = write_datasheet_prep(frames, args.out_dir)
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "datasheets":
        active_stems = pd.read_csv(args.active_stems)
        summary = write_plot_datasheets(
            active_stems,
            args.out_dir,
            survey_id=args.survey_id,
            difficulty=args.difficulty,
            template=args.template,
            compile_pdfs=args.compile,
            rows_per_page=args.rows_per_page,
        )
        print(json.dumps(summary, sort_keys=True))
    elif args.command == "transcribe-pdf":
        run_transcribe_command(args)
    elif args.command == "materialize-llm-review":
        run_materialize_review_command(args)
    elif args.command == "rematerialize-llm-run":
        run_rematerialize_command(args)
    elif args.command == "rebuild-review-layout":
        from .review_layout import rebuild_review_layouts

        print(json.dumps(rebuild_review_layouts(args.run_dir, overrides_path=args.overrides)))


if __name__ == "__main__":
    main()

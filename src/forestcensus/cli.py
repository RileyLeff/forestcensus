"""Command line interface for the forest census pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .config import load_config
from .llm_transcribe import add_transcribe_parser, run_transcribe_command
from .publish import build_census
from .validate import validate_census, write_diagnostics, write_issue_context


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="forestcensus")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build the canonical parquet dataset")
    build.add_argument("--raw-dir", default="data/raw/forest_census")
    build.add_argument("--config-dir", default="config")
    build.add_argument("--out", default=None)

    validate = subparsers.add_parser("validate", help="Validate an existing canonical parquet")
    validate.add_argument("parquet", nargs="?", default="output/forest_census.parquet")
    validate.add_argument("--config-dir", default="config")
    validate.add_argument("--out-dir", default="output/diagnostics")

    inspect = subparsers.add_parser("inspect", help="Write context rows for a diagnostic code")
    inspect.add_argument("code")
    inspect.add_argument("parquet", nargs="?", default="output/forest_census.parquet")
    inspect.add_argument("--config-dir", default="config")
    inspect.add_argument("--out", default=None)

    add_transcribe_parser(subparsers)

    args = parser.parse_args(argv)
    if args.command == "build":
        census = build_census(args.raw_dir, args.config_dir, args.out)
        output = Path(args.out) if args.out else Path("output/forest_census.parquet")
        print(json.dumps({"rows": len(census), "output": str(output)}, sort_keys=True))
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
    elif args.command == "transcribe-pdf":
        run_transcribe_command(args)


if __name__ == "__main__":
    main()

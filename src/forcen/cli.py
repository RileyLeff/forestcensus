"""Typer CLI entrypoint for forcen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .engine import (
    BuildError,
    SubmitError,
    SubmitResult,
    build_workspace,
    lint_transaction,
    submit_transaction,
)
from .exceptions import ConfigError, ForcenError
from .transactions import NormalizationConfig
from .transactions.exceptions import (
    TransactionDataError,
    TransactionError,
    TransactionFormatError,
)
from .dsl.exceptions import DSLParseError
from .ledger.storage import Ledger


EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 2
EXIT_DSL_ERROR = 3
EXIT_IO_ERROR = 4
EXIT_CONFIG_ERROR = 5


app = typer.Typer(help="Forest census transaction engine")
tx_app = typer.Typer(help="Transaction commands")
versions_app = typer.Typer(help="Version inspection")
app.add_typer(tx_app, name="tx")
app.add_typer(versions_app, name="versions")


@app.callback()
def main_callback() -> None:
    """Base command callback reserved for shared options."""


@tx_app.command("lint")
def tx_lint(
    tx_dir: Path = typer.Argument(..., exists=True, file_okay=False, readable=True),
    config_dir: Path = typer.Option(
        Path("config"),
        "--config",
        "-c",
        help="Path to configuration directory",
    ),
    report_path: Optional[Path] = typer.Option(
        None,
        "--report",
        help="Optional path for lint report JSON (defaults to <txdir>/lint-report.json)",
    ),
) -> None:
    """Lint a transaction directory."""

    report_path = report_path or tx_dir / "lint-report.json"

    try:
        report = lint_transaction(
            transaction_dir=tx_dir,
            config_dir=config_dir,
            normalization=NormalizationConfig(),
        )
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR) from exc
    except DSLParseError as exc:
        typer.echo(f"DSL parse error: {exc}", err=True)
        raise typer.Exit(EXIT_DSL_ERROR) from exc
    except TransactionFormatError as exc:
        typer.echo(f"Transaction error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc
    except TransactionDataError as exc:
        typer.echo(f"Transaction data error: {exc}", err=True)
        raise typer.Exit(EXIT_VALIDATION_ERROR) from exc
    except TransactionError as exc:
        typer.echo(f"Transaction error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc
    except ForcenError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    json_payload = json.dumps(report.as_dict(), indent=2)
    typer.echo(json_payload)

    try:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json_payload + "\n", encoding="utf-8")
    except OSError as exc:
        typer.echo(f"Failed to write report {report_path}: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    if report.has_errors:
        raise typer.Exit(EXIT_VALIDATION_ERROR)


@tx_app.command("submit")
def tx_submit(
    tx_dir: Path = typer.Argument(..., exists=True, file_okay=False, readable=True),
    config_dir: Path = typer.Option(
        Path("config"),
        "--config",
        "-c",
        help="Path to configuration directory",
    ),
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state",
    ),
) -> None:
    """Submit a transaction and update the ledger."""

    try:
        result = submit_transaction(
            transaction_dir=tx_dir,
            config_dir=config_dir,
            workspace=workspace,
            normalization=NormalizationConfig(),
        )
    except SubmitError as exc:
        typer.echo(f"Submit error: {exc}", err=True)
        raise typer.Exit(EXIT_VALIDATION_ERROR) from exc
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR) from exc
    except DSLParseError as exc:
        typer.echo(f"DSL parse error: {exc}", err=True)
        raise typer.Exit(EXIT_DSL_ERROR) from exc
    except TransactionFormatError as exc:
        typer.echo(f"Transaction error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc
    except TransactionDataError as exc:
        typer.echo(f"Transaction data error: {exc}", err=True)
        raise typer.Exit(EXIT_VALIDATION_ERROR) from exc
    except TransactionError as exc:
        typer.echo(f"Transaction error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc
    except ForcenError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    payload = {
        "tx_id": result.tx_id,
        "accepted": result.accepted,
        "version_seq": result.version_seq,
        "warnings": result.warnings,
    }
    typer.echo(json.dumps(payload, indent=2))


@app.command("build")
def build_command(
    config_dir: Path = typer.Option(
        Path("config"),
        "--config",
        "-c",
        help="Path to configuration directory",
    ),
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state",
    ),
) -> None:
    """Rebuild artifacts from ledger state."""

    try:
        result = build_workspace(config_dir, workspace)
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR) from exc
    except BuildError as exc:
        typer.echo(f"Build error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    payload = {
        "version_seq": result.version_seq,
        "tx_count": result.tx_count,
    }
    typer.echo(json.dumps(payload, indent=2))


@versions_app.command("list")
def versions_list(
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state",
    ),
) -> None:
    ledger = Ledger(workspace)
    versions = ledger.list_versions()
    payload = {"versions": versions}
    typer.echo(json.dumps(payload, indent=2))

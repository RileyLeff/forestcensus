"""Typer CLI entrypoint for forcen."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .engine import (
    BuildError,
    DatasheetOptions,
    DatasheetsError,
    SubmitError,
    SubmitResult,
    VersionNotFoundError,
    build_workspace,
    diff_manifests,
    generate_datasheet,
    lint_transaction,
    load_manifest,
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
datasheets_app = typer.Typer(help="Datasheet commands")
app.add_typer(tx_app, name="tx")
app.add_typer(versions_app, name="versions")
app.add_typer(datasheets_app, name="datasheets")


@app.callback()
def main_callback() -> None:
    """Base command callback reserved for shared options."""


@tx_app.command("new")
def tx_new(
    out: Path = typer.Option(
        ...,
        "--out",
        "-o",
        exists=False,
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Directory to write transaction scaffold",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing files if the directory already exists",
    ),
) -> None:
    """Create a new transaction scaffold."""

    header = "site,plot,tag,date,dbh_mm,health,standing,notes\n"
    out = Path(out)

    if out.exists():
        if not out.is_dir():
            typer.echo(f"Path {out} exists and is not a directory", err=True)
            raise typer.Exit(EXIT_IO_ERROR)
        if not force:
            typer.echo(
                f"Transaction directory {out} already exists; use --force to overwrite",
                err=True,
            )
            raise typer.Exit(EXIT_IO_ERROR)
    else:
        out.mkdir(parents=True, exist_ok=True)

    measurements_path = out / "measurements.csv"
    updates_path = out / "updates.tdl"

    try:
        measurements_path.write_text(header, encoding="utf-8")
        updates_path.write_text("", encoding="utf-8")
    except OSError as exc:
        typer.echo(f"Failed to write scaffold files: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc


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
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state (to include prior DSL)",
    ),
) -> None:
    """Lint a transaction directory."""

    report_path = report_path or tx_dir / "lint-report.json"

    try:
        report = lint_transaction(
            transaction_dir=tx_dir,
            config_dir=config_dir,
            normalization=NormalizationConfig(),
            workspace=workspace,
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


@versions_app.command("show")
def versions_show(
    seq: int = typer.Argument(..., min=1),
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state",
    ),
) -> None:
    """Show manifest for a specific version."""

    try:
        manifest = load_manifest(workspace, seq)
    except VersionNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    typer.echo(json.dumps(manifest, indent=2, sort_keys=True))


@versions_app.command("diff")
def versions_diff(
    seq_a: int = typer.Argument(..., min=1),
    seq_b: int = typer.Argument(..., min=1),
    workspace: Path = typer.Option(
        Path(".forcen"),
        "--workspace",
        "-w",
        help="Directory for ledger state",
    ),
) -> None:
    """Show differences between two versions."""

    try:
        manifest_a = load_manifest(workspace, seq_a)
        manifest_b = load_manifest(workspace, seq_b)
    except VersionNotFoundError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    diff_payload = diff_manifests(manifest_a, manifest_b)
    typer.echo(json.dumps(diff_payload, indent=2, sort_keys=True))


@datasheets_app.command("generate")
def datasheets_generate(
    survey: str = typer.Option(..., "--survey", help="Target survey id"),
    site: str = typer.Option(..., "--site", help="Site code"),
    plot: str = typer.Option(..., "--plot", help="Plot code"),
    out_dir: Path = typer.Option(
        Path("datasheets"),
        "--out",
        "-o",
        file_okay=False,
        dir_okay=True,
        writable=True,
        help="Output directory for datasheet context",
    ),
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
    """Generate datasheet context JSON for a plot."""

    try:
        options = DatasheetOptions(
            survey_id=survey,
            site=site,
            plot=plot,
            output_dir=out_dir,
        )
        output_path = generate_datasheet(config_dir, workspace, options)
    except ConfigError as exc:
        typer.echo(f"Config error: {exc}", err=True)
        raise typer.Exit(EXIT_CONFIG_ERROR) from exc
    except DatasheetsError as exc:
        typer.echo(f"Datasheets error: {exc}", err=True)
        raise typer.Exit(EXIT_IO_ERROR) from exc

    payload = {
        "output": str(output_path),
    }
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


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

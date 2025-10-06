"""CLI tests for transaction commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from forcen.cli import app


runner = CliRunner()


def run_cli(args: list[str], env: dict[str, str] | None = None):
    merged_env = {"PYTHONPATH": "src"}
    if env:
        merged_env.update(env)
    return runner.invoke(app, args, env=merged_env)


def test_tx_lint_success(tmp_path: Path) -> None:
    tx_dir = Path("planning/fixtures/transactions/tx-1-initial")
    config_dir = Path("planning/fixtures/configs")
    result = run_cli([
        "tx",
        "lint",
        str(tx_dir),
        "--config",
        str(config_dir),
        "--report",
        str(tmp_path / "report.json"),
        "--workspace",
        str(tmp_path / "lint-ledger"),
    ])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["summary"]["errors"] == 0
    assert (tmp_path / "report.json").is_file()


def test_tx_lint_reports_errors(tmp_path: Path) -> None:
    tx_dir = tmp_path / "tx"
    tx_dir.mkdir()
    (tx_dir / "updates.tdl").write_text("", encoding="utf-8")
    (tx_dir / "measurements.csv").write_text(
        """site,plot,tag,date,dbh_mm,health,standing,notes
UNKNOWN,H4,112,2019-06-16,171,9,TRUE,""
""",
        encoding="utf-8",
    )

    result = run_cli([
        "tx",
        "lint",
        str(tx_dir),
        "--config",
        "planning/fixtures/configs",
        "--workspace",
        str(tmp_path / "lint-ledger"),
    ])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["summary"]["errors"] >= 1


def test_tx_submit_success(tmp_path: Path) -> None:
    tx_dir = Path("planning/fixtures/transactions/tx-1-initial")
    config_dir = Path("planning/fixtures/configs")
    workspace = tmp_path / "ledger"

    result = run_cli(
        [
            "tx",
            "submit",
            str(tx_dir),
            "--config",
            str(config_dir),
            "--workspace",
            str(workspace),
        ]
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["accepted"] is True
    manifest = workspace / "versions" / "0001" / "manifest.json"
    assert manifest.exists()

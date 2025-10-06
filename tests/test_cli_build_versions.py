"""CLI tests for build and versions commands."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from forcen.cli import app


runner = CliRunner()


def run_cli(args: list[str]) -> any:
    env = {"PYTHONPATH": "src"}
    return runner.invoke(app, args, env=env)


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")


def test_build_creates_new_version(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"

    submit_result = run_cli(
        [
            "tx",
            "submit",
            str(TX1_DIR),
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    assert submit_result.exit_code == 0

    build_result = run_cli(
        [
            "build",
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    assert build_result.exit_code == 0
    payload = json.loads(build_result.stdout)
    assert payload["version_seq"] == 2


def test_versions_list(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"

    run_cli(
        [
            "tx",
            "submit",
            str(TX1_DIR),
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    run_cli(
        [
            "build",
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )

    list_result = run_cli(
        [
            "versions",
            "list",
            "--workspace",
            str(workspace),
        ]
    )
    assert list_result.exit_code == 0
    payload = json.loads(list_result.stdout)
    assert payload["versions"] == [1, 2]

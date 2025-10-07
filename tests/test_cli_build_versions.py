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


def test_versions_show_and_diff(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"

    submit_out = run_cli(
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
    assert submit_out.exit_code == 0

    build_out = run_cli(
        [
            "build",
            "--config",
            str(CONFIG_DIR),
            "--workspace",
            str(workspace),
        ]
    )
    assert build_out.exit_code == 0

    show_out = run_cli(
        [
            "versions",
            "show",
            "1",
            "--workspace",
            str(workspace),
        ]
    )
    assert show_out.exit_code == 0
    manifest = json.loads(show_out.stdout)
    assert manifest["version_seq"] == 1
    assert "artifact_checksums" in manifest

    diff_out = run_cli(
        [
            "versions",
            "diff",
            "1",
            "2",
            "--workspace",
            str(workspace),
        ]
    )
    assert diff_out.exit_code == 0
    diff_payload = json.loads(diff_out.stdout)
    assert diff_payload["seq_a"] == 1
    assert diff_payload["seq_b"] == 2
    assert diff_payload["tx_ids"]["only_in_a"] == []
    assert diff_payload["tx_ids"]["only_in_b"] == []


def test_versions_show_missing(tmp_path: Path) -> None:
    workspace = tmp_path / "ledger"

    result = run_cli(
        [
            "versions",
            "show",
            "1",
            "--workspace",
            str(workspace),
        ]
    )
    assert result.exit_code == 4

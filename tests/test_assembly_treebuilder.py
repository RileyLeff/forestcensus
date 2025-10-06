"""Tests for tree identity resolution."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from forcen.config import load_config_bundle
from forcen.engine.utils import determine_default_effective_date, with_default_effective
from forcen.assembly.treebuilder import assign_tree_uids, build_alias_resolver
from forcen.transactions import NormalizationConfig, load_transaction


CONFIG_DIR = Path("planning/fixtures/configs")
TX1_DIR = Path("planning/fixtures/transactions/tx-1-initial")
TX2_DIR = Path("planning/fixtures/transactions/tx-2-ops")


def _prepare_transaction(tx_dir: Path):
    config = load_config_bundle(CONFIG_DIR)
    tx = load_transaction(tx_dir, normalization=NormalizationConfig())
    default_effective = determine_default_effective_date(config, tx)
    tx.commands = with_default_effective(tx.commands, default_effective)
    resolver = build_alias_resolver(tx.measurements, tx.commands)
    assign_tree_uids(tx.measurements, resolver)
    return tx


def test_tree_uid_consistent_for_same_tag():
    tx = _prepare_transaction(TX1_DIR)
    tree_uids = {row.tree_uid for row in tx.measurements}
    assert len(tree_uids) == 1


def test_alias_rebinds_tag_to_existing_tree():
    tx_initial = _prepare_transaction(TX1_DIR)
    base_tree_uid = tx_initial.measurements[0].tree_uid

    tx_alias = _prepare_transaction(TX2_DIR)
    alias_tree_uid = tx_alias.measurements[0].tree_uid

    assert alias_tree_uid == base_tree_uid

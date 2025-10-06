"""Serialization helpers for DSL commands."""

from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from .types import (
    AliasCommand,
    Command,
    Selector,
    SelectorDateFilter,
    SelectorStrategy,
    SplitCommand,
    TagRef,
    TreeRef,
    UpdateCommand,
)


def serialize_command(command: Command) -> Dict:
    if isinstance(command, AliasCommand):
        return {
            "type": "alias",
            "line_no": command.line_no,
            "target": _serialize_tag(command.target),
            "tree_ref": _serialize_tree_ref(command.tree_ref),
            "primary": command.primary,
            "effective_date": _serialize_date(command.effective_date),
            "note": command.note,
        }
    if isinstance(command, UpdateCommand):
        return {
            "type": "update",
            "line_no": command.line_no,
            "tree_ref": _serialize_tree_ref(command.tree_ref),
            "assignments": command.assignments,
            "effective_date": _serialize_date(command.effective_date),
            "note": command.note,
        }
    if isinstance(command, SplitCommand):
        return {
            "type": "split",
            "line_no": command.line_no,
            "source": _serialize_tree_ref(command.source),
            "target": _serialize_tag(command.target),
            "primary": command.primary,
            "effective_date": _serialize_date(command.effective_date),
            "selector": _serialize_selector(command.selector),
            "note": command.note,
        }
    raise TypeError(f"Unsupported command type: {type(command)!r}")


def deserialize_command(data: Dict) -> Command:
    cmd_type = data.get("type")
    if cmd_type == "alias":
        return AliasCommand(
            line_no=int(data.get("line_no", 0)),
            target=_deserialize_tag(data["target"]),
            tree_ref=_deserialize_tree_ref(data["tree_ref"]),
            primary=bool(data.get("primary", False)),
            effective_date=_deserialize_date(data.get("effective_date")),
            note=data.get("note"),
        )
    if cmd_type == "update":
        return UpdateCommand(
            line_no=int(data.get("line_no", 0)),
            tree_ref=_deserialize_tree_ref(data["tree_ref"]),
            assignments=dict(data.get("assignments", {})),
            effective_date=_deserialize_date(data.get("effective_date")),
            note=data.get("note"),
        )
    if cmd_type == "split":
        return SplitCommand(
            line_no=int(data.get("line_no", 0)),
            source=_deserialize_tree_ref(data["source"]),
            target=_deserialize_tag(data["target"]),
            primary=bool(data.get("primary", False)),
            effective_date=_deserialize_date(data.get("effective_date")),
            selector=_deserialize_selector(data.get("selector")),
            note=data.get("note"),
        )
    raise ValueError(f"Unknown command type: {cmd_type}")


def _serialize_tag(tag: TagRef) -> Dict:
    return {
        "site": tag.site,
        "plot": tag.plot,
        "tag": tag.tag,
        "date": _serialize_date(tag.at),
    }


def _deserialize_tag(data: Dict) -> TagRef:
    at = _deserialize_date(data.get("date"))
    return TagRef(site=data["site"], plot=data["plot"], tag=data["tag"], at=at)


def _serialize_tree_ref(tree_ref: TreeRef) -> Dict:
    if tree_ref.tree_uid is not None:
        return {"tree_uid": tree_ref.tree_uid}
    assert tree_ref.tag is not None
    return {"tag": _serialize_tag(tree_ref.tag)}


def _deserialize_tree_ref(data: Dict) -> TreeRef:
    tree_uid = data.get("tree_uid")
    if tree_uid is not None:
        return TreeRef.from_tree_uid(tree_uid)
    tag_data = data.get("tag")
    if tag_data is None:
        raise ValueError("TreeRef must contain tree_uid or tag")
    return TreeRef.from_tag(_deserialize_tag(tag_data))


def _serialize_selector(selector: Optional[Selector]) -> Optional[Dict]:
    if selector is None:
        return None
    return {
        "strategy": selector.strategy.value,
        "ranks": list(selector.ranks),
        "date_filter": _serialize_date_filter(selector.date_filter),
    }


def _deserialize_selector(data: Optional[Dict]) -> Optional[Selector]:
    if data is None:
        return None
    strategy = SelectorStrategy(data["strategy"])
    ranks = tuple(int(rank) for rank in data.get("ranks", []))
    date_filter = _deserialize_date_filter(data.get("date_filter"))
    return Selector(strategy=strategy, ranks=ranks, date_filter=date_filter)


def _serialize_date_filter(date_filter: Optional[SelectorDateFilter]) -> Optional[Dict]:
    if date_filter is None:
        return None
    payload = {"kind": date_filter.kind, "first": _serialize_date(date_filter.first)}
    if date_filter.second is not None:
        payload["second"] = _serialize_date(date_filter.second)
    return payload


def _deserialize_date_filter(data: Optional[Dict]) -> Optional[SelectorDateFilter]:
    if data is None:
        return None
    first = _deserialize_date(data.get("first"))
    second = _deserialize_date(data.get("second"))
    return SelectorDateFilter(kind=data["kind"], first=first, second=second)


def _serialize_date(value: Optional[date]) -> Optional[str]:
    return value.isoformat() if value is not None else None


def _deserialize_date(value: Optional[str]) -> Optional[date]:
    if value is None:
        return None
    return date.fromisoformat(value)

"""Utilities for computing deterministic transaction identifiers."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Iterable

try:  # Python 3.11+
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore


def compute_tx_id(tx_dir: Path) -> str:
    """Compute the SHA256 transaction id for *tx_dir*."""

    tx_dir = Path(tx_dir)
    parts: list[str] = []
    for path in sorted(_iter_tx_files(tx_dir)):
        relative = path.relative_to(tx_dir).as_posix()
        normalized = _normalize_file(path)
        parts.append(f"## {relative}\n")
        parts.append(normalized)
        if not normalized.endswith("\n"):
            parts.append("\n")

    digest = hashlib.sha256("".join(parts).encode("utf-8")).hexdigest()
    return digest


def _iter_tx_files(tx_dir: Path) -> Iterable[Path]:
    for path in tx_dir.rglob("*"):
        if path.is_file():
            yield path


def _normalize_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".toml":
        return _normalize_toml(path)
    text = path.read_text(encoding="utf-8")
    return _normalize_text(text)


def _normalize_toml(path: Path) -> str:
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    return _dump_toml(data)


def _dump_toml(data: Any, indent: int = 0) -> str:
    if isinstance(data, dict):
        lines: list[str] = []
        for key in sorted(data.keys()):
            value = data[key]
            if isinstance(value, dict):
                if lines:
                    lines.append("")
                lines.append(f"{_indent(indent)}[{key}]")
                lines.append(_dump_toml(value, indent))
            elif isinstance(value, list) and _list_of_tables(value):
                for table in value:
                    if lines:
                        lines.append("")
                    lines.append(f"{_indent(indent)}[[{key}]]")
                    lines.append(_dump_toml(table, indent))
            else:
                serialized = _serialize_value(value)
                lines.append(f"{_indent(indent)}{key} = {serialized}")
        return "\n".join(lines)
    if isinstance(data, list):
        items = ", ".join(_serialize_value(item) for item in data)
        return f"[{items}]"
    return _serialize_value(data)


def _serialize_value(value: Any) -> str:
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("\"", "\\\"")
        return f'"{escaped}"'
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    raise TypeError(f"Unsupported TOML value: {value!r}")


def _list_of_tables(value: list[Any]) -> bool:
    return bool(value) and all(isinstance(item, dict) for item in value)


def _indent(level: int) -> str:
    return "    " * level


def _normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    return "\n".join(lines).strip("\n") + "\n"

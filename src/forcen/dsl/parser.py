"""DSL parser based on Lark."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional, Tuple

from lark import Lark, Transformer, UnexpectedInput

from .exceptions import DSLParseError
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


GRAMMAR = r"""
    ?command: alias_cmd
            | update_cmd
            | split_cmd

    alias_cmd: "ALIAS" tag_id "TO" tree_ref primary? effective? note?
    update_cmd: "UPDATE" tree_ref "SET" update_assignments effective? note?
    split_cmd: "SPLIT" tree_ref "INTO" tag_id primary? effective? select_clause? note?

    tag_id: IDENT "/" IDENT "/" IDENT
    tree_ref: UUID -> tree_uid
            | tag_id tree_ref_date?
    tree_ref_date: "@" DATE

    primary: "PRIMARY"
    effective: "EFFECTIVE" DATE
    note: "NOTE" QUOTED_STRING

    update_assignments: update_assignment ("," update_assignment)*
    update_assignment: UPDATE_FIELD "=" FIELD_VALUE

    select_clause: "SELECT" selector_mode selector_date?
    selector_mode: "ALL" -> select_all
                 | "LARGEST" -> select_largest
                 | "SMALLEST" -> select_smallest
                 | "RANKS" rank_list -> select_ranks
    selector_date: "BEFORE" DATE -> select_before
                 | "AFTER" DATE -> select_after
                 | "BETWEEN" DATE "AND" DATE -> select_between

    rank_list: INT ("," INT)*

    UPDATE_FIELD: "genus" | "species" | "code" | "site" | "plot"

    IDENT: /[A-Za-z0-9_]+/
    UUID.2: /[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}/
    FIELD_VALUE: /[A-Za-z0-9_.-]+/
    DATE: /\d{4}-\d{2}-\d{2}/

    %import common.INT
    %import common.ESCAPED_STRING -> QUOTED_STRING
    %import common.WS_INLINE
    %ignore WS_INLINE
"""


class _CommandTransformer(Transformer):
    def __init__(self) -> None:
        super().__init__(visit_tokens=True)

    def tag_id(self, items: list[Any]) -> TagRef:
        site, plot, tag = (str(tok) for tok in items)
        return TagRef(site=site, plot=plot, tag=tag)

    def tree_uid(self, items: list[Any]) -> TreeRef:
        token = str(items[0])
        return TreeRef.from_tree_uid(token)

    def tree_ref(self, items: list[Any]) -> TreeRef:
        if isinstance(items[0], TreeRef):
            # Already a tree UID
            return items[0]
        tag = items[0]
        if len(items) == 2:
            when = items[1]
            tag = tag.with_date(when)
        return TreeRef.from_tag(tag)

    def tree_ref_date(self, items: list[Any]) -> date:
        return date.fromisoformat(str(items[0]))

    def effective(self, items: list[Any]) -> date:
        return date.fromisoformat(str(items[0]))

    def note(self, items: list[Any]) -> str:
        raw = str(items[0])
        return raw[1:-1]

    def update_assignment(self, items: list[Any]) -> Tuple[str, str]:
        field = str(items[0])
        value = str(items[1])
        return field, value

    def update_assignments(self, items: list[Any]) -> Dict[str, str]:
        assignments: Dict[str, str] = {}
        for key, value in items:
            assignments[key] = value
        return assignments

    def select_all(self, _: list[Any]) -> Tuple[SelectorStrategy, Optional[Tuple[int, ...]]]:
        return SelectorStrategy.ALL, None

    def select_largest(self, _: list[Any]) -> Tuple[SelectorStrategy, Optional[Tuple[int, ...]]]:
        return SelectorStrategy.LARGEST, None

    def select_smallest(self, _: list[Any]) -> Tuple[SelectorStrategy, Optional[Tuple[int, ...]]]:
        return SelectorStrategy.SMALLEST, None

    def rank_list(self, items: list[Any]) -> Tuple[int, ...]:
        return tuple(int(token) for token in items)

    def select_ranks(self, items: list[Any]) -> Tuple[SelectorStrategy, Tuple[int, ...]]:
        ranks = items[0] if items else ()
        return SelectorStrategy.RANKS, ranks

    def select_before(self, items: list[Any]) -> SelectorDateFilter:
        when = date.fromisoformat(str(items[0]))
        return SelectorDateFilter(kind="before", first=when)

    def select_after(self, items: list[Any]) -> SelectorDateFilter:
        when = date.fromisoformat(str(items[0]))
        return SelectorDateFilter(kind="after", first=when)

    def select_between(self, items: list[Any]) -> SelectorDateFilter:
        start = date.fromisoformat(str(items[0]))
        end = date.fromisoformat(str(items[1]))
        return SelectorDateFilter(kind="between", first=start, second=end)

    def select_clause(self, items: list[Any]) -> Selector:
        strategy_info = items[0]
        date_filter = items[1] if len(items) == 2 else None
        strategy, ranks = strategy_info
        if strategy == SelectorStrategy.RANKS and not ranks:
            raise ValueError("RANKS selector requires at least one rank")
        return Selector(
            strategy=strategy,
            ranks=ranks if ranks is not None else (),
            date_filter=date_filter,
        )

    def alias_cmd(self, items: list[Any]) -> Tuple[str, Dict[str, Any]]:
        target = items[0]
        tree_ref = items[1]
        primary = False
        effective_date: Optional[date] = None
        note: Optional[str] = None
        for item in items[2:]:
            if isinstance(item, str):
                note = item
            elif isinstance(item, date):
                effective_date = item
            elif isinstance(item, bool):
                primary = item or primary
            elif item == "PRIMARY":
                primary = True
        return (
            "alias",
            {
                "target": target,
                "tree_ref": tree_ref,
                "primary": primary,
                "effective_date": effective_date,
                "note": note,
            },
        )

    def update_cmd(self, items: list[Any]) -> Tuple[str, Dict[str, Any]]:
        tree_ref = items[0]
        assignments = items[1]
        effective_date: Optional[date] = None
        note: Optional[str] = None
        for item in items[2:]:
            if isinstance(item, str):
                note = item
            elif isinstance(item, date):
                effective_date = item
        return (
            "update",
            {
                "tree_ref": tree_ref,
                "assignments": assignments,
                "effective_date": effective_date,
                "note": note,
            },
        )

    def split_cmd(self, items: list[Any]) -> Tuple[str, Dict[str, Any]]:
        source = items[0]
        target = items[1]
        primary = False
        effective_date: Optional[date] = None
        selector: Optional[Selector] = None
        note: Optional[str] = None
        for item in items[2:]:
            if isinstance(item, Selector):
                selector = item
            elif isinstance(item, str):
                note = item
            elif isinstance(item, date):
                effective_date = item
            elif item == "PRIMARY":
                primary = True
        return (
            "split",
            {
                "source": source,
                "target": target,
                "primary": primary,
                "effective_date": effective_date,
                "selector": selector,
                "note": note,
            },
        )

    def primary(self, _: list[Any]) -> bool:
        return True


class DSLParser:
    """Parse DSL text into command objects."""

    def __init__(self) -> None:
        self._parser = Lark(GRAMMAR, start="command", parser="lalr")
        self._transformer = _CommandTransformer()

    def parse(self, text: str) -> list[Command]:
        commands: list[Command] = []
        for line_no, raw_line in enumerate(text.splitlines(), start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            try:
                tree = self._parser.parse(stripped)
            except UnexpectedInput as exc:  # pragma: no cover - exercised via tests
                raise DSLParseError(line_no=line_no, line=raw_line, detail=str(exc)) from exc
            try:
                kind, payload = self._transformer.transform(tree)
            except ValueError as exc:  # pragma: no cover - error surfaced as parse issue
                raise DSLParseError(line_no=line_no, line=raw_line, detail=str(exc)) from exc
            command = self._instantiate_command(kind, payload, line_no)
            commands.append(command)
        return commands

    def _instantiate_command(
        self, kind: str, payload: Dict[str, Any], line_no: int
    ) -> Command:
        if kind == "alias":
            return AliasCommand(line_no=line_no, **payload)
        if kind == "update":
            return UpdateCommand(line_no=line_no, **payload)
        if kind == "split":
            return SplitCommand(line_no=line_no, **payload)
        raise ValueError(f"Unknown command kind: {kind}")

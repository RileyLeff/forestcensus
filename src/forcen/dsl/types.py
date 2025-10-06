"""Typed representations of DSL commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class TagRef:
    site: str
    plot: str
    tag: str
    at: Optional[date] = None

    def without_date(self) -> "TagRef":
        return TagRef(self.site, self.plot, self.tag, None)

    def with_date(self, when: date) -> "TagRef":
        return TagRef(self.site, self.plot, self.tag, when)

    def key(self) -> Tuple[str, str, str]:
        return (self.site, self.plot, self.tag)

    def key_with_date(self) -> str:
        base = "/".join(self.key())
        if self.at is not None:
            return f"{base}@{self.at.isoformat()}"
        return base

    def display(self) -> str:
        return self.key_with_date()


@dataclass(frozen=True)
class TreeRef:
    tree_uid: Optional[str] = None
    tag: Optional[TagRef] = None

    def __post_init__(self) -> None:
        if (self.tree_uid is None) == (self.tag is None):
            raise ValueError("TreeRef must contain exactly one of tree_uid or tag")

    @classmethod
    def from_tree_uid(cls, tree_uid: str) -> "TreeRef":
        return cls(tree_uid=tree_uid, tag=None)

    @classmethod
    def from_tag(cls, tag: TagRef) -> "TreeRef":
        return cls(tree_uid=None, tag=tag)

    def key(self) -> str:
        if self.tree_uid is not None:
            return f"tree:{self.tree_uid}"
        assert self.tag is not None
        return f"tag:{self.tag.key_with_date()}"

    def display(self) -> str:
        if self.tree_uid is not None:
            return self.tree_uid
        assert self.tag is not None
        return self.tag.display()


class SelectorStrategy(Enum):
    ALL = "ALL"
    LARGEST = "LARGEST"
    SMALLEST = "SMALLEST"
    RANKS = "RANKS"


@dataclass(frozen=True)
class SelectorDateFilter:
    kind: str  # "before", "after", or "between"
    first: date
    second: Optional[date] = None


@dataclass(frozen=True)
class Selector:
    strategy: SelectorStrategy
    ranks: Tuple[int, ...] = ()
    date_filter: Optional[SelectorDateFilter] = None


@dataclass(frozen=True)
class Command:
    line_no: int

    def signature(self) -> Tuple:
        raise NotImplementedError


@dataclass(frozen=True)
class AliasCommand(Command):
    target: TagRef
    tree_ref: TreeRef
    primary: bool = False
    effective_date: Optional[date] = None
    note: Optional[str] = None

    def signature(self) -> Tuple:
        return (
            self.target.key(),
            self.tree_ref.key(),
            self.primary,
            self.effective_date,
            self.note,
        )


@dataclass(frozen=True)
class UpdateCommand(Command):
    tree_ref: TreeRef
    assignments: Dict[str, str]
    effective_date: Optional[date] = None
    note: Optional[str] = None

    def signature(self) -> Tuple:
        return (
            self.tree_ref.key(),
            tuple(sorted(self.assignments.items())),
            self.effective_date,
            self.note,
        )


@dataclass(frozen=True)
class SplitCommand(Command):
    source: TreeRef
    target: TagRef
    primary: bool = False
    effective_date: Optional[date] = None
    selector: Optional[Selector] = None
    note: Optional[str] = None

    def signature(self) -> Tuple:
        selector_sig: Tuple
        if self.selector is None:
            selector_sig = ()
        else:
            selector_sig = (
                self.selector.strategy.value,
                self.selector.ranks,
                None
                if self.selector.date_filter is None
                else (
                    self.selector.date_filter.kind,
                    self.selector.date_filter.first,
                    self.selector.date_filter.second,
                ),
            )
        return (
            self.source.key(),
            self.target.key(),
            self.primary,
            self.effective_date,
            selector_sig,
            self.note,
        )

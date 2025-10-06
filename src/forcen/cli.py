"""Typer CLI entrypoint for forcen."""

from __future__ import annotations

import typer


app = typer.Typer(help="Forest census transaction engine")


@app.callback()
def main_callback() -> None:
    """Base command callback reserved for shared options."""


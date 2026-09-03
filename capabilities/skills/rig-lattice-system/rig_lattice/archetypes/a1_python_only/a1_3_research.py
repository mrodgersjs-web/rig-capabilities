"""A1.3 — Research (PYTHON_ONLY).

Does: fetch deterministic data from declared sources only.
Tools: httpx + SQLAlchemy + MCP clients (production). Model: NONE.

This reference implementation uses an injectable Fetcher protocol so the step
is testable with zero network/DB. A DeterministicFetcher returns canned rows
keyed by source.uri. Parallel fan-out is preserved via asyncio.gather.

Source-per-claim is free here: every row carries the Source it came from.
"""
from __future__ import annotations

import asyncio
from typing import Protocol

from ._types import ResearchPack, Source, StructuredQuery


class Fetcher(Protocol):
    async def fetch(self, source: Source, params: dict) -> list[dict]:
        ...


class DeterministicFetcher:
    """Canned, side-effect-free fetcher for tests and dry runs."""

    def __init__(self, fixtures: dict[str, list[dict]] | None = None) -> None:
        self._fixtures = fixtures or {}

    async def fetch(self, source: Source, params: dict) -> list[dict]:
        rows = self._fixtures.get(source.uri, [])
        # Tag each row with provenance so claims are sourced downstream.
        return [{**r, "_source": source.uri} for r in rows]


async def fetch(query: StructuredQuery, fetcher: Fetcher) -> ResearchPack:
    """Parallel fan-out over declared sources only."""
    if not query.sources:
        return ResearchPack(rows=[], sources=[], shim_slot={})
    batches = await asyncio.gather(
        *[fetcher.fetch(src, query.params) for src in query.sources]
    )
    rows: list[dict] = [row for batch in batches for row in batch]
    return ResearchPack(rows=rows, sources=list(query.sources), shim_slot={})


def run(query: StructuredQuery, fetcher: Fetcher | None = None) -> ResearchPack:
    """Synchronous entrypoint that drives the async fan-out."""
    fetcher = fetcher or DeterministicFetcher()
    return asyncio.run(fetch(query, fetcher))

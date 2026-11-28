"""
Index-level endpoints.

These answer "how are the individual indices doing?" — sizes, documents,
settings, mappings and per-index shard health.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Indices"])


@router.get(
    "/indices",
    summary="List indices with size, docs and health",
    description=(
        "The `_cat/indices` view: one row per index with its health colour, "
        "status (open/closed), document count, deleted docs and on-disk size.\n\n"
        "This is usually the first place to look when something is yellow or "
        "red — the unhealthy index is right there in the `health` column."
    ),
)
async def list_indices(
    index: str | None = Query(
        default=None,
        description="Comma-separated index names or wildcard patterns, e.g. `logs-*`.",
    ),
    health: Literal["green", "yellow", "red"] | None = Query(
        default=None,
        description="Only return indices at this health level or worse, e.g. `yellow`.",
    ),
    sort: str | None = Query(
        default=None,
        description="Column to sort by, e.g. `store.size:desc` for biggest first.",
    ),
) -> Any:
    params: dict[str, Any] = {"format": "json"}
    if health:
        params["health"] = health
    if sort:
        params["s"] = sort
    path = f"/_cat/indices/{index}" if index else "/_cat/indices"
    return await es_request("GET", path, params=params)


@router.get(
    "/indices/{index}/stats",
    summary="Statistics for one index (or pattern)",
    description=(
        "Per-index metrics: documents stored, index/merge/get/search operation "
        "counts and timings, segment counts, memory usage and cache sizes.\n\n"
        "Use it to see whether an index is actively written or searched, whether "
        "merges are falling behind, or how much memory its segments consume."
    ),
)
async def index_stats(
    index: str,
    metric: str | None = Query(
        default=None,
        description=(
            "Comma-separated metric groups, e.g. `docs,store,indexing,search,"
            "segments,merges`. Omit for all groups."
        ),
    ),
) -> Any:
    params: dict[str, Any] = {}
    if metric:
        params["metric"] = metric
    return await es_request("GET", f"/{index}/_stats", params=params)


@router.get(
    "/indices/{index}/settings",
    summary="Settings of one index (or pattern)",
    description=(
        "Shows the settings applied to an index: shard and replica counts, "
        "refresh interval, allocation rules, and whether the index is read-only.\n\n"
        "Two classic checks: an index stuck with `index.blocks.write: true` "
        "(frozen because a disk filled up) and `number_of_replicas` higher than "
        "your node count, which keeps the index yellow forever."
    ),
)
async def index_settings(
    index: str,
    flat_settings: bool = Query(
        default=True,
        description="Return settings as flat `a.b.c` keys instead of nested objects.",
    ),
) -> Any:
    return await es_request(
        "GET", f"/{index}/_settings", params={"flat_settings": flat_settings}
    )


@router.get(
    "/indices/{index}/mapping",
    summary="Field mapping of one index (or pattern)",
    description=(
        "Returns the mapping: every field, its type and indexing options. "
        "Essential when a document is rejected (`mapper_parsing_exception`), "
        "when queries return nothing because of a type mismatch, or when you "
        "suspect mapping explosions (thousands of dynamically-mapped fields)."
    ),
)
async def index_mapping(index: str) -> Any:
    return await es_request("GET", f"/{index}/_mapping")


@router.get(
    "/indices/{index}/recovery",
    summary="Shard recovery progress for one index",
    description=(
        "Shows ongoing or completed shard recoveries: replicas being copied, "
        "shards relocating between nodes, or restores from snapshots, with "
        "bytes and files transferred so far.\n\n"
        "If the cluster is yellow for a long time, this tells you whether "
        "replicas are actually being rebuilt and how far along they are."
    ),
)
async def index_recovery(
    index: str,
    active_only: bool = Query(
        default=False,
        description="Only show recoveries currently in progress.",
    ),
) -> Any:
    return await es_request(
        "GET", f"/{index}/_recovery", params={"active_only": active_only}
    )


@router.get(
    "/indices/{index}/segments",
    summary="Segment-level detail for one index",
    description=(
        "Lists the Lucene segments of each shard: how many there are, their "
        "sizes and memory footprint. Many tiny segments mean the index is "
        "spending heavily on merges and search overhead; a force-merge or a "
        "look at the refresh interval may be warranted."
    ),
)
async def index_segments(index: str) -> Any:
    return await es_request("GET", f"/{index}/_segments")


@router.get(
    "/indices/{index}/shard-stores",
    summary="On-disk shard copies for one index",
    description=(
        "Reports every physical shard copy that exists on disk for the index, "
        "on which node, and whether the copy is usable or corrupted.\n\n"
        "The key field is `store_status`: `used`, `unused` or — the one to "
        "worry about — `corrupt`. Corrupted copies are what "
        "`allocate_stale_primary` decisions are made against."
    ),
)
async def index_shard_stores(
    index: str,
    status: str | None = Query(
        default=None,
        description="Filter by copy health: `green`, `yellow`, `red` or `all`.",
    ),
) -> Any:
    params: dict[str, Any] = {}
    if status:
        params["status"] = status
    return await es_request("GET", f"/{index}/_shard_stores", params=params)


@router.get(
    "/indices/{index}/count",
    summary="Number of documents in one index (or pattern)",
    description=(
        "A lightweight count of documents, optionally restricted by a query in "
        "the body. Cheaper than fetching stats when you only need *how many* "
        "documents match."
    ),
)
async def index_count(
    index: str,
    body: dict[str, Any] | None = None,
) -> Any:
    return await es_request("POST", f"/{index}/_count", json_body=body)

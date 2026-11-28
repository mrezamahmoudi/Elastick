"""
Shard & allocation endpoints.

These answer "where is every shard, and why is any of them not where it
should be?" — the heart of troubleshooting yellow and red clusters.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Shards & Allocation"])


@router.get(
    "/shards",
    summary="Every shard: node, state, size",
    description=(
        "The `_cat/shards` view: one row per shard copy showing its index, "
        "shard number, primary/replica role, current state (`STARTED`, "
        "`INITIALIZING`, `RELOCATING`, `UNASSIGNED`), the node it lives on and "
        "its size.\n\n"
        "Anything not `STARTED` deserves attention: many `INITIALIZING` shards "
        "mean a recovery wave is running; `UNASSIGNED` shards mean the cluster "
        "could not place them at all."
    ),
)
async def list_shards(
    index: str | None = Query(
        default=None,
        description="Comma-separated index names or wildcard patterns to filter by.",
    ),
    bytes_format: str = Query(
        default="b", alias="bytes",
        description="Unit for sizes: `b`, `kb`, `mb`, `gb`, `tb`.",
    ),
) -> Any:
    path = f"/_cat/shards/{index}" if index else "/_cat/shards"
    return await es_request(
        "GET", path, params={"format": "json", "bytes": bytes_format}
    )


@router.get(
    "/shards/unassigned",
    summary="Shards with no copy allocated anywhere",
    description=(
        "Lists only the shards that exist in the index metadata but have **no "
        "copy on any node** (`state == UNASSIGNED`), together with their "
        "unassigned reason.\n\n"
        "An empty result means every shard is placed — the best possible "
        "outcome. A non-empty result is the concrete to-do list behind a "
        "yellow or red cluster health; follow up with "
        "`/shards/allocation-explain` to learn why a shard cannot be placed."
    ),
)
async def unassigned_shards(
    index: str | None = Query(
        default=None,
        description="Comma-separated index names or wildcard patterns to filter by.",
    ),
) -> Any:
    path = f"/_cat/shards/{index}" if index else "/_cat/shards"
    shards = await es_request(
        "GET", path, params={"format": "json", "bytes": "b"}
    )
    if not isinstance(shards, list):
        return shards
    return [
        shard for shard in shards
        if str(shard.get("state", "")).upper() == "UNASSIGNED"
    ]


@router.post(
    "/shards/allocation-explain",
    summary="Why is this shard unassigned? (or first unassigned found)",
    description=(
        "Ask Elasticsearch to explain, in its own words, why a shard copy is "
        "or is not allocated on a node — e.g. *disk watermark exceeded*, "
        "*no copy of the shard exists on any node*, or *allocation decider "
        "filtered the node out*.\n\n"
        "Call it with **no body** to get an explanation for the first "
        "unassigned shard the cluster finds, or pass a body to target a "
        "specific one:\n\n"
        "`{\"index\": \"logs-2026.01.01\", \"shard\": 0, \"primary\": false}`\n\n"
        "This is usually the single most useful diagnostic for red/yellow "
        "clusters."
    ),
)
async def allocation_explain(body: dict[str, Any] | None = None) -> Any:
    return await es_request("GET", "/_cluster/allocation/explain", json_body=body)


@router.post(
    "/shards/{index}/flush",
    summary="Flush an index's shards to disk",
    description=(
        "Moves the transaction log into the on-disk Lucene segments for the "
        "given index (all shards). Frees the translog and can help before "
        "snapshot or maintenance work. Safe but I/O-heavy — avoid flushing "
        "every index on a busy cluster on a schedule."
    ),
)
async def flush_index(
    index: str,
    force: bool = Query(
        default=False,
        description="Force a flush even if it may not be beneficial.",
    ),
    wait_if_ongoing: bool = Query(
        default=True,
        description="Wait for an in-progress flush to finish instead of erroring.",
    ),
) -> Any:
    return await es_request(
        "POST",
        f"/{index}/_flush",
        params={"force": force, "wait_if_ongoing": wait_if_ongoing},
    )


@router.post(
    "/shards/{index}/refresh",
    summary="Refresh an index to make recent writes searchable",
    description=(
        "Makes documents written since the last refresh visible to search. "
        "Normally unnecessary (the default `refresh_interval` is 1s), but "
        "useful after bulk loads or when troubleshooting *my document is not "
        "found* reports."
    ),
)
async def refresh_index(index: str) -> Any:
    return await es_request("POST", f"/{index}/_refresh")

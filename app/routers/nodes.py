"""
Node-level endpoints.

These answer "how are the individual machines in the cluster doing?" —
CPU, memory, disk, JVM, thread pools and whether a node is working too hard.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Nodes"])


@router.get(
    "/nodes",
    summary="List nodes and their basic info",
    description=(
        "Lists every node in the cluster with its role, version, uptime, "
        "IP address and heap settings. Use this first to see *who is in the "
        "cluster* and whether any node is on a different version or missing "
        "an expected role (e.g. no dedicated master)."
    ),
)
async def list_nodes(
    node_id: str | None = Query(
        default=None,
        description=(
            "Comma-separated node names/IDs or wildcards to filter by, "
            "e.g. `es-data-*`. Omit for all nodes."
        ),
    ),
) -> Any:
    path = f"/_nodes/{node_id}" if node_id else "/_nodes"
    return await es_request("GET", path)


@router.get(
    "/nodes/stats",
    summary="Per-node runtime statistics",
    description=(
        "Detailed live metrics per node: JVM heap and GC, indexing and search "
        "throughput, merge pressure, filesystem size and I/O, transport traffic, "
        "thread pool queues and rejections, circuit-breaker status.\n\n"
        "This is the workhorse endpoint for answering *why is this node slow or "
        "under pressure?* Use `metric` to trim the response."
    ),
)
async def node_stats(
    node_id: str | None = Query(
        default=None,
        description="Comma-separated node names/IDs or wildcards. Omit for all nodes.",
    ),
    metric: str | None = Query(
        default=None,
        description=(
            "Comma-separated metric groups to return, e.g. `jvm,os,thread_pool,"
            "indices,fs`. Omit for all groups."
        ),
    ),
) -> Any:
    path = f"/_nodes/{node_id}/stats" if node_id else "/_nodes/stats"
    params: dict[str, Any] = {}
    if metric:
        params["metric"] = metric
    return await es_request("GET", path, params=params)


@router.get(
    "/nodes/usage",
    summary="Per-node REST API usage",
    description=(
        "Shows how many times each REST API has been called on each node since "
        "the node last restarted. Mostly useful to understand which parts of the "
        "API clients actually use — not a health metric."
    ),
)
async def node_usage(
    node_id: str | None = Query(
        default=None,
        description="Comma-separated node names/IDs or wildcards. Omit for all nodes.",
    ),
) -> Any:
    path = f"/_nodes/{node_id}/usage" if node_id else "/_nodes/usage"
    return await es_request("GET", path)


@router.get(
    "/nodes/hot-threads",
    summary="Threads currently burning CPU per node",
    description=(
        "Snapshots the busiest threads on each node (the classic *hot threads* "
        "API). If a node is at 100% CPU, this tells you **which code path** is "
        "responsible — long-running searches, merges, GC, etc.\n\n"
        "Take two or three snapshots a few seconds apart to see whether the same "
        "thread is still busy."
    ),
)
async def hot_threads(
    node_id: str | None = Query(
        default=None,
        description="Comma-separated node names/IDs or wildcards. Omit for all nodes.",
    ),
    threads: int = Query(
        default=3, ge=1, le=100,
        description="How many hottest threads to show per node.",
    ),
    interval: str = Query(
        default="500ms",
        description="Sampling window used to measure CPU per thread, e.g. `500ms`.",
    ),
    type: str = Query(
        default="cpu",
        description="Sort threads by: `cpu`, `wait`, `block` or `mem`.",
    ),
) -> Any:
    path = f"/_nodes/{node_id}/hot_threads" if node_id else "/_nodes/hot_threads"
    params: dict[str, Any] = {"threads": threads, "interval": interval, "type": type}
    return await es_request("GET", path, params=params)


@router.get(
    "/nodes/disk-usage",
    summary="Disk usage and shard distribution per node",
    description=(
        "The `_cat/allocation` view: for every node, how much disk is used, how "
        "much is free, and how many shards it holds. Watch for nodes that drift "
        "away from the average — uneven shard distribution is the usual cause of "
        "one node filling its disk before the others.\n\n"
        "Compare the `disk.percent` values against the cluster flood-watermarks "
        "(default 85%/90%/95%): a node above them stops allocating new shards."
    ),
)
async def disk_usage(
    bytes_format: str = Query(
        default="b",
        alias="bytes",
        description="Unit for sizes: `b`, `kb`, `mb`, `gb`, `tb` (or `auto`-style via cat).",
    ),
) -> Any:
    return await es_request(
        "GET", "/_cat/allocation", params={"format": "json", "bytes": bytes_format}
    )


@router.get(
    "/nodes/thread-pools",
    summary="Thread-pool queues and rejections per node",
    description=(
        "The `_cat/thread_pool` view: for each node and thread pool (search, "
        "write, get, flush…), how many tasks are active, queued and rejected.\n\n"
        "`queue > 0` means work is piling up; `rejected > 0` means Elasticsearch "
        "started refusing work — usually the first visible symptom of overload."
    ),
)
async def thread_pools(
    node_id: str | None = Query(
        default=None,
        description="Comma-separated node names/IDs or wildcards. Omit for all nodes.",
    ),
    thread_pool_patterns: str | None = Query(
        default=None,
        description="Comma-separated pool name patterns, e.g. `search,write`.",
    ),
) -> Any:
    path = f"/_cat/thread_pool/{thread_pool_patterns}" if thread_pool_patterns else "/_cat/thread_pool"
    return await es_request("GET", path, params={"format": "json"})

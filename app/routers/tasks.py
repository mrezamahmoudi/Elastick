"""
Task & maintenance endpoints.

These answer "what is the cluster working on right now?" — running tasks,
their progress, and ways to stop a runaway one.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Tasks & Maintenance"])


@router.get(
    "/tasks",
    summary="List currently running tasks",
    description=(
        "Lists every task executing in the cluster right now: searches, "
        "bulk writes, reindexes, shard recoveries, snapshot operations… with "
        "the node, action, start time, running time and description.\n\n"
        "Sort mentally by `running_time_in_nanos`: a search stuck for an hour "
        "is usually your problem. Use `actions` to filter (e.g. "
        "`actions=*search*`) and `detailed=true` for extra context."
    ),
)
async def list_tasks(
    actions: str | None = Query(
        default=None,
        description="Comma-separated action name patterns, e.g. `*search*,*write*`.",
    ),
    detailed: bool = Query(
        default=False,
        description="Include detailed task descriptions where available.",
    ),
    nodes: str | None = Query(
        default=None,
        description="Comma-separated node names/IDs or wildcards to filter by.",
    ),
) -> Any:
    params: dict[str, Any] = {"detailed": detailed}
    if actions:
        params["actions"] = actions
    if nodes:
        params["nodes"] = nodes
    return await es_request("GET", "/_tasks", params=params)


@router.get(
    "/tasks/{task_id}",
    summary="Status of one task",
    description=(
        "Fetches progress for a single task by ID (get the ID from `/tasks`), "
        "including how many documents or requests it has processed so far — "
        "e.g. to watch a long reindex or update-by-query crawl forward."
    ),
)
async def task_status(task_id: str) -> Any:
    return await es_request("GET", f"/_tasks/{task_id}")


@router.post(
    "/tasks/{task_id}/cancel",
    summary="Cancel a running task",
    description=(
        "**Disruptive.** Cancels the task with the given ID (e.g. a runaway "
        "search or a mistaken reindex). Cancellation is cooperative: the task "
        "stops at the next safe checkpoint, so it may take a little time to "
        "disappear. Data is not corrupted by cancelling, but the work done so "
        "far is abandoned."
    ),
)
async def cancel_task(task_id: str) -> Any:
    return await es_request("POST", f"/_tasks/{task_id}/_cancel")


@router.post(
    "/indices/{index}/_forcemerge",
    summary="Force-merge an index into few segments",
    description=(
        "**Maintenance.** Rewrites an index's shards into a small number of "
        "larger segments, reducing memory and search overhead. Typically run "
        "on time-based indices that are no longer being written (e.g. "
        "yesterday's `logs-*`).\n\n"
        "`max_num_segments=1` gives the smallest footprint but the heaviest "
        "merge; avoid force-merging indices that still receive writes."
    ),
)
async def force_merge(
    index: str,
    max_num_segments: int = Query(
        default=1, ge=1,
        description="Target number of segments per shard after the merge.",
    ),
    only_expunge_deletes: bool = Query(
        default=False,
        description="Only purge documents marked as deleted; skip full merge.",
    ),
) -> Any:
    return await es_request(
        "POST",
        f"/{index}/_forcemerge",
        params={
            "max_num_segments": max_num_segments,
            "only_expunge_deletes": only_expunge_deletes,
        },
    )


@router.post(
    "/indices/{index}/_cache/clear",
    summary="Clear an index's caches",
    description=(
        "Drops query, request and fielddata caches for the given index. A "
        "classic remedy when a node's JVM heap is under pressure from cached "
        "queries — searches will be slower for a while as caches rebuild."
    ),
)
async def clear_cache(index: str) -> Any:
    return await es_request("POST", f"/{index}/_cache/clear")

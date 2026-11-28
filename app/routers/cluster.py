"""
Cluster-level endpoints.

These answer the question "is the cluster as a whole healthy?" — status,
resource usage, pending maintenance tasks and current settings.
"""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Cluster"])


@router.get(
    "/cluster/health",
    summary="Cluster health (green / yellow / red)",
    description=(
        "The single most important health check. Returns the overall status:\n\n"
        "- **green** — all primary and replica shards are allocated. Fully healthy.\n"
        "- **yellow** — all primaries are fine, but at least one replica shard is "
        "not allocated (often because fewer nodes exist than the replica count).\n"
        "- **red** — at least one **primary** shard is missing; data may be "
        "unavailable or at risk. Investigate immediately.\n\n"
        "Use `level=indices` or `level=shards` to drill down into *which* index "
        "or shard is causing a non-green status."
    ),
)
async def cluster_health(
    level: Literal["cluster", "indices", "shards"] = Query(
        default="indices",
        description=(
            "How much detail to return: `cluster` (summary only), `indices` "
            "(status per index) or `shards` (status per individual shard)."
        ),
    ),
    wait_for_status: Literal["green", "yellow", "red"] | None = Query(
        default=None,
        description=(
            "Optionally block until the cluster reaches at least this status "
            "(or `timeout` expires). Useful in scripts that wait for green."
        ),
    ),
    timeout: str | None = Query(
        default=None,
        description="How long to wait for `wait_for_status`, e.g. `30s`.",
    ),
) -> Any:
    params: dict[str, Any] = {"level": level}
    if wait_for_status:
        params["wait_for_status"] = wait_for_status
    if timeout:
        params["timeout"] = timeout
    return await es_request("GET", "/_cluster/health", params=params)


@router.get(
    "/cluster/stats",
    summary="Cluster-wide statistics",
    description=(
        "Numbers and sizes for the whole cluster: document counts, total stored "
        "bytes, JVM heap usage per node, field and mapping counts, and versions "
        "in use. The go-to endpoint for capacity questions like *how big is the "
        "cluster* and *how many documents does it hold*."
    ),
)
async def cluster_stats() -> Any:
    return await es_request("GET", "/_cluster/stats")


@router.get(
    "/cluster/settings",
    summary="Cluster settings (persistent + transient)",
    description=(
        "Shows the cluster-level settings that operators have changed, such as "
        "watermarks, shard-allocation enablement, or replication throttling.\n\n"
        "Set `include_defaults=true` to also see every built-in default — handy "
        "to check what a setting would be if nobody had touched it."
    ),
)
async def cluster_settings(
    include_defaults: bool = Query(
        default=False,
        description="Include built-in default values alongside changed settings.",
    ),
    flat_settings: bool = Query(
        default=True,
        description="Return settings as flat `a.b.c` keys instead of nested objects.",
    ),
) -> Any:
    return await es_request(
        "GET",
        "/_cluster/settings",
        params={"include_defaults": include_defaults, "flat_settings": flat_settings},
    )


@router.get(
    "/cluster/pending-tasks",
    summary="Pending cluster-state tasks",
    description=(
        "Lists maintenance tasks (index creation, mapping updates, shard moves…) "
        "that are queued but not yet applied to the cluster state. A long queue "
        "with a high `time_in_queue` means the master is struggling — a common "
        "root cause when the cluster feels stuck."
    ),
)
async def pending_tasks() -> Any:
    return await es_request("GET", "/_cluster/pending_tasks")


@router.get(
    "/cluster/state",
    summary="Cluster state (internal metadata)",
    description=(
        "The full internal metadata the master distributes to all nodes: "
        "routing tables, index metadata, node memberships and more.\n\n"
        "This is verbose — use `metric` to limit it, e.g. `metric=routing_table` "
        "to see only where shards live. For day-to-day checks prefer "
        "`/cluster/health` and `/shards` instead."
    ),
)
async def cluster_state(
    metric: str | None = Query(
        default=None,
        description=(
            "Comma-separated list of metric blocks to return, e.g. "
            "`routing_table,metadata,nodes`. Omit for everything."
        ),
    ),
    index: str | None = Query(
        default=None,
        description="Comma-separated index name or wildcard pattern to limit the output.",
    ),
) -> Any:
    params: dict[str, Any] = {}
    if metric:
        params["metric"] = metric
    if index:
        params["index"] = index
    return await es_request("GET", "/_cluster/state", params=params)


@router.get(
    "/cluster/remote-info",
    summary="Remote cluster connections",
    description=(
        "Lists the remote clusters this cluster is configured to talk to "
        "(used for cross-cluster search and replication). Also reports the "
        "connection health of each remote. Returns an empty list when no "
        "remote clusters are configured."
    ),
)
async def remote_info() -> Any:
    return await es_request("GET", "/_remote/info")


@router.post(
    "/cluster/reroute",
    summary="Explicitly move or allocate shards",
    description=(
        "**Advanced / potentially disruptive.** Manually command the cluster to "
        "move, allocate or cancel allocation of specific shards — for example to "
        "drain a node or retry a stuck shard.\n\n"
        "Always pass `dry_run=true` first: it validates the command and reports "
        "what *would* happen without touching anything. Commands go in the body, "
        "e.g. `{\"commands\": [{\"allocate_stale_primary\": {...}}]}`."
    ),
)
async def cluster_reroute(
    body: dict[str, Any] | None = None,
    dry_run: bool = Query(
        default=True,
        description="Validate the commands without applying them. Keep true unless you are sure.",
    ),
    explain: bool = Query(
        default=True,
        description="Include an explanation of the attempt in the response.",
    ),
) -> Any:
    params: dict[str, Any] = {"dry_run": dry_run, "explain": explain}
    return await es_request(
        "POST", "/_cluster/reroute", params=params, json_body=body or {"commands": []}
    )

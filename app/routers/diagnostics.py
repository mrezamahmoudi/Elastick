"""
Diagnostic endpoints.

These combine several raw Elasticsearch APIs into one ready-made report,
so a first-time responder can answer "what is wrong?" without knowing
which individual APIs to call. Start here if you are new to the service.
"""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter

from app.es_client import es_request

router = APIRouter(tags=["Diagnostics"])


async def _health(level: str = "indices") -> Any:
    return await es_request("GET", "/_cluster/health", params={"level": level})


async def _shards() -> list[Any]:
    shards = await es_request("GET", "/_cat/shards", params={"format": "json"})
    return shards if isinstance(shards, list) else []


@router.get(
    "/diagnostics/overview",
    summary="One-page cluster overview (start here)",
    description=(
        "A curated snapshot for a first responder, combining the four checks "
        "that matter most:\n\n"
        "1. **health** — cluster status and shard counts.\n"
        "2. **nodes** — how many nodes, their roles and versions.\n"
        "3. **disk** — disk usage per node.\n"
        "4. **problems** — automatically computed: unassigned shard count, "
        "nodes above the 85% disk watermark, and indices that are not green.\n\n"
        "If `problems` is empty, the cluster is in good shape; everything "
        "else on this page is context."
    ),
)
async def overview() -> dict[str, Any]:
    health, nodes, disk = await asyncio.gather(
        _health(),
        es_request("GET", "/_nodes"),
        es_request("GET", "/_cat/allocation", params={"format": "json", "bytes": "b"}),
    )

    shards = await _shards()
    unassigned = [s for s in shards if str(s.get("state", "")).upper() == "UNASSIGNED"]

    node_list = []
    for node_id, info in (nodes.get("nodes") or {}).items():
        node_list.append({
            "name": info.get("name"),
            "roles": info.get("roles"),
            "version": info.get("version"),
        })

    full_health = health  # _health() defaults to level=indices, already detailed
    non_green_indices = [
        {"index": name, "status": data.get("status")}
        for name, data in (full_health.get("indices") or {}).items()
        if data.get("status") != "green"
    ]

    problems: list[str] = []
    if full_health.get("status") == "red":
        problems.append("Cluster status is RED: primary shards are unassigned.")
    elif full_health.get("status") == "yellow":
        problems.append("Cluster status is YELLOW: at least one replica is unassigned.")
    if unassigned:
        problems.append(f"{len(unassigned)} shard(s) have no copy allocated anywhere.")
    for entry in disk if isinstance(disk, list) else []:
        try:
            percent = int(str(entry.get("disk.percent", "0")).rstrip("%"))
        except (TypeError, ValueError):
            continue
        if percent >= 85:
            problems.append(
                f"Node {entry.get('node')} is at {percent}% disk "
                "(at or above the low watermark)."
            )

    return {
        "health": health,
        "nodes": node_list,
        "disk": disk,
        "problems": problems,
        "unassigned_shards": unassigned,
        "non_green_indices": non_green_indices,
    }


@router.get(
    "/diagnostics/red-indices",
    summary="Indices that are yellow or red, with reasons",
    description=(
        "Finds every index whose health is not green and, for each, explains "
        "why: how many primary/replica shards are unassigned and the "
        "Elasticsearch-provided allocation explanation for the first "
        "unassigned shard of the index.\n\n"
        "Run this when `/cluster/health` is not green and you need the "
        "per-index story rather than the cluster-level summary."
    ),
)
async def red_indices() -> dict[str, Any]:
    full_health = await _health("indices")
    shards = await _shards()

    results: list[dict[str, Any]] = []
    for name, data in (full_health.get("indices") or {}).items():
        if data.get("status") == "green":
            continue
        index_shards = [
            s for s in shards
            if s.get("index") == name
            and str(s.get("state", "")).upper() == "UNASSIGNED"
        ]
        explain = None
        if index_shards:
            try:
                explain = await es_request(
                    "GET",
                    "/_cluster/allocation/explain",
                    json_body={
                        "index": name,
                        "shard": int(index_shards[0].get("shard", 0)),
                        "primary": str(index_shards[0].get("prirep", "")).lower() == "p",
                    },
                )
            except Exception:
                explain = {"error": "allocation explain failed for this shard"}
        results.append({
            "index": name,
            "status": data.get("status"),
            "unassigned_shards": index_shards,
            "allocation_explain": explain,
        })

    return {"cluster_status": full_health.get("status"), "indices": results}


@router.get(
    "/diagnostics/full-report",
    summary="Everything, in one call (slow but complete)",
    description=(
        "A full point-in-time report for archiving, ticket attachments or "
        "handovers. Collects cluster health, stats, settings, node info and "
        "stats, disk allocation, shard states, unassigned shards, pending "
        "tasks, thread pools and snapshot repositories in a single response.\n\n"
        "It is heavier than `/diagnostics/overview` — use it when you want the "
        "complete picture or a record of *how the cluster looked at time T*."
    ),
)
async def full_report() -> dict[str, Any]:
    shards = await _shards()
    unassigned = [s for s in shards if str(s.get("state", "")).upper() == "UNASSIGNED"]

    async def safe(label: str, coro) -> tuple[str, Any]:
        try:
            return label, await coro
        except Exception as exc:
            return label, {"error": str(exc)}

    (
        (_, health),
        (_, stats),
        (_, settings),
        (_, nodes_info),
        (_, nodes_stats),
        (_, disk),
        (_, pending),
        (_, thread_pools),
        (_, repositories),
    ) = await asyncio.gather(
        safe("health", _health("shards")),
        safe("stats", es_request("GET", "/_cluster/stats")),
        safe("settings", es_request("GET", "/_cluster/settings")),
        safe("nodes_info", es_request("GET", "/_nodes")),
        safe("nodes_stats", es_request("GET", "/_nodes/stats")),
        safe("disk", es_request("GET", "/_cat/allocation", params={"format": "json", "bytes": "b"})),
        safe("pending_tasks", es_request("GET", "/_cluster/pending_tasks")),
        safe("thread_pools", es_request("GET", "/_cat/thread_pool", params={"format": "json"})),
        safe("snapshot_repositories", es_request("GET", "/_snapshot")),
    )

    return {
        "health": health,
        "cluster_stats": stats,
        "cluster_settings": settings,
        "nodes_info": nodes_info,
        "nodes_stats": nodes_stats,
        "disk_allocation": disk,
        "shards": shards,
        "unassigned_shards": unassigned,
        "pending_tasks": pending,
        "thread_pools": thread_pools,
        "snapshot_repositories": repositories,
    }

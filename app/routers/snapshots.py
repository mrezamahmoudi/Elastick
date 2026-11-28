"""
Snapshot & backup endpoints.

These answer "is my data backed up and recoverable?" — repositories,
snapshot listings and restore/recovery progress.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.es_client import es_request

router = APIRouter(tags=["Snapshots & Recovery"])


@router.get(
    "/snapshots/repositories",
    summary="List snapshot repositories",
    description=(
        "Lists every registered backup repository (filesystem, S3, GCS…) with "
        "its type and settings. If this returns nothing, the cluster has **no "
        "backups configured** — a finding worth raising on its own."
    ),
)
async def list_repositories() -> Any:
    return await es_request("GET", "/_snapshot")


@router.get(
    "/snapshots/{repository}",
    summary="List snapshots in a repository",
    description=(
        "Lists the snapshots stored in the given repository, newest-first in "
        "practice, with start/end timestamps, duration, snapshot state "
        "(`SUCCESS`, `FAILED`, `IN_PROGRESS`, `PARTIAL`) and indices included.\n\n"
        "A quick audit: is there a recent `SUCCESS` snapshot? Are there "
        "`FAILED` ones nobody noticed?"
    ),
)
async def list_snapshots(
    repository: str,
    snapshot: str = Query(
        default="_all",
        description="Snapshot name, wildcard pattern (e.g. `daily-*`) or `_all`.",
    ),
) -> Any:
    return await es_request("GET", f"/_snapshot/{repository}/{snapshot}")


@router.get(
    "/snapshots/{repository}/status",
    summary="Detailed status of snapshots (running or finished)",
    description=(
        "Per-index, per-shard breakdown of snapshot progress: files and bytes "
        "already copied versus total. Use it to answer *how far along is the "
        "snapshot that is running right now?* — `_snapshot/{repo}/_status` "
        "targets the in-progress one."
    ),
)
async def snapshot_status(
    repository: str,
    snapshot: str | None = Query(
        default=None,
        description=(
            "Snapshot name or wildcard. Omit to get the status of the "
            "currently running snapshot."
        ),
    ),
) -> Any:
    suffix = f"/{snapshot}" if snapshot else ""
    return await es_request("GET", f"/_snapshot/{repository}{suffix}/_status")


@router.get(
    "/recovery",
    summary="Cluster-wide shard recovery progress",
    description=(
        "Shows all shard recoveries across the cluster — replica rebuilds, "
        "relocations and snapshot restores — with stage, progress and timing. "
        "Restrict with `index` and toggle `active_only`.\n\n"
        "After a node restart or failover, this is how you watch the cluster "
        "heal itself and estimate when it will be green again."
    ),
)
async def cluster_recovery(
    index: str | None = Query(
        default=None,
        description="Comma-separated index names or wildcard patterns to filter by.",
    ),
    active_only: bool = Query(
        default=False,
        description="Only show recoveries currently in progress.",
    ),
    detailed: bool = Query(
        default=False,
        description="Include per-file detail (verbose).",
    ),
) -> Any:
    params: dict[str, Any] = {"active_only": active_only, "detailed": detailed}
    path = f"/{index}/_recovery" if index else "/_recovery"
    return await es_request("GET", path, params=params)

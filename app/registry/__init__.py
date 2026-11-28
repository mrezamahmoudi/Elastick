"""The full Elasticsearch 8 API registry, organized by category.

`ALL_ENTRIES` is the complete list of raw Elasticsearch APIs exposed through
Elastick; `TAGS_METADATA` provides the Swagger category descriptions.
"""

from __future__ import annotations

from .builder import build_router
from .core import Entry, E
from . import (
    analytics,
    cat,
    cluster_nodes,
    documents,
    indices,
    platform,
    scripting_async,
    search,
    security,
    snapshots_lifecycle,
)

ALL_ENTRIES: list[Entry] = (
    cluster_nodes.ENTRIES
    + indices.ENTRIES
    + documents.ENTRIES
    + search.ENTRIES
    + cat.ENTRIES
    + snapshots_lifecycle.ENTRIES
    + security.ENTRIES
    + scripting_async.ENTRIES
    + analytics.ENTRIES
    + platform.ENTRIES
)

TAGS_METADATA = [
    {
        "name": "Documents",
        "description": (
            "Write and read documents: index/create/update/delete, bulk "
            "(NDJSON), multi-get, reindex, delete-by-query and count."
        ),
    },
    {
        "name": "Search",
        "description": (
            "The search surface: query DSL search, multi-search, scroll and "
            "point-in-time pagination, templates, term vectors, field "
            "capabilities and rank evaluation."
        ),
    },
    {
        "name": "Cat APIs",
        "description": (
            "Compact tabular views (`_cat/*`) designed for humans: one row "
            "per object. Always returned as JSON here. Great for quick "
            "checks from the command line."
        ),
    },
    {
        "name": "Security",
        "description": (
            "Users, roles, privileges, API keys, tokens, SAML/OpenID flows "
            "and TLS certificate inspection. Handle with care — this is the "
            "access-control surface."
        ),
    },
    {
        "name": "Snapshot Lifecycle (SLM)",
        "description": (
            "Automatic snapshot policies: schedules, retention, execution "
            "and the service start/stop state."
        ),
    },
    {
        "name": "Index Lifecycle (ILM)",
        "description": (
            "Index lifecycle policies (hot → warm → cold → delete), per-index "
            "lifecycle position, and moving stuck indices."
        ),
    },
    {
        "name": "Data Streams",
        "description": (
            "Append-only streams of time-based backing indices: creation, "
            "stats, rollover and migration from aliases."
        ),
    },
    {
        "name": "Index Templates",
        "description": (
            "Composable index templates and component templates (plus legacy "
            "templates), including simulation endpoints that show what a "
            "template would produce."
        ),
    },
    {
        "name": "Ingest",
        "description": (
            "Ingest pipelines and their processors, including simulation for "
            "testing transformation logic before it touches real data."
        ),
    },
    {
        "name": "Scripting",
        "description": (
            "Stored scripts, script contexts/languages and the Painless "
            "execute scratchpad."
        ),
    },
    {
        "name": "Async Search",
        "description": (
            "Background searches with a handle: submit, poll results, check "
            "status and cancel."
        ),
    },
    {
        "name": "SQL",
        "description": (
            "SQL queries over indices, async execution, cursors and SQL→DSL "
            "translation."
        ),
    },
    {
        "name": "EQL",
        "description": (
            "Event Query Language for sequence-based event analysis (security "
            "analytics)."
        ),
    },
    {
        "name": "Machine Learning",
        "description": (
            "Anomaly detection jobs and datafeeds, data frame analytics and "
            "trained model deployments — lifecycle plus results."
        ),
    },
    {
        "name": "Transforms",
        "description": (
            "Continuous aggregation jobs: definition, start/stop, preview, "
            "progress statistics."
        ),
    },
    {
        "name": "Rollup",
        "description": (
            "Pre-aggregated historical data jobs and searching rollup "
            "indices transparently."
        ),
    },
    {
        "name": "Watcher",
        "description": (
            "Alerting watches: definitions, acknowledge/activate, dry-run "
            "execution and service statistics."
        ),
    },
    {
        "name": "Enrich",
        "description": (
            "Enrichment policies that join reference data into documents at "
            "ingest time."
        ),
    },
    {
        "name": "Graph",
        "description": "Term-association exploration across documents.",
    },
    {
        "name": "Cross-Cluster Replication",
        "description": (
            "Follower indices, auto-follow patterns and replication "
            "statistics between clusters."
        ),
    },
    {
        "name": "Synonyms",
        "description": "Stored synonym sets and individual synonym rules.",
    },
    {
        "name": "Query Rules",
        "description": (
            "Curated query rulesets for result pinning/exclusion in search "
            "applications."
        ),
    },
    {
        "name": "Search Applications",
        "description": (
            "Named search applications wrapping indices with query templates."
        ),
    },
    {
        "name": "Licensing",
        "description": (
            "Current license, installing/removing licenses, starting trial "
            "or basic."
        ),
    },
    {
        "name": "Platform & X-Pack",
        "description": (
            "Cluster platform surface: X-Pack feature usage, upgrade "
            "deprecations, system features, monitoring ingestion and "
            "Logstash pipeline management."
        ),
    },
]

__all__ = ["ALL_ENTRIES", "TAGS_METADATA", "build_router", "Entry", "E"]

"""
Elastick — a FastAPI service for checking and administering an Elasticsearch
cluster through its REST APIs.

Run it with:

    uvicorn app.main:app --reload --port 8000

Then open the interactive Swagger UI at:

    http://localhost:8000/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import auth
from app.config import settings
from app.es_client import close_client
from app.registry import ALL_ENTRIES, TAGS_METADATA as REGISTRY_TAGS, build_router
from app.routers import cluster, diagnostics, indices, nodes, shards, snapshots, tasks

TAGS_METADATA = [
    {
        "name": "Diagnostics",
        "description": (
            "**Start here.** Ready-made reports that combine several raw APIs "
            "into one answer for *what is wrong with the cluster?* Ideal if you "
            "are new to Elasticsearch operations."
        ),
    },
    {
        "name": "Cluster",
        "description": (
            "Cluster-wide health and configuration: green/yellow/red status, "
            "resource statistics, cluster settings, pending maintenance tasks "
            "and shard-reroute commands."
        ),
    },
    {
        "name": "Nodes",
        "description": (
            "Per-machine checks: which nodes exist, their CPU/heap/disk usage, "
            "hot threads when a node is busy, and thread-pool queue/rejection "
            "counters."
        ),
    },
    {
        "name": "Indices",
        "description": (
            "Per-index checks: sizes and document counts, settings, mappings, "
            "segments, recovery progress and on-disk shard copies."
        ),
    },
    {
        "name": "Shards & Allocation",
        "description": (
            "The heart of red/yellow troubleshooting: where every shard lives, "
            "which ones are unassigned, and Elasticsearch's own explanation of "
            "why a shard cannot be placed."
        ),
    },
    {
        "name": "Snapshots & Recovery",
        "description": (
            "Backup checks: registered snapshot repositories, snapshot lists "
            "and statuses, and cluster-wide shard recovery progress."
        ),
    },
    {
        "name": "Tasks & Maintenance",
        "description": (
            "What the cluster is working on right now: running tasks and their "
            "progress, cancelling a runaway task, plus force-merge and cache "
            "maintenance operations."
        ),
    },
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Open Elasticsearch connections on startup, close them on shutdown."""
    yield
    await close_client()


app = FastAPI(
    title=settings.service_title,
    description=(
        "A REST service for **checking an Elasticsearch cluster** through its "
        "own APIs — built for administrators and first-time responders.\n\n"
        "### How to use this service\n"
        "1. Configure the target cluster via the `ELASTICSEARCH_URL`, "
        "`ELASTICSEARCH_USERNAME` and `ELASTICSEARCH_PASSWORD` environment "
        "variables (see `.env.example`).\n"
        "2. Open the **Diagnostics** category and call "
        "`GET /diagnostics/overview` — it tells you in one call whether "
        "anything needs attention.\n"
        "3. If something is wrong, drill down with the **Cluster**, "
        "**Shards & Allocation** and **Nodes** categories; every endpoint's "
        "description explains what it shows and when to use it.\n\n"
        "### Coverage\n"
        "This service exposes the **complete Elasticsearch 8 API surface** "
        "(every REST API group: cluster, nodes, indices, documents, search, "
        "cat, snapshots, SLM/ILM, data streams, templates, ingest, security, "
        "scripting, async search, SQL, EQL, ML, transforms, rollup, watcher, "
        "enrich, CCR, licensing and more). The curated endpoints use friendly "
        "paths (e.g. `/cluster/health`); the full raw surface uses the real "
        "Elasticsearch paths (e.g. `/_cluster/health`) and forwards path "
        "segments, query parameters and bodies verbatim.\n\n"
        "### Conventions\n"
        "- All endpoints proxy live Elasticsearch APIs; responses are passed "
        "through essentially unchanged so you can compare them with official "
        "Elasticsearch documentation.\n"
        "- Read-only checks are `GET`. Clearly disruptive operations "
        "(reroute, cancel task, force-merge) are `POST` and are labelled as "
        "such in their descriptions.\n"
        "- If Elasticsearch is unreachable, endpoints return HTTP 502 with "
        "the underlying reason."
    ),
    version=settings.service_version,
    openapi_tags=TAGS_METADATA + REGISTRY_TAGS,
    lifespan=lifespan,
)

# Protect the whole service with an API key when ELASTICK_API_KEY is set.
_protected = [Depends(auth.require_api_key)]

for router_module in (diagnostics, cluster, nodes, indices, shards, snapshots, tasks):
    app.include_router(router_module.router, dependencies=_protected)


@app.get("/service-info", tags=["Health"], summary="Service self-check")
async def service_info() -> dict:
    """Confirms the Elastick service itself is running (does not touch Elasticsearch)."""
    body: dict = {
        "service": settings.service_title,
        "version": settings.service_version,
        "docs": "/docs",
        "target_cluster": settings.elasticsearch_url,
    }
    if settings.ui_enabled:
        body["ui"] = "/"
    return body


@app.get("/health", tags=["Health"], summary="Service liveness probe")
async def health() -> dict:
    """Simple liveness endpoint for load balancers; does not touch Elasticsearch."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Bundled web UI (React SPA built into ui/dist).
#
# Routing contract:
#   /          -> the web UI (the default entry point)
#   /docs      -> Swagger UI (always available)
#   /ui        -> redirects to /
#   /ui/assets -> the built JS/CSS bundle
#
# When ELASTICK_UI_ENABLED=false, / redirects to /docs (Swagger-only mode).
# When the bundle is missing (local dev without a UI build), / explains how
# to build it. Registered BEFORE the registry router so catch-all API paths
# like GET /{index} never shadow it.
# ---------------------------------------------------------------------------
UI_DIST_DIR = Path(__file__).resolve().parent.parent / "ui" / "dist"


def _mount_ui() -> None:
    index_file = UI_DIST_DIR / "index.html"
    ui_available = settings.ui_enabled and index_file.is_file()

    @app.get("/", include_in_schema=False)
    async def root_page():
        if ui_available:
            return FileResponse(index_file)
        if not settings.ui_enabled:
            # UI disabled by configuration: Swagger is the only interface.
            return RedirectResponse("/docs")
        return {
            "detail": (
                "UI is enabled but not built. Run `cd ui && npm install && "
                "npm run build`, or use the Docker image (it builds the UI "
                "automatically). Swagger remains available at /docs."
            )
        }

    @app.get("/ui", include_in_schema=False)
    async def ui_redirect():
        return RedirectResponse("/")

    if ui_available:
        if (UI_DIST_DIR / "assets").is_dir():
            app.mount("/ui/assets", StaticFiles(directory=UI_DIST_DIR / "assets"),
                      name="ui-assets")

        @app.get("/ui/{full_path:path}", include_in_schema=False)
        async def ui_spa(full_path: str):
            # Serve real files (favicon, images…); everything else falls back
            # to index.html so the SPA keeps working on arbitrary sub-paths.
            candidate = (UI_DIST_DIR / full_path).resolve()
            if (
                full_path
                and candidate.is_file()
                and str(candidate).startswith(str(UI_DIST_DIR))
            ):
                return FileResponse(candidate)
            return FileResponse(index_file)


_mount_ui()


# Full raw Elasticsearch API surface, generated from the registry. Registered
# LAST so the curated endpoints above (and /docs, /health) always win on
# path conflicts; every registry route uses the real ES path (/_cluster/...,
# /{index}/_search, ...) and forwards path/query/body verbatim.
app.include_router(build_router(ALL_ENTRIES), dependencies=_protected)

# Elastick

A FastAPI service for **checking an Elasticsearch cluster** through its REST
APIs — designed for cluster administrators and for anyone responding to a
cluster problem for the first time.

Every endpoint is documented in the built-in Swagger UI so a newcomer can see
what each one is for, when to use it, and whether it is safe or disruptive.

**Further reading:** [docs/architecture.md](docs/architecture.md) explains the
project's structure and design patterns; [CLAUDE.md](CLAUDE.md) holds the
development guardrails.

## Quick start

```bash
# 1. Install dependencies (a virtualenv is recommended)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Point Elastick at your cluster
cp .env.example .env          # edit values, then:
set -a; source .env; set +a   # or export the variables your own way

# 3. Run the service
uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/docs** for Swagger. The web UI at `/` needs a
one-time build (`cd ui && npm install && npm run build`) — or just use
Docker, which builds it for you (next section).

## Web UI

The bundled React UI is the **default entry point**: open
**http://localhost:8000/** and you get the UI. Swagger stays at
**http://localhost:8000/docs**. (The Docker image builds the UI
automatically; for local development see below — `cd ui && npm install &&
npm run dev` starts it against a local backend on port 8000.)

Routing contract:

| Path | Serves |
|---|---|
| `/` | The web UI |
| `/docs` | Swagger UI |
| `/ui` | Redirects to `/` |
| `/service-info` | JSON self-check (service name, version, target cluster) |
| `/health` | Liveness probe for load balancers |

Screens:

- **Overview** — polls `GET /diagnostics/overview` every 15s: cluster status
  badge, node/disk tables and an auto-computed problem list.
- **Indices** — the `_cat/indices` table with live filtering.
- **Shards** — unassigned shards with a one-click **Explain** button that
  calls the allocation-explain API and shows Elasticsearch's reason.
- **API Explorer** — a form for *every* endpoint of the service, generated
  live from `openapi.json`: pick a category, pick an endpoint, fill path and
  query parameters, edit the JSON body, send, and see the response. New
  endpoints appear here automatically — the UI can never lag behind the API.

If the service runs with `ELASTICK_API_KEY` set, the UI prompts for the key
once (stored in the browser's localStorage) and sends it as `X-API-Key` on
every call.

### Disabling the UI

Set `ELASTICK_UI_ENABLED=false` for a Swagger-only deployment — `/` then
redirects to `/docs` and no UI assets are served.

## Run with Docker

```bash
# 1. Configure the target cluster
cp .env.example .env            # edit ELASTICSEARCH_URL / credentials

# 2. Build and run
docker compose up -d --build
# Web UI:  http://localhost:8000/
# Swagger: http://localhost:8000/docs
```

The compose file also ships an **optional local Elasticsearch** (single node,
security off) so you can test Elastick without a real cluster:

```bash
docker compose --profile dev up -d --build
```

With that profile, `ELASTICSEARCH_URL` defaults to `http://elasticsearch:9200`
and Elastick talks to the local dev node. The dev Elasticsearch is *not*
started by a plain `docker compose up`.

## Run the published image

The image reads seven environment variables at runtime — all optional, all
with defaults:

| Variable | Default | Purpose |
|---|---|---|
| `ELASTICSEARCH_URL` | `http://localhost:9200` | Target cluster base URL |
| `ELASTICSEARCH_USERNAME` | `elastic` | User for the target cluster |
| `ELASTICSEARCH_PASSWORD` | *(empty)* | Password for the target cluster |
| `ELASTIC_VERIFY_SSL` | `true` | `false` for self-signed certs |
| `ELASTIC_TIMEOUT` | `30` | Per-request timeout (seconds) |
| `ELASTICK_API_KEY` | *(empty)* | When set, clients must send `X-API-Key` |
| `ELASTICK_UI_ENABLED` | `true` | `false` for a Swagger-only deployment |

```bash
docker run -d --name elastick -p 8000:8000 \
  -e ELASTICSEARCH_URL=https://es-prod.internal:9200 \
  -e ELASTICSEARCH_USERNAME=elastick-monitor \
  -e ELASTICSEARCH_PASSWORD=secret \
  -e ELASTIC_VERIFY_SSL=false \
  your-dockerhub-username/elastick:latest
```

Or with a file instead of inline `-e` flags (better for secrets):

```bash
# elastick.env — do not commit this file
ELASTICSEARCH_URL=https://es-prod.internal:9200
ELASTICSEARCH_USERNAME=elastick-monitor
ELASTICSEARCH_PASSWORD=secret
ELASTIC_VERIFY_SSL=false
```

```bash
docker run -d --name elastick -p 8000:8000 --env-file elastick.env \
  your-dockerhub-username/elastick:latest
```

Then open `http://localhost:8000/` (UI) or `http://localhost:8000/docs` (Swagger).

## Publish to Docker Hub

```bash
docker build -t your-dockerhub-username/elastick:1.0.0 -t your-dockerhub-username/elastick:latest .
docker push your-dockerhub-username/elastick:1.0.0
docker push your-dockerhub-username/elastick:latest
```

Notes:

- The `.dockerignore` keeps `.env` out of the build context — credentials must
  only ever enter via `-e`/`--env-file` at runtime, never the image.
- Inside a container, `localhost` refers to the container itself, so
  `ELASTICSEARCH_URL` must point at a reachable address — on macOS/Windows
  Docker Desktop use `http://host.docker.internal:9200` to reach a cluster on
  the host.

## Configuration (environment variables)

| Variable | Default | Purpose |
|---|---|---|
| `ELASTICSEARCH_URL` | `http://localhost:9200` | Target cluster base URL |
| `ELASTICSEARCH_USERNAME` | `elastic` | User for the target cluster |
| `ELASTICSEARCH_PASSWORD` | *(empty)* | Password for the target cluster |
| `ELASTIC_VERIFY_SSL` | `true` | Set `false` for self-signed certs |
| `ELASTIC_TIMEOUT` | `30` | Per-request timeout in seconds |
| `ELASTICK_API_KEY` | *(empty)* | When set, clients must send `X-API-Key` |
| `ELASTICK_UI_ENABLED` | `true` | Set `false` for a Swagger-only deployment |

For the Elasticsearch user, a dedicated account with the built-in
`monitor` and `manage` cluster privileges is the least-privilege choice for
everything this service does.

## Project structure

```
Elastick/
├── app/
│   ├── main.py              # FastAPI app, Swagger metadata, UI serving, routing order
│   ├── config.py            # Env-based settings (no framework needed)
│   ├── es_client.py         # Shared async httpx client; error mapping to 502/504
│   ├── auth.py              # Optional X-API-Key protection
│   ├── routers/             # Curated endpoints (friendly paths)
│   │   ├── diagnostics.py   #   overview / red-indices / full-report
│   │   ├── cluster.py, nodes.py, indices.py, shards.py,
│   │   ├── snapshots.py, tasks.py
│   └── registry/            # Full raw ES-8 API surface, declared as data
│       ├── core.py          #   Entry/E types
│       ├── builder.py       #   Entry -> FastAPI route (path/query/body passthrough)
│       ├── cluster_nodes.py, indices.py, documents.py, search.py, cat.py,
│       ├── snapshots_lifecycle.py, security.py, scripting_async.py,
│       └── analytics.py, platform.py
├── ui/                      # React + TS + Vite + Ant Design web UI
│   ├── src/pages/           #   Overview, Indices, Shards, ApiExplorer
│   └── src/api.ts           #   fetch wrapper with X-API-Key handling
├── Dockerfile               # Multi-stage: Node builds ui/, Python serves everything
├── docker-compose.yml       # Service + optional dev Elasticsearch (profile: dev)
├── requirements.txt
└── .env.example
```

## Endpoint categories

| Category | Purpose |
|---|---|
| **Diagnostics** | Ready-made combined reports. Start with `GET /diagnostics/overview`. |
| **Cluster** | Health status, cluster stats, settings, pending tasks, reroute. |
| **Nodes** | Node list, per-node stats, hot threads, disk usage, thread pools. |
| **Indices** | Index listing, stats, settings, mappings, recovery, segments. |
| **Shards & Allocation** | Shard placement, unassigned shards, allocation explain. |
| **Documents** | Index/get/update/delete docs, bulk (NDJSON), reindex, count. |
| **Search** | Query DSL search, multi-search, scroll, PIT, templates, field caps. |
| **Cat APIs** | The full `_cat/*` family, returned as JSON. |
| **Snapshots & Recovery** | Repositories, snapshot create/restore/clone/status. |
| **Snapshot Lifecycle (SLM)** | Automatic snapshot policies and retention. |
| **Index Lifecycle (ILM)** | Lifecycle policies, per-index phase, stuck-index repair. |
| **Data Streams** | Create/stats/rollover/migrate data streams. |
| **Index Templates** | Composable + component + legacy templates, with simulation. |
| **Ingest** | Ingest pipelines, simulation, processor info. |
| **Security** | Users, roles, privileges, API keys, tokens, SAML/OIDC, TLS certs. |
| **Scripting** | Stored scripts, contexts, Painless execute. |
| **Async Search** | Background searches: submit, poll, status, cancel. |
| **SQL / EQL** | SQL queries and translation; EQL event searches. |
| **Machine Learning** | Anomaly jobs, datafeeds, data frame analytics, trained models. |
| **Transforms / Rollup** | Continuous aggregation jobs and rollup search. |
| **Watcher / Enrich / Graph** | Alerting watches, enrichment policies, graph explore. |
| **Cross-Cluster Replication** | Follow/auto-follow, pause/resume, stats. |
| **Synonyms / Query Rules / Search Applications** | Search curation features. |
| **Licensing / Platform & X-Pack** | License, X-Pack usage, deprecations, features. |
| **Tasks & Maintenance** | Running tasks, task cancel, force-merge, cache clear. |
| **Health** | Elastick's own endpoints: `/health` (liveness), `/service-info` (self-check). |

### Two layers of endpoints

- **Curated endpoints** (friendly paths like `/cluster/health`, `/shards`) —
  hand-written with the most useful parameters exposed directly. Best starting
  point; these are the ones the Diagnostics reports use.
- **Full raw API surface** (real ES paths like `/_cluster/health`,
  `/{index}/_search`, `/_security/user/{username}`) — generated from an
  internal registry covering every Elasticsearch 8 API group, with path
  segments, query parameters and bodies forwarded verbatim. If an endpoint
  exists in the Elasticsearch API docs, it is available here. `_cat` endpoints
  automatically return JSON unless you override `format`.

### Where do I find…? (curated ↔ raw mapping)

Key diagnostics exist in both layers, sometimes under different paths and
categories. The raw paths always match the official Elasticsearch API docs:

| Task | Curated path | Raw ES path (category) |
|---|---|---|
| Cluster health | `GET /cluster/health` | `GET /_cluster/health` (Cluster) |
| Cluster stats / settings | `GET /cluster/stats`, `GET /cluster/settings` | `GET /_cluster/stats`, `GET /_cluster/settings` (Cluster) |
| Why is a shard unassigned? | `POST /shards/allocation-explain` | `GET /_cluster/allocation/explain` or `POST` with a body (Shards & Allocation) |
| List shards / unassigned | `GET /shards`, `GET /shards/unassigned` | `GET /_cat/shards` (Cat APIs) |
| Node stats / hot threads | `GET /nodes/stats`, `GET /nodes/hot-threads` | `GET /_nodes/stats`, `GET /_nodes/hot_threads` (Nodes) |
| Disk per node | `GET /nodes/disk-usage` | `GET /_cat/allocation` (Cat APIs) |
| Index stats / settings / mapping | `GET /indices/{index}/stats` … | `GET /{index}/_stats`, `GET /{index}/_settings`, `GET /{index}/_mapping` (Indices) |
| Snapshot repositories / status | `GET /snapshots/repositories` | `GET /_snapshot`, `GET /_snapshot/{repo}/{snapshot}/_status` (Snapshots & Recovery) |
| Running tasks | `GET /tasks` | `GET /_tasks` (Tasks & Maintenance) |
| One-page health report | `GET /diagnostics/overview` | — (curated only; combines the raw APIs above) |

Tip: in Swagger UI, use the search/filter box at the top of `/docs` and type
a fragment such as `allocation` or `explain` — it filters every endpoint
across all categories.

## Suggested first-time walkthrough

1. `GET /diagnostics/overview` — one call; if `problems` is empty, all good.
2. If the cluster is yellow/red: `GET /shards/unassigned`, then
   `POST /shards/allocation-explain` (empty body) for the reason.
3. If a node misbehaves: `GET /nodes/stats` and `GET /nodes/hot-threads`.
4. Before sign-off: `GET /snapshots/repositories` to confirm backups exist.

## Notes

- Responses are the raw Elasticsearch API payloads (pass-through), so they can
  be compared directly with the official Elasticsearch documentation.
- Disruptive operations (`reroute`, `cancel`, `force-merge`, …) are marked as
  such in their descriptions. Read-only checks never modify the cluster.
- If the target cluster is unreachable, endpoints return HTTP 502 (or 504 on
  timeout) with the underlying reason in the body.
- A few endpoints target newer 8.x APIs and will be rejected by older
  clusters: `GET /_health_report` (8.11+), node shutdown APIs (8.0+),
  synonyms and query rules (8.10+). Their descriptions note the requirement.

# Elastick — Architecture & Design Report

*Audience: developers joining the project. Read this before changing code.*

## 1. What Elastick is

Elastick is a FastAPI service that exposes an Elasticsearch cluster's REST
APIs for administrators and first-time responders. It has two jobs:

1. **Health checking** — curated, well-documented endpoints and combined
   diagnostic reports that answer "what is wrong with this cluster?".
2. **Full API coverage** — the complete Elasticsearch 8 API surface,
   proxied verbatim, so nothing in the official API docs is missing.

A bundled React UI (served by the same service at `/`) gives a live
operational view; Swagger at `/docs` documents every endpoint.

## 2. Architecture: layered, with two presentation paths

```
                 ┌─────────────────────────────────────────┐
   Browser ────► │  UI (React SPA)  ── also served by ──┐  │
   curl/Swagger  │  Swagger (/docs)                     │  │
                 └──────────────────────────────────────┼──┘
                                                        ▼
   ┌─────────────────────────────────────────────────────────────┐
   │ Presentation layer                                          │
   │  ① Curated routers (app/routers/*.py)  ← friendly paths     │
   │  ② Registry-built routes (app/registry/) ← raw ES paths     │
   ├─────────────────────────────────────────────────────────────┤
   │ Cross-cutting: app/auth.py (API-key dependency)             │
   ├─────────────────────────────────────────────────────────────┤
   │ Client layer: app/es_client.py (one async httpx client)     │
   ├─────────────────────────────────────────────────────────────┤
   │ Config layer: app/config.py (env-driven settings)           │
   └──────────────────────────────────────┬──────────────────────┘
                                          ▼
                              Elasticsearch cluster
```

The key structural decision: **two presentation layers over one shared
client**.

- **Curated routers** (`app/routers/`) are hand-written endpoints with
  friendly paths (`/cluster/health`, `/shards/unassigned`) and the most
  useful parameters exposed directly. They include the Diagnostics reports
  that combine several raw APIs into one answer.
- **The registry** (`app/registry/`) declares ~300 endpoints as *data* and
  generates FastAPI routes from them. Paths are the real Elasticsearch paths
  (`/_cluster/health`, `/{index}/_search`), and path segments, query
  parameters and bodies are forwarded verbatim.

Both layers funnel into the same `es_request()`, so authentication, TLS
verification, timeouts and error handling exist in exactly one place.

### Route precedence (important)

`main.py` registers routes in a deliberate order:

1. FastAPI's own routes (`/docs`, `/openapi.json`)
2. Curated routers
3. `/service-info`, `/health`
4. UI routes (`/`, `/ui`, `/ui/assets`)
5. **Registry router last**

Registry routes include catch-all patterns like `GET /{index}`, so anything
registered after the registry would be shadowed by it. **Never move the
registry include earlier.**

## 3. Design patterns

### Backend

| Pattern | Where | Purpose |
|---|---|---|
| Singleton (lazy) | `es_client.get_client()` | One connection pool per process; closed on shutdown via the lifespan hook. |
| Facade | `es_request()` | Hides auth, TLS, timeouts, NDJSON vs JSON bodies, and error translation behind one call. |
| Data-driven / table-driven design | `app/registry/*.py` | Endpoints are declarative `Entry` records; behavior lives in one builder. Adding an API = adding one `E(...)` line. |
| Factory + Builder | `E()`, `build_router()` | Entries are normalized by the factory; the builder assembles FastAPI routes, injecting path parameters via a generated `__signature__`. |
| Dependency Injection | `Depends(auth.require_api_key)` | Auth is a pluggable dependency applied to every router in one line. |
| Adapter / anti-corruption layer | error mapping in `es_client.py` | Elasticsearch errors become stable HTTP semantics: 502 unreachable, 504 timeout, with the original reason preserved. |
| Pass-through proxy | registry endpoints | Raw ES payloads are returned unmodified — the service is never a second source of truth for response shapes. |
| Graceful degradation | `_mount_ui()` | Three UI states (built / not built / disabled), each with a sensible fallback instead of a crash. |
| Value object | `Entry` frozen dataclass | Immutable endpoint definitions. |
| Composition root | `main.py` | Single place where wiring and route order are explicit. |

### Frontend (`ui/`)

| Pattern | Where | Purpose |
|---|---|---|
| Provider | `QueryClientProvider`, `ConfigProvider` | Server state and theming live above the components. |
| Declarative data fetching | TanStack Query `useQuery` | Polling, caching and error states are library concerns, not hand-rolled effects. |
| Observer / event bus | `elastick:unauthorized` window event | Any 401 anywhere opens the API-key modal without prop drilling. |
| Error boundary | `main.tsx` | Render crashes surface as a visible report, never a blank page. |
| Schema-driven UI | `ApiExplorer` page | Forms are generated from `/openapi.json` at runtime — the UI cannot drift from the API. |
| Repository module | `ui/src/api.ts` | Single fetch wrapper (API-key injection, error normalization); components never call `fetch` directly. |

## 4. Data flow example

A user opens the UI Overview page:

1. React calls `GET /diagnostics/overview` (curated router) every 15 s.
2. The handler runs several `es_request()` calls concurrently
   (`/_cluster/health`, `/_nodes`, `/_cat/allocation`, `/_cat/shards`).
3. `es_request()` sends them through the shared httpx client with the
   configured credentials; ES errors become HTTP 502/504 with reasons.
4. The handler merges the results into one report and computes the
   `problems` list (red/yellow status, unassigned shards, disk watermarks).
5. The UI renders status, tables and alerts; the API Explorer would expose
   the same underlying raw endpoints as forms, generated from
   `openapi.json`.

## 5. How to extend

| Goal | Where | Cost |
|---|---|---|
| Expose a new Elasticsearch API | one `E(...)` line in the relevant `app/registry/*.py` file | ~5 lines; UI picks it up automatically |
| Add a curated workflow/diagnostic | new function in an `app/routers/*.py` module (or a new router registered in `main.py`) | a function with a rich docstring |
| Add a UI screen | new page in `ui/src/pages/`, register it in `App.tsx` | component + menu entry |
| Add a configuration knob | field in `app/config.py` + `.env.example` + README tables | three small edits |

Nothing else in the system needs to change for any of the above — that is
the point of the structure.

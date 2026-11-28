# CLAUDE.md — Development guardrails for Elastick

Guidance for AI coding agents and developers working in this repository.
Read `docs/architecture.md` first for the full architecture and design
rationale; this file states the rules that keep it intact.

## Project in one paragraph

Elastick is a FastAPI service that proxies an Elasticsearch cluster's REST
APIs for administrators: curated health-check endpoints, a data-driven
registry exposing the complete Elasticsearch 8 API surface, and a bundled
React UI served from the same process at `/` (Swagger at `/docs`).

## Commands

```bash
# Backend (local)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# UI (local dev — hot reload, proxies API calls to :8000)
cd ui && npm install && npm run dev     # open http://localhost:5173/ui

# UI production build (required for `/` to serve the UI outside Docker)
cd ui && npm install && npm run build

# Docker (builds the UI automatically)
docker compose up -d --build

# Syntax check (no test suite exists yet)
python3 -m compileall app
```

There is no test suite. Until there is one, **verify every backend change by
booting the app** (`uvicorn app.main:app`) and confirm it starts without
tracebacks; verify UI changes with `npm run build` (or at minimum
`npm run typecheck`).

## Architecture invariants — do not break these

1. **All Elasticsearch traffic goes through `app/es_client.py`.** Never call
   `httpx`/`requests` directly from a router or the UI. Error handling
   (502 unreachable / 504 timeout, original reason preserved) lives only
   there.
2. **Route registration order in `main.py` is load-bearing.** Order is:
   curated routers → `/service-info`, `/health` → UI routes → registry
   router **last**. The registry contains catch-alls like `GET /{index}`;
   anything registered after it is unreachable. Never move the registry
   include earlier, and never register new routes after it.
3. **New Elasticsearch APIs go in the registry, not as hand-written
   routes.** Add one `E(method, path, tag, summary, description)` entry to
   the matching `app/registry/*.py` file. Use the real ES path. Never
   duplicate a `method + path` pair across registry files.
4. **Curated routers are for workflows, not coverage.** Only add a
   hand-written endpoint when it combines APIs, transforms data, or needs
   custom logic (like `/diagnostics/overview`). Pure pass-throughs belong in
   the registry.
5. **The UI must stay schema-driven.** The API Explorer reads
   `/openapi.json` — never hardcode endpoint lists in UI code. Purpose-built
   pages (Overview, Indices, Shards) may call curated endpoints only.
6. **The `ELASTICK_UI_ENABLED` toggle must keep working end-to-end:**
   disabled → `/` redirects to `/docs`, no UI assets served; enabled-but-
   unbuilt → explanatory JSON; built → SPA at `/` with fallback at `/ui`.
   Any change to UI serving must preserve all three states.

## Documentation requirements (non-negotiable, user requirement)

- **Every endpoint must have a `summary` and a `description`** written for
  someone seeing Elasticsearch for the first time: what it shows, when to
  use it, and what the key fields mean. No bare endpoints.
- **Disruptive operations must be labelled** in their description
  ("**Destructive**", "**Advanced / potentially disruptive**",
  "**Maintenance**"): delete, reroute, cancel, force-merge, restore, ILM
  stop, settings changes, etc.
- Registry entries must set the correct `tag` — the category is part of the
  deliverable (e.g. allocation explain belongs in "Shards & Allocation",
  not "Cluster").
- When you add or change behavior, update `README.md` in the same change
  (env-var tables, endpoint categories, routing contract) and, when the
  architecture itself changes, `docs/architecture.md`.

## Security guardrails

- Never commit secrets: no `.env`, credentials, tokens, or real cluster
  hostnames in code, tests, or docs. `.env.example` holds placeholders only.
- `.dockerignore` must keep `.env`, `.venv`, `ui/node_modules`, and `ui/dist`
  out of the build context. Verify after any Dockerfile change.
- The Elasticsearch user should be least-privilege (`monitor` + `manage`);
  do not document or default to superuser accounts.
- `ELASTICK_API_KEY` is optional but is the only gate on destructive
  operations — when touching `app/auth.py`, fail **closed** (401) and never
  weaken the comparison (no substring/prefix matching).
- UI path serving must keep the traversal check
  (`resolve()` + `startswith(UI_DIST_DIR)`) intact.

## Conventions

- **Config:** every knob is an environment variable read in
  `app/config.py`; prefix target-cluster settings with `ELASTIC_` and
  service settings with `ELASTICK_`. Any new variable must be added to
  `.env.example`, `docker-compose.yml`, and both README tables.
- **Responses:** pass Elasticsearch payloads through unchanged; do not
  reshape raw-API responses (curated diagnostics may compose/transform).
- **Code style:** Python with type hints and module docstrings; TypeScript
  with explicit types where practical. Comments and docs in English.
- **Dependencies:** keep minimal. The backend should stay on
  `fastapi`/`uvicorn`/`httpx` only; add nothing without strong justification.
- **Alpine gotchas:** the image is `python:3.13-alpine` — the unprivileged
  user is `nobody:nobody` (not `nogroup`), and compiled wheels need musl
  support. Do not switch base images casually.

## Known gaps (fair game for improvement, in priority order)

1. No test suite — a pytest suite mocking `es_request` would be the single
   highest-value addition.
2. The registry was never diffed against the official Elasticsearch API
   list — expect a few missing/renamed endpoints; fix by editing entries.
3. No CI, no linting config, no git repository initialized yet.
4. `ui/dist` is gitignored from Docker context but the repo has no
   `.gitignore` yet — create one before `git init` (exclude `.env`,
   `.venv`, `__pycache__`, `ui/node_modules`, `ui/dist`).

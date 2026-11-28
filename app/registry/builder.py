"""Turns registry entries into FastAPI routes.

The generated endpoints are faithful pass-through proxies: path segments,
query parameters and the request body are forwarded to Elasticsearch
unchanged, so every call behaves exactly like the equivalent call against
Elasticsearch itself (responses are the raw Elasticsearch payloads).
"""

from __future__ import annotations

import inspect
import re

from fastapi import APIRouter, Request

from app.es_client import es_request

from .core import Entry

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_PATH_PARAM_RE = re.compile(r"\{(\w+)\}")


def _operation_name(entry: Entry) -> str:
    slug = _SLUG_RE.sub("_", entry.path.lower()).strip("_")
    return f"{entry.method.lower()}_{slug}"


def make_endpoint(entry: Entry):
    """
    Build the async endpoint function for one registry entry.

    The function reads everything it needs from the `Request` object, but its
    *declared* signature (via `__signature__`) lists every `{param}` from the
    path as a `str` argument. That satisfies FastAPI's path-parameter
    validation and documents each parameter in the OpenAPI schema, while the
    real call site simply accepts them via `**kwargs`.
    """
    param_names = _PATH_PARAM_RE.findall(entry.path)

    async def endpoint(request: Request, **kwargs: str) -> object:
        # Substitute dynamic segments, e.g. {index} -> logs-2026.01.01.
        path = entry.path
        for key, value in request.path_params.items():
            path = path.replace(f"{{{key}}}", value)

        # Forward every query parameter (repeated ones keep their last value).
        params: dict[str, str] = dict(request.query_params.multi_items())

        # `_cat` endpoints return plain text by default; ask for JSON so the
        # response decodes cleanly and renders properly in Swagger.
        if path.startswith("/_cat") and "format" not in params:
            params["format"] = "json"

        # Forward the raw body (JSON, NDJSON for _bulk, anything else).
        body = await request.body()
        content_type = request.headers.get("content-type") if body else None

        return await es_request(
            entry.method,
            path,
            params=params,
            content=body or None,
            content_type=content_type,
        )

    endpoint.__name__ = _operation_name(entry)
    endpoint.__signature__ = inspect.Signature(
        [
            inspect.Parameter(
                "request", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=Request
            )
        ]
        + [
            inspect.Parameter(
                name, inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str
            )
            for name in param_names
        ]
    )
    return endpoint


def build_router(entries: list[Entry]) -> APIRouter:
    router = APIRouter()
    for entry in entries:
        router.add_api_route(
            entry.path,
            make_endpoint(entry),
            methods=[entry.method],
            summary=entry.summary,
            description=entry.description,
            tags=[entry.tag],
            name=_operation_name(entry),
        )
    return router

"""
Shared asynchronous HTTP client for talking to Elasticsearch.

Every router in Elastick goes through `es_request()` here, so authentication,
TLS verification, timeouts and error handling are defined in exactly one place.
"""

from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException, status

from app.config import settings

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    """Return (and lazily create) the shared httpx client for Elasticsearch."""
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            auth=(
                (settings.elasticsearch_username, settings.elasticsearch_password)
                if settings.elasticsearch_password
                else None
            ),
            verify=settings.verify_ssl,
            timeout=settings.request_timeout,
            headers={"User-Agent": f"elastick/{settings.service_version}"},
        )
    return _client


async def close_client() -> None:
    """Dispose of the shared client (called on application shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def es_request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json_body: Any = None,
    content: bytes | None = None,
    content_type: str | None = None,
) -> Any:
    """
    Perform a request against Elasticsearch and return the decoded JSON body.

    Args:
        json_body: A Python object to send as `application/json`.
        content: Raw bytes to send as-is (used for NDJSON endpoints like
            `/_bulk`, where the payload must not be re-encoded as JSON).
        content_type: Content-Type header to send alongside `content`.

    Raises:
        HTTPException(502): Elasticsearch could not be reached, returned an
            error status, or replied with a non-JSON body. The original error
            detail is included so the caller can see what went wrong.
    """
    url = f"{settings.elasticsearch_url.rstrip('/')}{path}"
    client = get_client()
    headers: dict[str, str] = {}
    if content and content_type:
        headers["Content-Type"] = content_type
    try:
        response = await client.request(
            method, url, params=params, json=json_body,
            content=content, headers=headers,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Elasticsearch timed out after {settings.request_timeout}s: {exc}",
        ) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not reach Elasticsearch at {url}: {exc}",
        ) from exc

    if response.status_code >= 400:
        detail = _extract_error(response)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Elasticsearch returned {response.status_code}: {detail}",
        )

    if not response.content:
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Elasticsearch returned non-JSON output: {response.text[:500]}",
        ) from exc


def _extract_error(response: httpx.Response) -> str:
    """Pull a human-readable error message out of an Elasticsearch response."""
    try:
        body = response.json()
    except ValueError:
        return response.text[:500]
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict):
            reason = error.get("reason")
            error_type = error.get("type")
            return f"{error_type}: {reason}" if error_type else str(reason or error)
        if error is not None:
            return str(error)
        return str(body)[:500]
    return response.text[:500]

"""Core types for the API registry.

Each `Entry` describes one Elasticsearch REST API: its HTTP method, its real
Elasticsearch path (with `{placeholders}` for dynamic segments), the Swagger
category it belongs to, and the documentation shown in Swagger UI.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    method: str
    path: str
    tag: str
    summary: str
    description: str


def E(method: str, path: str, tag: str, summary: str, description: str = "") -> Entry:
    """Compact constructor: uppercases the method and defaults the description."""
    return Entry(method.upper(), path, tag, summary, description)

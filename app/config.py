"""
Application configuration for Elastick.

All settings are read from environment variables (or a `.env` file if you
load one yourself). See `.env.example` for a template.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class Settings:
    """Runtime settings for the Elastick service."""

    # Base URL of the Elasticsearch cluster this service talks to,
    # e.g. "https://es-internal.example.com:9200". Multiple nodes can be
    # provided as a comma-separated list; requests fail over between them.
    elasticsearch_url: str = field(
        default_factory=lambda: os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
    )

    # Credentials used for every call to Elasticsearch. For a read-only
    # monitoring/admin service, a dedicated user with the "monitor" and
    # "manage" cluster privileges is recommended.
    elasticsearch_username: str = field(
        default_factory=lambda: os.getenv("ELASTICSEARCH_USERNAME", "elastic")
    )
    elasticsearch_password: str = field(
        default_factory=lambda: os.getenv("ELASTICSEARCH_PASSWORD", "")
    )

    # Set to false when Elasticsearch uses self-signed TLS certificates.
    verify_ssl: bool = field(
        default_factory=lambda: _env_bool("ELASTIC_VERIFY_SSL", True)
    )

    # Per-request timeout (seconds) when calling Elasticsearch.
    request_timeout: float = field(
        default_factory=lambda: _env_float("ELASTIC_TIMEOUT", 30.0)
    )

    # Optional API key that clients must send as "X-API-Key" to use this
    # service. Leave empty to disable authentication on Elastick itself
    # (fine for local development; protect it in production).
    api_key: str = field(default_factory=lambda: os.getenv("ELASTICK_API_KEY", ""))

    # Set to false to disable the bundled web UI entirely — for operators who
    # prefer a Swagger-only deployment. When disabled, /ui redirects to /docs.
    ui_enabled: bool = field(
        default_factory=lambda: _env_bool("ELASTICK_UI_ENABLED", True)
    )

    # Title/branding shown in the Swagger UI.
    service_title: str = "Elastick"
    service_version: str = "1.0.0"


settings = Settings()

"""Optional API-key protection for Elastick itself.

If `ELASTICK_API_KEY` is configured, every request must carry the header
`X-API-Key: <key>`. If it is not configured, the service is open (fine for
local development, not recommended for production).
"""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from app.config import settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> None:
    """FastAPI dependency that enforces the configured API key, if any."""
    if not settings.api_key:
        return
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid X-API-Key header.",
        )

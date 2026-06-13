"""JWT verification middleware — attaches user payload to request state."""
from __future__ import annotations

import structlog
from fastapi import Request, Response
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.config import get_settings

logger = structlog.get_logger(__name__)

_OPEN_PATHS = {
    "/",
    "/api/v1/health",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that decodes the Bearer token and stores user on request.state.

    Routes that require authentication should still use the `get_current_user`
    dependency; this middleware is a convenience layer that makes the decoded
    payload available early (e.g. for logging correlation).
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        settings = get_settings()
        request.state.user = None

        if request.url.path in _OPEN_PATHS or request.method == "OPTIONS":
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            try:
                payload = jwt.decode(
                    token,
                    settings.SUPABASE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"verify_aud": False},
                )
                request.state.user = payload
                logger.bind(user_id=payload.get("sub"))
            except JWTError as exc:
                logger.debug("jwt_middleware_decode_failed", error=str(exc))

        return await call_next(request)

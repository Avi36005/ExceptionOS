"""FastAPI dependency injection: auth, database clients, settings."""
from __future__ import annotations

from typing import Annotated
from uuid import UUID

import structlog
import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from supabase import Client, create_client

from app.config import Settings, get_settings

logger = structlog.get_logger(__name__)

# Cached Supabase JWKS (ES256 signing keys). Modern Supabase projects sign
# access tokens with asymmetric ES256 keys served at the JWKS URL below.
_JWKS_CACHE: dict[str, dict] = {}


async def _get_jwks_key(supabase_url: str, kid: str) -> dict | None:
    """Return the JWK matching ``kid`` from the project's JWKS (cached)."""
    def _find() -> dict | None:
        for k in _JWKS_CACHE.get("keys", []):
            if k.get("kid") == kid:
                return k
        return None

    key = _find()
    if key:
        return key
    url = f"{supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _JWKS_CACHE.clear()
            _JWKS_CACHE.update(resp.json())
    except Exception as exc:  # noqa: BLE001
        logger.warning("jwks_fetch_failed", error=str(exc))
        return None
    return _find()


# ---------------------------------------------------------------------------
# Supabase client
# ---------------------------------------------------------------------------

def get_supabase(settings: Annotated[Settings, Depends(get_settings)]) -> Client:
    """Return a Supabase client using the service-role key (bypasses RLS)."""
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# ---------------------------------------------------------------------------
# Current user from JWT
# ---------------------------------------------------------------------------

async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    """Verify the Supabase JWT and return the decoded payload."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not authorization:
        raise credentials_exception

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise credentials_exception

    # Determine signing algorithm from the token header.
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        logger.warning("jwt_header_failed", error=str(exc))
        raise credentials_exception from exc
    alg = header.get("alg", "HS256")

    try:
        if alg == "HS256":
            # Legacy: shared-secret signed Supabase JWTs.
            if not settings.SUPABASE_JWT_SECRET:
                raise JWTError("SUPABASE_JWT_SECRET not configured")
            payload = jwt.decode(
                token, settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"], options={"verify_aud": False},
            )
        else:
            # Modern: asymmetric (ES256) keys verified via the project JWKS.
            key = await _get_jwks_key(settings.SUPABASE_URL, header.get("kid", ""))
            if not key:
                raise JWTError("no matching JWKS key")
            payload = jwt.decode(
                token, key,
                algorithms=[alg], options={"verify_aud": False},
            )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return payload
    except JWTError as exc:
        logger.warning("jwt_decode_failed", error=str(exc), alg=alg)
        raise credentials_exception from exc


async def get_optional_user(
    authorization: Annotated[str | None, Header()] = None,
    settings: Settings = Depends(get_settings),
) -> dict | None:
    """Return user payload if a valid token is provided, else None."""
    if not authorization:
        return None
    try:
        return await get_current_user(authorization=authorization, settings=settings)
    except HTTPException:
        return None


# ---------------------------------------------------------------------------
# Organisation membership check
# ---------------------------------------------------------------------------

async def require_org_member(
    organization_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase)],
) -> dict:
    """Raise 403 if the current user is not a member of the organisation."""
    user_id = current_user["sub"]
    resp = (
        supabase.table("organization_memberships")
        .select("role,status")
        .eq("organization_id", str(organization_id))
        .eq("user_id", user_id)
        .eq("status", "active")
        .maybe_single()
        .execute()
    )
    if not resp.data:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of this organisation",
        )
    return {**current_user, "org_role": resp.data["role"]}


async def require_org_admin(
    organization_id: UUID,
    current_user: Annotated[dict, Depends(get_current_user)],
    supabase: Annotated[Client, Depends(get_supabase)],
) -> dict:
    """Raise 403 if the current user is not an admin/owner of the organisation."""
    member = await require_org_member(organization_id, current_user, supabase)
    if member["org_role"] not in ("owner", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return member

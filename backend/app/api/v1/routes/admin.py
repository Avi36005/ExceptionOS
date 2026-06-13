"""Admin routes — requires admin/owner role."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    # Check if user has admin app_metadata role (set in Supabase)
    app_meta = current_user.get("app_metadata", {})
    role = app_meta.get("role", "")
    if role not in ("admin", "superadmin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user


@router.get("/organizations")
async def admin_list_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(_require_admin),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    offset = (page - 1) * page_size
    resp = (
        supabase.table("organizations")
        .select("*", count="exact")
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return DataResponse(
        data=resp.data or [],
        meta={"total": resp.count or 0, "page": page, "page_size": page_size},
    )


@router.get("/users")
async def admin_list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(_require_admin),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    offset = (page - 1) * page_size
    resp = (
        supabase.table("profiles")
        .select("*", count="exact")
        .range(offset, offset + page_size - 1)
        .execute()
    )
    return DataResponse(
        data=resp.data or [],
        meta={"total": resp.count or 0, "page": page, "page_size": page_size},
    )


@router.get("/stats")
async def admin_stats(
    current_user: dict = Depends(_require_admin),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    orgs = supabase.table("organizations").select("id", count="exact").execute()
    cases = supabase.table("exception_cases").select("id", count="exact").execute()
    decisions = supabase.table("human_decisions").select("id", count="exact").execute()
    runs = supabase.table("agent_runs").select("id", count="exact").execute()

    return DataResponse(data={
        "total_organizations": orgs.count or 0,
        "total_cases": cases.count or 0,
        "total_decisions": decisions.count or 0,
        "total_agent_runs": runs.count or 0,
    })

"""User management routes."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse, MessageResponse, ProfileRead, UserInvite

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
async def get_current_profile(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """Return the current user's profile."""
    user_id = current_user["sub"]
    resp = (
        supabase.table("profiles")
        .select("*")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not resp.data:
        return DataResponse(data={"id": user_id, "display_name": None})
    return DataResponse(data=resp.data)


@router.get("/me/organizations")
async def get_my_organizations(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """List organisations the current user belongs to."""
    user_id = current_user["sub"]
    resp = (
        supabase.table("organization_memberships")
        .select("*, organizations(*)")
        .eq("user_id", user_id)
        .eq("status", "active")
        .execute()
    )
    return DataResponse(data=resp.data or [])


@router.get("/{organization_id}/members")
async def list_members(
    organization_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    """List members of an organisation."""
    resp = (
        supabase.table("organization_memberships")
        .select("*, profiles(*)")
        .eq("organization_id", str(organization_id))
        .eq("status", "active")
        .execute()
    )
    return DataResponse(data=resp.data or [])


@router.post("/{organization_id}/members/invite", status_code=status.HTTP_201_CREATED)
async def invite_member(
    organization_id: UUID,
    payload: UserInvite,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> MessageResponse:
    """Invite a user to an organisation (creates a pending membership)."""
    from uuid import uuid4
    from datetime import datetime

    # Look up user by email in auth.users via Supabase admin API
    # For now, we insert a pending membership with the email in metadata
    membership_id = str(uuid4())
    supabase.table("organization_memberships").insert({
        "id": membership_id,
        "organization_id": str(organization_id),
        "user_id": membership_id,  # placeholder — resolved on accept
        "role": payload.role.value,
        "status": "pending",
        "invited_by": current_user["sub"],
    }).execute()

    return MessageResponse(message="Invitation sent", data={"email": payload.email})


@router.delete("/{organization_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def remove_member(
    organization_id: UUID,
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> None:
    supabase.table("organization_memberships").update({"status": "removed"}).eq(
        "organization_id", str(organization_id)
    ).eq("user_id", str(user_id)).execute()

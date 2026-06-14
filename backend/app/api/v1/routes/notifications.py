"""Notification routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from supabase import Client

from app.dependencies import get_current_user, get_supabase
from app.schemas import DataResponse, MessageResponse

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(
    organization_id: UUID | None = Query(None),
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> DataResponse:
    user_id = current_user["sub"]
    query = supabase.table("notifications").select("*").eq("user_id", user_id)
    if organization_id:
        query = query.eq("organization_id", str(organization_id))
    resp = query.order("created_at", desc=True).limit(100).execute()
    return DataResponse(data=resp.data or [])


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: UUID,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase),
) -> MessageResponse:
    user_id = current_user["sub"]
    supabase.table("notifications").update({"read": True}).eq("id", str(notification_id)).eq(
        "user_id", user_id
    ).execute()
    return MessageResponse(message="Notification marked as read", data={"id": str(notification_id)})

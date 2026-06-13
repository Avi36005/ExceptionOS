"""Per-organisation Hindsight bank ID management."""
from __future__ import annotations

from uuid import UUID

import structlog
from supabase import Client

from app.memory.hindsight_client import HindsightClient

logger = structlog.get_logger(__name__)


class BankManager:
    """Manages Hindsight memory banks, one per organisation."""

    def __init__(self, supabase: Client, hindsight: HindsightClient):
        self.supabase = supabase
        self.hindsight = hindsight

    async def get_or_create_bank(self, organization_id: UUID, org_name: str) -> str:
        """Return the Hindsight bank_id for an org, creating it if needed."""
        # 1. Try cached bank_id in DB
        resp = (
            self.supabase.table("organizations")
            .select("hindsight_bank_id")
            .eq("id", str(organization_id))
            .single()
            .execute()
        )
        bank_id: str | None = resp.data.get("hindsight_bank_id") if resp.data else None

        if bank_id:
            return bank_id

        # 2. Create a new bank in Hindsight
        try:
            bank = await self.hindsight.create_bank(
                name=f"exceptionos-{org_name}-{organization_id}",
                description=f"Memory bank for organisation '{org_name}' on ExceptionOS",
            )
            bank_id = bank.get("id") or bank.get("bank_id")
            if not bank_id:
                raise ValueError(f"Hindsight did not return a bank id: {bank}")
        except Exception as exc:
            logger.error(
                "bank_creation_failed",
                organization_id=str(organization_id),
                error=str(exc),
            )
            raise

        # 3. Persist bank_id
        self.supabase.table("organizations").update(
            {"hindsight_bank_id": bank_id}
        ).eq("id", str(organization_id)).execute()

        logger.info(
            "hindsight_bank_created",
            organization_id=str(organization_id),
            bank_id=bank_id,
        )
        return bank_id

    async def get_bank_id(self, organization_id: UUID) -> str | None:
        """Return the Hindsight bank_id or None if not set."""
        resp = (
            self.supabase.table("organizations")
            .select("hindsight_bank_id")
            .eq("id", str(organization_id))
            .maybe_single()
            .execute()
        )
        return resp.data.get("hindsight_bank_id") if resp.data else None

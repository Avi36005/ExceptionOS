"""Main orchestrator agent.

Coordinates the full multi-agent debate pipeline and emits SSE events.
"""
from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime
from typing import Any, AsyncGenerator
from uuid import UUID, uuid4

import structlog
from supabase import Client

from app.agents.intake_agent import IntakeAgent
from app.agents.policy_agent import PolicyAgent
from app.agents.precedent_agent import PrecedentAgent
from app.agents.finance_agent import FinanceAgent
from app.agents.customer_impact_agent import CustomerImpactAgent
from app.agents.risk_agent import RiskAgent
from app.agents.counter_precedent_agent import CounterPrecedentAgent
from app.agents.consistency_agent import ConsistencyAgent
from app.agents.critic_agent import CriticAgent
from app.agents.final_decision_agent import FinalDecisionAgent
from app.llm.provider_router import ProviderRouter
from app.memory.hindsight_client import HindsightClient
from app.memory.bank_manager import BankManager
from app.usage import AggregatedUsage

logger = structlog.get_logger(__name__)


def _sse(event: str, data: dict[str, Any]) -> str:
    """Format a Server-Sent Event string."""
    payload = json.dumps({"event": event, "data": data, "ts": datetime.utcnow().isoformat()})
    return f"data: {payload}\n\n"


class Orchestrator:
    """Runs the full multi-agent debate pipeline for an exception case."""

    def __init__(self, router: ProviderRouter, hindsight: HindsightClient, supabase: Client):
        self.router = router
        self.hindsight = hindsight
        self.supabase = supabase
        self.bank_manager = BankManager(supabase, hindsight)

        # Instantiate agents
        self.intake_agent = IntakeAgent(router)
        self.policy_agent = PolicyAgent(router)
        self.precedent_agent = PrecedentAgent(router, hindsight)
        self.finance_agent = FinanceAgent(router)
        self.customer_agent = CustomerImpactAgent(router)
        self.risk_agent = RiskAgent(router)
        self.counter_agent = CounterPrecedentAgent(router)
        self.consistency_agent = ConsistencyAgent(router)
        self.critic_agent = CriticAgent(router)
        self.final_agent = FinalDecisionAgent(router)

    async def run_stream(
        self,
        case_id: UUID,
        organization_id: UUID,
        demo_mode: bool = False,
    ) -> AsyncGenerator[str, None]:
        """Stream SSE events for the debate pipeline."""
        start_time = time.monotonic()
        trace_id = str(uuid4())
        usage = AggregatedUsage()

        yield _sse("start", {"trace_id": trace_id, "case_id": str(case_id)})

        try:
            # ── Load case ──────────────────────────────────────────────────
            case_row = self._get_case(case_id, organization_id)
            if not case_row:
                yield _sse("error", {"message": "Case not found"})
                return

            org_row = self._get_org(organization_id)
            bank_id = org_row.get("hindsight_bank_id", "") if org_row else ""

            # Update status
            self._update_case_status(case_id, "analyzing")
            yield _sse("status", {"status": "analyzing", "case_id": str(case_id)})

            case_facts: dict[str, Any] = {
                "title": case_row.get("title", ""),
                "description": case_row.get("description", ""),
                "entity_name": case_row.get("entity_name"),
                "requested_amount": case_row.get("requested_amount"),
                "currency": case_row.get("currency", "USD"),
                "urgency": case_row.get("urgency", "medium"),
                "root_cause": case_row.get("root_cause"),
            }

            # ── Stage 1: Intake ────────────────────────────────────────────
            yield _sse("agent_start", {"agent": "intake_agent"})
            intake_result = await self.intake_agent.run(
                case_id=case_id,
                title=case_facts["title"],
                description=case_facts.get("description", ""),
                additional_context=case_facts,
                demo_mode=demo_mode,
            )
            if intake_result.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**intake_result["usage"]))
            yield _sse("agent_done", {"agent": "intake_agent", "output": intake_result["output"]})

            # ── Stage 2: Policy ────────────────────────────────────────────
            yield _sse("agent_start", {"agent": "policy_agent"})
            policy_content, policy_name = self._get_latest_policy(organization_id)
            policy_result = await self.policy_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                policy_content=policy_content,
                policy_name=policy_name,
                demo_mode=demo_mode,
            )
            if policy_result.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**policy_result["usage"]))
            yield _sse("agent_done", {"agent": "policy_agent", "output": policy_result["output"]})

            # ── Stage 3: Precedents ────────────────────────────────────────
            yield _sse("agent_start", {"agent": "precedent_agent"})
            precedent_result = await self.precedent_agent.run(
                case_id=case_id,
                bank_id=bank_id,
                case_facts=case_facts,
                case_description=f"{case_facts['title']} {case_facts.get('description', '')}",
                demo_mode=demo_mode,
            )
            if precedent_result.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**precedent_result["usage"]))
            yield _sse("agent_done", {"agent": "precedent_agent", "output": precedent_result["output"]})

            # ── Stage 4: Parallel debate agents ───────────────────────────
            yield _sse("debate_start", {"agents": ["finance", "customer_impact", "risk", "counter_precedent"]})

            # Determine preliminary direction from policy + precedents
            preliminary_dir = self._derive_preliminary_direction(
                policy_result["output"], precedent_result["output"]
            )

            finance_task = asyncio.create_task(
                self.finance_agent.run(case_id, case_facts, intake_result["output"], demo_mode=demo_mode)
            )
            customer_task = asyncio.create_task(
                self.customer_agent.run(case_id, case_facts, intake_result["output"], demo_mode=demo_mode)
            )
            risk_task = asyncio.create_task(
                self.risk_agent.run(case_id, case_facts, policy_result["output"], intake_result["output"], demo_mode=demo_mode)
            )
            counter_task = asyncio.create_task(
                self.counter_agent.run(
                    case_id, case_facts, preliminary_dir,
                    precedent_result["output"], {},
                    demo_mode=demo_mode,
                )
            )

            finance_r, customer_r, risk_r, counter_r = await asyncio.gather(
                finance_task, customer_task, risk_task, counter_task,
                return_exceptions=True,
            )

            # Handle exceptions from gather
            for name, r in [
                ("finance_agent", finance_r),
                ("customer_impact_agent", customer_r),
                ("risk_agent", risk_r),
                ("counter_precedent_agent", counter_r),
            ]:
                if isinstance(r, Exception):
                    logger.error(f"{name}_failed", error=str(r))
                    yield _sse("agent_error", {"agent": name, "error": str(r)})
                else:
                    if r.get("usage"):
                        from app.usage import TokenUsage
                        usage.add(TokenUsage(**r["usage"]))
                    yield _sse("agent_done", {"agent": name, "output": r.get("output", {})})

            # Safe dereference
            finance_out = finance_r.get("output", {}) if not isinstance(finance_r, Exception) else {}
            customer_out = customer_r.get("output", {}) if not isinstance(customer_r, Exception) else {}
            risk_out = risk_r.get("output", {}) if not isinstance(risk_r, Exception) else {}
            counter_out = counter_r.get("output", {}) if not isinstance(counter_r, Exception) else {}

            # ── Stage 5: Consistency ───────────────────────────────────────
            yield _sse("agent_start", {"agent": "consistency_agent"})
            consistency_r = await self.consistency_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                precedent_output=precedent_result["output"],
                policy_output=policy_result["output"],
                current_direction=preliminary_dir,
                demo_mode=demo_mode,
            )
            if consistency_r.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**consistency_r["usage"]))
            yield _sse("agent_done", {"agent": "consistency_agent", "output": consistency_r["output"]})

            # ── Stage 6: Critic ────────────────────────────────────────────
            yield _sse("agent_start", {"agent": "critic_agent"})
            all_outputs = {
                "intake": intake_result["output"],
                "policy": policy_result["output"],
                "precedent": precedent_result["output"],
                "finance": finance_out,
                "customer_impact": customer_out,
                "risk": risk_out,
                "counter_precedent": counter_out,
                "consistency": consistency_r["output"],
            }
            critic_r = await self.critic_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                all_agent_outputs=all_outputs,
                preliminary_recommendation=preliminary_dir,
                demo_mode=demo_mode,
            )
            if critic_r.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**critic_r["usage"]))
            yield _sse("agent_done", {"agent": "critic_agent", "output": critic_r["output"]})

            # ── Stage 7: Final decision ────────────────────────────────────
            yield _sse("agent_start", {"agent": "final_decision_agent"})
            final_r = await self.final_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                all_outputs=all_outputs,
                critic_output=critic_r["output"],
                demo_mode=demo_mode,
            )
            if final_r.get("usage"):
                from app.usage import TokenUsage
                usage.add(TokenUsage(**final_r["usage"]))
            final_out = final_r["output"]
            yield _sse("agent_done", {"agent": "final_decision_agent", "output": final_out})

            # ── Stage 8: Persist recommendation ───────────────────────────
            rec_id = self._save_recommendation(case_id, final_out, precedent_result)
            self._update_case_status(case_id, "pending_decision", rec_id)

            # ── Stage 9: Save agent run ────────────────────────────────────
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._save_agent_run(
                case_id=case_id,
                trace_id=trace_id,
                final_provider=final_r.get("provider", ""),
                fallback_path=final_r.get("fallback_path", []),
                latency_ms=latency_ms,
                token_usage=usage.to_dict(),
            )

            yield _sse("complete", {
                "recommendation_id": str(rec_id),
                "recommendation_type": final_out.get("recommendation_type"),
                "confidence": final_out.get("confidence"),
                "latency_ms": latency_ms,
                "token_usage": usage.totals,
            })

        except Exception as exc:
            logger.exception("orchestrator_failed", case_id=str(case_id), error=str(exc))
            self._update_case_status(case_id, "submitted")
            yield _sse("error", {"message": str(exc), "case_id": str(case_id)})

    # ── Helpers ────────────────────────────────────────────────────────────

    def _get_case(self, case_id: UUID, organization_id: UUID) -> dict | None:
        resp = (
            self.supabase.table("exception_cases")
            .select("*")
            .eq("id", str(case_id))
            .eq("organization_id", str(organization_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def _get_org(self, organization_id: UUID) -> dict | None:
        resp = (
            self.supabase.table("organizations")
            .select("*")
            .eq("id", str(organization_id))
            .maybe_single()
            .execute()
        )
        return resp.data

    def _get_latest_policy(self, organization_id: UUID) -> tuple[str, str]:
        try:
            resp = (
                self.supabase.table("policies")
                .select("id, name, policy_versions(content, status)")
                .eq("organization_id", str(organization_id))
                .eq("status", "active")
                .limit(1)
                .execute()
            )
            if resp.data:
                policy = resp.data[0]
                versions = policy.get("policy_versions", [])
                active_versions = [v for v in versions if v.get("status") == "active"]
                content = active_versions[0]["content"] if active_versions else (versions[0]["content"] if versions else "")
                return content, policy.get("name", "Organisational Policy")
        except Exception:
            pass
        return (
            "Standard organisational policy: all exceptions require documented justification, "
            "financial impact assessment, and approval from appropriate authority level.",
            "Default Policy",
        )

    def _derive_preliminary_direction(self, policy_out: dict, precedent_out: dict) -> str:
        compliance = policy_out.get("compliance_status", "unclear")
        pattern = precedent_out.get("consistency_pattern", "mixed")
        if compliance == "compliant":
            return "approve"
        if compliance == "non_compliant" and pattern == "consistent":
            return "deny"
        return "partially_approve"

    def _save_recommendation(
        self,
        case_id: UUID,
        final_out: dict[str, Any],
        precedent_result: dict[str, Any],
    ) -> UUID:
        rec_id = uuid4()
        self.supabase.table("recommendations").insert({
            "id": str(rec_id),
            "case_id": str(case_id),
            "version": 1,
            "recommendation_type": final_out.get("recommendation_type", "needs_more_info"),
            "recommended_amount": final_out.get("recommended_amount"),
            "conditions_json": json.dumps(final_out.get("conditions", [])),
            "confidence": final_out.get("confidence", 0.5),
            "reasoning": final_out.get("reasoning", ""),
            "risk_json": json.dumps(final_out.get("risk", {})),
            "provider_summary_json": json.dumps(final_out.get("provider_summary", {})),
            "hindsight_evidence_json": json.dumps(precedent_result.get("raw_memories", [])),
        }).execute()
        return rec_id

    def _update_case_status(
        self,
        case_id: UUID,
        status: str,
        recommendation_id: UUID | None = None,
    ) -> None:
        update: dict[str, Any] = {"status": status, "updated_at": datetime.utcnow().isoformat()}
        if recommendation_id:
            update["current_recommendation_id"] = str(recommendation_id)
        self.supabase.table("exception_cases").update(update).eq("id", str(case_id)).execute()

    def _save_agent_run(
        self,
        case_id: UUID,
        trace_id: str,
        final_provider: str,
        fallback_path: list[str],
        latency_ms: int,
        token_usage: dict[str, Any],
    ) -> None:
        self.supabase.table("agent_runs").insert({
            "id": str(uuid4()),
            "case_id": str(case_id),
            "run_type": "full_debate",
            "status": "completed",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
            "final_provider": final_provider,
            "fallback_path_json": json.dumps(fallback_path),
            "latency_ms": latency_ms,
            "token_usage_json": json.dumps(token_usage),
        }).execute()

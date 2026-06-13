"""Main orchestrator agent.

Coordinates the full multi-agent debate pipeline and emits SSE events,
including the Hindsight memory-operation taxonomy (RETAIN/RECALL/REFLECT
started/completed, MEMORY_USED, PROVIDER_FALLBACK, OPERATION_FAILED).
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
from app.memory.document_ids import case_decision_document_id
from app.memory.hindsight_client import HindsightClient
from app.memory.bank_manager import BankManager
from app.memory.operation_logger import OperationLogContext
from app.memory.recall_service import RecallService
from app.memory.retain_service import RetainService
from app.usage import AggregatedUsage, TokenUsage

logger = structlog.get_logger(__name__)

# ── SSE event taxonomy ─────────────────────────────────────────────────────
EVT_RETAIN_STARTED = "RETAIN_STARTED"
EVT_RETAIN_COMPLETED = "RETAIN_COMPLETED"
EVT_RECALL_STARTED = "RECALL_STARTED"
EVT_RECALL_COMPLETED = "RECALL_COMPLETED"
EVT_REFLECT_STARTED = "REFLECT_STARTED"
EVT_REFLECT_COMPLETED = "REFLECT_COMPLETED"
EVT_MEMORY_USED = "MEMORY_USED"
EVT_PROVIDER_FALLBACK = "PROVIDER_FALLBACK"
EVT_OPERATION_FAILED = "OPERATION_FAILED"


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
        self.recall_service = RecallService(hindsight)
        self.retain_service = RetainService(hindsight)

        # Instantiate agents
        self.intake_agent = IntakeAgent(router)
        self.policy_agent = PolicyAgent(router)
        self.precedent_agent = PrecedentAgent(router)
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
        agent_run_id = uuid4()
        usage = AggregatedUsage()

        yield _sse("start", {"trace_id": trace_id, "case_id": str(case_id), "agent_run_id": str(agent_run_id)})

        self._create_agent_run(agent_run_id, case_id, trace_id)
        log_ctx = OperationLogContext(
            supabase=self.supabase,
            organization_id=organization_id,
            case_id=case_id,
            agent_run_id=agent_run_id,
        )

        try:
            # ── Load case ──────────────────────────────────────────────────
            case_row = self._get_case(case_id, organization_id)
            if not case_row:
                self._finalize_agent_run(agent_run_id, "failed", usage, 0, [], error="Case not found")
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
            self._add_usage(usage, intake_result)
            yield _sse("agent_done", {"agent": "intake_agent", "output": intake_result["output"]})
            fb = self._fallback_event("intake_agent", intake_result)
            if fb:
                yield fb

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
            self._add_usage(usage, policy_result)
            yield _sse("agent_done", {"agent": "policy_agent", "output": policy_result["output"]})
            fb = self._fallback_event("policy_agent", policy_result)
            if fb:
                yield fb

            # ── Stage 3: Memory recall + Precedents ────────────────────────
            case_description = f"{case_facts['title']} {case_facts.get('description', '')}"

            recall_events, recall_buckets = await self._recall_with_events(
                bank_id=bank_id,
                case_description=case_description,
                entity_name=case_facts.get("entity_name"),
                policy_name=policy_name,
                top_k=10,
                log_ctx=log_ctx,
            )
            for evt in recall_events:
                yield evt

            yield _sse("agent_start", {"agent": "precedent_agent"})
            precedent_result = await self.precedent_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                memories=recall_buckets.get("merged", []),
                demo_mode=demo_mode,
            )
            self._add_usage(usage, precedent_result)
            yield _sse("agent_done", {"agent": "precedent_agent", "output": precedent_result["output"]})
            fb = self._fallback_event("precedent_agent", precedent_result)
            if fb:
                yield fb

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
                    self._add_usage(usage, r)
                    yield _sse("agent_done", {"agent": name, "output": r.get("output", {})})
                    fb = self._fallback_event(name, r)
                    if fb:
                        yield fb

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
            self._add_usage(usage, consistency_r)
            yield _sse("agent_done", {"agent": "consistency_agent", "output": consistency_r["output"]})
            fb = self._fallback_event("consistency_agent", consistency_r)
            if fb:
                yield fb

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
            self._add_usage(usage, critic_r)
            yield _sse("agent_done", {"agent": "critic_agent", "output": critic_r["output"]})
            fb = self._fallback_event("critic_agent", critic_r)
            if fb:
                yield fb

            # ── Stage 7: Final decision ────────────────────────────────────
            yield _sse("agent_start", {"agent": "final_decision_agent"})
            final_r = await self.final_agent.run(
                case_id=case_id,
                case_facts=case_facts,
                all_outputs=all_outputs,
                critic_output=critic_r["output"],
                demo_mode=demo_mode,
            )
            self._add_usage(usage, final_r)
            final_out = final_r["output"]
            yield _sse("agent_done", {"agent": "final_decision_agent", "output": final_out})
            fb = self._fallback_event("final_decision_agent", final_r)
            if fb:
                yield fb

            # ── Stage 8: Persist recommendation ───────────────────────────
            rec_id = self._save_recommendation(case_id, final_out, recall_buckets.get("merged", []))
            self._update_case_status(case_id, "pending_decision", rec_id)

            # ── Stage 9: Retain the decision to Hindsight ───────────────────
            retain_events = await self._retain_decision_with_events(
                bank_id=bank_id,
                organization_id=organization_id,
                case_id=case_id,
                rec_id=rec_id,
                case_facts=case_facts,
                final_out=final_out,
                log_ctx=log_ctx,
            )
            for evt in retain_events:
                yield evt

            # ── Stage 10: Finalize agent run ────────────────────────────────
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._finalize_agent_run(
                agent_run_id=agent_run_id,
                status="completed",
                usage=usage,
                latency_ms=latency_ms,
                fallback_path=final_r.get("fallback_path", []),
                final_provider=final_r.get("provider", ""),
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
            latency_ms = int((time.monotonic() - start_time) * 1000)
            self._finalize_agent_run(agent_run_id, "failed", usage, latency_ms, [], error=str(exc))
            self._update_case_status(case_id, "submitted")
            yield _sse("error", {"message": str(exc), "case_id": str(case_id)})

    # ── Memory operation helpers (Retain/Recall SSE taxonomy) ───────────────

    async def _recall_with_events(
        self,
        bank_id: str,
        case_description: str,
        entity_name: str | None,
        policy_name: str,
        top_k: int,
        log_ctx: OperationLogContext,
    ) -> tuple[list[str], dict[str, Any]]:
        """Recall precedents/outcomes/policy-notes for a case, returning SSE
        events for the RECALL/MEMORY_USED/OPERATION_FAILED taxonomy plus the
        recalled+deduped buckets (see ``RecallService.recall_structured``).
        """
        events = [_sse(EVT_RECALL_STARTED, {"bank_id": bank_id, "query": case_description[:200]})]

        if not bank_id:
            events.append(_sse(EVT_OPERATION_FAILED, {
                "operation": "recall",
                "error": "No Hindsight bank configured for this organisation",
            }))
            return events, {"precedents": [], "outcomes": [], "outcome_lessons": [], "policy_notes": [], "merged": []}

        try:
            buckets = await self.recall_service.recall_structured(
                bank_id=bank_id,
                case_description=case_description,
                entity_name=entity_name,
                policy_name=policy_name,
                top_k=top_k,
                log_ctx=log_ctx,
            )
        except Exception as exc:
            events.append(_sse(EVT_OPERATION_FAILED, {"operation": "recall", "error": str(exc)}))
            return events, {"precedents": [], "outcomes": [], "outcome_lessons": [], "policy_notes": [], "merged": []}

        for err in buckets.get("errors", []):
            events.append(_sse(EVT_OPERATION_FAILED, {"operation": "recall", **err}))

        merged = buckets.get("merged", [])
        events.append(_sse(EVT_RECALL_COMPLETED, {
            "counts": {k: len(v) for k, v in buckets.items() if k != "errors"},
        }))

        if merged:
            events.append(_sse(EVT_MEMORY_USED, {
                "memories": [
                    {
                        "memory_id": m.get("id"),
                        "score": m.get("score"),
                        "type": (m.get("metadata") or {}).get("type"),
                        "document_id": (m.get("metadata") or {}).get("document_id"),
                        "snippet": (m.get("content") or "")[:160],
                    }
                    for m in merged[:5]
                ],
            }))

        return events, buckets

    async def _retain_decision_with_events(
        self,
        bank_id: str,
        organization_id: UUID,
        case_id: UUID,
        rec_id: UUID,
        case_facts: dict[str, Any],
        final_out: dict[str, Any],
        log_ctx: OperationLogContext,
    ) -> list[str]:
        """Retain this case's decision/recommendation as a Hindsight memory
        under a stable ``case:{org}:{case}:decision:{rec_id}`` document id,
        emitting RETAIN_STARTED/COMPLETED/OPERATION_FAILED events.
        """
        if not bank_id:
            return []

        document_id = case_decision_document_id(organization_id, case_id, rec_id)
        events = [_sse(EVT_RETAIN_STARTED, {"document_id": document_id, "bank_id": bank_id})]

        try:
            await self.retain_service.retain_case_decision(
                bank_id=bank_id,
                case_id=case_id,
                case_title=case_facts.get("title", ""),
                decision_type=final_out.get("recommendation_type", "needs_more_info"),
                reasoning=final_out.get("reasoning", ""),
                metadata={
                    "entity_name": case_facts.get("entity_name"),
                    "requested_amount": case_facts.get("requested_amount"),
                    "recommended_amount": final_out.get("recommended_amount"),
                    "confidence": final_out.get("confidence"),
                    "recommendation_id": str(rec_id),
                },
                document_id=document_id,
                log_ctx=log_ctx,
            )
            events.append(_sse(EVT_RETAIN_COMPLETED, {"document_id": document_id}))
        except Exception as exc:
            events.append(_sse(EVT_OPERATION_FAILED, {"operation": "retain", "document_id": document_id, "error": str(exc)}))

        return events

    def _fallback_event(self, agent_name: str, result: dict[str, Any]) -> str | None:
        """Emit PROVIDER_FALLBACK if the agent's LLM call fell back from its
        primary provider (``fallback_path`` non-empty == at least one
        provider failed before the one that succeeded).
        """
        fallback_path = result.get("fallback_path") or []
        if not fallback_path:
            return None
        return _sse(EVT_PROVIDER_FALLBACK, {
            "agent": agent_name,
            "failed_providers": fallback_path,
            "final_provider": result.get("provider"),
        })

    @staticmethod
    def _add_usage(usage: AggregatedUsage, result: dict[str, Any]) -> None:
        if result.get("usage"):
            usage.add(TokenUsage(**result["usage"]))

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
        merged_memories: list[dict[str, Any]],
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
            "hindsight_evidence_json": json.dumps(merged_memories),
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

    def _create_agent_run(self, agent_run_id: UUID, case_id: UUID, trace_id: str) -> None:
        self.supabase.table("agent_runs").insert({
            "id": str(agent_run_id),
            "case_id": str(case_id),
            "run_type": "full_debate",
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "trace_id": trace_id,
        }).execute()

    def _finalize_agent_run(
        self,
        agent_run_id: UUID,
        status: str,
        usage: AggregatedUsage,
        latency_ms: int,
        fallback_path: list[str],
        final_provider: str = "",
        error: str | None = None,
    ) -> None:
        update: dict[str, Any] = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat(),
            "final_provider": final_provider,
            "fallback_path_json": json.dumps(fallback_path),
            "latency_ms": latency_ms,
            "token_usage_json": json.dumps(usage.to_dict()),
        }
        if error:
            update["error_json"] = json.dumps({"message": error})
        self.supabase.table("agent_runs").update(update).eq("id", str(agent_run_id)).execute()

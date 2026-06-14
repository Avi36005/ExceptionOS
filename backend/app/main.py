"""ExceptionOS FastAPI application entry point."""
from __future__ import annotations

import structlog
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.middleware.auth import JWTAuthMiddleware

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer() if True else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info(
        "exceptionos_startup",
        version="1.0.0",
        environment=settings.APP_ENV,
        groq_configured=bool(settings.GROQ_API_KEY),
        hindsight_configured=bool(settings.HINDSIGHT_API_KEY),
        openclaw_enabled=settings.ENABLE_OPENCLAW,
    )
    yield
    logger.info("exceptionos_shutdown")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ExceptionOS API",
        description="Multi-tenant Organisational Decision Intelligence Platform",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── Middleware ──────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JWTAuthMiddleware)

    # ── Global exception handler ────────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", path=request.url.path, error=str(exc))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Internal server error", "detail": str(exc)},
        )

    # ── Routers ─────────────────────────────────────────────────────────────
    from app.api.v1.routes.health import router as health_router
    from app.api.v1.routes.organizations import router as org_router
    from app.api.v1.routes.users import router as users_router
    from app.api.v1.routes.exceptions import router as exceptions_router
    from app.api.v1.routes.policies import router as policies_router
    from app.api.v1.routes.precedents import router as precedents_router
    from app.api.v1.routes.decisions import router as decisions_router
    from app.api.v1.routes.outcomes import router as outcomes_router
    from app.api.v1.routes.recommendations import router as recommendations_router
    from app.api.v1.routes.debate import router as debate_router
    from app.api.v1.routes.memory import router as memory_router
    from app.api.v1.routes.training import router as training_router
    from app.api.v1.routes.voice import router as voice_router
    from app.api.v1.routes.insights import router as insights_router
    from app.api.v1.routes.admin import router as admin_router
    from app.api.v1.routes.notifications import router as notifications_router
    from app.api.v1.routes.integrations.openclaw import router as openclaw_router
    from app.api.v1.routes.integrations.slack import router as slack_router
    from app.api.v1.routes.assistant import router as assistant_router

    prefix = "/api/v1"

    app.include_router(health_router, prefix=prefix)
    app.include_router(org_router, prefix=prefix)
    app.include_router(users_router, prefix=prefix)
    app.include_router(exceptions_router, prefix=prefix)
    app.include_router(policies_router, prefix=prefix)
    app.include_router(precedents_router, prefix=prefix)
    app.include_router(decisions_router, prefix=prefix)
    app.include_router(outcomes_router, prefix=prefix)
    app.include_router(recommendations_router, prefix=prefix)
    app.include_router(debate_router, prefix=prefix)
    app.include_router(memory_router, prefix=prefix)
    app.include_router(training_router, prefix=prefix)
    app.include_router(voice_router, prefix=prefix)
    app.include_router(insights_router, prefix=prefix)
    app.include_router(admin_router, prefix=prefix)
    app.include_router(notifications_router, prefix=prefix)
    app.include_router(openclaw_router, prefix=prefix)
    app.include_router(slack_router, prefix=prefix)
    app.include_router(assistant_router, prefix=prefix)

    # Root
    @app.get("/")
    async def root() -> dict[str, Any]:
        return {
            "service": "ExceptionOS API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()

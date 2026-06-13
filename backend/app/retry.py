"""Retry logic with exponential backoff."""
from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar

import structlog

logger = structlog.get_logger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


async def retry_async(
    fn: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    **kwargs,
) -> Any:
    """Retry an async callable with exponential backoff."""
    last_exc: Exception | None = None
    delay = base_delay

    for attempt in range(1, max_attempts + 1):
        try:
            return await fn(*args, **kwargs)
        except exceptions as exc:
            last_exc = exc
            if attempt == max_attempts:
                logger.warning(
                    "retry_exhausted",
                    fn=getattr(fn, "__name__", str(fn)),
                    attempts=attempt,
                    error=str(exc),
                )
                raise
            logger.info(
                "retry_attempt",
                fn=getattr(fn, "__name__", str(fn)),
                attempt=attempt,
                delay=delay,
                error=str(exc),
            )
            await asyncio.sleep(min(delay, max_delay))
            delay *= backoff_factor

    raise last_exc  # type: ignore[misc]


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """Decorator that adds retry behaviour to an async function."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            return await retry_async(
                fn,
                *args,
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                exceptions=exceptions,
                **kwargs,
            )

        return wrapper  # type: ignore[return-value]

    return decorator

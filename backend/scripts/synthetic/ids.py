"""Deterministic UUID helpers.

The generator must be reproducible: running it twice with the same seed and
organization name should produce the same primary keys, so ``load.py`` can
``upsert`` rows idempotently and ``--reset`` can find exactly the rows it
created previously.

We derive UUIDv5 values from a stable namespace + a human-readable "path"
string (e.g. ``"novaflow:case:EX-101"``). UUIDv5 is deterministic for a given
(namespace, name) pair.
"""
from __future__ import annotations

import uuid

# Fixed namespace UUID for the ExceptionOS synthetic-data system. Any valid
# UUID works here as long as it is constant across runs.
EXCEPTIONOS_NAMESPACE = uuid.UUID("a8e6f0c0-2026-4eb1-9c2a-ec0e7c10ee5a")


def deterministic_uuid(*parts: str) -> uuid.UUID:
    """Return a stable UUIDv5 derived from ``parts`` joined with ':'."""
    name = ":".join(str(p) for p in parts)
    return uuid.uuid5(EXCEPTIONOS_NAMESPACE, name)


def deterministic_id_str(*parts: str) -> str:
    return str(deterministic_uuid(*parts))

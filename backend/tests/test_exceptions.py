"""Tests for exception case endpoints."""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient


ORG_ID = str(uuid4())
CASE_ID = str(uuid4())
USER_ID = str(uuid4())

MOCK_CASE = {
    "id": CASE_ID,
    "organization_id": ORG_ID,
    "case_number": "EXC-TEST-0001",
    "title": "Test Exception",
    "description": "A test exception case",
    "entity_name": "Test Corp",
    "requested_amount": 10000.0,
    "currency": "USD",
    "urgency": "medium",
    "status": "draft",
    "version": 1,
    "created_at": "2024-01-01T00:00:00+00:00",
    "updated_at": "2024-01-01T00:00:00+00:00",
}


def _make_mock_supabase(case_data=None, count=1):
    mock = MagicMock()
    mock_table = MagicMock()
    mock.table.return_value = mock_table
    for method in ("select", "insert", "update", "delete", "eq", "neq",
                   "in_", "order", "range", "limit", "maybe_single", "single"):
        getattr(mock_table, method).return_value = mock_table
    mock_table.execute.return_value = MagicMock(
        data=[case_data] if case_data else [],
        count=count,
    )
    return mock


def _make_jwt_payload(user_id: str = USER_ID) -> dict:
    return {
        "sub": user_id,
        "email": "test@example.com",
        "app_metadata": {},
    }


@pytest.fixture
def client():
    mock_supabase = _make_mock_supabase(MOCK_CASE)

    with (
        patch("app.dependencies.create_client", return_value=mock_supabase),
        patch(
            "app.dependencies.jwt.decode",
            return_value=_make_jwt_payload(),
        ),
    ):
        from app.main import app
        with TestClient(app) as c:
            yield c


AUTH_HEADER = {"Authorization": "Bearer fake.jwt.token"}


def test_list_exceptions_requires_auth(client):
    resp = client.get(f"/api/v1/exceptions/?organization_id={ORG_ID}")
    # Without auth header, should return 401
    assert resp.status_code == 401


def test_list_exceptions_with_auth(client):
    resp = client.get(
        f"/api/v1/exceptions/?organization_id={ORG_ID}",
        headers=AUTH_HEADER,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body


def test_get_exception_with_auth(client):
    resp = client.get(
        f"/api/v1/exceptions/{CASE_ID}?organization_id={ORG_ID}",
        headers=AUTH_HEADER,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "data" in body


def test_create_exception_with_auth(client):
    payload = {
        "title": "New Test Exception",
        "description": "A brand new exception",
        "urgency": "high",
        "requested_amount": 50000.0,
    }
    resp = client.post(
        f"/api/v1/exceptions/?organization_id={ORG_ID}",
        json=payload,
        headers=AUTH_HEADER,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert "data" in body


def test_health_no_auth_required():
    with patch("app.dependencies.create_client") as mock_create:
        mock_supabase = _make_mock_supabase()
        mock_create.return_value = mock_supabase
        from app.main import app
        with TestClient(app) as c:
            resp = c.get("/api/v1/health")
            assert resp.status_code == 200

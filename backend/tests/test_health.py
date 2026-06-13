"""Tests for the health check endpoint."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


@pytest.fixture
def client():
    """Create a test client with mocked Supabase."""
    with patch("app.dependencies.create_client") as mock_create:
        mock_supabase = MagicMock()
        mock_table = MagicMock()
        mock_supabase.table.return_value = mock_table
        mock_table.select.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = MagicMock(data=[], count=0)
        mock_create.return_value = mock_supabase

        from app.main import app
        with TestClient(app) as c:
            yield c


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "ExceptionOS API"
    assert "version" in data


def test_health_endpoint(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data
    assert "database" in data["services"]
    assert "groq" in data["services"]
    assert "hindsight" in data["services"]


def test_health_returns_version(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json()["version"] == "1.0.0"

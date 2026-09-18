from fastapi.testclient import TestClient
from app.main import app


def test_health_and_routes_contract():
    with TestClient(app) as client:
        assert client.get("/health").json()["status"] == "ok"
        route = client.get("/api/v1/routes").json()[0]
        assert {"id", "origin", "destination", "dgca_traffic_weight"} <= route.keys()


def test_index_always_returns_confidence_metadata():
    with TestClient(app) as client:
        point = client.get("/api/v1/index?freq=daily").json()[0]
        assert {"value", "confidence_score", "coverage_pct", "chain_break"} <= point.keys()

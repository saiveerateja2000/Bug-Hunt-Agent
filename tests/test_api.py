from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Bug Hunt Agent"


def test_emergency_stop_blocks_new_jobs() -> None:
    with TestClient(app) as client:
        resp = client.post("/emergency-stop", params={"active": "true"})
        assert resp.status_code == 200
        blocked = client.post(
            "/campaigns/c1/jobs",
            params={
                "target": "https://api.example.local/v1/health",
                "in_scope_host": "api.example.local",
            },
        )
        assert blocked.status_code == 423

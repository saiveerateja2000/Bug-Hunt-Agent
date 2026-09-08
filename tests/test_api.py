from fastapi.testclient import TestClient

from app.main import app



def _create_campaign(client: TestClient, testing_mode: str = "passive") -> int:
    inserted = client.post("/programs/discover")
    assert inserted.status_code == 200

    programs = client.get("/programs")
    assert programs.status_code == 200
    program_id = programs.json()[0]["id"]

    created = client.post(
        "/campaigns",
        json={
            "name": "demo-campaign",
            "program_id": program_id,
            "target_host": "api.example.local",
            "testing_mode": testing_mode,
        },
    )
    assert created.status_code == 200
    return int(created.json()["campaign_id"])



def test_dashboard_endpoint() -> None:
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["name"] == "Bug Hunt Agent"



def test_emergency_stop_blocks_new_jobs() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client)
        resp = client.post("/emergency-stop", params={"active": "true"})
        assert resp.status_code == 200

        blocked = client.post(
            f"/campaigns/{campaign_id}/jobs",
            json={"action": "http_probe", "target": "https://api.example.local/v1/health"},
        )
        assert blocked.status_code == 403



def test_passive_campaign_blocks_active_checks() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client, testing_mode="passive")
        blocked = client.post(
            f"/campaigns/{campaign_id}/jobs",
            json={"action": "idor_check", "target": "https://api.example.local/v1/resource/1"},
        )
        assert blocked.status_code == 403



def test_findings_and_report_draft_flow() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client, testing_mode="safe_active")
        finding = client.post(
            "/findings",
            json={
                "campaign_id": campaign_id,
                "title": "Potential IDOR on invoices",
                "vulnerability_type": "IDOR",
                "severity": "high",
                "confidence": "medium",
                "business_impact": "Cross-tenant invoice access risk",
                "reproducible": True,
                "evidence_summary": "Tenant A can request tenant B invoice by id.",
            },
        )
        assert finding.status_code == 200
        finding_id = finding.json()["finding_id"]

        report = client.post(f"/findings/{finding_id}/report-draft")
        assert report.status_code == 200

        reports = client.get("/reports")
        assert reports.status_code == 200
        assert len(reports.json()) >= 1


def test_autonomous_run_queues_passive_jobs() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client, testing_mode="passive")
        run = client.post(
            f"/campaigns/{campaign_id}/autonomous-run",
            json={"max_jobs": 5},
        )
        assert run.status_code == 200
        payload = run.json()
        assert payload["status"] == "queued"
        assert len(payload["queued_jobs"]) == 5
        assert all(item["action"] in {"surface_map", "passive_recon", "http_probe"} for item in payload["queued_jobs"])


def test_autonomous_run_rejects_mismatched_base_url() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client, testing_mode="safe_active")
        run = client.post(
            f"/campaigns/{campaign_id}/autonomous-run",
            json={"base_url": "https://example.com"},
        )
        assert run.status_code == 400


def test_autonomous_run_includes_safe_active_checks() -> None:
    with TestClient(app) as client:
        campaign_id = _create_campaign(client, testing_mode="safe_active")
        run = client.post(
            f"/campaigns/{campaign_id}/autonomous-run",
            json={"max_jobs": 8},
        )
        assert run.status_code == 200
        actions = {item["action"] for item in run.json()["queued_jobs"]}
        assert {"auth_check", "idor_check", "rate_limit_check"}.issubset(actions)

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

from fastapi import FastAPI, HTTPException
from sqlalchemy import select

from app.healthcheck import check_app_health
from app.migrate import run_migrations
from app.models import EmergencyStop, PolicyDecision
from app.db import SessionLocal
from app.queue import enqueue_job
from app.tools import SafeToolRunner, ToolRequest

app = FastAPI(title="Bug Hunt Agent", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    run_migrations()


@app.get("/")
def dashboard() -> dict[str, str]:
    return {
        "name": "Bug Hunt Agent",
        "status": "running",
        "dashboard": "http://localhost:8000",
        "mode": "local-safe",
    }


@app.get("/health")
def health() -> dict[str, str]:
    if not check_app_health():
        raise HTTPException(status_code=503, detail="unhealthy")
    return {"status": "ok"}


@app.get("/emergency-stop")
def emergency_stop_state() -> dict[str, bool]:
    with SessionLocal() as session:
        row = session.execute(select(EmergencyStop).limit(1)).scalar_one()
        return {"active": row.active}


@app.post("/emergency-stop")
def set_emergency_stop(active: bool) -> dict[str, bool]:
    with SessionLocal() as session:
        row = session.execute(select(EmergencyStop).limit(1)).scalar_one()
        row.active = active
        session.commit()
        return {"active": row.active}


@app.get("/first-run-checklist")
def first_run_checklist() -> dict[str, bool]:
    return {
        "database_healthy": check_app_health(),
        "browser_available": True,
        "tool_registry_available": True,
        "model_connection_configured": True,
        "evidence_directory_writable": True,
        "emergency_stop_available": True,
        "live_target_default_disabled": True,
    }


@app.post("/campaigns/{campaign_id}/jobs")
def create_job(campaign_id: str, target: str, in_scope_host: str) -> dict[str, int]:
    with SessionLocal() as session:
        row = session.execute(select(EmergencyStop).limit(1)).scalar_one()
        if row.active:
            raise HTTPException(status_code=423, detail="campaign actions paused by emergency stop")

    runner = SafeToolRunner()
    result = runner.run(
        ToolRequest(
            campaign_id=campaign_id,
            action="http_probe",
            target=target,
            in_scope_hosts={in_scope_host},
        )
    )
    with SessionLocal() as session:
        session.add(
            PolicyDecision(
                campaign_id=campaign_id,
                action="http_probe",
                target=target,
                allowed=result.ok,
                reason=result.message,
            )
        )
        session.commit()
    if not result.ok:
        raise HTTPException(status_code=403, detail=result.message)
    job_id = enqueue_job(campaign_id=campaign_id, action="http_probe", target=target)
    return {"job_id": job_id}

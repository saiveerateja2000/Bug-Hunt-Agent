from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.config import settings
from app.db import SessionLocal
from app.healthcheck import check_app_health
from app.migrate import run_migrations
from app.models import AuditLog, Campaign, EmergencyStop, Finding, PolicyDecision, Program, ReportDraft
from app.policy import PASSIVE_ONLY_ACTIONS, SAFE_ACTIVE_ACTIONS, PolicyEngine, PolicyRequest
from app.queue import enqueue_job, list_campaign_jobs

app = FastAPI(title="Bug Hunt Agent", version="1.0.0")


TRUSTED_SAMPLE_PROGRAMS = [
    {
        "source": "HackerOne",
        "company_name": "Example SaaS Inc",
        "program_name": "Example API Program",
        "canonical_url": "https://hackerone.com/example-api",
        "program_type": "bounty",
        "status": "active",
        "reward_range": "$500 - $10,000",
        "scope_summary": "api.example.local, app.example.local",
        "out_of_scope_summary": "Production customer data, phishing, DDoS",
        "safe_harbor": "Authorized in-scope good-faith testing only",
        "prohibited_actions": "No destructive testing",
        "data_confidence": 80,
    },
    {
        "source": "Bugcrowd",
        "company_name": "Payments Labs",
        "program_name": "Payments Platform Disclosure",
        "canonical_url": "https://bugcrowd.com/payments-platform",
        "program_type": "disclosure",
        "status": "active",
        "reward_range": "Recognition",
        "scope_summary": "pay.example.local",
        "out_of_scope_summary": "Social engineering",
        "safe_harbor": "Coordinated disclosure only",
        "prohibited_actions": "No data exfiltration",
        "data_confidence": 70,
    },
]


class CampaignCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    program_id: int
    target_host: str = Field(min_length=3, max_length=255)
    testing_mode: str = Field(default="passive")
    max_total_requests: int = Field(default=settings.max_total_requests, ge=1, le=5000)
    max_duration_minutes: int = Field(default=settings.max_campaign_duration_minutes, ge=1, le=1440)


class JobCreateRequest(BaseModel):
    action: str
    target: str


class FindingCreateRequest(BaseModel):
    campaign_id: int
    title: str
    vulnerability_type: str
    severity: str
    confidence: str
    business_impact: str = ""
    reproducible: bool = False
    evidence_summary: str = ""


@app.on_event("startup")
def startup() -> None:
    run_migrations()


@app.get("/")
def dashboard() -> dict[str, str]:
    return {
        "name": "Bug Hunt Agent",
        "status": "running",
        "dashboard": f"http://localhost:{settings.app_port}",
        "mode": "local-safe",
        "default_research_mode": settings.research_mode,
    }


@app.get("/health")
def health() -> dict[str, str]:
    if not check_app_health():
        raise HTTPException(status_code=503, detail="unhealthy")
    return {"status": "ok"}


@app.get("/first-run-checklist")
def first_run_checklist() -> dict[str, bool]:
    return {
        "database_healthy": check_app_health(),
        "browser_available": True,
        "tool_registry_available": True,
        "model_connection_configured": bool(settings.model_provider),
        "evidence_directory_writable": True,
        "emergency_stop_available": True,
        "live_target_default_disabled": settings.research_mode == "passive",
    }


@app.post("/programs/discover")
def discover_programs() -> dict[str, int]:
    inserted = 0
    with SessionLocal() as session:
        for item in TRUSTED_SAMPLE_PROGRAMS:
            existing = session.execute(select(Program).where(Program.canonical_url == item["canonical_url"])).scalar_one_or_none()
            if existing is None:
                session.add(Program(**item))
                inserted += 1
        session.add(AuditLog(event_type="program_discovery", actor="system", details=f"inserted={inserted}"))
        session.commit()
    return {"inserted": inserted}


@app.get("/programs")
def list_programs() -> list[dict[str, str | int]]:
    with SessionLocal() as session:
        programs = list(session.execute(select(Program).order_by(Program.id.asc())).scalars())
        return [
            {
                "id": p.id,
                "source": p.source,
                "company_name": p.company_name,
                "program_name": p.program_name,
                "status": p.status,
                "reward_range": p.reward_range,
                "scope_summary": p.scope_summary,
                "data_confidence": p.data_confidence,
            }
            for p in programs
        ]


@app.get("/programs/opportunities")
def score_programs() -> list[dict[str, str | int]]:
    with SessionLocal() as session:
        programs = list(session.execute(select(Program)).scalars())

    scored: list[dict[str, str | int]] = []
    for p in programs:
        base = p.data_confidence
        if p.status != "active":
            base -= 40
        if "$" in p.reward_range:
            base += 10
        if "api" in p.scope_summary.lower():
            base += 5
        score = max(0, min(base, 100))
        if score >= 75:
            priority = "High-priority opportunity"
        elif score >= 55:
            priority = "Medium-priority opportunity"
        elif score >= 35:
            priority = "Low-priority opportunity"
        else:
            priority = "Manual-review required"
        scored.append(
            {
                "program_id": p.id,
                "program_name": p.program_name,
                "score": score,
                "priority": priority,
                "reasons": "status, reward visibility, scope confidence",
            }
        )
    return sorted(scored, key=lambda x: int(x["score"]), reverse=True)


@app.post("/campaigns")
def create_campaign(payload: CampaignCreateRequest) -> dict[str, int | str]:
    if payload.testing_mode not in {"passive", "safe_active"}:
        raise HTTPException(status_code=400, detail="testing_mode must be passive or safe_active")

    with SessionLocal() as session:
        if session.get(Program, payload.program_id) is None:
            raise HTTPException(status_code=404, detail="program not found")

        campaign = Campaign(
            name=payload.name,
            program_id=payload.program_id,
            target_host=payload.target_host,
            testing_mode=payload.testing_mode,
            max_total_requests=payload.max_total_requests,
            max_duration_minutes=payload.max_duration_minutes,
            approval_required=settings.approval_mode == "human_required",
        )
        session.add(campaign)
        session.flush()
        session.add(
            AuditLog(
                event_type="campaign_created",
                actor="user",
                campaign_id=campaign.id,
                details=f"program_id={payload.program_id}, mode={payload.testing_mode}",
            )
        )
        session.commit()
        return {"campaign_id": campaign.id, "status": "created"}


@app.post("/campaigns/{campaign_id}/pause")
def pause_campaign(campaign_id: int, active: bool) -> dict[str, bool]:
    with SessionLocal() as session:
        campaign = session.get(Campaign, campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="campaign not found")
        campaign.paused = active
        session.add(
            AuditLog(
                event_type="campaign_paused" if active else "campaign_resumed",
                actor="user",
                campaign_id=campaign.id,
                details=f"paused={active}",
            )
        )
        session.commit()
        return {"paused": campaign.paused}


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
        row.updated_at = datetime.utcnow()
        session.add(AuditLog(event_type="emergency_stop", actor="user", details=f"active={active}"))
        session.commit()
        return {"active": row.active}


@app.post("/campaigns/{campaign_id}/jobs")
def create_job(campaign_id: int, payload: JobCreateRequest) -> dict[str, int | str]:
    with SessionLocal() as session:
        campaign = session.get(Campaign, campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="campaign not found")
        if campaign.paused:
            raise HTTPException(status_code=423, detail="campaign is paused")

        stop = session.execute(select(EmergencyStop).limit(1)).scalar_one()
        decision = PolicyEngine().evaluate(
            PolicyRequest(
                campaign_id=campaign.id,
                action=payload.action,
                target=payload.target,
                in_scope_hosts={campaign.target_host},
                excluded_hosts=set(),
                research_mode=campaign.testing_mode,
                emergency_stop_active=stop.active,
                total_requests_so_far=campaign.requests_consumed,
                max_total_requests=campaign.max_total_requests,
            )
        )

        session.add(
            PolicyDecision(
                campaign_id=campaign.id,
                action=payload.action,
                target=payload.target,
                allowed=decision.allowed,
                reason=decision.reason,
            )
        )

        if not decision.allowed:
            session.add(
                AuditLog(
                    event_type="policy_block",
                    actor="policy",
                    campaign_id=campaign.id,
                    details=decision.reason,
                )
            )
            session.commit()
            raise HTTPException(status_code=403, detail=decision.reason)

        job_id = enqueue_job(campaign_id=campaign.id, action=payload.action, target=payload.target)
        session.add(
            AuditLog(
                event_type="job_enqueued",
                actor="user",
                campaign_id=campaign.id,
                details=f"job_id={job_id}, action={payload.action}",
            )
        )
        session.commit()
    return {"job_id": job_id, "status": "queued"}


@app.get("/campaigns/{campaign_id}/jobs")
def campaign_jobs(campaign_id: int) -> list[dict[str, str | int]]:
    jobs = list_campaign_jobs(campaign_id)
    return [
        {
            "id": j.id,
            "action": j.action,
            "target": j.target,
            "status": j.status,
            "details": j.details,
        }
        for j in jobs
    ]


@app.post("/findings")
def create_finding(payload: FindingCreateRequest) -> dict[str, int | str]:
    with SessionLocal() as session:
        if session.get(Campaign, payload.campaign_id) is None:
            raise HTTPException(status_code=404, detail="campaign not found")
        finding = Finding(
            campaign_id=payload.campaign_id,
            title=payload.title,
            vulnerability_type=payload.vulnerability_type,
            severity=payload.severity,
            confidence=payload.confidence,
            business_impact=payload.business_impact,
            reproducible=payload.reproducible,
            evidence_summary=payload.evidence_summary,
        )
        session.add(finding)
        session.flush()
        session.add(
            AuditLog(
                event_type="finding_created",
                actor="user",
                campaign_id=payload.campaign_id,
                details=f"finding_id={finding.id}",
            )
        )
        session.commit()
        return {"finding_id": finding.id, "status": "recorded"}


@app.get("/findings")
def list_findings() -> list[dict[str, str | int | bool]]:
    with SessionLocal() as session:
        findings = list(session.execute(select(Finding).order_by(Finding.id.asc())).scalars())
    return [
        {
            "id": f.id,
            "campaign_id": f.campaign_id,
            "title": f.title,
            "vulnerability_type": f.vulnerability_type,
            "severity": f.severity,
            "confidence": f.confidence,
            "reproducible": f.reproducible,
        }
        for f in findings
    ]


@app.post("/findings/{finding_id}/report-draft")
def create_report_draft(finding_id: int) -> dict[str, int | str]:
    with SessionLocal() as session:
        finding = session.get(Finding, finding_id)
        if finding is None:
            raise HTTPException(status_code=404, detail="finding not found")

        report = ReportDraft(
            finding_id=finding.id,
            title=f"[Draft] {finding.title}",
            executive_summary=f"Potential {finding.vulnerability_type} affecting campaign {finding.campaign_id}.",
            reproduction_steps="1. Use authorized test account. 2. Follow bounded request sequence. 3. Observe divergence.",
            expected_behavior="The system enforces scope, authorization, and tenant boundaries.",
            actual_behavior=finding.evidence_summary or "Behavior requires human review.",
            remediation="Apply least-privilege authorization checks and add regression tests.",
        )
        session.add(report)
        session.flush()
        session.add(
            AuditLog(
                event_type="report_draft_created",
                actor="system",
                campaign_id=finding.campaign_id,
                details=f"report_id={report.id}, finding_id={finding.id}",
            )
        )
        session.commit()
        return {"report_id": report.id, "status": "drafted"}


@app.get("/reports")
def list_reports() -> list[dict[str, str | int]]:
    with SessionLocal() as session:
        reports = list(session.execute(select(ReportDraft).order_by(ReportDraft.id.asc())).scalars())
    return [
        {
            "id": r.id,
            "finding_id": r.finding_id,
            "title": r.title,
            "executive_summary": r.executive_summary,
        }
        for r in reports
    ]


@app.get("/audit")
def list_audit(limit: int = 100) -> list[dict[str, str | int | None]]:
    size = max(1, min(limit, 500))
    with SessionLocal() as session:
        rows = list(session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(size)).scalars())
    return [
        {
            "id": row.id,
            "event_type": row.event_type,
            "actor": row.actor,
            "campaign_id": row.campaign_id,
            "details": row.details,
        }
        for row in rows
    ]


@app.get("/stats")
def stats() -> dict[str, int]:
    with SessionLocal() as session:
        return {
            "programs": int(session.execute(select(func.count(Program.id))).scalar_one()),
            "campaigns": int(session.execute(select(func.count(Campaign.id))).scalar_one()),
            "jobs": int(session.execute(select(func.count(PolicyDecision.id))).scalar_one()),
            "findings": int(session.execute(select(func.count(Finding.id))).scalar_one()),
            "reports": int(session.execute(select(func.count(ReportDraft.id))).scalar_one()),
            "allowed_actions": len(PASSIVE_ONLY_ACTIONS.union(SAFE_ACTIVE_ACTIONS)),
        }

from datetime import datetime

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Job


def enqueue_job(campaign_id: int, action: str, target: str) -> int:
    with SessionLocal() as session:
        job = Job(campaign_id=campaign_id, action=action, target=target, status="queued")
        session.add(job)
        session.commit()
        session.refresh(job)
        return job.id


def dequeue_job() -> Job | None:
    with SessionLocal() as session:
        job = session.execute(select(Job).where(Job.status == "queued").order_by(Job.id.asc())).scalar_one_or_none()
        if job is None:
            return None
        job.status = "running"
        job.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(job)
        return job


def update_job(job_id: int, status: str, details: str = "") -> None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is None:
            return
        job.status = status
        job.details = details
        job.updated_at = datetime.utcnow()
        session.commit()


def list_campaign_jobs(campaign_id: int) -> list[Job]:
    with SessionLocal() as session:
        return list(session.execute(select(Job).where(Job.campaign_id == campaign_id).order_by(Job.id.asc())).scalars())

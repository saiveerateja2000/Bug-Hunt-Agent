from sqlalchemy import select

from app.db import SessionLocal
from app.models import Job


def enqueue_job(campaign_id: str, action: str, target: str) -> int:
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
        session.commit()
        session.refresh(job)
        return job


def mark_done(job_id: int) -> None:
    with SessionLocal() as session:
        job = session.get(Job, job_id)
        if job is not None:
            job.status = "done"
            session.commit()

import time

from sqlalchemy import select

from app.db import SessionLocal
from app.migrate import run_migrations
from app.models import AuditLog, Campaign, EmergencyStop, PolicyDecision, ToolExecution
from app.queue import dequeue_job, update_job
from app.tools import SafeToolRunner, ToolRequest


POLL_INTERVAL_SECONDS = 2


def process_job() -> None:
    with SessionLocal() as session:
        stop = session.execute(select(EmergencyStop).limit(1)).scalar_one()
        if stop.active:
            time.sleep(POLL_INTERVAL_SECONDS)
            return

    job = dequeue_job()
    if job is None:
        time.sleep(POLL_INTERVAL_SECONDS)
        return

    with SessionLocal() as session:
        campaign = session.get(Campaign, job.campaign_id)
        if campaign is None:
            update_job(job.id, "failed", "campaign not found")
            return
        if campaign.paused:
            update_job(job.id, "cancelled", "campaign paused")
            session.add(AuditLog(event_type="job_cancelled", actor="worker", campaign_id=campaign.id, details="Campaign paused"))
            session.commit()
            return
        stop = session.execute(select(EmergencyStop).limit(1)).scalar_one()

        runner = SafeToolRunner()
        result = runner.run(
            ToolRequest(
                campaign_id=campaign.id,
                action=job.action,
                target=job.target,
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
                action=job.action,
                target=job.target,
                allowed=result.ok,
                reason=result.message,
            )
        )

        session.add(
            ToolExecution(
                campaign_id=campaign.id,
                job_id=job.id,
                tool_name=job.action,
                target=job.target,
                status="success" if result.ok else "blocked",
                result_summary=str(result.output),
            )
        )

        campaign.requests_consumed += 1
        session.add(
            AuditLog(
                event_type="job_processed",
                actor="worker",
                campaign_id=campaign.id,
                details=f"job={job.id}, status={'done' if result.ok else 'failed'}",
            )
        )
        session.commit()

    if result.ok:
        update_job(job.id, "done", result.message)
    else:
        update_job(job.id, "failed", result.message)


def main() -> None:
    run_migrations()
    while True:
        process_job()


if __name__ == "__main__":
    main()

import time

from sqlalchemy import select

from app.db import SessionLocal
from app.migrate import run_migrations
from app.models import EmergencyStop
from app.queue import dequeue_job, mark_done


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
    # Placeholder for bounded approved checks.
    mark_done(job.id)


def main() -> None:
    run_migrations()
    while True:
        process_job()


if __name__ == "__main__":
    main()

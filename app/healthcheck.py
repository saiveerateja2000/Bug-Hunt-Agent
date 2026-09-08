import sys

from sqlalchemy import select, text

from app.db import SessionLocal
from app.models import EmergencyStop, Program, SchemaVersion
from app.policy import PolicyEngine, PolicyRequest


def _db_ready() -> bool:
    with SessionLocal() as session:
        session.execute(text("SELECT 1"))
    return True


def _migrations_current() -> bool:
    with SessionLocal() as session:
        return session.execute(select(SchemaVersion).limit(1)).scalar_one_or_none() is not None


def _emergency_stop_readable() -> bool:
    with SessionLocal() as session:
        return session.execute(select(EmergencyStop).limit(1)).scalar_one_or_none() is not None


def _policy_available() -> bool:
    engine = PolicyEngine()
    result = engine.evaluate(
        PolicyRequest(
            campaign_id=0,
            action="http_probe",
            target="https://example.local/health",
            in_scope_hosts={"example.local"},
            excluded_hosts=set(),
            research_mode="passive",
            emergency_stop_active=False,
            total_requests_so_far=0,
            max_total_requests=2,
        )
    )
    return result.allowed


def _seed_table_available() -> bool:
    with SessionLocal() as session:
        session.execute(select(Program).limit(1))
    return True


def check_app_health() -> bool:
    return (
        _db_ready()
        and _migrations_current()
        and _emergency_stop_readable()
        and _policy_available()
        and _seed_table_available()
    )


def check_worker_health() -> bool:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("data:text/html,<html><body>ok</body></html>")
        browser.close()

    return check_app_health()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "app"
    ok = check_worker_health() if mode == "worker" else check_app_health()
    if not ok:
        raise SystemExit(1)

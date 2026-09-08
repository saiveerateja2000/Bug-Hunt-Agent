from sqlalchemy import select

from app.db import SessionLocal, engine
from app.models import Base, EmergencyStop, SchemaVersion


CURRENT_SCHEMA_VERSION = 2


def run_migrations() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        row = session.execute(select(SchemaVersion).limit(1)).scalar_one_or_none()
        if row is None:
            session.add(SchemaVersion(version=CURRENT_SCHEMA_VERSION))
        else:
            row.version = CURRENT_SCHEMA_VERSION
        if session.execute(select(EmergencyStop).limit(1)).scalar_one_or_none() is None:
            session.add(EmergencyStop(active=False))
        session.commit()


if __name__ == "__main__":
    run_migrations()

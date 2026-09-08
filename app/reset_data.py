import shutil
from pathlib import Path

from app.config import settings
from app.db import engine
from app.migrate import run_migrations
from app.models import Base


def _wipe(path: str) -> None:
    p = Path(path)
    if not p.exists():
        return
    for child in p.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def main() -> None:
    for d in (settings.evidence_dir, settings.reports_dir, settings.log_dir, settings.backup_dir):
        _wipe(d)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    run_migrations()


if __name__ == "__main__":
    main()

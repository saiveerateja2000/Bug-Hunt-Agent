import shutil
from pathlib import Path

from app.config import settings


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


if __name__ == "__main__":
    main()

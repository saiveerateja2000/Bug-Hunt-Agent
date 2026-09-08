#!/usr/bin/env sh
set -eu

export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python -m app.migrate

cmd="${1:-app}"
case "$cmd" in
  app)
    exec uvicorn app.main:app --host 0.0.0.0 --port "${APP_PORT:-8000}"
    ;;
  worker)
    exec python -m app.worker
    ;;
  test)
    exec pytest -q
    ;;
  reset-data)
    if [ "${CONFIRM_DATA_RESET:-}" != "YES" ]; then
      echo "Refusing reset. Re-run with CONFIRM_DATA_RESET=YES"
      exit 1
    fi
    exec python -m app.reset_data
    ;;
  *)
    exec "$@"
    ;;
esac

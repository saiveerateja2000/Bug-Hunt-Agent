FROM python:3.11.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip==24.2 && pip install -r /app/requirements.txt

# Install browser binaries in image and verify launch works.
RUN python -m playwright install --with-deps chromium

COPY app /app/app
COPY scripts /app/scripts
COPY tests /app/tests
COPY README.md /app/README.md

RUN useradd -m -u 10001 appuser && \
    mkdir -p /data/evidence /data/reports /data/logs /data/backups && \
    chown -R appuser:appuser /app /data

USER appuser

RUN python -m app.browser_smoke

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
CMD ["app"]

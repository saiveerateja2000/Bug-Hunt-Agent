# Bug-Hunt-Agent

Local-first, policy-controlled bug-bounty research platform MVP rebuilt from `Readme2.md` requirements.

## What this MVP now provides

- Trusted program discovery seed flow (`/programs/discover`)
- Program inventory and explainable opportunity scoring (`/programs`, `/programs/opportunities`)
- Campaign creation with strict target host binding and mode selection (`passive` / `safe_active`)
- Mandatory policy enforcement before every queued action
- Emergency stop and campaign pause controls
- Policy decision logging, audit logging, and job lifecycle tracking
- Finding capture and report draft generation workflows
- First-run and service health checks
- Three-container Docker architecture (`app`, `worker`, `postgres`)

## Safety defaults

- Local-only operation
- Passive research mode by default
- Human approval mode enabled
- No destructive testing
- No automatic report submission

## Quick start

1. Copy environment template:
   ```bash
   cp .env.example .env
   ```
2. Build:
   ```bash
   docker compose build
   ```
3. Start:
   ```bash
   docker compose up -d
   ```
4. Open dashboard/API:
   - `http://localhost:8000`
5. Stream logs:
   ```bash
   docker compose logs -f
   ```
6. Run tests:
   ```bash
   docker compose run --rm app test
   ```
7. Stop services:
   ```bash
   docker compose down
   ```

## Data reset (destructive)

```bash
CONFIRM_DATA_RESET=YES docker compose run --rm app reset-data
```

## Local data directories

- `./data/postgres`
- `./data/evidence`
- `./data/reports`
- `./data/logs`
- `./data/backups`

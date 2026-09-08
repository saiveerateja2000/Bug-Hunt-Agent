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

## Beginner guide: AI-driven autonomous run

After setup, the platform can automatically queue a safe hunt sequence for a campaign.

1. Seed trusted programs:
   ```bash
   curl -X POST http://localhost:8000/programs/discover
   ```
2. List programs and pick a program `id`:
   ```bash
   curl http://localhost:8000/programs
   ```
3. Create a campaign (replace `program_id` and `target_host`):
   ```bash
   curl -X POST http://localhost:8000/campaigns \
     -H "Content-Type: application/json" \
     -d '{"name":"my-first-campaign","program_id":1,"target_host":"api.example.local","testing_mode":"passive"}'
   ```
4. Start autonomous job planning and queueing (replace `campaign_id`):
   ```bash
   curl -X POST http://localhost:8000/campaigns/1/autonomous-run \
     -H "Content-Type: application/json" \
     -d '{"max_jobs":5}'
   ```
5. Check queued/processed jobs:
   ```bash
   curl http://localhost:8000/campaigns/1/jobs
   ```

Notes:
- `passive` mode queues passive actions only.
- `safe_active` mode can also queue bounded active checks (`auth_check`, `idor_check`, `rate_limit_check`).
- `base_url` is optional; if provided, it must match the campaign `target_host`.
- Emergency stop and policy rules still block unsafe actions.

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

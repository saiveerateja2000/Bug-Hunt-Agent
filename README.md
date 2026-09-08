# Bug-Hunt-Agent

Local-first, policy-controlled bug-bounty research platform MVP scaffold.

## Safety-first defaults

- Local-only mode enabled by default
- Passive research mode by default
- Human approval required for impactful actions
- Strict in-scope target enforcement
- No destructive testing
- No automatic report submission

## Minimal Docker architecture (3 containers)

- `app`: FastAPI API + local dashboard + orchestration APIs
- `worker`: background job runner (same image as app)
- `postgres`: persistent state

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
4. Open dashboard:
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

Use the explicit reset command with confirmation:

```bash
CONFIRM_DATA_RESET=YES docker compose run --rm app reset-data
```

## Local directories

- `./data/postgres`
- `./data/evidence`
- `./data/reports`
- `./data/logs`
- `./data/backups`

## Notes

- PostgreSQL is not exposed to host by default.
- Worker runs as a non-root user with dropped Linux capabilities.
- Browser automation uses isolated Playwright Chromium in-container.
- Tool execution must pass policy checks before running.

# Deployment and operations

No live hosting deployment was performed during delivery. The following is a concrete deployment configuration for your account. Hosting, persistent storage, domain and model API charges are separate; do not assume a free tier preserves SQLite files.

## Recommended small deployment: Render native Python + persistent disk

1. Put the release contents in a GitHub repository. Commit source, lock file, docs and tests. Exclude `.env`, data, backups and tokens. Keep README at repository root.
2. In Render, create a new **Web Service**, connect this repository and choose a Python runtime.
3. Set Python version to **3.12** (use the currently available 3.12 patch).
4. Build command: `pip install -r requirements.lock.txt`
5. Start command: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1`
6. Choose a plan supporting a persistent disk. Attach the disk at `/var/data`.
7. Configure the environment below before startup:

```dotenv
APP_ENV=production
PUBLIC_ORIGIN=https://YOUR-SERVICE.onrender.com
DATABASE_PATH=/var/data/nextstep.sqlite3
ACCESS_CODE=REPLACE_WITH_A_LONG_RANDOM_PRIVATE_CODE
LLM_PROVIDER=demo
SESSION_DAYS=30
```

Generate the access code locally with `python -c "import secrets; print(secrets.token_urlsafe(24))"`. Store it as a secret in the host dashboard. Use the exact assigned service origin, with no path. Set a custom domain's origin instead if that is how judges will visit. Production startup rejects missing/short access codes and non-HTTPS origins.

8. Set the health-check path to `/health` and deploy. Initialization/seed happens at runtime, when the persistent disk is available.
9. Visit the HTTPS origin, enter the code, create a request, then restart the service and verify Resume in the same browser.
10. Add model settings from AI_SETUP.md and redeploy if using cloud AI. A hosted service cannot reach Ollama running at 127.0.0.1 on your laptop; use a reachable private model service or cloud endpoint.
11. Generate a fresh MCP token in the hosted UI and run the smoke client with its HTTPS `/mcp/` URL.
12. Keep the disk, origin, secrets and service available through judging. Provide judges the application access code in private testing instructions, not in a public README.

Render's default filesystem is ephemeral. A persistent disk requires a suitable paid service and only its mount path survives restarts/redeploys. This SQLite design supports one replica; disk-backed deployments cannot be horizontally scaled as-is. Consult current pricing before creating paid resources.

## Docker locally

Copy `.env.example` to `.env`, then:

```powershell
docker compose up --build -d
docker compose logs -f
```

Open http://127.0.0.1:8000. The named volume stores SQLite; do not run `docker compose down -v` unless you intend to delete all application data. The image runs as an unprivileged user. Docker build/run was not executed in the delivery environment; validate locally before using it on a host.

## Docker on a server

Use a reverse proxy with a valid HTTPS certificate. Forward the configured PUBLIC_ORIGIN to the application's port 8000, keep the container bound to a private interface, and pass production settings plus a persistent `/data` volume. Run one replica and one worker. The current Compose binds to 127.0.0.1 deliberately. Configure your reverse proxy/network rather than publishing an unauthenticated development service to the internet.

The application's per-process rate limits are a basic safeguard, not a replacement for edge protection. Reverse-proxy users may share a source IP for session-creation limits. Configure a trusted gateway appropriately; do not trust arbitrary forwarded IP headers.

## Backup and restore

Make a consistent snapshot using SQLite's backup API while the app is running:

```powershell
.\.venv\Scripts\python.exe -m scripts.backup backups\nextstep-2026-10-07.sqlite3
```

Use a new filename each time. Copy verified backups to access-controlled storage off the service. Backups include conversations and token hashes; protect them. Automate backups in your deployment environment and verify retention.

Restore procedure:

1. Stop the application and ensure no process has the database open.
2. Preserve the current database and any `-wal`/`-shm` files in a separate recovery directory.
3. Copy the verified backup to DATABASE_PATH; remove stale WAL/SHM siblings from the active path only after preserving them.
4. Run SQLite `PRAGMA integrity_check` on the restored database; it must return `ok`.
5. Restart with the same origin. Test saved requests and a new booking.

Perform a restore drill before relying on backups. Do not copy only an actively written `.sqlite3` file; pending writes may be in WAL.

## Before a commercial launch

This package is a hardened prototype, not a completed public SaaS. Add real identity/recovery, data deletion/retention policy, provider integrations, monitoring and alerting, external security review, load testing, managed database migrations and support processes. The access code is a gate for a controlled demo; it is not per-user account authentication.

Sources checked during preparation:
- https://render.com/docs/deploy-fastapi
- https://render.com/docs/disks

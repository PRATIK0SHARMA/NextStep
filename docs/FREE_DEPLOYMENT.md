# Free deployment: GitHub + Render + Neon

This guide supersedes the SQLite/persistent-disk instructions for this deployment.
Use free plans and stay within their quotas. Render Free sleeps after inactivity;
Neon can suspend idle compute while retaining database storage. This is a demo
hosting path, not an always-on service guarantee. Groq usage has separate limits.

## 1. Install this update

Back up your project. Copy the ZIP contents into the folder containing README.md,
merging app/, docs/, scripts/, tests/, and .github/. Keep your .env and frontend.
This update does not replace the existing README. It does not copy local demo
bookings into Neon: your hosted deployment starts with a fresh workspace.

In your activated PowerShell terminal:

```powershell
python -m pip install -r requirements.lock.txt
python -m pytest -q
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

DATABASE_URL blank/unset uses your existing local SQLite database. Stop the
server after the check, then commit:

```powershell
git add .
git status
git commit -m "Add PostgreSQL support and free deployment guide"
git push
```

Check GitHub Actions. Both SQLite and PostgreSQL jobs must pass before deployment.
The PostgreSQL job uses a disposable database. NEVER set NEXTSTEP_TEST_DATABASE_URL
to Neon or any database with data you want to keep: the tests reset its schema.

## 2. Create Neon Free database

Go to https://console.neon.tech and create a Free project named nextstep.
Choose a region close to your Render service when available. Use the default
Postgres database. Open Connect, select the database and role, turn connection
pooling OFF for this small deployment, and copy the PostgreSQL connection URL.
Keep sslmode=require (and any supplied channel_binding setting) in the URL.
Copy only the URL, not a psql command or surrounding quotation marks.
The password is inside this URL. Save it privately; do not commit or share it.

No SQL pasting is required: startup creates tables and seeds fictional providers.

## 3. Create Render Free web service

Go to https://dashboard.render.com -> New -> Web Service. Connect your GitHub
repository PRATIK0SHARMA/NextStep and select main.

- Runtime/Language: Python 3 (explicitly choose Python, not Docker)
- Root directory: leave blank
- Build command: pip install -r requirements.lock.txt
- Start command: python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
- Instance: Free
- Health check path: /health
- No disk and no Render PostgreSQL instance are required.

## 4. Environment settings

Add these in Render, not GitHub:

| Variable | Value |
| --- | --- |
| APP_ENV | production |
| DATABASE_URL | Your private Neon connection URL |
| PUBLIC_ORIGIN | Exact Render HTTPS URL, no trailing slash/path |
| ACCESS_CODE | A private random access code generated below |
| LLM_PROVIDER | compatible |
| LLM_BASE_URL | https://api.groq.com/openai/v1 |
| LLM_MODEL | The exact model ID that already works in your local .env |
| LLM_API_KEY | Your existing private Groq key |
| LLM_TIMEOUT | 30 |
| SESSION_DAYS | 30 |

Generate ACCESS_CODE on your own laptop:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

Keep it: visitors need it to open the controlled demo. Do not publish it in README.
The .python-version file selects Python 3.12. Do not set DATABASE_PATH in Render.

If Render has not assigned a URL yet, initially set PUBLIC_ORIGIN to
https://pending.invalid. Create the service, copy its actual onrender.com URL,
then replace PUBLIC_ORIGIN and choose Save/rebuild/redeploy before testing.
A temporary 400 Invalid host header until this is corrected is expected.

## 5. Verify the live deployment

Wait for Render to report Live. Visit /health and check status ok. Open the base
URL in your normal browser and enter ACCESS_CODE. Enable microphone permission
and Speaker: on if using speech. Test a new request, preference change, selection,
and button confirmation. Save another unfinished request, reload, and resume.
Then use Render's restart control and check the same browser can still see both.
Cookies are per browser/domain; localhost requests do not appear in hosted sessions.
Never paste database URLs or API keys into chat or public screenshots.

## 6. Database design and operations

DATABASE_URL selects psycopg/PostgreSQL; blank keeps SQLite. Text dates and JSON
columns preserve the existing response format. IDs for slots/messages/audit use
Postgres identity columns. A transaction-level advisory lock serializes app
transactions, preserving this demo's original SQLite BEGIN IMMEDIATE behavior.
Unique constraints remain a second line of defense against duplicate bookings.
This is intentionally a small-demo design: use one worker/instance, not a
high-throughput deployment. Transactions do not stay open during model inference.

The local SQLite backup script refuses to run when DATABASE_URL is configured.
For PostgreSQL exports use pg_dump from a trusted machine with PGDATABASE set
privately to the connection URL, e.g. pg_dump --format=custom --file=nextstep.dump.
Store exports privately. Do not rely on free-tier retention as your only backup.

## 7. Common issues

- Missing psycopg: install the updated requirements.lock.txt; deploy latest commit.
- Invalid host header: PUBLIC_ORIGIN must exactly match the URL being visited.
- Storage error: check DATABASE_URL privately, SSL parameters, Neon status and quota.
- App takes time to open: Render Free can sleep; open it before a scheduled demo.
- Cloud AI error: keep the known-working local model ID; check Groq limits.
- GitHub tests fail: inspect the failed job before deploying; share redacted errors.

After the live verification, update the public README with the real URL, features,
architecture, local setup, limits and demonstration instructions.

References:
https://render.com/docs/free
https://render.com/docs/deploy-fastapi
https://render.com/docs/python-version
https://neon.com/docs/get-started-with-neon/connect-neon

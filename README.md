# NextStep

**Start a repair request. Leave it. Return without starting over.**

A complete Alexa+ track prototype with a working web experience, persistent repair-booking workflow, an official-SDK Streamable HTTP MCP server, and optional local/cloud LLM planning. The frontend and backend run from one Python process.

**Release status:** deployable, production-oriented hackathon prototype. Fictional service providers; no real dispatch, payments, Amazon account linking, or claim of commercial production certification. See `docs/VALIDATION.md` for exactly what was tested.

## Start on Windows

Extract into a NEW folder, for example `NEXTSTEP_COMPLETE`. Do not overwrite your previous project or copy its database into this release.

```powershell
cd C:\Users\sharm\OneDrive\Desktop\NEXTSTEP_COMPLETE
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Use the folder containing this README, `app`, and `frontend`; ZIP extraction may add an extra parent folder. Open **http://127.0.0.1:8000**. Do not start the old port-5173 static server. Activation is optional because these commands use the environment's Python directly. Python 3.12 is recommended; source uses Python 3.11+ syntax. Dependencies and runtime were tested on Python 3.12/Linux.

Database and 6 fictional providers are initialized automatically. New slots cover the next 14 days (168 slots on first startup), refreshed hourly and on restart. No API key is required for the labeled rule-based demo. For natural language with a real model, follow `docs/AI_SETUP.md`.

After installation, you can double-click `start.bat`.

## What is implemented

- Full responsive workspace: chat, repair form, comparison cards, confirmation, saved tasks and appointments.
- SQLite-backed task, selection, conversation and audit persistence.
- Browser workspace isolation using hashed opaque session tokens and HttpOnly cookies.
- Current-revision checks; preference changes invalidate previous selections.
- Transactional slot booking with unique constraints and idempotent confirmation retries.
- Dynamic budget, zone, appliance, date and time filtering.
- Resume checks for stale/taken slots.
- One bounded AI planner with schema validation; grounded service responses.
- Ollama native API and configurable OpenAI-compatible chat adapters.
- Explicit deterministic demo mode, never an undisclosed model fallback.
- Six authenticated MCP tools over Streamable HTTP; negotiated protocol 2025-11-25.
- Browser-only final confirmation: model and MCP clients cannot autonomously confirm.
- Optional browser dictation (where supported); transcript reviewed before sending.
- Production configuration gate, origin checks, request-size limits, rate limits, security headers.
- Docker, Compose, CI workflow, backup script, MCP smoke client and automated tests.

## Fast demo

1. Click the sample fan request and submit the form.
2. Select a provider but do not confirm.
3. Save & leave, reload, and resume.
4. Type `under ₹400 tomorrow morning` to change preferences and invalidate the old selection.
5. Select again and explicitly confirm.
6. Open Appointments and show the saved booking reference.
7. Optionally use MCP connection to generate a scoped token, then run the MCP smoke script.

All providers are fictional. Monetary values are INR **visit/inspection fees**, not the final repair cost. Times are Asia/Kolkata.

## Documentation map

| Document | Purpose |
|---|---|
| `docs/QUICKSTART_WINDOWS.md` | Exact setup and integration with your current work |
| `docs/AI_SETUP.md` | Enable Ollama or a compatible cloud endpoint |
| `docs/ARCHITECTURE.md` | How the system works and why these choices were made |
| `docs/API_AND_MCP.md` | API payloads, MCP client integration and security boundary |
| `docs/DEPLOYMENT.md` | Render, Docker, persistent storage and operations |
| `docs/VALIDATION.md` | Test evidence, untested integrations and release limits |
| `docs/PRESENTATION_2_3_MIN.md` | Spoken presentation and demo cues |
| `docs/SUBMISSION.md` | Alexa+ track mapping and submission checklist |
| `docs/FRICTION_LOG.md` | Real development observations and feedback template |

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The lock file includes the tested development dependencies. Tests use temporary databases, never your workspace database. Browser tests are documented separately in the validation report.

## Production deployment boundaries

Use HTTPS, a long ACCESS_CODE and a persistent volume with APP_ENV=production. Run exactly one service replica; move to a managed transactional database before horizontal scaling. This is anonymous browser-workspace access, not a full identity/account system. Clearing cookies or session expiry loses access to that workspace. Provide a dedicated access code to judges and keep the same deployment origin and volume throughout judging.

Read `docs/DEPLOYMENT.md` before deploying. No hosting account was accessed or live deployment performed as part of this handoff.

## License

MIT. External Python dependencies retain their own licenses. No third-party image assets are included.

# Windows setup and integration

## 1. Preserve your earlier work

Keep your existing NEXTSTEP folder. Extract this complete release into NEXTSTEP_COMPLETE (or another new folder). Locate the directory containing README.md, app, frontend and requirements.lock.txt. Open that directory in VS Code.

This release replaces the separate mock UI and partial backend with one connected service. It uses a NEW versioned SQLite schema at `data/nextstep.sqlite3`. Your previous `nextstep.db`, SQLAlchemy models, and old frontend localStorage are not imported. They contain the earlier seed/demo work; providers are recreated here. Do not point DATABASE_PATH at the old database.

SQLite's standard-library driver is used here to make transaction boundaries explicit and simplify the distribution. The complete release supersedes the earlier SQLAlchemy scaffold. No old code needs to be pasted in.

## 2. Create the environment

In PowerShell at the release root:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
```

Python 3.12 is the tested version. If multiple versions are installed, use `py -3.12 -m venv .venv` instead. Using the explicit executable avoids PowerShell activation policy problems. Select `.venv\Scripts\python.exe` as your VS Code Python interpreter.

## 3. Run

Stop the earlier port-8000 server with Ctrl+C if it is running. The old port-5173 static server is no longer needed.

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open http://127.0.0.1:8000 in the same browser each time. Do not mix localhost and 127.0.0.1: browser cookies are tied to the hostname. No separate Node/npm/frontend build is required.

## 4. Validate

Open `/health` and confirm status `ok`. Run the README demo. Stop and restart the server, keeping the database and browser cookies; open the same URL and resume a saved request. Run `python -m pytest -q` through the environment executable.

The first database now has 6 providers and 168 future slots because the booking window is 14 days. Reseeding does not duplicate slots. Old slots remain as booking history.

## 5. Enable the model

Follow AI_SETUP.md, edit only `.env`, then restart the server. The badge will change from Rule-based demo to Local AI or Cloud AI. Provider errors leave the request unchanged and direct you to Edit details. The badge identifies the configured provider, not a guarantee that every model request succeeds.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Module not found | Install with this release's `.venv\Scripts\python.exe`, then run with that executable |
| Port already in use | Stop the old server; keep PUBLIC_ORIGIN and browser URL aligned if changing port |
| Origin not allowed | Open the configured PUBLIC_ORIGIN; stop using the old 5173 UI |
| Login access code appears | Enter ACCESS_CODE from your deployment configuration |
| No options | Use a date in the next 14 days and raise the fee limit; ₹300 is the cheapest fan visit in Central |
| AI unavailable | Check base URL, model name, API key, model JSON support, internet/Ollama server and provider limits |
| Session expired | A new browser workspace is created after access-code entry; old anonymous sessions cannot be recovered through the UI |
| Database locked | Keep one service replica, use a local disk, and avoid syncing an actively written SQLite file through OneDrive |
| Styles seem stale | Ctrl+F5 on the new port-8000 URL |
| Dictation unavailable | Use text input; browser speech support and permissions vary |

For reliable storage, a local folder outside OneDrive is preferable while the application is running. Use the backup script to copy consistent snapshots for safekeeping.

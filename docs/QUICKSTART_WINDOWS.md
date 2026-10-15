# Windows quickstart

Use Python 3.12 and Git. From PowerShell:

```powershell
git clone https://github.com/PRATIK0SHARMA/NextStep.git
cd NextStep
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open http://127.0.0.1:8000. Do not overwrite an existing .env. No activation, Node build, separate frontend server or access code is required. Startup seeds fictional providers. Leave DATABASE_URL blank for SQLite, or configure a private PostgreSQL URL. See [AI setup](AI_SETUP.md) for real model inference; default demo mode requires no API key.

Run tests with `.\.venv\Scripts\python.exe -m pytest -q`. Never set NEXTSTEP_TEST_DATABASE_URL to a real deployment database: PostgreSQL tests reset its schema. Keep .env and database files out of Git.

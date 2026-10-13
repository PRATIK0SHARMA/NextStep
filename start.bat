@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Create the environment first: python -m venv .venv
  echo Then install: .venv\Scripts\python.exe -m pip install -r requirements.lock.txt
  pause
  exit /b 1
)
if not exist ".env" copy ".env.example" ".env" >nul
echo Open http://127.0.0.1:8000 after startup completes.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
pause

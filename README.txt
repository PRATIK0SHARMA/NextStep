NEXTSTEP CONVERSATION FIX

1. Stop the server with Ctrl+C.
2. Back up app/agent.py, then replace it with the included agent.py.
3. Leave .env, database, and frontend unchanged.
4. Restart from the activated project terminal:
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
5. Refresh the browser and start a new request.

Try these messages in order:
I need to fix my refrigerator.
Help me fix it under 500 tomorrow.
Service zone is central side.
It is making noise.
Choose 1st slot and confirm the booking.

When three options are displayed, also test: Choose 3rd slot.
Final confirmation still requires the Confirm booking button.

Changes:
- Full-match routing for simple zone replies and the reported basic repair requests.
- Numeric ordinal selections: 1st, 2nd, 3rd, plus slot/option wording.
- Missing fault details trigger a useful question, not an invented fault.
- Conversational prose is sent as quoted context rather than planner assistant examples.
- One retry for provider json_validate_failed or invalid planner JSON/schema output.
- No retry for arbitrary HTTP 400s; known error codes are displayed safely.
- Credentials, provider messages, and raw generated content are not logged.
- No automatic booking or hidden switch to demo mode after model failures.

Validation: 35 backend tests passed against the available release scaffold,
including mocked cloud/local adapters, reported phrases, retry behavior,
ownership, revision checks, concurrency, and confirmation safeguards.
Live Groq inference and your Windows installation remain to be checked.
An unknown HTTP 400 still requires diagnosis; this patch does not claim
all provider errors are eliminated. Share the displayed status/code if it recurs.

Reference: https://console.groq.com/docs/structured-outputs
JSON-object mode can return errors when the model cannot generate valid JSON.

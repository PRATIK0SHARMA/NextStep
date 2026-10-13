# Validation report — 7 October 2026

## Automated backend checks

Result: **22 passed** on Python 3.12/Linux using the delivered lock file versions. Run `python -m pytest -q` from the project root.

Covered behaviors:

- Idempotent provider/slot seeding.
- Appliance, time, zone and budget-based option filtering.
- Invalid dates, unsupported values, negative and fractional fee validation.
- Persistence after database reinitialization and browser workspace ownership isolation.
- Invalidation of selected appointments when preferences change.
- Atomic booking with a stable result on the same confirmation-key retry.
- Rejection of reused confirmation keys for different tasks.
- Rejection of unselected and unapproved confirmations.
- Rechecking a taken slot on resume.
- Concurrent reservation attempts for the same slot: exactly one succeeds.
- Rule-based conversation and rejection of model-style automatic confirmation.
- Model transport failures and invalid JSON/action plans without booking mutation.
- Mocked request/response contracts for BOTH Ollama and compatible cloud adapters.
- Origin/header checks and body-size rejection.
- Access-code gate and production configuration validation.
- MCP 2025-11-25 initialization, six-tool discovery, actual create_request call, token requirement and revocation.
- Health, static frontend and favicon responses.

Tests are functional evidence for these scenarios, not proof against all attacks or workloads. The two model adapters use mock HTTP transports in tests; this does not measure live model reasoning quality.

## Real HTTP MCP smoke

The official Python MCP client connected to a running Uvicorn process, negotiated **2025-11-25**, discovered these tools, and executed list_requests successfully:

`list_requests, create_request, resume_request, update_request, find_appointments, select_appointment`

No token is included in this report. Repeat using `python -m scripts.mcp_smoke` after generating a token in the UI.

## Browser verification

Headless Chromium automation exercised the connected app at desktop 1440×1000 and mobile 390×844:

- Create request through the form, display options and select.
- Save/leave, reload and resume the saved selection.
- Change preferences through chat and verify stale confirmation disappears.
- Select, confirm, reload and verify the recorded booking.
- Exercise no-matching-options state.
- Check mobile width for horizontal overflow.
- Generate and revoke a scoped MCP token.
- No uncaught page JavaScript errors during this sequence.

Desktop/mobile screenshots are included in `docs/screenshots`. Layouts were visually inspected. Browser checks used rule-based mode. The test runner is `tests/browser.cjs`; optionally install Playwright (`npm install --no-save playwright`, `npx playwright install chromium`) and run `node tests/browser.cjs` against a running local server. Start with a fresh disposable test database so repeated runs do not exhaust the same slots. CHROMIUM_EXECUTABLE can point to an existing test browser.

## Storage and syntax

The backup script copied a running test database using SQLite backup and returned `integrity_check=ok`. Python compilation and JavaScript syntax checks passed. Restore procedure is documented but a hosted disaster-recovery drill has not been performed.

## Not verified during delivery

- Live Ollama inference on the user's laptop or a live paid/cloud model response.
- Real Alexa+ account linking, Echo integration, private SDK access or Amazon certification.
- Browser speech recognition/synthesis on the user's Windows machine (dictation and read-aloud controls are optional).
- Docker image build/run, Render provisioning, production TLS or hosted restart persistence.
- Windows-specific installation behavior (instructions are supplied; runtime testing used Linux).
- Sustained load, independent penetration testing, real provider dispatch or payments.

## Release classification

Deployable production-oriented hackathon prototype, with tested core workflow and deployment safeguards. Not a certified or fully operated commercial service. Controlled access, one replica, persistent disk and fictional data are the supported release scope. See ARCHITECTURE.md and DEPLOYMENT.md for the remaining commercial-launch work.

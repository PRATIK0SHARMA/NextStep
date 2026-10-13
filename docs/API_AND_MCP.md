# API and MCP integration

## Browser API

All JSON API paths start `/api`. Cookies identify the workspace. Mutations require `X-NextStep: 1`; browser requests must come from PUBLIC_ORIGIN. IDs never substitute for authorization: queries also check workspace ownership.

| Method | Path | Body / result |
|---|---|---|
| GET | /health | Liveness + database query |
| GET | /api/config | Mode, timezone, today and access-code requirement |
| POST | /api/session | `{ "access_code": "..." }`; creates or resumes cookie session |
| GET | /api/session | Current session status |
| GET | /api/tasks | All current workspace task snapshots |
| POST | /api/tasks | Optional Details fields; returns new snapshot |
| GET | /api/tasks/{id} | Snapshot including options, selection, messages, booking, audit |
| PATCH | /api/tasks/{id} | `revision` plus explicitly changed Details fields |
| POST | /api/tasks/{id}/resume | Rechecks selection and records resume event |
| GET | /api/tasks/{id}/options | Current matching comparison options |
| POST | /api/tasks/{id}/select | `slot_id`, `revision` |
| POST | /api/tasks/{id}/confirm | `slot_id`, `revision`, `request_id`, `confirmed: true` |
| POST | /api/tasks/{id}/messages | `text`, `revision` |
| POST | /api/mcp-token | New 24-hour token, revoking the previous token |
| DELETE | /api/mcp-token | Revoke the current workspace's MCP token |

Details fields: appliance (fan/refrigerator/washing_machine), zone (north/central/south), preferred_date (YYYY-MM-DD; tomorrow through 14 days), time_preference (any/morning/afternoon), max_visit_fee (integer rupees or null), issue_description (up to 500 characters).

Confirmation keys must be 8–100 ASCII letters/digits/underscores/hyphens. Preserve a key across retries of the exact same slot/revision; create a new key after changing the request. The UI uses sessionStorage for pending confirmation keys, while all authoritative data lives in the database.

Errors: 401 session/token problem; 403 origin/header rejection; 404 nonexistent or other-owner task; 409 stale revision/taken slot/conflicting confirmation; 413 body too large; 422 invalid fields; 429 rate or workspace limits; 503 storage temporarily unavailable. Display errors; do not silently simulate success.

## Connect an MCP client

1. Start NextStep and open the browser UI.
2. Click **MCP connection** and **Generate 24-hour token**.
3. Configure your MCP client for **Streamable HTTP** at `http://127.0.0.1:8000/mcp/` (or your HTTPS deployed origin plus `/mcp/`).
4. Add an `Authorization: Bearer YOUR_TOKEN` header using the client's secure configuration mechanism.
5. Initialize with protocol version `2025-11-25` and discover tools.
6. Do not paste tokens into GitHub, screenshots, prompts, or the demo video.

Client configuration formats vary. The portable contract is endpoint + Streamable HTTP + Authorization header; this release does not assume a particular client supports custom headers or OAuth.

PowerShell smoke test, with the server running in another terminal:

```powershell
$env:NEXTSTEP_MCP_TOKEN = Read-Host 'Paste the scoped token'
$env:NEXTSTEP_MCP_URL = 'http://127.0.0.1:8000/mcp/'
.\.venv\Scripts\python.exe -m scripts.mcp_smoke
Remove-Item Env:NEXTSTEP_MCP_TOKEN
```

This script negotiates the protocol, lists tools and executes `list_requests` using the official MCP client. The entered value is in the process environment until removed; do not run on a shared terminal.

## Tools

| Tool | Purpose |
|---|---|
| list_requests | Read this workspace's requests |
| create_request | Start a request with optional details |
| resume_request | Recheck availability and resume |
| update_request | Change explicit preferences with revision validation |
| find_appointments | Retrieve current task and eligible options |
| select_appointment | Select a slot and return a browser review URL |

There is deliberately **no confirm_booking MCP tool**. The user approves the exact appointment in the authenticated browser. This prevents an external model from asserting its own approval.

## Alexa+ track framing

Submit as a working self-hosted MCP integration demonstrated through your own web experience. The SDK negotiates 2025-11-25 over Streamable HTTP. This is not an installed Alexa+ add-on, certification, private SDK access, or working Echo integration. A custom MCP bearer token does not implement Alexa account linking. The hackathon permits a simulated web experience; check the final rules before submitting.

Sources:
- https://amazonappdev2026.devpost.com/rules
- https://amazonappdev2026.devpost.com/details/faqs
- https://github.com/modelcontextprotocol/python-sdk
- https://modelcontextprotocol.io/specification/2025-11-25/basic/transports

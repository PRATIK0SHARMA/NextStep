# Validation status — submission preparation, 15 October 2026

Evidence is separated by type. This is not a certification or an exhaustive security assessment.

| Area | Evidence and limits |
|---|---|
| Latest public-access patch | 26 local tests passed on SQLite, including public-session behavior, Secure/HttpOnly cookie settings, request limits, ownership isolation and existing booking protections. |
| PostgreSQL | Adapter tests passed locally. GitHub Actions is configured to run the suite against a disposable PostgreSQL service. Verify the submitted commit's Actions result; a PostgreSQL CI pass is not independently asserted here. |
| Earlier backend release | 22 tests passed, including concurrent reservations, idempotency, stale revisions, owner isolation, MCP and mocked model adapters. Later patches added focused tests; historical counts are not cumulative. |
| MCP | Earlier official-client HTTP smoke test negotiated 2025-11-25, discovered six tools and called list_requests. Repeat against the final hosted build before submission. |
| Browser workflows | Earlier desktop/mobile headless checks covered create, save, resume, change, confirm and token revocation. They used demo mode; screenshots are historical. |
| Groq and voice | Developer supplied successful interaction/booking transcripts and reported working speech. Prior model-not-found, HTTP 400 and ordinal parsing failures informed fixes. No quantitative accuracy or latency benchmark is claimed. |
| Hosted app | On 13 October, homepage and /health returned HTTP 200; health reported ok. Developer subsequently reported working public deployment. Health alone does not establish model or complete booking behavior. |
| Data persistence | Database-backed storage is implemented. Record a final hosted restart/resume check before asserting it as independently verified. |

## Final verification

- Check both database CI jobs for the exact submitted commit.
- Run `python -m pytest -q` with a disposable local database configuration.
- Run `python -m scripts.mcp_smoke` against the hosted endpoint with a private scoped token.
- Record real create/change/save/resume/select/confirm actions in the live app.
- Test with a fresh/incognito session and ensure another browser cannot view its requests.
- Check the video duration and public visibility after upload.

No live Echo integration, Amazon account linking, AWS runtime integration, production load benchmark, independent penetration test, commercial dispatch or payment integration is claimed. Do not run PostgreSQL tests against production: they reset the test schema.

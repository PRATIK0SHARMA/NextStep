# Alexa+ track submission preparation

## Suggested title

NextStep — Finish what you started

## Suggested short description

NextStep is a persistent repair-booking assistant that helps users continue unfinished requests, adapt when plans change, and confirm appointments safely. It combines a conversational web experience with a working authenticated Streamable HTTP MCP server. Its core workflows preserve task state, recheck availability, invalidate stale selections, and prevent duplicate bookings.

## Track fit

Primary: Alexa+. The implementation uses the official Python MCP SDK at runtime. The server negotiates protocol 2025-11-25 over Streamable HTTP. The repository includes the server, a client smoke test and the complete simulated web experience. No gated Alexa+ SDK or actual Echo device is required for this submitted path under the reviewed rules.

The web planner uses shared service functions directly; external MCP clients use the same functions through protocol tools. Explain this accurately. This is not Amazon-certified, not a private-preview add-on, and not connected to actual Alexa accounts.

## What to submit

- GitHub repository containing source, assets, lock file, tests, setup and this documentation.
- Public MIT repository, or private repository shared with all required current reviewers.
- Public YouTube/Vimeo demonstration under three minutes, in English.
- Project description identifying implemented capabilities and fictional provider data.
- Product feedback for every tool/API/SDK actually used.
- Testing instructions and deployed access code if using a gated deployment.
- Feature requests and a factual friction log if desired.

Do not publish secrets. If sharing privately, review the current required usernames and invitation acceptance/expiry requirements on the rules page.

## Mini challenges

No AWS Builder eligibility is claimed by this package: no AWS runtime or Kiro Crew usage was performed. You may add a genuine documented integration later. The Open Source mini challenge needs its own qualifying additional contribution; publishing this primary project alone should not be represented as satisfying all of that challenge's requirements.

## Useful demo evidence

1. A persisted request resumes after refresh/server restart.
2. A changed budget/date invalidates the old selection.
3. A booking is confirmed only after explicit review.
4. Tests show duplicate and competing reservation behavior.
5. The MCP smoke client negotiates 2025-11-25, lists six tools and executes a tool.

## Dates from the reviewed rules

Submission deadline: October 23, 2026 at 12:00 Pacific Time (October 24 at 00:30 India Standard Time). Judging: November 9–20, 2026. Recheck the official page before submitting in case the organizer changes requirements.

## Sources

- https://amazonappdev2026.devpost.com/rules
- https://amazonappdev2026.devpost.com/resources
- https://amazonappdev2026.devpost.com/details/faqs

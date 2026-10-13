# NextStep — 2–3 minute presentation

Target: approximately 2 minutes 40 seconds at a natural pace, including short interaction pauses. Rehearse once with a timer. Keep the final video below three minutes. Say “rule-based demo” if you have not enabled and checked a real model.

## Spoken script with screen cues

**0:00–0:25 — Show the workspace**

Hello, we are Team THE MORTAL, and this is NextStep: an assistant that helps people finish everyday tasks, even when life interrupts them.

Booking a repair sounds simple, but it involves several small decisions: finding a provider, checking availability, comparing visit fees, and confirming a time. If someone stops halfway through, they often have to start again.

**0:25–0:55 — Enter a request and display options**

NextStep keeps that progress.

Here, I need a fan repaired in the Central zone tomorrow afternoon, with a visit fee below five hundred rupees. The application checks its provider directory and available slots, then presents matching options. These are fictional providers for the demonstration, but the availability checks and database operations are real.

I will select one appointment, but I will not confirm it yet.

**0:55–1:25 — Save, refresh and resume**

Now I can leave the request and return later. After refreshing and resuming, NextStep restores my requirements and checks availability again. It remembers what I was doing without assuming that an old appointment is still available.

This is the main idea: continuity that helps someone complete a task.

**1:25–1:55 — Change budget/time, select a new option**

Suppose my plans change. I now need a morning visit within four hundred rupees. NextStep updates those requirements and clears the previous selection, so an outdated choice cannot accidentally be booked.

I select a suitable appointment, review the details, and explicitly confirm it. The booking reference appears only after the database transaction succeeds. Repeated confirmation requests do not create duplicate bookings.

**1:55–2:25 — Show MCP tools or briefly show the connection panel**

For the Alexa+ track, we built a working Streamable HTTP MCP server and our own web experience. MCP clients can create, resume, update, and select repair requests using scoped access. Final booking approval stays with the user in the browser.

The conversational layer can use a local Ollama model or a compatible cloud model. A clearly labeled rule-based mode is also available for reproducible testing.

**2:25–2:45 — Show the confirmed appointment**

We tested the core workflow, including changed requirements, competing bookings, retry handling, and workspace isolation.

Our current scope is appliance repair. The same approach could later support other appointment workflows. NextStep's goal is simple: help people return to an unfinished task and confidently take the next step.

Thank you.

## Recording checklist

- Start with a fresh request in a familiar browser workspace.
- Use a date in the next 14 days; say “tomorrow” rather than a fixed past date.
- Prepare your model configuration before recording, or explicitly disclose rule-based mode.
- Show the full MCP tool list with `scripts.mcp_smoke` if time permits. Never display the token or API key.
- Do not claim official Alexa installation, real technician dispatch, deployed customer traction, or measured business impact.
- Show actual interactions. Avoid a presentation consisting only of slides.
- If speaking slowly, shorten the architecture paragraph; keep the resume and changed-plan demonstration.

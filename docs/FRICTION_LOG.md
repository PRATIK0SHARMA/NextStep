# Development friction and tool feedback

These entries describe observed development issues. They are not fabricated product reviews or evidence of tools that were not used.

| Tool/area | Attempt | Expected vs actual | Severity | Resolution / suggestion |
|---|---|---|---|---|
| Python MCP SDK | Import FastMCP after installing unbounded `mcp` | Installed 2.x no longer exposes the v1 FastMCP import | Important | Pinned and tested MCP 1.30.0. Document major-version migration prominently in examples. |
| MCP session manager | Reuse one app instance across test lifespans | SDK manager can run only once per instance | Important | Tests construct fresh imported app/MCP instances. Maintain one lifespan per production process. |
| Earlier static frontend setup | Serve extracted frontend directory | ZIP nesting caused root 404 | Minor | Complete release serves UI and backend from one service; document extraction root explicitly. |
| UI test infrastructure | Download standard Playwright Chromium | Downloads were truncated in the execution environment | Important for validation | Used a bundled Chromium distribution and software-independent headless flags to complete browser checks. This is environment friction, not an Amazon SDK defect. |

## Feedback based on actual usage

- Official MCP Python SDK: runtime tool registration, Streamable HTTP transport, protocol negotiation and client smoke testing. Typed schemas and generated tool metadata reduced implementation work. Major-version import changes and one-shot lifecycle behavior required care. Would use again with pinned versions and protocol tests.
- FastAPI/Pydantic: JSON routes, request validation and static serving. Kept the browser integration small. Deployment-specific origin and cookie configuration still need explicit documentation. Would use again for a bounded Python application.
- SQLite: durable requests and atomic booking transactions on one instance. Simple to distribute; not appropriate for shared multi-replica storage. Would use again for this prototype's scale.
- Ollama and compatible cloud APIs: adapters implemented and request/response contracts tested with mock transports. Live inference was not performed during packaging. Add your actual onboarding, latency, failure, model-quality and cost observations after configuring a provider; do not claim live feedback now.

## Add your real observations

For each new issue record: date, tool/version, task, steps, expected result, actual result, severity, workaround and actionable suggestion. Avoid including tokens, credentials or private conversation text.

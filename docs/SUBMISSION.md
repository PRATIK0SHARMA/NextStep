# Submission checklist — NextStep

Live app: https://nextstep-298t.onrender.com
Repository: https://github.com/PRATIK0SHARMA/NextStep
GitHub username: PRATIK0SHARMA

## Description draft

NextStep is a voice-enabled repair appointment assistant that helps users return to unfinished requests and complete them safely. Users describe a fault, choose preferences, compare fictional providers, save progress and resume later. Changed requirements clear stale selections. A validated planner supports conversation; transactional booking logic checks ownership, availability and revision. Final confirmation is a browser action. PostgreSQL stores the hosted state, while a self-hosted MCP server exposes six scoped request-management tools.

## Track and mini challenges

- Intended primary track: **Alexa+ — self-hosted MCP server**, with an accompanying web experience.
- The rules checked on 15 October 2026 accept a self-hosted MCP server with minimum protocol version 2025-11-25. Repeat the actual client smoke test for the final build.
- No actual Echo connection, Alexa account linking, Amazon-specific SDK or certification is claimed.
- **AWS Builder:** not claimed; no verified qualifying direct integration or Kiro Crew usage.
- **Open Source:** not claimed on the main repository alone. If entering, provide a genuine additional contribution URL, project URL, GitHub username, and explanation of what changed/how it works/why it matters.

## Required submission material

- [ ] Public working GitHub repository with open-source licence and setup instructions.
- [ ] Live app URL and clear testing instructions; this version needs no access code.
- [ ] Public English YouTube/Vimeo video, strictly under three minutes, showing actual function.
- [ ] Product feedback for every directly used tool/API/SDK: purpose, positives, improvements, onboarding, repeat-use decision. Review FRICTION_LOG.md and add omitted tools.
- [ ] Track and mini-challenge selections, with their extra fields if applicable.
- [ ] Accurate new-versus-existing project statement below.
- [ ] Latest GitHub CI checked; hosted flow and MCP smoke checked; no secrets in recording or repository.
- [ ] Video viewed while signed out; final duration checked after upload.

## Project timing — author confirmation required

The official submission window checked on 15 October is 31 August–23 October 2026 (Pacific time). The available development record shows NextStep work in October, but it does not prove whether any code existed before the window.

Before submitting, choose the true statement and replace the prompts with facts:

**If entirely new:** “NextStep was created during the submission window. Development began on [verified date]. We built [verified scope] during that period.”

**If pre-existing:** “Before the submission window, NextStep contained [specific prior functionality]. During the window we added or significantly changed [specific features], implemented in [commits/dates]. The video demonstrates these additions.”

Documented development areas include the connected booking UI/API, persistence/resume, MCP server, planner clarification and ordinal fixes, browser speech, PostgreSQL deployment and public access. Verify their dates and attribution before using them in this answer. Do not submit both alternatives or leave placeholders.

## Video and tool attribution

Use PRESENTATION_2_3_MIN.md. Lead with resume, show voice and changed preferences, then explain the tools. Use original narration and app footage. Do not add third-party music, footage or logos without permission. Naming a tool in plain text does not imply certification or sponsorship.

## Official sources

Rules checked: 15 October 2026. Recheck before submitting; organizer decisions govern eligibility.
- https://amazonappdev2026.devpost.com/rules
- https://amazonappdev2026.devpost.com/details/faqs

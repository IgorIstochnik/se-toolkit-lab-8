# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

**"What is the agentic loop?"**
The agentic loop refers to the continuous cycle of perception, reasoning, and action... (paste full response)

**"What labs are available in our LMS?"**
I don't have access to your specific Learning Management System (LMS)... (paste full response)

## Task 1B — Agent with LMS tools

**"What labs are available?"**
Here are the available labs: Lab 01 – Products, Architecture & Roles, Lab 02 — Run, Fix, and Deploy... (paste full response)

**"Is the LMS backend healthy?"**
Yes, the LMS backend is healthy. The system is currently showing 56 items in the database... (paste full response)

## Task 1C — Skill prompt

**"Show me the scores"**
I can see several labs available in the system. Could you please specify which lab you'd like to see the scores for?... (paste full response)

## Task 2A — Deployed agent

Nanobot runs as Docker Compose service via `nanobot gateway`.
Startup log excerpt:
- Using config: /app/nanobot/config.resolved.json
- Channels enabled: webchat
- MCP server 'lms': connected, 9 tools registered
- MCP server 'mcp_webchat': connected, 1 tools registered
- Agent loop started

## Task 2B — Web client

WebSocket test: `echo '{"content":"What labs are available?"}' | websocat "ws://localhost:42002/ws/chat?access_key=..."` returns real lab names.

Flutter client at `/flutter` — login works, agent answers questions with real backend data. "Show me the scores" prompts for lab selection.

## Task 3A — Structured logging

Happy-path log excerpt:
backend-1 | … request_started … auth_success … db_query … request_completed


Error-path log excerpt (postgres stopped):
backend-1 | … ERROR … db_query … items_list_failed_as_not_found


VictoriaLogs query `_time:10m severity:ERROR OR severity:WARNING` returns matching error entries.

## Task 3B — Traces

Healthy trace shows: `connect` → `SELECT db-lab-8` → `GET /items/` → `BEGIN;` → `ROLLBACK;`
Error trace shows: `connect` → `GET /items/` (with failure in db_query span).

## Task 3C — Observability MCP tools

Normal conditions: "No errors found in the LMS backend over the last 10 minutes. Everything looks clean."

After stopping postgres and triggering a request: "There's 1 error in the LMS backend over the last 10 minutes. Let me grab the details."

## Task 4A — Multi-step investigation

Agent response to "What went wrong?" (postgres stopped):
- Found 3 errors in the last 10 minutes
- Root cause: Database hostname DNS resolution failure
- Evidence: socket.gaierror: [Errno -2] Name or service not known
- Trace analysis: GET /items/ failed during database connection phase
- Impact: All database queries fail, LMS returns HTTP 404

## Task 4B — Proactive health check

Cron job a85c44b6 created (every 2 minutes).
Proactive report: "**1 error** found in the last 2 minutes for the Learning Management Service." with details about the database connection failure.

## Task 4C — Bug fix and recovery

**Root cause:** In `backend/src/lms_backend/routers/items.py`, the `get_items()` endpoint caught all exceptions with `except Exception` and returned `HTTP 404 "Items not found"`, masking the real database connection error.

**Fix:** Changed the exception handler to return `HTTP 500` with the actual error message: `f"Internal server error: {exc}"`, and changed log level from `warning` to `error`.

**Post-fix failure check:** After fix, agent reports "GET /items/ returning HTTP 500" with root cause "Database DNS Resolution Failure" — the real error is now visible instead of the misleading 404.

**Healthy follow-up:** After restarting postgres, cron health check reports: "✅ System looks healthy — no errors in the last 2 minutes."

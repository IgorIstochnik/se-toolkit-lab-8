---
name: observability
description: Use observability MCP tools to investigate system health
always: true
---

# Observability Skill

You have tools to investigate logs and traces. Use them to diagnose failures.

## Investigation strategy

When the user asks "What went wrong?", "Check system health", or "Diagnose the problem":

1. Call `logs_error_count` with service "Learning Management Service" and minutes=10
2. If errors exist, call `logs_search` with query `_time:10m service.name:"Learning Management Service" severity:ERROR`
3. Look for a `trace_id` or `otelTraceID` field in the error logs
4. Call `traces_get` with that trace_id to inspect the failing request path
5. Write a coherent investigation that:
   - Names the affected service
   - Cites specific log evidence (error messages, status codes)
   - Cites trace evidence (which span failed, how long it took)
   - Identifies the root failing operation
   - Does NOT dump raw JSON

## Proactive monitoring

When the user asks about recent errors or system status:
- Call `logs_error_count` first with a narrow window (10 minutes)
- If no errors, report the system is healthy
- If errors exist, investigate further with `logs_search` and `traces_get`

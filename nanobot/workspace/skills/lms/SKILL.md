---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to LMS MCP tools for querying live course data. Use them strategically.

## Available tools

- `lms_health` — check if the LMS backend is healthy, returns item count and error status
- `lms_labs` — list all available labs with their IDs and titles
- `lms_pass_rates` — get pass rates for a specific lab (requires `lab` parameter)
- `lms_scores` — get scores for a specific lab
- `lms_learners` — get learner information
- `lms_timeline` — get submission timeline for a lab
- `lms_groups` — get group performance data
- `lms_top_learners` — get top learners for a lab
- `lms_completion_rate` — get completion rate for a lab
- `lms_sync_pipeline` — trigger the LMS data sync pipeline

## Strategy

- If the user asks for scores, pass rates, completion, groups, timeline, or top learners **without naming a lab**, call `lms_labs` first to get available labs
- If multiple labs are available, ask the user to choose one, or present a summary across all labs
- Use each lab title as the default user-facing label unless the tool output gives a better identifier
- When a lab parameter is needed and not provided, ask the user which lab they want
- Format numeric results nicely — show percentages with one decimal place, counts with commas
- Keep responses concise — lead with the answer, then provide details if needed
- When the user asks "what can you do?", explain your current LMS tools and limits clearly
- If the LMS is unhealthy, report the error and suggest triggering a sync

## Response format

- Lead with the direct answer
- Use bullet points or tables for multi-item results
- Include relevant percentages and counts
- Note when data is unavailable

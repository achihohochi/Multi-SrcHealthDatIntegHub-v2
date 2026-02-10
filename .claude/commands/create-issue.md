# Create Issue

User is mid-development and thought of a bug/feature/improvement. Capture it fast so they can keep working.

## Your Goal

Create a complete Jira issue with:
- Clear title
- TL;DR of what this is about
- Current state vs expected outcome
- Relevant files that need touching
- Risk/notes if applicable
- Proper type/priority/effort labels

## How to Get There

**Ask questions** to fill gaps - be concise, respect the user's time. They're mid-flow and want to capture this quickly. Usually need:
- What's the issue/feature
- Current behavior vs desired behavior
- Type (bug/feature/improvement) and priority if not obvious

Keep questions brief. One message with 2-3 targeted questions beats multiple back-and-forths.

**Search for context** only when helpful:
- Web search for best practices if it's a complex feature
- Grep codebase to find relevant files
- Note any risks or dependencies you spot

**Skip what's obvious** - If it's a straightforward bug, don't search web. If type/priority is clear from description, don't ask.

**Create the issue in Jira via API** using the credentials from .env:

Project Details:
- Project Key: PLUSH
- Issue Type IDs: Task (10134), Epic (10135), Subtask (10136)
- Site: https://aichihohochi.atlassian.net

Issue Format:
- Title: Clear, concise
- Description (ADF format):
  - TL;DR (1 line)
  - Current State (what's happening now)
  - Expected Outcome (what should happen)
  - Context (files/best practices/risks/notes)

API Endpoint:
```bash
curl -X POST "https://aichihohochi.atlassian.net/rest/api/3/issue" \
  -H "Content-Type: application/json" \
  -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
  -d '{"fields": {"project": {"key": "PLUSH"}, "summary": "...", "description": {...}, "issuetype": {"id": "10134"}}}'
```


**Keep it fast** - Total exchange under 2min. Be conversational but brief. Get what you need, create ticket, done.

## Behavior Rules

- Be conversational - ask what makes sense, not a checklist
- Default priority: normal, effort: medium (ask only if unclear)
- Max 3 files in context - most relevant only
- Bullet points over paragraphs

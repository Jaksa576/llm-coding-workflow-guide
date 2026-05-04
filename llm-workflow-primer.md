# LLM Coding Workflow Primer

Use this compact primer as reference material inside each ChatGPT Project. Keep the full HTML guide as the day-to-day operating manual.

## Core workflow

Use ChatGPT for planning, roadmap decisions, QA triage, and coding-agent handoffs. Use Codex or another coding agent for repo-based implementation. The user remains the product owner and approves direction, QA, and merge decisions.

The repository is the durable memory. Chat history is temporary.

## Default environment

Assume a Windows-native workflow with PowerShell unless the user explicitly says otherwise. Do not assume WSL. Use Windows paths such as `C:\Code\ProjectName` when examples are needed.

## Source-of-truth docs

When current state matters, inspect or ask for the latest versions of:

- `AGENTS.md`
- `docs/product.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/current-task.md`
- active `docs/campaigns/*.md` files when relevant

Do not rely on memory or prior chat assumptions when repo state matters. If docs conflict, call out the conflict before recommending next steps.

## Implementation loop

Use the same loop for most work:

1. Refresh current state.
2. Plan a campaign, slice, or patch.
3. Generate a lean Codex handoff.
4. Codex implements, validates, updates docs, commits, and reports back.
5. The user QA reviews the preview/local result.
6. Merge, patch, revise the campaign, or stop.

Use a campaign for a large swath of related work. Use a slice for one independently reviewable unit of implementation. Use a patch for a narrow correction.

## Codex handoff expectations

Codex handoffs should include:

- goal
- source-of-truth docs to inspect
- readiness gate
- scope
- non-goals
- files likely to change
- acceptance criteria
- validation expectations
- documentation expectations
- stop conditions
- final reporting expectations

Do not restate all project context when the repo docs already contain it. Keep handoffs copy-paste ready.

## Documentation freshness

Codex owns documentation freshness during implementation. Every implementation should update `docs/current-task.md`. Update campaign docs when slice status changes. Update architecture or roadmap docs only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

Every Codex final report should include a documentation delta and a compact state packet.

The state packet is not a source of truth. It is a transition note that helps the next ChatGPT session orient quickly. Repo docs remain authoritative.

## ChatGPT behavior

Start with the recommendation. Focus on what the user should do next. Prefer reviewable slices. Push back on unclear scope, overengineering, generic product drift, stale docs, and unnecessary AI dependencies.

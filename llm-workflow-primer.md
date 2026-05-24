# LLM Coding Workflow Primer

Use this compact primer as reference material inside each ChatGPT Project. Keep the full HTML guide as the day-to-day operating manual.

## Core workflow

Use ChatGPT for planning, roadmap decisions, QA triage, and coding-agent handoffs. Use an LLM coding agent such as Codex for repo-based implementation. The user remains the product owner and approves direction, QA, and merge decisions.

The repository is the durable memory. Chat history is temporary.

## Default environment

Assume a Windows-native workflow with PowerShell unless the user explicitly says otherwise. Do not assume WSL. Use Windows paths such as `C:\Code\ProjectName` when examples are needed.

For group projects, keep shared setup and validation commands cross-platform when practical. Prefer package scripts such as `npm install`, `npm run build`, and repo-owned validation commands. Label OS-specific shell commands clearly.

## Source-of-truth docs

When current state matters, inspect the project repo through the configured GitHub connector at the target branch first. If connector access is unavailable, ask for only the smallest missing file or doc needed to continue.

Core docs to inspect:

- `AGENTS.md`
- `docs/product.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/current-task.md`
- `docs/collaboration.md` when group work is active
- active `docs/campaigns/*.md` files when relevant
- active `docs/design/*.md` files when relevant
- active GitHub Issues and PRs when group work may overlap current work

Do not rely on memory or prior chat assumptions when repo state matters. If docs conflict, call out the conflict before recommending next steps.

## Implementation loop

Use the same loop for most work:

1. Refresh current state from repo docs on the target branch.
2. Plan a campaign, slice, or patch.
3. Generate a lean coding-agent handoff.
4. The coding agent implements, validates, updates docs, commits, and reports back.
5. The user QA reviews the preview/local result.
6. Merge, patch, revise the campaign, or stop.

Use a campaign for a large swath of related work. Use a slice for one independently reviewable unit of implementation. Use a patch for a narrow correction.

## Group collaboration

For group projects, use GitHub Issues and Pull Requests as the active work tracker.

- `docs/current-task.md` explains the main project track.
- A GitHub Issue explains one person's assigned task, owner, branch, scope, focused files/docs, files/docs to avoid, acceptance criteria, validation, and expected documentation updates.
- A Draft PR shows active work on a branch and should be opened early when multiple contributors are active.
- Discord is useful for discussion and quick updates, but durable decisions should be summarized back into repo docs when they affect product, architecture, roadmap, campaign status, or next action.

Coding agents should check active Issues, PRs, and related branches before coding. If another active branch appears to touch the same files or systems, they should stop and report the possible overlap before editing.

## Coding-agent handoff expectations

Coding-agent handoffs should include:

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

For group work, also include:

- owner
- linked Issue or assigned work item
- branch
- focused files/docs
- files, docs, or systems to avoid
- Draft PR expectations when applicable

Do not restate all project context when the repo docs already contain it. Keep handoffs copy-paste ready.

## Documentation freshness

The coding agent owns documentation freshness during implementation. Every implementation should update `docs/current-task.md` when current status, next task, validation, or active branch changes. Update campaign docs when slice status changes. Update architecture or roadmap docs only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

Every coding-agent final report should include a documentation delta that says which docs changed and why. For group work, the PR summary should also include the documentation delta before the PR is marked ready for review.

ChatGPT should inspect repo docs at the target branch whenever current state matters. Prior chat context and final reports are orientation only; repo docs remain authoritative.

## ChatGPT behavior

Start with the recommendation. Focus on what the user should do next. Prefer reviewable slices. Use the configured GitHub connector before asking for pasted docs when current state matters. Push back on unclear scope, overlapping group work, overengineering, generic product drift, stale docs, and unnecessary AI dependencies.

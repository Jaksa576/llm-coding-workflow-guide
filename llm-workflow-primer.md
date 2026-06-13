# LLM Coding Workflow Primer

Use this compact primer as reference material inside each ChatGPT Project. Keep the full HTML guide as the day-to-day operating manual.

## Core workflow

Use ChatGPT for planning, QA triage, and coding-agent handoffs. Use Codex or another agent for repo implementation. This two-context split is most valuable when planning and coding have different token costs, context limits, latency, or ergonomics. The user owns direction, QA, and merge decisions.

The repository is the durable memory. Chat history is temporary.

## Default environment

Assume a Windows-native workflow with PowerShell unless the user explicitly says otherwise. Do not assume WSL. Use Windows paths such as `C:\Code\ProjectName` when examples are needed.

For group or cross-platform projects, keep shared setup and validation commands cross-platform when practical. Prefer package scripts such as `npm install`, `npm run build`, and repo-owned validation commands. Label OS-specific shell commands clearly.

## Source-of-truth docs

When current state matters, inspect the project repo through the configured GitHub connector at the target branch first. If connector access is unavailable, ask for only the smallest missing file or doc needed to continue.

Core docs to inspect:

- `AGENTS.md`
- `docs/product.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/current-task.md`
- `docs/collaboration.md` when group work is active
- active `docs/design/*.md` files when a specific design decision is relevant
- active GitHub Issues and PRs when planning, implementing, reviewing, checking overlap, or resuming work

Do not rely on memory or prior chat assumptions when repo state matters. If docs, Issues, or PRs conflict, call out the conflict before recommending next steps.

## Implementation loop

Use the same loop for most work:

1. Refresh current state from repo docs, active Issues, and active PRs when relevant.
2. Plan or refine the next Issue, reviewable slice, or patch.
3. Generate a lean coding-agent handoff.
4. The coding agent implements, validates, updates docs, Issues, and PRs, commits, and reports back.
5. The user QA reviews the preview/local result.
6. Merge, patch, revise the Issue, split follow-up Issues, or stop.

Use GitHub Issues for durable backlog items, implementation-ready work, active work contracts, and follow-ups. Use slices for independently reviewable implementation units inside an Issue or standalone effort. Use patches for narrow corrections.

## Issue-first backlog and PR tracking

Issues are the default durable tracking layer for future implementation work. PRs are the active branch and review record for implementing an Issue or patch.

Keep roles distinct:

- Roadmap: strategic sequence, milestones, and broader deferred themes.
- `docs/current-task.md`: short current project pointer, including active Issue/PR when useful.
- Issue: specific backlog item, implementation contract, or follow-up with owner, scope, done-when, validation, and expected docs updates.
- Draft PR: active branch and review record with summary, validation, documentation delta, risks, and manual QA notes.
- Discord/chat: discussion, not durable truth.

For group work, Issues and Draft PRs are required. Each meaningful item needs an owner, branch, scope, focused files/docs, files/docs to avoid, validation, and done-when criteria. Add `docs/collaboration.md` during setup or before the first group work item. Solo long-running branches are recommended.

Coding agents should check active Issues, PRs, and related branches before coding when work may overlap another branch. If another active branch appears to touch the same files or systems, they should stop and report the possible overlap before editing.

## Coding-agent handoff expectations

Coding-agent handoffs should include: goal, linked Issue or work item when available, source-of-truth docs to inspect, readiness gate, scope, non-goals, files likely to change, acceptance criteria, validation expectations, documentation expectations, stop conditions, and final reporting expectations.

When Issue/PR tracking is in use, also include owner, linked Issue or assigned work item, branch, focused files/docs, files or systems to avoid, and Draft PR expectations when applicable.

Do not restate all project context when the repo docs and linked Issue already contain it. Keep handoffs copy-paste ready.

## Documentation freshness

The coding agent owns documentation freshness during implementation. Every implementation should update `docs/current-task.md` when current status, next task, validation, active Issue/PR, or active branch changes. Update linked Issues/PRs when status, scope, validation, docs delta, or follow-ups change. Update architecture or roadmap docs only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

Every coding-agent final report should include a documentation delta that says which docs, Issues, or PRs changed and why. When Issue/PR tracking is in use, the PR summary should include the documentation delta before the PR is marked ready for review.

ChatGPT should inspect repo docs at the target branch whenever current state matters. Prior chat context and final reports are orientation only; repo docs, Issues, and PRs remain authoritative.

## ChatGPT behavior

Start with the recommendation. Focus on what the user should do next. Prefer reviewable slices. Use the configured GitHub connector before asking for pasted docs when current state matters. Push back on unclear scope, overlapping branch work, overengineering, generic product drift, stale docs, and unnecessary AI dependencies.

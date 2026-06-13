# LLM Coding Workflow Guide

Use this guide to build software with a planning LLM plus a repo-based coding agent.

In five seconds:

1. ChatGPT helps plan the work.
2. The GitHub repo and repo docs are the source of truth.
3. The coding agent implements one clear slice at a time.
4. The user reviews, QA checks, and decides whether to merge, patch, revise, or stop.
5. The loop repeats through GitHub Issues, reviewable slices, patches, PRs, and docs updates.

![LLM Coding Workflow](llm_coding_workflow_diagram.png)

## What this guide is for

This workflow is for hobbyist and solo builders who want real software projects without losing control to the coding agent. It also scales to small group repos by adding Issues, Draft PRs, branch ownership, overlap checks, and clear review points.

The default setup is **ChatGPT for planning** and **Codex or another LLM coding agent for implementation**. Windows-native PowerShell examples are used unless a project says otherwise.

This workflow is especially valuable when ChatGPT planning and coding-agent execution have different token costs, context limits, latency, or ergonomics. It keeps exploratory planning in ChatGPT and sends the coding agent only the task-specific context it needs. If you use a tool where planning and implementation share the same context and token economics, such as an all-in-one coding environment, the workflow can still help with source-of-truth docs, reviewable slices, QA, and documentation freshness, but the token-efficiency advantage may be smaller.

The goal is not to create perfect prompts. The goal is to create a repeatable system where projects use the same source-of-truth docs, reviewable implementation loop, validation expectations, documentation deltas, and QA decision points.

## Why the split works

Keep planning context and execution context separate. ChatGPT carries product thinking, roadmap decisions, QA triage, and handoff generation. The coding agent receives only the current task, source-of-truth docs, acceptance criteria, validation expectations, and documentation delta.

That separation keeps handoffs lean, reduces stale context, and makes projects easier to resume across chats, branches, devices, and collaborators. It is also a token-routing strategy: do broad, messy planning where it is cheapest and most useful, then send the coding agent a narrow execution packet.

If your planning LLM and coding agent have similar costs and context behavior, you can streamline some planning steps for small tasks. Do not collapse source-of-truth docs, acceptance criteria, validation expectations, documentation delta, or the final report loop unless the project is truly disposable.

## Workflow at a glance

1. Create the GitHub repo and local Windows workspace.
2. Create the ChatGPT Project and add the compact workflow primer.
3. Configure GitHub source-of-truth access and the local coding-agent project.
4. Define the project, generate app-specific instructions, and create core repo docs.
5. Add `docs/collaboration.md` if this is a group repo or overlapping branch work is likely.
6. Bootstrap the project with a coding-agent handoff.
7. Repeat the main loop: plan or refine a GitHub Issue -> generate handoff -> implement -> validate -> update docs/Issue/PR -> final report -> QA -> merge, patch, revise, split follow-ups, or stop.
8. Close or update the Issue/PR, clean stale context from the hot path, and start a new chat for the next Issue or phase when useful.

Most time is spent in the implementation loop, not setup.

## Stage 0 - Create the repo and local workspace

Create a GitHub repository for the project. Use `main` as the default branch. Choose public or private based on the project. Add a basic `.gitignore` if you already know the stack; otherwise Codex can add one during bootstrap.

Clone the repo to your Windows machine. Record the project name, GitHub repo URL, local repo path, target branch, and whether the repo is public or private.

Do not commit secrets. Environment variable values belong in `.env.local` or platform settings, not docs.

```powershell
Set-Location C:\Code
git clone {{Paste the GitHub repo URL}}
Set-Location C:\Code\{{What is the local repo folder name?}}
git status
```


## Stage 1 - Create the ChatGPT Project

Create a ChatGPT Project for the software project before deep planning.

Use the full HTML guide as your operating manual, not as the default project source. The ChatGPT Project should receive only lightweight reusable workflow context plus app-specific instructions.

Add a starter instruction block. Later, replace or refine it with the project-specific instructions generated in Stage 4.

```md
You are my planning partner for LLM-assisted software development.

Use the attached compact workflow primer as the generic workflow reference. Do not restate the primer unless needed.

I use ChatGPT for planning and Codex or another coding agent for implementation. The GitHub repository and repo docs are the source of truth. I remain the product owner and approve direction.

Default environment: Windows-native workflow with PowerShell. Do not assume WSL unless I explicitly request it.

When current repo state matters, inspect the project repo through the configured GitHub connector at the target branch first. If connector access is unavailable, ask me to provide only the smallest specific missing file or input. Do not rely on memory or prior chat assumptions.

For group repos, require Issues and Draft PRs for meaningful work, confirm branch ownership before implementation, and stop before editing if active work appears to overlap another branch.

Prefer step-by-step guidance, lean Codex handoffs, reviewable slices, clear stop conditions, documentation delta requirements, and clear final reports from coding agents.
```

## Stage 1A - Add the compact workflow primer

Add the compact workflow primer to each ChatGPT Project as a source file. Do **not** add the full HTML guide unless you specifically want it available for reference.

Why this split exists:

- **HTML guide:** your day-to-day operating manual and prompt console.
- **Workflow primer:** lightweight reusable workflow context for ChatGPT Projects.
- **Project Instructions:** app-specific rules, source-of-truth routing, and output style.
- **Repo docs:** actual product, architecture, roadmap, and current-state truth.

This keeps ChatGPT aware of the workflow without turning every Project Instruction block into a large generic manual.

Use the primer file included in the bundle: `llm-workflow-primer.md`.

## Stage 1B - Configure GitHub source-of-truth access

After adding the primer, connect or confirm access to the project's GitHub repo if your ChatGPT environment supports it. The connector is not the source of truth by itself; it is the access path to the repo docs.

Record the default target branch in the Project Instructions or in your first source-of-truth check. After the project is connected to GitHub, normal prompts should clarify branch context only when needed. When current state matters, ChatGPT should inspect repo docs at the target branch before asking you to paste docs.

If connector access is unavailable, expired, or missing a file, fall back to the smallest manual paste or upload needed. Do not paste secrets or environment variable values.

```md
Confirm GitHub source-of-truth access for this project.


Target branch for source-of-truth checks:
{{target branch:}}

Please verify whether you can inspect these files from the configured GitHub repo at the target branch:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant

Rules:
- Inspect the target branch before using prior chat state.
- Treat repo docs as authoritative.
- If you cannot access a needed file, ask me for only that file.
- If the branch is unmerged, do not assume main includes its changes.
- If docs conflict, stop and call out the conflict before recommending next steps.
```

## Stage 2 - Configure Codex before handoffs

Configure Codex before any Codex handoff is created. Point Codex at the local repo path. Confirm it can see the repo, the branch is correct, Git status is clean or intentionally empty, and worktree/local environment settings are configured.

Keep worktree setup in Codex project settings or helper scripts, not in every handoff prompt.

As a project matures, move repeated setup, validation, and branch-verification commands into repo-owned scripts or package commands. Handoffs should reference those helpers instead of re-teaching the LLM agent the same command sequence.
## Stage 2A - Optional Codex worktrees

Codex worktrees are optional. Use them when you want isolated implementation branches, parallel slices, or safer experimentation without disturbing your main local checkout.

Keep repeatable setup and cleanup logic in repo helper scripts or Codex project settings, not in every handoff prompt. A handoff should mention worktree setup only when the task depends on it.

If a worktree uses a local branch, the work is not complete until the branch is committed, pushed to the remote repo, and verified as pushed. Prefer a repo-owned branch verification script, such as `.\scripts\verify-branch-pushed.ps1`, when the project provides one.

If you use worktrees, see **Optional Codex worktrees** in the reference material for setup and cleanup templates.

## Stage 3 - Define the project

Paste this into the ChatGPT Project. Fill in the double-brace prompts with your project idea, constraints, and local path.

```md
Help me define a new software project for an LLM-assisted coding workflow.

Project idea:
{{project idea in plain language}}

Why I want it:
{{why  you want to build this}}

Primary user:
{{who is the primary user}}

First useful version must do:
{{what must the first useful version do}}

Known constraints:
{{important constraints, assumptions, or preferences, or write "none"}}

Local repo path:
{{local repo path}}

Default environment:
Windows-native workflow with PowerShell. Do not assume WSL.

Please produce:
1. concise product brief
2. smallest sensible MVP
3. explicit non-goals
4. recommended project type
5. smallest sensible technical approach
6. likely risks and simplifications
7. whether this should proceed to repo-doc setup
8. any clarifying questions that truly block progress
```


## Stage 4 - Generate project-specific ChatGPT instructions

Use this after the project direction is clear. Copy the generated instructions into the ChatGPT Project Instructions field.

The generated instructions should be short and app-specific. They should reference the compact workflow primer instead of duplicating it.

```md
Create concise ChatGPT Project Instructions for this software project.

Project name:
{{project name}}

Local repo path:
{{local repo path (e.g. C:\Code\Project\)}}

Approved product brief:
{{approved project summary}}

Attached workflow reference:
The ChatGPT Project will include the compact LLM workflow primer as a source file. The Project Instructions should reference the primer for generic workflow rules instead of duplicating it.

Instructions architecture:
- Project Instructions should be app-specific and concise.
- The workflow primer covers Issue/slice/patch workflow, documentation freshness, documentation deltas, current-state refresh behavior, and prompt-manager placeholder style.
- Repo docs are the source of truth for product, architecture, roadmap, and current task. When connector access is available, inspect repo docs at the target branch before asking for pasted docs.

Environment:
- Default to Windows-native workflow.
- Use PowerShell command examples when needed.
- Do not assume WSL unless explicitly requested.

The instructions should include only:
1. role for this specific project
2. reference to the attached workflow primer
3. project-specific source-of-truth docs
4. current-state behavior
5. Windows/PowerShell assumption
6. concise Codex handoff style
7. project-specific guardrails and pushback rules
8. output style

Codex handoff rule:
Do not require a standard project/repository/header block by default. Codex should already have the project, repo, environment, and worktree settings configured. Include target branch, repo, or environment details only when the task needs them or when they are not obvious.

If the repo provides standard commands in `AGENTS.md`, package scripts, or `scripts/`, generated handoffs should reference those helpers instead of restating common setup and validation steps. Prefer repo-owned validation and branch-push verification commands, such as `npm run check`, `.\scripts\validate.ps1`, or `.\scripts\verify-branch-pushed.ps1`, when present.

Keep the instruction block concise and purposeful. Avoid restating the full workflow primer or duplicating repo docs.
```

## Stage 5 - Generate the core repo docs

Generate the docs that both ChatGPT and Codex will use as source of truth. These docs should be concise, not historical.

```md
Create the initial source-of-truth repo docs for this project.

Project name:
{{project name}}

Local repo path:
{{local repo path (e.g. C:\Code\Project\)}}

Approved product brief:
{{approved project summary}}

Approved MVP:
{{approved MVP outline}}

Approved technical approach:
{{approved technical approach}}

Environment assumptions:
- Windows-native workflow
- PowerShell for local commands
- ChatGPT for planning
- Codex or equivalent coding agent for implementation
- GitHub and repo docs are the durable source of truth

Please draft these core files:
1. AGENTS.md
2. docs/product.md
3. docs/architecture.md
4. docs/roadmap.md
5. docs/current-task.md

If this will be a group repo, continue to **Stage 5A - Add group collaboration docs when needed** before committing the docs.

Requirements:
- Keep each file concise and useful for LLM-assisted development.
- Do not include long historical narrative.
- Make docs/current-task.md point clearly to the next implementation action.
- Clearly mark anything that is planned but not implemented yet.
- Include Windows/PowerShell assumptions where relevant, but do not over-repeat them.
- Include the expectation that Codex updates docs/current-task.md after every implementation.
- For projects using worktrees, include that branch work must be pushed to the remote repo before final report.
- If the repo has standard setup, validation, or branch-verification scripts, document them in `AGENTS.md` instead of repeating those commands in every handoff.
- For group repos, keep collaboration rules in `docs/collaboration.md` instead of burying them in chat history.

Output each file in a separate fenced markdown block with the file path as the heading.
```


## Stage 5A - Add group collaboration docs when needed

Skip this stage for a solo repo unless you expect another person, coding agent, or long-running branch to overlap your work. Use it when the project is a group repo, when you are inviting collaborators, or when multiple active branches need coordination rules.

`docs/collaboration.md` should stay short. It is not a social contract or full team handbook. It is the repo-level operating rule for ownership, branch hygiene, Issues, Draft PRs, review expectations, and overlap checks.

```md
Create a concise group collaboration doc for this repo.

Project name:
{{project name}}

Repo context:
{{short description of who may collaborate and how, or write "small group repo"}}

Default branch:
main

Expected work style:
- ChatGPT for planning and QA triage
- Codex or another coding agent for implementation
- GitHub Issues for active work contracts
- Draft PRs for active branches and review records
- Repo docs as the source of truth

Please draft `docs/collaboration.md` with these sections:
1. collaboration purpose
2. roles and ownership
3. branch rules
4. Issue rules
5. Draft PR rules
6. overlap-check rules before coding
7. review and QA expectations
8. where durable decisions belong
9. what not to put in chat only

Rules:
- Keep it concise and practical.
- Require an owner, branch, scope, focused files/docs, files/docs to avoid, validation expectations, and done-when criteria for each meaningful group work item.
- Require coding agents to check active Issues, PRs, and related remote branches before editing.
- Require the agent to stop and report if another active branch may touch the same files or systems.
- Clarify that Discord/chat is for discussion, not durable project truth.
- Do not duplicate product, architecture, roadmap, or current-task content.
```

After creating the file, commit it with the other source-of-truth docs or as a small follow-up docs commit.

## Stage 6 - Add the core docs to the repo

The easiest path is manual: create the files locally in the repo folder, paste in the generated contents, then commit and push. This avoids a Codex handoff before the docs exist.

Create these files:

- `AGENTS.md`
- `docs/product.md`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/current-task.md`
- `docs/collaboration.md` only when group work is active

Then run:

```powershell
git status
git add AGENTS.md docs/product.md docs/architecture.md docs/roadmap.md docs/current-task.md
# For group repos, also include:
git add docs/collaboration.md
git commit -m "Add initial project source-of-truth docs"
git push origin main
```


## Stage 7 - Bootstrap the project

Bootstrap creates the first working shell, validation path, and optional first deploy/run. It does not build the full MVP unless the project is tiny. Use ChatGPT to generate the Codex handoff, then paste the result into Codex.

```md
Before creating the handoff, inspect repo docs at the target branch through the configured GitHub connector if available. If connector access is unavailable, ask for only the smallest missing doc.

Create a lean Codex-ready bootstrap handoff.

Project name:
{{project name}}

Target branch:
main

Source-of-truth docs now in repo:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md, if group work is active

Bootstrap goal:
Create the initial working project shell, first validation path, and any minimal deploy/run setup appropriate for the project. Do not build the full MVP unless the repo docs explicitly say the project is tiny enough for that.

The Codex handoff must include:
- goal
- docs to inspect first
- readiness gate
- scope
- non-goals
- files likely to change
- acceptance criteria
- validation expectations
- documentation delta expectations
- final reporting expectations

Keep the handoff copy-paste ready.
Do not include command-by-command worktree setup unless it is required for this specific task.
If the repo docs already define standard commands, the handoff should refer to them instead of listing the whole command sequence. If worktrees are used, require the branch to be pushed before final report.
```


## Stage 8 - Review bootstrap


```md
Review this completed bootstrap and help me decide the next step.

Branch:
{{target branch}}

LLM agent final report:
{{LLM agent final report}}

Manual observations:
{{Add any manual observations, or write "none"}}

Please do the following:
1. assess whether the bootstrap is complete enough to proceed
2. identify blocking setup issues
3. list what I should manually QA now
4. recommend whether to merge, patch, or hold
5. if ready, recommend the first implementation Issue or standalone slice
6. if ready, summarize what the next work item should accomplish

```


# Main implementation loop

Start a new ChatGPT chat at the beginning of a major phase, a new implementation-ready Issue, or whenever context feels stale. Ask ChatGPT to inspect repo docs, active Issues, and active PRs at the target branch when current state matters.

## Loop Step A - Ground a new ChatGPT chat in the repo

Use this at the start of a new ChatGPT chat, after closing a meaningful Issue/PR, or whenever the chat context feels stale. This step is only for grounding. Do not plan new work here; use Step B or Step C for that.

```md
I am starting a new ChatGPT chat for an existing project.

Target branch:
{{target branch}}

Please re-establish context by inspecting repo docs at the target branch:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant

Rules:
- Treat repo docs, Issues, and PRs as authoritative for current state.
- Do not rely on memory from prior chats.
- If connector access is unavailable, ask me for only the smallest missing file or GitHub item.
- If docs, Issues, or PRs conflict, call out the conflict before recommending next steps.

After reading the docs and relevant GitHub items, summarize:
1. current product direction
2. current architecture/state
3. active Issue/PR or current task
4. next action according to docs/current-task.md
5. any doc, Issue, or PR conflicts or stale areas
```

## Loop Step B - Plan or refine the next GitHub Issue

Use this for backlog capture, implementation-ready Issue planning, a standalone slice, or a patch. GitHub Issues are the default durable place for future implementation items and detailed work contracts. The roadmap stays broader and more strategic.

```md
Before planning, do a fresh source-of-truth check using repo docs and relevant GitHub Issues/PRs at the target branch.

Target branch:
{{target branch}}

Work mode:
{{Backlog Issue, Implementation-ready Issue, Standalone slice, or Patch}}

Current objective:
{{what you want to accomplish}}

Additional context:
{{anything important that is not already in repo docs or Issues, or write "none"}}

Please inspect the configured GitHub repo at the target branch, or ask me for only the smallest missing file or GitHub item if connector access is unavailable:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant

First, recommend the Issue/PR tracking level for this work:
- backlog Issue only
- implementation-ready Issue recommended
- Issue + Draft PR recommended
- Issue + Draft PR required

Use this rule:
- Tiny same-session patch: no Issue needed unless it should be remembered.
- Future implementation idea: create or refine a backlog Issue.
- Meaningful feature, multi-step slice, multi-day branch, worktree, project switching, risky architecture/product change, or group work: use an implementation-ready Issue.
- Group work: Issue + Draft PR required.

If this should become or update a GitHub Issue, draft the Issue body with:
1. objective and target state
2. current state and source-of-truth notes
3. scope and non-goals
4. implementation slices/checklist when useful
5. acceptance criteria
6. validation and manual QA expectations
7. docs update expectations
8. risks and stop conditions
9. follow-up backlog
10. PR expectations when implementation starts

If Work mode is STANDALONE_SLICE, produce a concise implementation plan with:
1. goal and scope
2. non-goals
3. acceptance criteria
4. validation and docs update expectations
5. stop conditions
6. whether the slice should be captured as an Issue

If Work mode is PATCH, produce a narrow patch plan with:
1. issues to fix and expected behavior
2. non-goals
3. acceptance criteria
4. validation expectations
5. risks
6. whether this should update an existing Issue/PR or create a follow-up Issue

The plan should support larger features when appropriate, but keep each implementation step independently reviewable.
```

## Loop Step C - Generate the next LLM agent handoff

Use this for an Issue implementation, standalone slice, or patch. The prompt intentionally does not ask for the repo URL because the ChatGPT Project Instructions should already contain it. Branch context still matters.

```md
Before creating the handoff, do a fresh source-of-truth check using repo docs and relevant GitHub Issues/PRs at the target branch.

Target branch:
{{target branch}}

Work type:
{{Issue implementation, Standalone slice, or Patch}}

Linked Issue or work item:
{{GitHub Issue number/title, Issue draft, or patch description}}

Task context:
{{any context LLM agent needs beyond the repo docs and linked Issue, or write "none"}}

Please inspect the configured GitHub repo at the target branch, or ask me for only the smallest missing file or GitHub item if connector access is unavailable:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- linked Issue or Issue draft, if applicable
- active PR for the branch, if applicable

Then create a lean LLM agent-ready handoff containing only what LLM agent needs for this task.

If Issue/PR tracking is in use, include:
- owner
- linked Issue or assigned work item
- branch
- focused files/docs
- files/docs/systems to avoid
- Draft PR expectations

When Issue/PR tracking is in use, the readiness gate must also require LLM agent to check active Issues, PRs, and related remote branches before coding. If another active branch appears to touch the same files or systems, LLM agent must stop and report the possible overlap before editing. For group work, the readiness gate should also confirm the linked Issue or Draft PR, branch owner, focused files/docs, files/docs to avoid, and whether `docs/collaboration.md` adds project-specific rules.

A normal handoff should include:
- goal
- linked Issue or work item when available
- source-of-truth docs to inspect
- readiness gate
- context specific to this task
- scope
- non-goals
- files likely to change, if useful
- acceptance criteria
- validation expectations
- documentation delta expectations
- stop conditions
- final reporting expectations

Rules:
- Do not include a standard project/repository/header block by default.
- Only mention repo, target branch, environment, or worktree details if they are not obvious or the task depends on them.
- Do not restate the entire product or Issue if the repo docs and linked Issue already cover it.
- Do not include command-by-command setup unless explicitly needed.
- Keep the handoff copy-paste ready.
- Prefer repo-owned standard commands from `AGENTS.md`, package scripts, or `scripts/` for setup, validation, and branch verification.
- If the repo provides a branch-push verification script and the work uses a worktree, include it in validation or final-report expectations.
- Do not create extra active-context files just to repeat the handoff; the handoff is the active execution packet and repo docs/Issues are durable truth.
```

## Loop Step D - Let LLM agent implement

In LLM agent:

1. Start a fresh LLM agent thread/worktree for each Issue implementation or standalone implementation branch.
2. Reuse the same branch/thread only for focused patch corrections to the same implementation.
3. Paste the handoff.
4. For group work or overlapping branch risk, have LLM agent confirm the linked Issue or Draft PR, branch owner, and overlap check before editing. Do not implement directly on `main` unless the repo explicitly allows it for this task.
5. Let LLM agent inspect docs, linked Issue/PR, implement, validate, update docs/Issues/PRs, commit, push, and verify the branch is pushed when a repo helper exists.
6. If Issue/PR tracking is in use, let LLM agent open or update the Draft PR when possible and include PR status in the final report.
7. Copy LLM agent's final report back into ChatGPT.

A meaningful feature implementation usually follows this path:

1. Issue defines scope and done-when criteria.
2. Branch implements the Issue.
3. Draft PR tracks implementation progress and validation.
4. PR is marked ready after validation and docs updates.
5. User QA decides merge, patch, revise, or stop.
6. Linked Issue is closed, updated, or split into follow-up Issues.

A good LLM agent final report must include:

- branch
- commit
- pushed remote branch, when work was done on a branch or worktree
- linked Issue status, when Issue tracking is in use
- Draft PR status, when Issue/PR tracking is in use
- owner and overlap-check result, when group work is active
- branch-push verification result, when the repo provides a verification script
- files changed
- validation results
- documentation delta
- manual QA recommendations
- known risks

## Loop Step E - QA and decide merge or patch

```md
Help me review this completed implementation.

Branch:
{{target branch:}}

Work type:
{{type of work completed: Issue implementation, Standalone slice, or Patch}}

Linked Issue or PR:
{{GitHub Issue/PR number or title, or write "none"}}

LLM agent final report:
{{LLM implementation notes:}}

My rough QA notes:
{{rough QA notes:}}

Please do the following:
1. assess whether the work appears aligned with the linked Issue, roadmap, or slice plan
2. clean up my QA notes into clear issues
3. classify each issue as blocker, follow-up patch, Issue follow-up, new Issue, later roadmap, or reject
4. identify what should change before merge, if anything
5. identify what should be updated in the Issue or PR before review, patch, merge, or closeout
6. tell me exactly what to manually QA
7. recommend one of: merge, narrow patch, revise Issue scope, split follow-up Issues, or abandon branch
8. if a patch is needed, create a lean LLM agent-ready patch handoff
```

## Loop Step F - Patch when needed

```md
Create a narrow LLM agent-ready patch handoff.

Branch to patch:
{{target branch:}}

Linked Issue or PR:
{{GitHub Issue/PR number or title, or write "none"}}

Issues to fix:
{{list of issues this patch should fix:}}

Additional context:
{{anything LLM agent needs that is not already in repo docs, Issue, or PR, or write "none":}}

Please inspect repo docs and the linked Issue/PR at the target branch if current state matters. Then generate a concise patch handoff with:
1. goal
2. source-of-truth docs to inspect
3. scope
4. non-goals
5. acceptance criteria
6. validation expectations
7. documentation delta expectations
8. final reporting expectations

Rules:
- Only fix the listed issues.
- Do not redesign adjacent flows.
- Do not start the next Issue or slice unless explicitly requested.
- Do not change schema/auth/deployment unless required and reported first.
- Do not rewrite unrelated code.

Final report must include:
- branch
- commit
- linked Issue/PR updates, if applicable
- files changed
- validation results
- documentation delta
- manual QA recommendations
- remaining risks or follow-ups

Keep this handoff short and copy-paste ready.
```

## Loop Step G - Close the Issue, PR, or phase

When an Issue, PR, or major phase is complete, close it out, update docs, and usually start a new ChatGPT chat for the next Issue or phase.

```md
Help me close out this work item and prepare the project for the next stage.

Target branch:
{{target branch:}}

Work item to close:
{{name of Issue, PR, slice, patch, or phase being closed out:}}

Known remaining issues:
{{any outstanding issues, or write "none":}}

Please do a fresh source-of-truth check using repo docs and relevant GitHub Issues/PRs at the target branch. If connector access is unavailable, ask me for only the smallest missing file or GitHub item from:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- linked Issue or PR if relevant

Then recommend:
1. whether the work item appears complete
2. what docs should be updated
3. what old context should be removed from the hot path
4. what docs/current-task.md should say next
5. whether the linked Issue should be closed, updated, split, or left open
6. whether the PR should be merged, patched, closed, updated, or marked ready for review
7. whether roadmap should change because scope or sequencing changed
8. whether the next step should be a patch, new Issue, standalone slice, production hardening, or pause
9. whether I should start a new ChatGPT chat for the next Issue or phase
10. a LLM agent-ready docs-update handoff if needed
```

# Reference material

Use this section when the main workflow points you to supporting material. It is deliberately shorter than the old appendices: the main workflow stays actionable, and reference material stays available without becoming a second manual.

## Issue-first backlog and PR tracking

GitHub Issues are the default durable tracking layer for future implementation work. Use them for specific backlog items, implementation-ready work, active work contracts, follow-ups, and ideas you do not want buried in chat.

PRs are the implementation and review record for a branch. A meaningful feature normally starts as an Issue, moves to a branch and Draft PR during implementation, then closes or updates the linked Issue after QA and merge.

Keep the roles distinct:

- Roadmap = strategic sequence, milestones, and broader deferred themes.
- GitHub Issue = specific backlog item, implementation contract, or follow-up.
- Draft PR = active branch and review record.
- `docs/current-task.md` = short current project pointer, including active Issue/PR when useful.
- Discord/chat = discussion, not durable truth.
- `docs/collaboration.md` = reusable group rules when branch ownership, review expectations, or overlap checks need to be explicit.

Use Issues by default for future implementation ideas, multi-step features, project switching, worktrees, risky architecture or product changes, and group work. Tiny same-session patches can skip Issues unless the decision or follow-up needs to be remembered.

For solo projects, this can stay lightweight: one clear Issue and one PR is enough for most meaningful work. For group work, Issues and Draft PRs are required.

## Issue body shape

Use this as the default shape when ChatGPT drafts an implementation-ready GitHub Issue.

```md
Goal:
{{what should change}}

Why:
{{user/product value}}

Scope:
- {{included work}}

Non-goals:
- {{excluded work}}

Implementation notes:
- {{known files, APIs, routes, docs, or constraints}}

Acceptance criteria:
- {{what must be true}}

Validation:
- {{tests, build, preview, or manual QA}}

Docs update expectations:
- {{docs/current-task.md, architecture, roadmap, or none}}

PR expectations:
- Branch: {{branch name or naming convention}}
- Draft PR until validation is complete
- Link this Issue in the PR body
```

## Group repo mode

Group repo mode is the same core workflow with stricter coordination. Use it when another person, another coding agent, or another active branch might touch the same files, features, docs, or deployment path.

For group work:

- Create `docs/collaboration.md` during setup or before the first group work item.
- Use an Issue plus Draft PR for each meaningful work item.
- Give each work item an owner, branch, scope, focused files/docs, files/docs to avoid, validation expectations, and done-when criteria.
- Do not implement directly on `main` unless the repo explicitly allows that for the specific task.
- Before coding, check active Issues, PRs, and related remote branches for overlap.
- If another active branch appears to touch the same files or systems, stop and coordinate before editing.
- Use Discord or chat for discussion, but record durable decisions in Issues, PRs, or repo docs.
- Add `docs/collaboration.md` when collaboration rules, ownership, review expectations, or branch conventions need to be reusable across the project. Use **Stage 5A - Add group collaboration docs when needed** for the setup prompt.

For solo projects, keep this lightweight. Use Issue/PR tracking for multi-day branches, risky changes, worktrees, project switching, or anything you may need to review later. Skip it for tiny same-session patches.

## Keep repo docs fresh

Use `docs/current-task.md` as the active work pointer for current status and next action. Keep it concise: it should point to the active Issue/PR instead of copying the full Issue or final report.

LLM agent should update `docs/current-task.md` after every implementation when current status, next action, active branch, active Issue, or active PR changes. Update linked Issues/PRs when scope, status, validation, documentation delta, or follow-ups change. Update `docs/architecture.md` or `docs/roadmap.md` only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

ChatGPT should inspect repo docs at the target branch whenever current state matters. For group work or overlap risk, active Issues, PRs, related remote branches, and `docs/collaboration.md` are part of the current-state check. Chat memory and prior final reports are orientation only; repo docs, Issues, and PRs are authoritative.

Golden rules:

1. The repo is durable memory. Chats are temporary.
2. Current-state checks beat chat memory.
3. Keep LLM agent handoffs lean and task-specific.
4. Prefer reviewable slices over vague large changes.
5. LLM agent updates docs, Issues, and PRs after implementation when status changes.
6. The user approves product direction, QA judgment, and merge decisions.
7. Remove stale detail from the hot path instead of letting it bury the next action.

## Documentation delta

Every LLM agent final report should include a documentation delta.

```md
Documentation delta:
- docs/current-task.md: {{Summarize what changed in docs/current-task.md}}
- linked Issue/PR, if applicable: {{Summarize what changed, or write 'not applicable'}}
- docs/architecture.md: {{Summarize what changed, or write 'not applicable'}}
- docs/roadmap.md: {{Summarize what changed, or write 'not applicable'}}
```

## Token-efficient repo helpers

As a project matures, move repeated setup, validation, and branch hygiene into repo-owned helpers instead of repeating commands in every handoff.

Useful helpers include:

- a single package validation command, such as `npm run check`
- a setup script, such as `.\scripts\setup-codex-worktree.ps1`
- a validation script, such as `.\scripts\validate.ps1`
- a branch-push verification script, such as `.\scripts\verify-branch-pushed.ps1`
- a small command menu in `AGENTS.md`

Use these helpers to keep handoffs short. The handoff should say what to accomplish, what docs to inspect, and what acceptance criteria matter. The repo should own repeatable command details.

Do not create a separate active-context file just to duplicate the handoff. The handoff is the active execution packet for the current run. Repo docs are the durable source of truth, and `docs/current-task.md` should stay concise enough to point to current status and next action without becoming a long final-report archive.

For worktree-based development, local-only completion is not enough. The LLM agent should commit, push the branch to the remote repo, run the repo's branch verification helper when one exists, and include the pushed branch plus verification result in the final report.

## Switching computers safely

Switching computers is a reference workflow for moving active work between machines. It is not part of one-time project setup.

Use GitHub as the sync layer. Do not try to sync local coding-agent state, generated folders, local worktrees, or runtime files between computers.

Default to a **clean project switch** whenever possible: finish or pause at a safe checkpoint, commit real work, push the branch, verify the branch is available on GitHub, and make sure the next action is clear before leaving the current computer.

Use three switch types:

- **Clean project switch:** the normal path. Use this when the current Issue, slice, patch, or checkpoint is committed and pushed.
- **Mid-task switch:** use only when you must move computers before work is complete. Commit only meaningful checkpoint work, and provide a short passoff in ChatGPT, the LLM agent final report, or another temporary note.
- **Remote or cloud coding-agent switch:** optional. Use this only when work is already running in a supported remote or cloud coding-agent environment.

Before leaving the current computer:

```powershell
git status
git branch --show-current
git fetch --all --prune
git status
git log --oneline --decorate -5
```

If there are meaningful changes that should travel to the next computer:

```powershell
git add {{Files to commit}}
git commit -m '{{Short checkpoint message}}'
git push -u origin {{Branch name}}
# If the repo provides one, then run:
.\scripts\verify-branch-pushed.ps1
```

Do not create a new repo file just because you are switching computers. If the project is mid-Issue and the next action would otherwise be unclear, provide a short passoff in ChatGPT or include it with the LLM agent final report. Update `docs/current-task.md` only when the actual project state or next action changed.

On the new computer, rebuild local state from GitHub:

```powershell
Set-Location C:\Code\{{Project folder}}
git fetch --all --prune
git checkout {{Branch name}}
git pull --ff-only
npm install
npm run build
git status
```

If the repo does not exist on the new computer yet:

```powershell
Set-Location C:\Code
git clone {{Paste the GitHub repo URL}}
Set-Location C:\Code\{{Project folder}}
git checkout {{Branch name}}
npm install
npm run build
git status
```

Restore only local-only secrets and machine setup that the project actually needs. Do not copy generated folders or runtime files just because they exist locally. Recreate generated state from the repo.

Usually recreate or ignore:

- `node_modules/`
- `dist/`, `.next/`, coverage folders, and other build output
- local dev server logs or temporary runtime files

Restore manually and securely only when required:

- `.env.local`
- local API keys or credentials
- local database files that are intentionally excluded from Git
- editor, desktop app, or machine-specific settings

Secrets and machine-specific setup do not travel through Git. Use a password manager, secure note, platform dashboard, or another user-controlled source. Never commit secrets.

If this is the first time using the project with Codex or another coding agent on the new computer, return to **Stage 2 - Configure Codex before handoffs** and configure the local coding-agent project before giving it implementation work:

1. Open the coding agent on the new computer.
2. Add or open the local repo folder, such as `C:\Code\{{Project folder}}`.
3. Confirm the agent can see the repo files.
4. Confirm the active branch is the branch you pulled from GitHub.
5. Confirm the working tree is clean or intentionally dirty.
6. Confirm the terminal environment is Windows-native PowerShell unless the project intentionally uses something else.
7. Confirm the repo's standard commands run, such as `npm install`, `npm run build`, and `npm run dev` or the commands listed in `AGENTS.md`.
8. Start a fresh coding-agent thread for continued implementation unless you are intentionally using a supported remote or cloud coding-agent task.

Use this readiness prompt before asking the coding agent to implement on the new computer:

```md
This project has just been resumed on a new computer.

Please inspect:
- AGENTS.md
- docs/current-task.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant

Then confirm:
1. current branch
2. git status
3. repo docs are readable
4. standard local commands from AGENTS.md or package scripts
5. whether anything appears missing from the local setup

Do not change files yet. Stop after reporting readiness.
```

## Docs health check

Run a docs health check after a meaningful Issue/PR, before a major phase, or whenever docs seem stale. Do not make this a weekly chore unless the project is moving quickly.

```md
Create a LLM agent-ready docs health check handoff.

Target branch:
{{target branch:}}

Reason for audit:
{{reason for running this docs health check:}}

Goal:
Audit and update project documentation so the hot-path docs accurately reflect the current project state.

Read first from repo docs at the target branch:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant
- recent git history

Scope:
Documentation only. Do not implement app features.

Tasks:
1. Identify stale, conflicting, or bloated docs.
2. Update docs/current-task.md so it reflects current status and next action.
3. Update the active Issue doc only if slice or Issue/PR status is stale.
4. Update docs/architecture.md only if architecture changed.
5. Update docs/roadmap.md only if roadmap status changed.
6. Remove obsolete detail from hot-path docs when it clearly no longer helps current work.
7. Preserve uncertainty instead of guessing.

Validation:
- Confirm docs agree on the active Issue, PR, or work item.
- Confirm current status and next action are clear.
- Report unresolved conflicts.

Final report:
- docs changed
- conflicts found and resolved
- conflicts still unresolved
- recommended next action
```

## Current-state check prompt

Use this whenever ChatGPT might be stale and the task depends on current repo state.

```md
Before answering, do a fresh source-of-truth check for this project.

Target branch:
{{target branch:}}

Current situation:
{{why you need a source-of-truth check:}}

Please inspect repo docs at the target branch for the latest versions of:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md when group work is active
- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap
- active docs/design/*.md when a specific design decision is relevant

Rules:
- Do not rely on memory or prior chat assumptions.
- Treat repo docs as authoritative.
- If connector access is unavailable or a file is missing, ask me to paste or upload only the specific missing files.
- If the branch is unmerged, do not assume main includes the branch changes.
- If docs conflict, call out the conflict before making recommendations.

After the source-of-truth check, answer my request:
{{What do you want ChatGPT to answer or help with?}}
```

## Computer switch check prompt

Use this before moving active work to another computer, especially during an Issue implementation or patch.

```md
Help me safely switch computers for this project.

Current computer:
{{Computer A name or description}}

New computer:
{{Computer B name or description}}

Target branch:
{{target branch}}

Current state:
{{What work is active, or paste the LLM agent final report}}

Please help me:
1. identify what must be committed and pushed before switching
2. identify which docs should be updated before switching
3. give me the PowerShell commands to verify the branch is safe to leave
4. give me the PowerShell commands to resume on the new computer
5. call out anything that should not be synced, such as secrets, generated folders, or runtime logs
6. recommend whether to start a fresh coding-agent thread, continue through a supported remote/cloud task, or only do QA on the new computer
```


## Minimal LLM agent handoff shape

Use this as the default structure for normal Issue implementations, standalone slices, and patches. Add repo, branch, environment, or worktree details only when the task depends on them or when they are not already configured in LLM agent.

```md
Goal:
{{what the LLM agent should accomplish:}}

Read first:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- docs/collaboration.md, if group work is active
- {{Linked Issue or Issue draft, if applicable}}

Readiness gate:
Before coding, confirm the docs, target branch, and requested scope agree. If they conflict, stop and report the conflict.

Scope:
- {{scope:}}

Non-goals:
- {{anything the LLm agent should avoid:}}

Acceptance criteria:
- {{what must be true when the work is complete:}}

Validation:
- {{what commands, tests, preview checks, or manual checks should be run:}}
- Prefer the repo's standard validation command or script when present, such as `npm run check` or `.\scripts\validate.ps1`.

Documentation delta:
Update docs/current-task.md and any linked Issue, PR, architecture, or roadmap docs affected by the work.

Stop conditions:
Stop and report before making unrelated architecture, schema, auth, deployment, or scope changes.

Final report:
- branch
- commit
- files changed
- validation results
- documentation delta
- manual QA recommendations
- known risks or follow-ups
```

## Standard repo docs

The workflow uses a small source-of-truth doc set. Keep these docs concise and current rather than historical.

- `AGENTS.md` defines coding-agent rules, repo conventions, validation expectations, and documentation update expectations. Update it when agent behavior or repo conventions change.
- `docs/product.md` defines the product goal, target user, MVP, non-goals, and product decisions. Update it when product direction changes.
- `docs/architecture.md` defines the technical approach, important routes/services/data flows, deployment assumptions, and constraints. Update it when architecture changes.
- `docs/roadmap.md` defines milestones, sequencing, major deferred themes, and strategic backlog categories. Update it when scope, order, or milestone status changes.
- `docs/current-task.md` defines current status and the next action. Update it after every implementation.
- `docs/collaboration.md` defines branch ownership, Issue/PR, review, and overlap-check expectations when group work is active. Keep it optional for solo repos.
- GitHub Issues track specific backlog items, implementation-ready work, active work contracts, and follow-ups. PRs track branch implementation, validation, documentation delta, QA notes, and merge readiness.
- `docs/design/*.md` can hold active design notes for complex product, UX, data, or architecture decisions. Use it only when a decision is too large for the hot-path docs.

## Optional Codex worktrees

Use worktrees only when they reduce friction. They are useful for isolated branches, parallel slices, and safer experimentation. They are unnecessary for tiny projects or single-threaded work where a normal branch is simpler.

Good setup scripts should:

- run from the repo root
- show tool versions
- fetch and prune Git refs
- stop if the worktree appears stale or detached from known branch tips
- copy local-only environment files only from a user-controlled path
- validate required environment keys without printing secret values
- install dependencies using the project's package manager
- fail loudly instead of continuing with a partial environment

Good cleanup scripts should:

- remove only disposable generated folders
- never delete source files, docs, migrations, config, or local secrets
- be safe to run more than once


Good branch-verification scripts should:

- fail on `main` unless explicitly allowed
- fail when uncommitted changes exist
- fetch and prune remote refs
- verify the current branch has an upstream
- verify local `HEAD` is pushed to the upstream branch
- fail if the local branch is ahead of the remote branch

Generic cleanup template:

```powershell
$ErrorActionPreference = 'Stop'

Write-Host 'Running Codex cleanup script from:' (Get-Location)

$pathsToRemove = @(
  '.next',
  'node_modules',
  'coverage',
  'playwright-report',
  'test-results',
  '.vercel',
  '.turbo'
)

foreach ($path in $pathsToRemove) {
  if (Test-Path $path) {
    Write-Host 'Removing disposable path:' $path
    Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
  } else {
    Write-Host 'Not present, skipping:' $path
  }
}

Write-Host 'Codex cleanup complete.'
```

Generic setup template:

```powershell
$ErrorActionPreference = 'Stop'

# App-specific settings
$SourceEnvPath = '{{Optional path to source .env.local, or leave blank}}'
$RequiredEnvKeys = @(
  '{{OPTIONAL_REQUIRED_ENV_KEY}}'
)
$RequiredRepoFiles = @(
  'package.json'
)
$InstallCommand = 'npm install'

Write-Host 'Codex Worktree Setup'
Write-Host 'Working directory:' (Get-Location)

Write-Host 'Tool versions:'
git --version
if (Get-Command node -ErrorAction SilentlyContinue) { node -v }
if (Get-Command npm -ErrorAction SilentlyContinue) { npm -v }
if (Get-Command gh -ErrorAction SilentlyContinue) { gh --version }

Write-Host 'Fetching latest Git refs...'
git fetch --all --prune
if ($LASTEXITCODE -ne 0) {
  throw 'Git fetch failed. Cannot verify worktree freshness.'
}

$head = (git rev-parse HEAD).Trim()
$matchingRefs = @(
  git for-each-ref refs/heads refs/remotes --format='%(refname:short) %(objectname)' |
    Where-Object { -not $_.StartsWith('origin/HEAD ') } |
    ForEach-Object {
      $parts = $_ -split ' '
      if ($parts.Length -ge 2 -and $parts[1] -eq $head) { $parts[0] }
    }
)

if ($matchingRefs.Count -eq 0) {
  git log --oneline --decorate -5
  throw 'Stopping setup: this worktree HEAD is not the current tip of any known local or remote branch after fetch.'
}

foreach ($file in $RequiredRepoFiles) {
  if (-not (Test-Path $file)) {
    throw 'Required repo file not found: ' + $file
  }
}

$targetEnv = Join-Path (Get-Location) '.env.local'
if (-not (Test-Path $targetEnv) -and -not [string]::IsNullOrWhiteSpace($SourceEnvPath)) {
  if (-not (Test-Path $SourceEnvPath)) {
    throw '.env.local missing in worktree and source path does not exist: ' + $SourceEnvPath
  }
  Copy-Item $SourceEnvPath $targetEnv -Force -ErrorAction Stop
  Write-Host '.env.local copied into worktree.'
}

if ($RequiredEnvKeys.Count -gt 0) {
  if (-not (Test-Path $targetEnv)) {
    throw '.env.local is required but missing.'
  }
  foreach ($key in $RequiredEnvKeys) {
    if ([string]::IsNullOrWhiteSpace($key) -or $key.StartsWith('{')) { continue }
    if (-not (Select-String -Path $targetEnv -Pattern "^$key=" -Quiet)) {
      throw $key + ' missing from .env.local'
    }
  }
  Write-Host '.env.local validation passed.'
}

if (-not [string]::IsNullOrWhiteSpace($InstallCommand)) {
  Write-Host 'Running dependency install command:' $InstallCommand
  Invoke-Expression $InstallCommand
  if ($LASTEXITCODE -ne 0) { throw 'Dependency install command failed.' }
}

Write-Host 'Codex environment setup complete.'
```

## Terminal cheat sheet

These commands are written for a Windows-native PowerShell terminal. If a project uses a different shell, adapt the path and process-management syntax instead of assuming WSL.

### Navigation

```powershell
Set-Location C:\Code\{{Project folder}}
Get-ChildItem
git status
```

### Git status and freshness

```powershell
git status
git branch --show-current
git fetch --all --prune
git log --oneline --decorate -5
```

### Commit and push

```powershell
git status
git add {{Files to commit}}
git commit -m '{{Short commit message}}'
git push -u origin {{Branch name}}
# If the repo provides one, then run:
.\scripts\verify-branch-pushed.ps1
```

### Local development

```powershell
npm install
npm run dev
# Keep this terminal open while the local app runs.
# To stop the local dev server, press Ctrl+C in this terminal.
# If PowerShell asks for confirmation, type Y and press Enter.
npm test
npm run build
```

### Close a stuck local dev server

Start simple. Most local dev servers close from the same terminal where you ran `npm run dev`.

```powershell
# In the terminal running the dev server:
Ctrl+C
# If PowerShell asks for confirmation, type Y and press Enter.
```

If that terminal is gone or stuck, check whether Node is still running:

```powershell
Get-Process node
```

If you only have one local dev server running, stop all Node processes:

```powershell
Stop-Process -Name node -Force
```

If you have multiple Node processes and want to stop only one, use the `Id` from `Get-Process node`:

```powershell
Stop-Process -Id {{Node process Id}} -Force
```

After stopping it, run `npm run dev` again from the project folder when you want to restart the local app.

### Clean generated files

```powershell
Remove-Item -Recurse -Force .next,node_modules,coverage,playwright-report,test-results -ErrorAction SilentlyContinue
```

## Key terms

- **Planning LLM:** The conversational model used for strategy, planning, QA triage, and handoff generation.
- **Coding agent:** The tool that works directly in the repo to edit files, run checks, commit, and push.
- **Source-of-truth docs:** The repo docs that define current product, architecture, roadmap, and active work.
- **Issue:** A repo-native backlog item or implementation contract for a specific future or active work item.
- **Pull request:** The branch review record that implements an Issue or patch and captures validation, documentation delta, QA notes, and merge readiness.
- **Slice:** One independently reviewable implementation unit inside an Issue or standalone effort.
- **Patch:** A narrow correction to a specific branch or issue.
- **Bootstrap:** The first implementation run that creates the working shell, validation path, and initial deploy/run setup.
- **Readiness gate:** The pre-coding check that confirms docs, branch, and scope agree before implementation.
- **Documentation delta:** The final-report section explaining which docs changed and why.
- **Worktree:** A separate working directory connected to the same Git repo, useful for isolated branches.

## Prompt library and placeholders

A prompt manager is useful when you reuse the same source-of-truth checks, planning prompts, handoff prompts, and QA review prompts across projects. It should reduce typing, not replace repo docs or Project Instructions.

Recommended tool: use the ChatGPT Prompt Manager with **Awesome Prompts** when available.

Suggested placeholder style:

- Use `{{VARIABLE_NAME}}` for short values.
- Use `{{Plain-language prompt question}}` for user-filled fields.
- Keep placeholders specific enough that future you knows what to paste.

Recommended prompt groups:

- Project setup prompts
- Current-state check prompts
- Issue and slice planning prompts
- Codex handoff prompts
- QA review prompts
- Patch prompts
- Docs health check prompts

Rule: save reusable prompts, but keep project-specific truth in repo docs. Do not let a prompt library become a hidden source of truth.

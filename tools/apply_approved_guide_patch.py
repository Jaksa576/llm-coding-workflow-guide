#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
PRIMER = ROOT / 'llm-workflow-primer.md'
RENDERER = ROOT / 'tools' / 'render_guide.py'
VALIDATOR = ROOT / 'tools' / 'validate_guide.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-guide-patch.yml'
SELF = ROOT / 'tools' / 'apply_approved_guide_patch.py'

NOOP_SELF = """#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'


def main() -> int:
    print('No patch operations configured. Add approved edits to this helper before running it.')
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
"""

MANUAL_WORKFLOW = """name: Apply guide patch

# Manual fallback only. Normal guide edits should update Markdown/source files directly
# and let the Build guide HTML workflow render and validate the generated HTML.
on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  apply-guide-patch:
    runs-on: ubuntu-latest
    if: github.actor != 'github-actions[bot]'
    steps:
      - name: Check out repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Apply approved guide patch
        run: python tools/apply_approved_guide_patch.py

      - name: Render guide HTML
        run: python tools/render_guide.py

      - name: Validate guide HTML
        run: python tools/validate_guide.py

      - name: Commit guide patch output
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: 'Apply approved guide patch'
          file_pattern: |
            llm_coding_workflow_guide.md
            llm-workflow-primer.md
            llm_coding_workflow_guide.html
            llm_coding_workflow_diagram.png
            tools/render_guide.py
            tools/apply_approved_guide_patch.py
            .github/workflows/apply-guide-patch.yml
"""

PRIMER_CONTENT = """# LLM Coding Workflow Primer

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
4. The coding agent implements, validates, updates docs/Issues/PRs, commits, and reports back.
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

For group work, Issues and Draft PRs are required. Each meaningful item needs an owner, branch, scope, focused files/docs, files/docs to avoid, validation, and done-when criteria. Add `docs/collaboration.md` during setup or before the first group work item. Solo long-running branches: recommended.

Coding agents should check active Issues, PRs, and related branches before coding when work may overlap another branch. If another active branch appears to touch the same files or systems, they should stop and report the possible overlap before editing.

## Coding-agent handoff expectations

Coding-agent handoffs should include:

- goal
- linked Issue or work item when available
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

When Issue/PR tracking is in use, also include:

- owner
- linked Issue or assigned work item
- branch
- focused files/docs
- files, docs, or systems to avoid
- Draft PR expectations when applicable

Do not restate all project context when the repo docs and linked Issue already contain it. Keep handoffs copy-paste ready.

## Documentation freshness

The coding agent owns documentation freshness during implementation. Every implementation should update `docs/current-task.md` when current status, next task, validation, active Issue/PR, or active branch changes. Update linked Issues/PRs when status, scope, validation, docs delta, or follow-ups change. Update architecture or roadmap docs only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

Every coding-agent final report should include a documentation delta that says which docs, Issues, or PRs changed and why. When Issue/PR tracking is in use, the PR summary should include the documentation delta before the PR is marked ready for review.

ChatGPT should inspect repo docs at the target branch whenever current state matters. Prior chat context and final reports are orientation only; repo docs, Issues, and PRs remain authoritative.

## ChatGPT behavior

Start with the recommendation. Focus on what the user should do next. Prefer reviewable slices. Use the configured GitHub connector before asking for pasted docs when current state matters. Push back on unclear scope, overlapping branch work, overengineering, generic product drift, stale docs, and unnecessary AI dependencies.
"""


def replace_section(text: str, heading: str, replacement: str) -> str:
    pattern = rf"(?ms)^## {re.escape(heading)}\n.*?(?=^## |^# |\Z)"
    new_text, count = re.subn(pattern, replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise SystemExit(f'Expected section not found: ## {heading}')
    return new_text


def replace_top_section(text: str, heading: str, replacement: str) -> str:
    pattern = rf"(?ms)^# {re.escape(heading)}\n.*?(?=^# |\Z)"
    new_text, count = re.subn(pattern, replacement.rstrip() + "\n\n", text, count=1)
    if count != 1:
        raise SystemExit(f'Expected section not found: # {heading}')
    return new_text


def patch_guide() -> None:
    text = GUIDE.read_text(encoding='utf-8')

    replacements = {
        '5. The loop repeats through campaigns, slices, patches, and docs updates.': '5. The loop repeats through GitHub Issues, reviewable slices, patches, PRs, and docs updates.',
        '7. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.': '7. Repeat the main loop: plan or refine a GitHub Issue -> generate handoff -> implement -> validate -> update docs/Issue/PR -> final report -> QA -> merge, patch, revise, split follow-ups, or stop.',
        '8. Close out campaigns, clean stale context from the hot path, and start a new chat for the next phase when useful.': '8. Close or update the Issue/PR, clean stale context from the hot path, and start a new chat for the next Issue or phase when useful.',
        '- active docs/campaigns/*.md if relevant': '- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap\n- active docs/design/*.md when a specific design decision is relevant',
        '- The workflow primer covers campaign/slice/patch workflow, documentation freshness, documentation deltas, current-state refresh behavior, and prompt-manager placeholder style.': '- The workflow primer covers Issue/slice/patch workflow, documentation freshness, documentation deltas, current-state refresh behavior, and prompt-manager placeholder style.',
        '5. if ready, recommend the first implementation campaign or standalone slice': '5. if ready, recommend the first implementation Issue or standalone slice',
        'Update campaign docs when slice status changes.': 'Update linked Issues/PRs when scope, status, validation, or follow-ups change.',
        'Update campaign docs when slice status, acceptance criteria, or follow-up backlog changes.': 'Update linked Issues/PRs when status, scope, acceptance criteria, validation, or follow-up backlog changes.',
        '- campaign doc, if applicable: {{Summarize what changed, or write \'not applicable\'}}': '- linked Issue/PR, if applicable: {{Summarize what changed, or write \'not applicable\'}}',
        'during a campaign or patch': 'during an Issue implementation or patch',
        'during a campaign or patch.': 'during an Issue implementation or patch.',
        'current slice, patch, or checkpoint': 'current Issue, slice, patch, or checkpoint',
        'mid-campaign': 'mid-Issue',
        'after a campaign, before a major campaign, or whenever docs seem stale': 'after a meaningful Issue/PR, before a major phase, or whenever docs seem stale',
        'active campaign or active work item': 'active Issue, PR, or work item',
        'Confirm docs agree on the active campaign or active work item.': 'Confirm docs agree on the active Issue, PR, or work item.',
        'for normal campaign slices, standalone slices, and patches': 'for normal Issue implementations, standalone slices, and patches',
        '- {{Active campaign doc, if applicable}}': '- {{Linked Issue or Issue draft, if applicable}}',
        'Update docs/current-task.md and any campaign, architecture, or roadmap docs affected by the work.': 'Update docs/current-task.md and any linked Issue, PR, architecture, or roadmap docs affected by the work.',
        '- `docs/roadmap.md` defines milestones, sequencing, campaign backlog, and deferred work. Update it when scope or order changes.': '- `docs/roadmap.md` defines milestones, sequencing, major deferred themes, and strategic backlog categories. Update it when scope, order, or milestone status changes.',
        '- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.': '- GitHub Issues track specific backlog items, implementation-ready work, active work contracts, and follow-ups. PRs track branch implementation, validation, documentation delta, QA notes, and merge readiness.',
        '- **Campaign:** A large swath of related work broken into reviewable slices.\n- **Slice:** One independently reviewable implementation unit inside a campaign or standalone effort.': '- **Issue:** A repo-native backlog item or implementation contract for a specific future or active work item.\n- **Pull request:** The branch review record that implements an Issue or patch and captures validation, documentation delta, QA notes, and merge readiness.\n- **Slice:** One independently reviewable implementation unit inside an Issue or standalone effort.',
        '- Campaign and slice planning prompts': '- Issue and slice planning prompts',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = replace_top_section(text, 'Main implementation loop', '''# Main implementation loop

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
''')

    text = replace_section(text, 'Lightweight Issue and PR tracking', '''## Issue-first backlog and PR tracking

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
''')

    text = replace_section(text, 'Keep repo docs fresh', '''## Keep repo docs fresh

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
''')

    text = replace_section(text, 'Documentation delta', '''## Documentation delta

Every LLM agent final report should include a documentation delta.

```md
Documentation delta:
- docs/current-task.md: {{Summarize what changed in docs/current-task.md}}
- linked Issue/PR, if applicable: {{Summarize what changed, or write 'not applicable'}}
- docs/architecture.md: {{Summarize what changed, or write 'not applicable'}}
- docs/roadmap.md: {{Summarize what changed, or write 'not applicable'}}
```
''')

    # Remove old routine campaign-doc checks that may remain after section replacement.
    text = text.replace('- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap\n- active docs/design/*.md when a specific design decision is relevant if relevant', '- active GitHub Issues and PRs when planning, implementing, reviewing, or checking overlap\n- active docs/design/*.md when a specific design decision is relevant')
    text = text.replace('- active campaign doc if relevant', '- linked Issue or PR if relevant')
    text = text.replace('campaign, slice or patch name', 'Issue, slice, or patch name')
    text = text.replace('Campaign slice', 'Issue implementation')
    text = text.replace('campaign slice', 'Issue implementation')
    text = text.replace('campaign backlog', 'Issue follow-up')
    text = text.replace('revise plan/campaign', 'revise Issue scope')
    text = text.replace('new campaign', 'new Issue')
    text = text.replace('next campaign', 'next Issue')
    text = text.replace('major campaign', 'major phase')
    text = text.replace('campaign status', 'Issue/PR status')
    text = text.replace('active campaign', 'active Issue')
    text = text.replace('Campaign and slice', 'Issue and slice')
    text = text.replace('PowerShell cheat sheet', 'Terminal cheat sheet')

    forbidden = ['docs/campaigns/*.md', 'campaign document', 'Campaign doc']
    remaining = [term for term in forbidden if term in text]
    if remaining:
        raise SystemExit(f'Retired campaign workflow references remain: {remaining}')

    GUIDE.write_text(text, encoding='utf-8')


def patch_renderer() -> None:
    text = RENDERER.read_text(encoding='utf-8')
    text = text.replace('"Loop Step B - Plan the next work item",', '"Loop Step B - Plan or refine the next GitHub Issue",')
    text = text.replace('"Loop Step G - Close the campaign or phase",', '"Loop Step G - Close the Issue, PR, or phase",')
    text = text.replace('"Keep repo docs fresh",', '"Issue-first backlog and PR tracking",\n            "Issue body shape",\n            "Keep repo docs fresh",')
    text = text.replace('"PowerShell cheat sheet",', '"Terminal cheat sheet",')
    text = text.replace('    "Campaign": "A large swath of related work broken into reviewable slices.",\n    "Slice": "One independently reviewable implementation unit inside a campaign or standalone effort.",', '    "Issue": "A repo-native backlog item or implementation contract for a specific future or active work item.",\n    "Pull request": "The branch review record that implements an Issue or patch and captures validation, documentation delta, QA notes, and merge readiness.",\n    "Slice": "One independently reviewable implementation unit inside an Issue or standalone effort.",')
    text = text.replace('"A docs-only audit to align current-task, roadmap, architecture, and campaign status."', '"A docs-only audit to align current-task, roadmap, architecture, and Issue/PR status."')
    RENDERER.write_text(text, encoding='utf-8')


def patch_validator() -> None:
    text = VALIDATOR.read_text(encoding='utf-8')
    if 'retired campaign doc workflow references absent' not in text:
        marker = '    check("State packet" not in text and "state packet" not in text, "state packet references absent", failures)\n'
        insert = '''    retired_campaign_doc_terms = ["docs/campaigns/*.md", "campaign document", "Campaign doc"]\n    retired_present = [term for term in retired_campaign_doc_terms if term in html or term in markdown]\n    check(not retired_present, "retired campaign doc workflow references absent", failures)\n    check("Issue-first backlog" in text, "Issue-first backlog guidance exists", failures)\n    check("Issue body shape" in text, "Issue body shape exists", failures)\n'''
        if marker not in text:
            raise SystemExit('Validator insertion marker not found.')
        text = text.replace(marker, marker + insert)
    VALIDATOR.write_text(text, encoding='utf-8')


def main() -> int:
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')
    patch_guide()
    PRIMER.write_text(PRIMER_CONTENT, encoding='utf-8')
    patch_renderer()
    patch_validator()
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    SELF.write_text(NOOP_SELF, encoding='utf-8')
    print('Applied Issue-first workflow guide patch and reset helper/workflow.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

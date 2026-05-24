#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
PRIMER = ROOT / 'llm-workflow-primer.md'
RENDER = ROOT / 'tools' / 'render_guide.py'
SELF = Path(__file__).resolve()
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-guide-patch.yml'

NOOP = '''#!/usr/bin/env python3
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
'''

MANUAL_WORKFLOW = '''name: Apply guide patch

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
            tools/render_guide.py
            tools/apply_approved_guide_patch.py
            .github/workflows/apply-guide-patch.yml
'''

NEW_INTRO = '''# LLM Coding Workflow Guide

Use this guide to build software with a planning LLM plus a repo-based coding agent.

In five seconds:

1. ChatGPT helps plan the work.
2. The GitHub repo and repo docs are the source of truth.
3. The coding agent implements one clear slice at a time.
4. The user reviews, QA checks, and decides whether to merge, patch, revise, or stop.
5. The loop repeats through campaigns, slices, patches, and docs updates.

![LLM Coding Workflow](llm_coding_workflow_diagram.png)

## What this guide is for

This workflow is for hobbyist and solo builders who want real software projects without losing control to the coding agent. It also scales to small group repos by adding Issues, Draft PRs, branch ownership, overlap checks, and clear review points.

The default setup is **ChatGPT for planning** and **Codex or another LLM coding agent for implementation**. Windows-native PowerShell examples are used unless a project says otherwise.

The goal is not to create perfect prompts. The goal is to create a repeatable system where projects use the same source-of-truth docs, reviewable implementation loop, validation expectations, documentation deltas, and QA decision points.

## Why the split works

Keep planning context and execution context separate. ChatGPT carries product thinking, roadmap decisions, QA triage, and handoff generation. The coding agent receives only the current task, source-of-truth docs, acceptance criteria, validation expectations, and documentation delta.

That separation keeps handoffs lean, reduces stale context, and makes projects easier to resume across chats, branches, devices, and collaborators.

If your planning LLM and coding agent have similar costs and context behavior, you can streamline some planning steps for small tasks. Do not collapse source-of-truth docs, acceptance criteria, validation expectations, documentation delta, or the final report loop unless the project is truly disposable.

## Workflow at a glance

1. Create the GitHub repo and local Windows workspace.
2. Create the ChatGPT Project and add the compact workflow primer.
3. Configure GitHub source-of-truth access and the local coding-agent project.
4. Define the project, generate app-specific instructions, and create core repo docs.
5. Bootstrap the project with a coding-agent handoff.
6. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.
7. Close out campaigns, clean stale context from the hot path, and start a new chat for the next phase when useful.

Most time is spent in the implementation loop, not setup.'''

GROUP_REPO_SECTION = '''## Group repo mode

Group repo mode is the same core workflow with stricter coordination. Use it when another person, another coding agent, or another active branch might touch the same files, features, docs, or deployment path.

For group work:

- Use an Issue plus Draft PR for each meaningful work item.
- Give each work item an owner, branch, scope, focused files/docs, files/docs to avoid, validation expectations, and done-when criteria.
- Do not implement directly on `main` unless the repo explicitly allows that for the specific task.
- Before coding, check active Issues, PRs, and related remote branches for overlap.
- If another active branch appears to touch the same files or systems, stop and coordinate before editing.
- Use Discord or chat for discussion, but record durable decisions in Issues, PRs, or repo docs.
- Add `docs/collaboration.md` when collaboration rules, ownership, review expectations, or branch conventions need to be reusable across the project.

For solo projects, keep this lightweight. Use Issue/PR tracking for multi-day branches, risky changes, worktrees, project switching, or anything you may need to review later. Skip it for tiny same-session patches.

'''


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    require(old in text, f'Expected text not found for {label}.')
    return text.replace(old, new, 1)


def replace_all(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    require(count > 0, f'Expected text not found for {label}.')
    return text.replace(old, new)


def update_guide() -> None:
    require(GUIDE.exists(), 'Guide source not found.')
    text = GUIDE.read_text(encoding='utf-8')

    stage0 = '## Stage 0 - Create the repo and local workspace'
    require(stage0 in text, 'Stage 0 marker not found.')
    text = NEW_INTRO + '\n\n' + text[text.index(stage0):]

    text = replace_once(
        text,
        'When current repo state matters, inspect the project repo through the configured GitHub connector at the target branch first. If connector access is unavailable, ask me to provide only the smallest specific missing file or input. Do not rely on memory or prior chat assumptions.\n\nPrefer step-by-step guidance, lean Codex handoffs, reviewable slices, clear stop conditions, documentation delta requirements, and clear final reports from coding agents.',
        'When current repo state matters, inspect the project repo through the configured GitHub connector at the target branch first. If connector access is unavailable, ask me to provide only the smallest specific missing file or input. Do not rely on memory or prior chat assumptions.\n\nFor group repos, require Issues and Draft PRs for meaningful work, confirm branch ownership before implementation, and stop before editing if active work appears to overlap another branch.\n\nPrefer step-by-step guidance, lean Codex handoffs, reviewable slices, clear stop conditions, documentation delta requirements, and clear final reports from coding agents.',
        'starter instructions group repo rule',
    )

    text = replace_all(
        text,
        '- docs/current-task.md\n- active docs/campaigns/*.md if relevant',
        '- docs/current-task.md\n- docs/collaboration.md when group work is active\n- active docs/campaigns/*.md if relevant',
        'active campaign source lists',
    )
    text = text.replace(
        '- docs/current-task.md\n- the active campaign doc if applicable',
        '- docs/current-task.md\n- docs/collaboration.md when group work is active\n- the active campaign doc if applicable',
    )
    text = text.replace(
        '- docs/current-task.md\n- active campaign doc if relevant',
        '- docs/current-task.md\n- docs/collaboration.md when group work is active\n- active campaign doc if relevant',
    )
    text = text.replace(
        '- docs/current-task.md\n- recent git history',
        '- docs/current-task.md\n- docs/collaboration.md when group work is active\n- recent git history',
    )
    text = text.replace(
        '- docs/current-task.md\n- {{Active campaign doc, if applicable}}',
        '- docs/current-task.md\n- docs/collaboration.md, if group work is active\n- {{Active campaign doc, if applicable}}',
    )
    text = text.replace(
        '- docs/current-task.md\n- active docs/campaigns/*.md if relevant\n\nRules:',
        '- docs/current-task.md\n- docs/collaboration.md when group work is active\n- active docs/campaigns/*.md if relevant\n\nRules:',
    )

    text = replace_once(
        text,
        'Please draft these files:\n1. AGENTS.md\n2. docs/product.md\n3. docs/architecture.md\n4. docs/roadmap.md\n5. docs/current-task.md',
        'Please draft these core files:\n1. AGENTS.md\n2. docs/product.md\n3. docs/architecture.md\n4. docs/roadmap.md\n5. docs/current-task.md\n\nIf this will be a group repo, also draft `docs/collaboration.md` with branch, Issue, Draft PR, review, and overlap-check expectations.',
        'core docs optional collaboration doc',
    )

    text = replace_once(
        text,
        '- If the repo has standard setup, validation, or branch-verification scripts, document them in `AGENTS.md` instead of repeating those commands in every handoff.',
        '- If the repo has standard setup, validation, or branch-verification scripts, document them in `AGENTS.md` instead of repeating those commands in every handoff.\n- For group repos, keep collaboration rules in `docs/collaboration.md` instead of burying them in chat history.',
        'core docs group repo requirement',
    )

    text = replace_once(
        text,
        'If Issue/PR tracking is recommended or required, include the Issue scope and Draft PR expectations inside the normal plan. Do not create a separate Issue/PR decision workflow.',
        'If Issue/PR tracking is recommended or required, include the Issue scope and Draft PR expectations inside the normal plan. Do not create a separate Issue/PR decision workflow.\n\nFor group work, also include owner, branch, focused files/docs, files/docs or systems to avoid, reviewer expectations, and where durable discussion should be recorded.',
        'planning group repo details',
    )

    text = replace_once(
        text,
        'When Issue/PR tracking is in use, the readiness gate must also require LLM agent to check active Issues, PRs, and related remote branches before coding. If another active branch appears to touch the same files or systems, LLM agent must stop and report the possible overlap before editing.',
        'When Issue/PR tracking is in use, the readiness gate must also require LLM agent to check active Issues, PRs, and related remote branches before coding. If another active branch appears to touch the same files or systems, LLM agent must stop and report the possible overlap before editing. For group work, the readiness gate should also confirm the linked Issue or Draft PR, branch owner, focused files/docs, files/docs to avoid, and whether `docs/collaboration.md` adds project-specific rules.',
        'handoff readiness group repo details',
    )

    text = replace_once(
        text,
        "4. Let LLM agent inspect docs, implement, validate, update docs, commit, push, and verify the branch is pushed when a repo helper exists.\n5. If Issue/PR tracking is in use, let LLM agent open or update the Draft PR when possible and include PR status in the final report.\n6. Copy LLM agent's final report back into ChatGPT.",
        "4. For group work, have LLM agent confirm the linked Issue or Draft PR, branch owner, and overlap check before editing. Do not implement directly on `main` unless the repo explicitly allows it for this task.\n5. Let LLM agent inspect docs, implement, validate, update docs, commit, push, and verify the branch is pushed when a repo helper exists.\n6. If Issue/PR tracking is in use, let LLM agent open or update the Draft PR when possible and include PR status in the final report.\n7. Copy LLM agent's final report back into ChatGPT.",
        'implementation group repo step',
    )

    text = replace_once(
        text,
        '- Draft PR status, when Issue/PR tracking is in use\n- branch-push verification result, when the repo provides a verification script',
        '- Draft PR status, when Issue/PR tracking is in use\n- owner and overlap-check result, when group work is active\n- branch-push verification result, when the repo provides a verification script',
        'final report group repo fields',
    )

    text = replace_once(
        text,
        '## Keep repo docs fresh\n',
        GROUP_REPO_SECTION + '## Keep repo docs fresh\n',
        'group repo reference section',
    )

    text = replace_once(
        text,
        '- Discord/chat = discussion, not durable truth.',
        '- Discord/chat = discussion, not durable truth.\n- `docs/collaboration.md` = reusable group rules when branch ownership, review expectations, or overlap checks need to be explicit.',
        'issue pr role distinction collaboration doc',
    )

    text = replace_once(
        text,
        'ChatGPT should inspect repo docs at the target branch whenever current state matters. Chat memory and prior final reports are orientation only; repo docs are authoritative.',
        'ChatGPT should inspect repo docs at the target branch whenever current state matters. For group work, active Issues, PRs, related remote branches, and `docs/collaboration.md` are part of the current-state check. Chat memory and prior final reports are orientation only; repo docs are authoritative.',
        'repo freshness group current state',
    )

    text = replace_once(
        text,
        '- `docs/current-task.md` defines current status and the next action. Update it after every implementation.\n- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.',
        '- `docs/current-task.md` defines current status and the next action. Update it after every implementation.\n- `docs/collaboration.md` defines branch ownership, Issue/PR, review, and overlap-check expectations when group work is active. Keep it optional for solo repos.\n- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.\n- `docs/design/*.md` can hold active design notes for complex product, UX, data, or architecture decisions. Use it only when a decision is too large for the hot-path docs.',
        'standard docs collaboration and design docs',
    )

    GUIDE.write_text(text, encoding='utf-8')
    print('Updated guide intro, collaboration guidance, and source-of-truth checks.')


def update_primer() -> None:
    require(PRIMER.exists(), 'Primer source not found.')
    text = PRIMER.read_text(encoding='utf-8')
    text = replace_once(
        text,
        'For group work, Issues and Draft PRs are required. For solo campaign or long-running branch work, they are recommended.',
        'For group work, Issues and Draft PRs are required. Each meaningful group work item should have an owner, branch, scope, focused files/docs, files/docs to avoid, validation expectations, and done-when criteria. Do not implement directly on `main` unless the repo explicitly allows it for the task. Add `docs/collaboration.md` when these rules need to be reusable across the repo. For solo campaign or long-running branch work, Issues and Draft PRs are recommended.',
        'primer group repo mode',
    )
    PRIMER.write_text(text, encoding='utf-8')
    print('Updated compact primer group collaboration rule.')


def update_renderer() -> None:
    require(RENDER.exists(), 'Renderer source not found.')
    text = RENDER.read_text(encoding='utf-8')
    text = text.replace(
        '"LLM Coding Workflow Guide", "Design assumption", "Purpose", "Why this workflow works", "Quick start"',
        '"LLM Coding Workflow Guide", "What this guide is for", "Why the split works", "Workflow at a glance"',
    )
    text = text.replace('"Reference material",\n            "Keep repo docs fresh",', '"Reference material",\n            "Lightweight Issue and PR tracking",\n            "Group repo mode",\n            "Keep repo docs fresh",')
    text = text.replace('"PowerShell cheat sheet"', '"Terminal cheat sheet"')
    RENDER.write_text(text, encoding='utf-8')
    print('Aligned renderer navigation groups with updated guide headings.')


def main() -> int:
    update_guide()
    update_primer()
    update_renderer()
    SELF.write_text(NOOP, encoding='utf-8')
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    print('Reset patch helper and Apply guide patch workflow to manual no-op state.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

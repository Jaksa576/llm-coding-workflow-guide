#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
SELF = Path(__file__).resolve()

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

GROUP_SECTION = '''## Group project workflow

Use this reference workflow when more than one human contributor, more than one coding agent, or both may work on the same repo.

Keep the main solo workflow intact. Add a thin collaboration layer instead of turning the guide into a team-management system.

Recommended group model:

- `docs/current-task.md` explains the main project track.
- `docs/collaboration.md` defines group-work rules, not a live task board.
- A GitHub Issue explains one person's assigned task: owner, branch, scope, focused files/docs, files/docs to avoid, acceptance criteria, validation, and expected documentation updates.
- A Draft PR shows active branch work and should be opened early when multiple contributors are active.
- Discord is for discussion, quick updates, and webhook notifications. Durable decisions should be summarized back into repo docs when they affect product, architecture, roadmap, campaign status, or next action.

Do not use `docs/current-task.md` as a live task board for every contributor. Keep it focused on current status and the next main project action.

### Recommended group repo additions

For a group project, add:

```text
docs/collaboration.md
.github/ISSUE_TEMPLATE/work-item.md
.github/pull_request_template.md
```

Keep `AGENTS.md` as the shared coding-agent rulebook. Do not create person-specific agent files by default.

Update `AGENTS.md` so coding agents read `docs/collaboration.md` when group work is active and check active Issues, PRs, and related remote branches before coding.

### Contributor issue template

Use this shape for each assigned task:

```md
## Owner
{{Contributor name or GitHub handle}}

## Work item
{{Short description of the task}}

## Branch
{{branch-name}}

## Scope
- {{what this task may change}}

## Non-goals
- {{what this task must not change}}

## Focused files/docs
- {{files or docs expected to change}}

## Avoid
- {{files, docs, systems, or design areas to avoid}}

## Done when
- {{acceptance criteria}}

## Validation
- npm install
- {{repo test command, if relevant}}
- npm run build
- npm run dev / manual QA, if relevant

## Expected docs update
- {{which docs should be updated if this work changes project state}}
```

### Friend onboarding message

```md
For every task, use this flow:

1. Create or claim a GitHub Issue.
2. Put owner, branch, scope, focused files/docs, files/docs to avoid, done-when, validation, and expected docs updates in the Issue.
3. Create the branch.
4. Open a Draft PR early so the active branch is visible.
5. Use your AI coding tool only inside the Issue scope.
6. If the AI wants to touch files outside scope, pause and ask first.
7. Before review, make the AI update relevant repo docs, update the PR summary, run validation, commit, and push.

Main rule: do not let two humans or two AI agents independently redesign the same system at the same time.
```

### Prompt: start a group task

```md
I want to start a task in this repo without overlapping other work.

Please inspect the repo docs first:
- AGENTS.md
- docs/collaboration.md, if present
- docs/current-task.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- active docs/campaigns/*.md
- active docs/design/*.md, if relevant
- active GitHub Issues and PRs that may overlap this task

Task idea:
{{Describe what I want to work on}}

Please create a GitHub Issue draft with:
- title
- owner
- recommended branch name
- work item
- scope
- non-goals
- focused files/docs
- files/systems to avoid
- acceptance criteria
- validation steps
- expected documentation updates

Also tell me whether this task looks safe to do in parallel with current work, or whether I should ask before starting.
```

### Prompt: hand a group task to a coding agent

```md
You are working in this repo.

Before coding, read:
- AGENTS.md
- docs/collaboration.md, if present
- docs/current-task.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- active docs/campaigns/*.md
- active docs/design/*.md, if relevant

GitHub Issue:
{{Paste issue link or issue body}}

Branch:
{{branch name from the Issue}}

Rules:
- Work only on the Issue scope.
- Do not touch files/systems listed under Avoid.
- If you need to change files outside the scope, stop and report before editing.
- If another active branch/PR appears to touch the same files, stop and report the possible conflict.
- Open or update a Draft PR early if possible.
- Keep repo docs updated when project state changes.

Validation:
- {{repo install command}}
- {{repo test command, if relevant}}
- {{repo build command}}
- {{manual QA, if relevant}}

Before final report:
- Commit changes.
- Push the branch.
- Update the PR summary.
- Update relevant repo docs.
- Report validation results and documentation delta.
```

### Prompt: docs update check before finishing

```md
Before finishing, audit whether this branch requires repo doc updates.

Read:
- AGENTS.md
- docs/collaboration.md, if present
- docs/current-task.md
- active campaign docs
- docs/architecture.md
- docs/product.md
- docs/roadmap.md
- docs/design/*.md, if relevant

Branch work completed:
{{Summary of what changed}}

Decide which docs must be updated:
- docs/current-task.md if current status, next task, validation, or active branch changed
- active campaign doc if slice status changed
- docs/architecture.md if structure, systems, commands, or technical decisions changed
- docs/product.md if product scope or feature boundaries changed
- docs/roadmap.md if milestone status or sequencing changed
- docs/design/*.md if design decisions changed

Update only the docs that actually need changes. Do not create archive or backup docs.
```

### Prompt: final group-work report

```md
Prepare the final report for this branch and update the PR summary.

Include:
- Issue link
- branch
- summary
- files changed
- validation results
- documentation delta
- manual QA notes
- known risks
- follow-up work

Also confirm:
- branch is pushed
- PR is open or updated
- repo docs were updated if needed
- no out-of-scope files were changed
```

'''


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f'Expected text not found:\n{old[:300]}')
    return text.replace(old, new, 1)


def main() -> int:
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')

    text = GUIDE.read_text(encoding='utf-8')
    original = text

    text = replace_once(
        text,
        '- `docs/current-task.md` defines current status and the next action. Update it after every implementation.\n- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.\n',
        '- `docs/current-task.md` defines current status and the next main action. Update it after every implementation when status, validation, active branch, or next action changes.\n- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.\n- `docs/collaboration.md` is optional for group projects. It defines group-work rules, Issue/PR ownership conventions, AI-tool expectations, and Discord coordination. It should not become a live task board.\n- `.github/ISSUE_TEMPLATE/work-item.md` is optional for group projects. Use it to define owner, branch, scope, focused files/docs, files/docs to avoid, validation, and expected documentation updates.\n- `.github/pull_request_template.md` is optional for group projects. Use it to keep branch summary, validation, documentation delta, and review readiness visible.\n'
    )

    text = replace_once(
        text,
        '## Switching computers safely\n\nSwitching computers is a reference workflow for moving active work between machines. It is not part of one-time project setup.\n',
        GROUP_SECTION + '\n## Switching computers safely\n\nSwitching computers is a reference workflow for moving active work between machines. It is not part of one-time project setup.\n'
    )

    text = replace_once(
        text,
        '- docs/current-task.md\n- active docs/campaigns/*.md if relevant\n\nRules:\n',
        '- docs/current-task.md\n- docs/collaboration.md if group work is active\n- active docs/campaigns/*.md if relevant\n- active GitHub Issues and PRs if group work may overlap this task\n\nRules:\n'
    )

    text = replace_once(
        text,
        '- docs/current-task.md\n- active docs/campaigns/*.md if relevant\n\nIf Work mode is CAMPAIGN, produce a campaign document with:\n',
        '- docs/current-task.md\n- docs/collaboration.md if group work is active\n- active docs/campaigns/*.md if relevant\n- active GitHub Issues and PRs if group work may overlap this task\n\nIf Work mode is CAMPAIGN, produce a campaign document with:\n'
    )

    text = replace_once(
        text,
        '- docs/current-task.md\n- the active campaign doc if applicable\n\nThen create a lean LLM agent-ready handoff containing only what LLM agent needs for this task.\n',
        '- docs/current-task.md\n- docs/collaboration.md if group work is active\n- the active campaign doc if applicable\n- active GitHub Issues and PRs if group work may overlap this task\n\nThen create a lean LLM agent-ready handoff containing only what LLM agent needs for this task.\n'
    )

    text = replace_once(
        text,
        '- If the repo provides a branch-push verification script and the work uses a worktree, include it in validation or final-report expectations.\n- Do not create extra active-context files just to repeat the handoff; the handoff is the active execution packet and repo docs are durable truth.\n',
        '- If the repo provides a branch-push verification script and the work uses a worktree, include it in validation or final-report expectations.\n- For group work, include owner, linked Issue or assigned work item, branch, focused files/docs, files/docs/systems to avoid, and Draft PR expectations when applicable.\n- For group work, require the coding agent to check active Issues, PRs, and related remote branches before coding and to stop if another active branch appears to touch the same files or systems.\n- Do not create extra active-context files just to repeat the handoff; the handoff is the active execution packet and repo docs are durable truth.\n'
    )

    text = replace_once(
        text,
        '- known risks\n\n## Loop Step E - QA and decide merge or patch\n',
        '- known risks\n- PR link or draft PR status, when group work uses Issues/PRs\n\n## Loop Step E - QA and decide merge or patch\n'
    )

    if text == original:
        print('No guide changes were needed.')
    else:
        GUIDE.write_text(text, encoding='utf-8')
        print('Applied approved group collaboration guide patch.')

    SELF.write_text(NOOP, encoding='utf-8')
    print('Reset patch helper to no-op.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

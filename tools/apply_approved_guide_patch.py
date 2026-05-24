#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
PRIMER = ROOT / 'llm-workflow-primer.md'
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

STAGE_5A = '''## Stage 5A - Add group collaboration docs when needed

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

'''


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    require(old in text, f'Expected text not found for {label}.')
    return text.replace(old, new, 1)


def update_guide() -> None:
    text = GUIDE.read_text(encoding='utf-8')

    text = replace_once(
        text,
        'The default setup is **ChatGPT for planning** and **Codex or another LLM coding agent for implementation**. Windows-native PowerShell examples are used unless a project says otherwise.\n\nThe goal is not to create perfect prompts.',
        'The default setup is **ChatGPT for planning** and **Codex or another LLM coding agent for implementation**. Windows-native PowerShell examples are used unless a project says otherwise.\n\nThis workflow is especially valuable when ChatGPT planning and coding-agent execution have different token costs, context limits, latency, or ergonomics. It keeps exploratory planning in ChatGPT and sends the coding agent only the task-specific context it needs. If you use a tool where planning and implementation share the same context and token economics, such as an all-in-one coding environment, the workflow can still help with source-of-truth docs, reviewable slices, QA, and documentation freshness, but the token-efficiency advantage may be smaller.\n\nThe goal is not to create perfect prompts.',
        'top token-efficiency clarification',
    )

    text = replace_once(
        text,
        'Keep planning context and execution context separate. ChatGPT carries product thinking, roadmap decisions, QA triage, and handoff generation. The coding agent receives only the current task, source-of-truth docs, acceptance criteria, validation expectations, and documentation delta.\n\nThat separation keeps handoffs lean, reduces stale context, and makes projects easier to resume across chats, branches, devices, and collaborators.',
        'Keep planning context and execution context separate. ChatGPT carries product thinking, roadmap decisions, QA triage, and handoff generation. The coding agent receives only the current task, source-of-truth docs, acceptance criteria, validation expectations, and documentation delta.\n\nThat separation keeps handoffs lean, reduces stale context, and makes projects easier to resume across chats, branches, devices, and collaborators. It is also a token-routing strategy: do broad, messy planning where it is cheapest and most useful, then send the coding agent a narrow execution packet.',
        'split token routing clarification',
    )

    text = replace_once(
        text,
        '5. Bootstrap the project with a coding-agent handoff.\n6. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.',
        '5. Add `docs/collaboration.md` if this is a group repo or overlapping branch work is likely.\n6. Bootstrap the project with a coding-agent handoff.\n7. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.',
        'workflow at a glance collaboration step',
    )

    text = replace_once(
        text,
        'If this will be a group repo, also draft `docs/collaboration.md` with branch, Issue, Draft PR, review, and overlap-check expectations.',
        'If this will be a group repo, continue to **Stage 5A - Add group collaboration docs when needed** before committing the docs.',
        'stage 5 collaboration handoff pointer',
    )

    text = replace_once(
        text,
        'Output each file in a separate fenced markdown block with the file path as the heading.\n```\n\n\n## Stage 6 - Add the core docs to the repo',
        'Output each file in a separate fenced markdown block with the file path as the heading.\n```\n\n\n' + STAGE_5A + '## Stage 6 - Add the core docs to the repo',
        'insert stage 5a',
    )

    text = replace_once(
        text,
        'Create these files:\n\n- `AGENTS.md`\n- `docs/product.md`\n- `docs/architecture.md`\n- `docs/roadmap.md`\n- `docs/current-task.md`\n\nThen run:',
        'Create these files:\n\n- `AGENTS.md`\n- `docs/product.md`\n- `docs/architecture.md`\n- `docs/roadmap.md`\n- `docs/current-task.md`\n- `docs/collaboration.md` only when group work is active\n\nThen run:',
        'stage 6 file list collaboration doc',
    )

    text = replace_once(
        text,
        'git add AGENTS.md docs/product.md docs/architecture.md docs/roadmap.md docs/current-task.md',
        'git add AGENTS.md docs/product.md docs/architecture.md docs/roadmap.md docs/current-task.md\n# For group repos, also include:\ngit add docs/collaboration.md',
        'stage 6 git add collaboration doc',
    )

    text = replace_once(
        text,
        'Source-of-truth docs now in repo:\n- AGENTS.md\n- docs/product.md\n- docs/architecture.md\n- docs/roadmap.md\n- docs/current-task.md',
        'Source-of-truth docs now in repo:\n- AGENTS.md\n- docs/product.md\n- docs/architecture.md\n- docs/roadmap.md\n- docs/current-task.md\n- docs/collaboration.md, if group work is active',
        'stage 7 source docs collaboration doc',
    )

    text = replace_once(
        text,
        'For group work:\n\n- Use an Issue plus Draft PR for each meaningful work item.',
        'For group work:\n\n- Create `docs/collaboration.md` during setup or before the first group work item.\n- Use an Issue plus Draft PR for each meaningful work item.',
        'group repo mode setup doc bullet',
    )

    text = replace_once(
        text,
        '- Add `docs/collaboration.md` when collaboration rules, ownership, review expectations, or branch conventions need to be reusable across the project.',
        '- Add `docs/collaboration.md` when collaboration rules, ownership, review expectations, or branch conventions need to be reusable across the project. Use **Stage 5A - Add group collaboration docs when needed** for the setup prompt.',
        'group repo mode stage 5a pointer',
    )

    GUIDE.write_text(text, encoding='utf-8')
    print('Updated guide token-optimization clarification and Stage 5A collaboration doc setup.')


def update_primer() -> None:
    text = PRIMER.read_text(encoding='utf-8')
    text = replace_once(
        text,
        'Use ChatGPT for planning, roadmap decisions, QA triage, and coding-agent handoffs. Use an LLM coding agent such as Codex for repo-based implementation. The user remains the product owner and approves direction, QA, and merge decisions.',
        'Use ChatGPT for planning, QA triage, and handoffs; use Codex or another agent for repo implementation. This two-context split is most valuable when planning and coding have different token costs or context behavior. The user owns direction, QA, and merges.',
        'primer compact token-efficiency clarification',
    )
    text = replace_once(
        text,
        'For group work, Issues and Draft PRs are required. Each meaningful group work item should have an owner, branch, scope, focused files/docs, files/docs to avoid, validation expectations, and done-when criteria. Do not implement directly on `main` unless the repo explicitly allows it for the task. Add `docs/collaboration.md` when these rules need to be reusable across the repo. For solo campaign or long-running branch work, Issues and Draft PRs are recommended.',
        'For group work, Issues and Draft PRs are required. Each meaningful item needs an owner, branch, scope, focused files/docs, files/docs to avoid, validation, and done-when criteria. Add `docs/collaboration.md` during setup or before the first group work item. Solo long-running branches: recommended.',
        'primer compact collaboration setup clarification',
    )
    PRIMER.write_text(text, encoding='utf-8')
    print('Updated primer while keeping it under the compactness limit.')


def main() -> int:
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')
    if not PRIMER.exists():
        raise SystemExit('Primer source not found.')
    update_guide()
    update_primer()
    SELF.write_text(NOOP, encoding='utf-8')
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    print('Reset patch helper and Apply guide patch workflow to manual no-op state.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

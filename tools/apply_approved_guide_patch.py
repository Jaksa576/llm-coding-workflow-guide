#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
PRIMER = ROOT / 'llm-workflow-primer.md'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-guide-patch.yml'
HELPER = Path(__file__).resolve()

DEFAULT_WORKFLOW = '''name: Apply guide patch

on:
  push:
    branches: [main]
    paths:
      - tools/apply_approved_guide_patch.py
      - .github/workflows/apply-guide-patch.yml
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
            tools/apply_approved_guide_patch.py
            .github/workflows/apply-guide-patch.yml
'''

DEFAULT_HELPER = r'''#!/usr/bin/env python3
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


def insert_after(text: str, anchor: str, addition: str, label: str) -> str:
    if addition.strip() in text:
        return text
    index = text.find(anchor)
    if index < 0:
        raise SystemExit(f'Missing anchor for {label}: {anchor}')
    return text[: index + len(anchor)] + addition + text[index + len(anchor):]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        if new in text:
            return text
        raise SystemExit(f'Missing text for {label}')
    return text.replace(old, new, 1)


def patch_guide(text: str) -> str:
    text = insert_after(
        text,
        'Keep worktree setup in Codex project settings or helper scripts, not in every handoff prompt.',
        '\n\nAs a project matures, move repeated setup, validation, and branch-verification commands into repo-owned scripts or package commands. Handoffs should reference those helpers instead of re-teaching the LLM agent the same command sequence.',
        'Stage 2 helper guidance',
    )

    text = insert_after(
        text,
        'Keep repeatable setup and cleanup logic in repo helper scripts or Codex project settings, not in every handoff prompt. A handoff should mention worktree setup only when the task depends on it.',
        '\n\nIf a worktree uses a local branch, the work is not complete until the branch is committed, pushed to the remote repo, and verified as pushed. Prefer a repo-owned branch verification script, such as `.\\scripts\\verify-branch-pushed.ps1`, when the project provides one.',
        'Stage 2A branch-push guidance',
    )

    text = insert_after(
        text,
        'Codex handoff rule:\nDo not require a standard project/repository/header block by default. Codex should already have the project, repo, environment, and worktree settings configured. Include target branch, repo, or environment details only when the task needs them or when they are not obvious.',
        '\n\nIf the repo provides standard commands in `AGENTS.md`, package scripts, or `scripts/`, generated handoffs should reference those helpers instead of restating common setup and validation steps. Prefer repo-owned validation and branch-push verification commands, such as `npm run check`, `.\\scripts\\validate.ps1`, or `.\\scripts\\verify-branch-pushed.ps1`, when present.',
        'Stage 4 handoff optimization guidance',
    )

    text = insert_after(
        text,
        '- Include the expectation that Codex updates docs/current-task.md after every implementation.',
        '\n- For projects using worktrees, include that branch work must be pushed to the remote repo before final report.\n- If the repo has standard setup, validation, or branch-verification scripts, document them in `AGENTS.md` instead of repeating those commands in every handoff.',
        'Stage 5 repo docs requirements',
    )

    text = insert_after(
        text,
        'Do not include command-by-command worktree setup unless it is required for this specific task.',
        '\nIf the repo docs already define standard commands, the handoff should refer to them instead of listing the whole command sequence. If worktrees are used, require the branch to be pushed before final report.',
        'Stage 7 bootstrap handoff guidance',
    )

    text = insert_after(
        text,
        '- Do not include command-by-command setup unless explicitly needed.\n- Keep the handoff copy-paste ready.',
        '\n- Prefer repo-owned standard commands from `AGENTS.md`, package scripts, or `scripts/` for setup, validation, and branch verification.\n- If the repo provides a branch-push verification script and the work uses a worktree, include it in validation or final-report expectations.\n- Do not create extra active-context files just to repeat the handoff; the handoff is the active execution packet and repo docs are durable truth.',
        'Loop Step C rules',
    )

    text = replace_once(
        text,
        '4. Let LLM agent inspect docs, implement, validate, update docs, commit, and push.',
        '4. Let LLM agent inspect docs, implement, validate, update docs, commit, push, and verify the branch is pushed when a repo helper exists.',
        'Loop Step D implementation step',
    )

    text = insert_after(
        text,
        'A good LLM agent final report must include:\n\n- branch\n- commit',
        '\n- pushed remote branch, when work was done on a branch or worktree\n- branch-push verification result, when the repo provides a verification script',
        'Loop Step D final report fields',
    )

    text = insert_after(
        text,
        'Final report must include:\n- branch\n- commit',
        '\n- pushed remote branch, when work was done on a branch or worktree\n- branch-push verification result, when the repo provides a verification script',
        'Loop Step F final report fields',
    )

    repo_helpers_section = '''
## Token-efficient repo helpers

As a project matures, move repeated setup, validation, and branch hygiene into repo-owned helpers instead of repeating commands in every handoff.

Useful helpers include:

- a single package validation command, such as `npm run check`
- a setup script, such as `.\\scripts\\setup-codex-worktree.ps1`
- a validation script, such as `.\\scripts\\validate.ps1`
- a branch-push verification script, such as `.\\scripts\\verify-branch-pushed.ps1`
- a small command menu in `AGENTS.md`

Use these helpers to keep handoffs short. The handoff should say what to accomplish, what docs to inspect, and what acceptance criteria matter. The repo should own repeatable command details.

Do not create a separate active-context file just to duplicate the handoff. The handoff is the active execution packet for the current run. Repo docs are the durable source of truth, and `docs/current-task.md` should stay concise enough to point to current status and next action without becoming a long final-report archive.

For worktree-based development, local-only completion is not enough. The LLM agent should commit, push the branch to the remote repo, run the repo's branch verification helper when one exists, and include the pushed branch plus verification result in the final report.

'''
    text = insert_after(
        text,
        "## Documentation delta\n\nEvery LLM agent final report should include a documentation delta.\n\n```md\nDocumentation delta:\n- docs/current-task.md: {{Summarize what changed in docs/current-task.md}}\n- campaign doc, if applicable: {{Summarize what changed, or write 'not applicable'}}\n- docs/architecture.md: {{Summarize what changed, or write 'not applicable'}}\n- docs/roadmap.md: {{Summarize what changed, or write 'not applicable'}}\n```\n\n",
        repo_helpers_section,
        'Token-efficient repo helpers section',
    )

    text = replace_once(
        text,
        'Validation:\n- {{what commands, tests, preview checks, or manual checks should be run:}}',
        "Validation:\n- {{what commands, tests, preview checks, or manual checks should be run:}}\n- Prefer the repo's standard validation command or script when present, such as `npm run check` or `.\\scripts\\validate.ps1`.",
        'Minimal handoff validation guidance',
    )

    text = insert_after(
        text,
        'Final report:\n- branch\n- commit',
        '\n- pushed remote branch, when work was done on a branch or worktree\n- branch-push verification result, when the repo provides a verification script',
        'Minimal handoff final report fields',
    )

    branch_script_section = '''
Good branch-verification scripts should:

- fail on `main` unless explicitly allowed
- fail when uncommitted changes exist
- fetch and prune remote refs
- verify the current branch has an upstream
- verify local `HEAD` is pushed to the upstream branch
- fail if the local branch is ahead of the remote branch

'''
    text = insert_after(
        text,
        'Good cleanup scripts should:\n\n- remove only disposable generated folders\n- never delete source files, docs, migrations, config, or local secrets\n- be safe to run more than once\n\n',
        branch_script_section,
        'Branch verification script guidance',
    )

    text = replace_once(
        text,
        'git push origin {{Branch name}}',
        'git push -u origin {{Branch name}}\n# If the repo provides one, then run:\n.\\scripts\\verify-branch-pushed.ps1',
        'PowerShell push command',
    )

    return text


def patch_primer(text: str) -> str:
    text = insert_after(
        text,
        'Do not restate all project context when the repo docs already contain it. Keep handoffs copy-paste ready.',
        '\n\nWhen the repo provides standard setup, validation, or branch-verification scripts, reference those helpers instead of restating command sequences. For worktree branches, require the coding agent to push the branch and report branch-push verification when the repo provides that helper.',
        'Primer handoff helper guidance',
    )
    return text


def main() -> int:
    guide = GUIDE.read_text(encoding='utf-8')
    primer = PRIMER.read_text(encoding='utf-8')

    guide = patch_guide(guide)
    primer = patch_primer(primer)

    GUIDE.write_text(guide, encoding='utf-8')
    PRIMER.write_text(primer, encoding='utf-8')
    WORKFLOW.write_text(DEFAULT_WORKFLOW, encoding='utf-8')
    HELPER.write_text(DEFAULT_HELPER, encoding='utf-8')

    print('Applied token-efficient handoff and branch-verification guide updates.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

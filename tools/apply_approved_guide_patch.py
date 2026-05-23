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


def patch_guide(text: str) -> str:
    stage_2b = r'''

## Stage 2B - Switching computers safely

Switching computers should be a GitHub checkpoint and resume workflow, not a local-folder sync workflow.

Default to a **clean project switch** whenever possible: finish or pause at a safe checkpoint, commit real work, push the branch, verify the branch is available on GitHub, and make sure the next action is clear before leaving the current computer.

Use three switch types:

- **Clean project switch:** the normal path. Use this when the current slice, patch, or checkpoint is committed and pushed.
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

Do not create a new repo file just because you are switching computers. If the project is mid-campaign and the next action would otherwise be unclear, provide a short passoff in ChatGPT or include it with the LLM agent final report. Update `docs/current-task.md` only when the actual project state or next action changed.

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

If this is the first time using the project with Codex or another coding agent on the new computer, configure the local coding-agent project before giving it implementation work:

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
- active docs/campaigns/*.md if relevant

Then confirm:
1. current branch
2. git status
3. repo docs are readable
4. standard local commands from AGENTS.md or package scripts
5. whether anything appears missing from the local setup

Do not change files yet. Stop after reporting readiness.
```
'''

    text = insert_after(
        text,
        'If you use worktrees, see **Optional Codex worktrees** in the reference material for setup and cleanup templates.',
        stage_2b,
        'Stage 2B computer switching section',
    )

    computer_switch_prompt = r'''

## Computer switch check prompt

Use this before moving active work to another computer, especially during a campaign or patch.

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
'''

    text = insert_after(
        text,
        'After the source-of-truth check, answer my request:\n{{What do you want ChatGPT to answer or help with?}}\n```',
        computer_switch_prompt,
        'Computer switch check prompt',
    )

    powershell_resume = r'''

### Resume on another computer

```powershell
Set-Location C:\Code\{{Project folder}}
git fetch --all --prune
git checkout {{Branch name}}
git pull --ff-only
npm install
npm run build
git status
```

Do not copy `node_modules`, build output, coverage folders, or local runtime logs between computers. Restore only required local-only secrets or machine settings, and never commit them.
'''

    text = insert_after(
        text,
        'git log --oneline --decorate -5\n```',
        powershell_resume,
        'PowerShell resume on another computer commands',
    )

    return text


def patch_primer(text: str) -> str:
    addition = r'''

## Switching computers

Use GitHub as the sync layer when moving between computers. Before leaving a computer, commit and push meaningful work, verify the branch is available on GitHub, and make sure the next action is clear in repo docs, a final report, or a short ChatGPT passoff.

On the new computer, clone or pull from GitHub, recreate generated state with the repo's normal setup commands, restore only required local-only secrets or machine settings, and configure the local coding-agent project if it does not already exist. Do not copy generated folders, runtime logs, local worktrees, or coding-agent cache/state as the source of truth.
'''
    return insert_after(
        text,
        'Do not assume WSL. Use Windows paths such as `C:\\Code\\ProjectName` when examples are needed.',
        addition,
        'Primer switching computers section',
    )


def main() -> int:
    guide = GUIDE.read_text(encoding='utf-8')
    primer = PRIMER.read_text(encoding='utf-8')

    guide = patch_guide(guide)
    primer = patch_primer(primer)

    GUIDE.write_text(guide, encoding='utf-8')
    PRIMER.write_text(primer, encoding='utf-8')
    WORKFLOW.write_text(DEFAULT_WORKFLOW, encoding='utf-8')
    HELPER.write_text(DEFAULT_HELPER, encoding='utf-8')

    print('Applied computer-switching workflow guide updates.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

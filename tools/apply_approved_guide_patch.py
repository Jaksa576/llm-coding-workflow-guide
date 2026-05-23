#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
RENDER = ROOT / 'tools' / 'render_guide.py'
WORKFLOW = ROOT / '.github' / 'workflows' / 'apply-guide-patch.yml'
HELPER = Path(__file__).resolve()

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

DEFAULT_HELPER = '''#!/usr/bin/env python3
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


def cut_section(text: str, start_heading: str, next_heading: str) -> tuple[str, str]:
    start = text.find(start_heading)
    if start < 0:
        return text, ''
    end = text.find(next_heading, start + len(start_heading))
    if end < 0:
        raise SystemExit(f'Missing following heading: {next_heading}')
    section = text[start:end].strip() + '\n\n'
    text = text[:start].rstrip() + '\n\n' + text[end:]
    return text, section


def clean_switching_section(section: str) -> str:
    section = section.replace('## Stage 2B - Switching computers safely', '## Switching computers safely', 1)
    old_open = 'Switching computers should be a GitHub checkpoint and resume workflow, not a local-folder sync workflow.\n\nDefault to a **clean project switch** whenever possible: finish or pause at a safe checkpoint, commit real work, push the branch, verify the branch is available on GitHub, and make sure the next action is clear before leaving the current computer.'
    new_open = 'Switching computers is a reference workflow for moving active work between machines. It is not part of one-time project setup.\n\nUse GitHub as the sync layer. Do not try to sync local coding-agent state, generated folders, local worktrees, or runtime files between computers.\n\nDefault to a **clean project switch** whenever possible: finish or pause at a safe checkpoint, commit real work, push the branch, verify the branch is available on GitHub, and make sure the next action is clear before leaving the current computer.'
    section = section.replace(old_open, new_open, 1)
    duplicate_start = section.find('\n### Resume on another computer\n')
    if duplicate_start >= 0:
        duplicate_end = section.find('\nIf there are meaningful changes that should travel to the next computer:', duplicate_start)
        if duplicate_end >= 0:
            section = section[:duplicate_start].rstrip() + '\n\n' + section[duplicate_end:].lstrip()
    section = section.replace('If this is the first time using the project with Codex or another coding agent on the new computer, configure the local coding-agent project before giving it implementation work:', 'If this is the first time using the project with Codex or another coding agent on the new computer, return to **Stage 2 - Configure Codex before handoffs** and configure the local coding-agent project before giving it implementation work:', 1)
    return section.strip() + '\n\n'


def patch_guide(text: str) -> str:
    text, section = cut_section(text, '## Stage 2B - Switching computers safely', '## Stage 3 - Define the project')
    if not section:
        text, section = cut_section(text, '## Switching computers safely', '## Docs health check')
    if not section:
        raise SystemExit('Switching computers section not found.')
    section = clean_switching_section(section)
    insert_anchor = "For worktree-based development, local-only completion is not enough. The LLM agent should commit, push the branch to the remote repo, run the repo's branch verification helper when one exists, and include the pushed branch plus verification result in the final report.\n\n"
    if insert_anchor not in text:
        raise SystemExit('Reference insertion anchor missing.')
    return text.replace(insert_anchor, insert_anchor + section, 1)


def patch_renderer(text: str) -> str:
    text = text.replace('            "Stage 2B - Switching computers safely",\n', '')
    if '            "Switching computers safely",\n' not in text:
        text = text.replace('            "Token-efficient repo helpers",\n', '            "Token-efficient repo helpers",\n            "Switching computers safely",\n', 1)
    return text


def main() -> int:
    GUIDE.write_text(patch_guide(GUIDE.read_text(encoding='utf-8')), encoding='utf-8')
    RENDER.write_text(patch_renderer(RENDER.read_text(encoding='utf-8')), encoding='utf-8')
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    HELPER.write_text(DEFAULT_HELPER, encoding='utf-8')
    print('Moved computer switching from setup into reference material.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

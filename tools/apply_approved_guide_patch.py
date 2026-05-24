#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
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

OLD = '''## PowerShell cheat sheet

### Navigation

```powershell
Set-Location C:\\Code\\{{Project folder}}
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
.\\scripts\\verify-branch-pushed.ps1
```

### Local development

```powershell
npm install
npm run dev
npm test
npm run build
```

### Clean generated files

```powershell
Remove-Item -Recurse -Force .next,node_modules,coverage,playwright-report,test-results -ErrorAction SilentlyContinue
```
'''

NEW = '''## Terminal cheat sheet

These commands are written for a Windows-native PowerShell terminal. If a project uses a different shell, adapt the path and process-management syntax instead of assuming WSL.

### Navigation

```powershell
Set-Location C:\\Code\\{{Project folder}}
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
.\\scripts\\verify-branch-pushed.ps1
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

Use this only when `Ctrl+C` did not close the dev server. Replace the port with the port shown by the dev server, such as `3000`, `5173`, or `8080`.

```powershell
$port = 5173
$devServer = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($devServer) {
  Get-Process -Id $devServer.OwningProcess
  Stop-Process -Id $devServer.OwningProcess -Force
} else {
  Write-Host "No dev server is listening on port $port."
}
```

### Clean generated files

```powershell
Remove-Item -Recurse -Force .next,node_modules,coverage,playwright-report,test-results -ErrorAction SilentlyContinue
```
'''


def main() -> int:
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')

    text = GUIDE.read_text(encoding='utf-8')
    if OLD not in text:
        raise SystemExit('Expected PowerShell cheat sheet block was not found.')

    GUIDE.write_text(text.replace(OLD, NEW, 1), encoding='utf-8')
    print('Updated terminal cheat sheet and local dev shutdown guidance.')

    SELF.write_text(NOOP, encoding='utf-8')
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    print('Reset patch helper and Apply guide patch workflow to manual no-op state.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

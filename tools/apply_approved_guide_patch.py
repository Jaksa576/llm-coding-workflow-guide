#!/usr/bin/env python3
"""Reusable helper for applying approved guide edits.

This temporary patch performs the approved cleanup of the generated guide's
post-loop reference material, then resets this helper and the patch workflow to
safe no-op/manual defaults.
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "llm_coding_workflow_guide.md"
PRIMER = ROOT / "llm-workflow-primer.md"
WORKFLOW = ROOT / ".github" / "workflows" / "apply-guide-patch.yml"
HELPER = Path(__file__).resolve()

DEFAULT_WORKFLOW = """name: Apply guide patch

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  apply-guide-patch:
    runs-on: ubuntu-latest
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
"""

DEFAULT_HELPER = r'''#!/usr/bin/env python3
"""Reusable helper for applying approved guide edits.

This script is intentionally small and conservative. It gives future guide edits a
checked-in place for section replacements and guardrails instead of embedding large
patch scripts in temporary workflow YAML.

Typical use:
1. Add or edit a small patch function in this file.
2. Run this script.
3. Run tools/render_guide.py.
4. Run tools/validate_guide.py.
5. Commit the source changes and generated HTML.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "llm_coding_workflow_guide.md"
PRIMER = ROOT / "llm-workflow-primer.md"


@dataclass
class EditReport:
    label: str
    count: int


class PatchContext:
    def __init__(self) -> None:
        self.reports: list[EditReport] = []
        self.guide = GUIDE.read_text(encoding="utf-8")
        self.primer = PRIMER.read_text(encoding="utf-8") if PRIMER.exists() else ""

    def replace_exact(self, target: str, old: str, new: str, label: str, *, required: bool = True) -> None:
        text = getattr(self, target)
        count = text.count(old)
        if count == 0:
            if required:
                raise SystemExit(f"Missing expected text for replacement: {label}")
            print(f"SKIP: {label}")
            return
        setattr(self, target, text.replace(old, new))
        self.reports.append(EditReport(label, count))

    def replace_between(self, target: str, start: str, end: str, replacement: str, label: str) -> None:
        text = getattr(self, target)
        start_index = text.find(start)
        if start_index < 0:
            raise SystemExit(f"Missing start marker for {label}: {start}")
        end_index = text.find(end, start_index + len(start))
        if end_index < 0:
            raise SystemExit(f"Missing end marker for {label}: {end}")
        setattr(self, target, text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:])
        self.reports.append(EditReport(label, 1))

    def replace_regex(self, target: str, pattern: str, replacement: str, label: str, *, required: bool = True, flags: int = re.S) -> None:
        text = getattr(self, target)
        new_text, count = re.subn(pattern, replacement, text, flags=flags)
        if count == 0:
            if required:
                raise SystemExit(f"Missing regex match for {label}")
            print(f"SKIP: {label}")
            return
        setattr(self, target, new_text)
        self.reports.append(EditReport(label, count))

    def assert_absent(self, target: str, terms: list[str], label: str) -> None:
        text = getattr(self, target)
        lowered = text.lower()
        for term in terms:
            index = lowered.find(term.lower())
            if index >= 0:
                start = max(0, index - 160)
                end = min(len(text), index + 240)
                print(f"Forbidden term remains in {label}: {term}")
                print(text[start:end])
                raise SystemExit(1)

    def write(self) -> None:
        GUIDE.write_text(self.guide, encoding="utf-8")
        if PRIMER.exists():
            PRIMER.write_text(self.primer, encoding="utf-8")
        for report in self.reports:
            print(f"UPDATED: {report.label} ({report.count})")


def apply_noop_patch(ctx: PatchContext) -> None:
    """Default patch placeholder.

    Future approved edits should replace this body with small, named operations.
    Keeping the helper checked in lets workflow/YAML stay simple and reusable.
    """
    print("No patch operations configured. Add approved edits to apply_noop_patch().")


def main() -> int:
    ctx = PatchContext()
    apply_noop_patch(ctx)
    ctx.write()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


@dataclass
class EditReport:
    label: str
    count: int


class PatchContext:
    def __init__(self) -> None:
        self.reports: list[EditReport] = []
        self.guide = GUIDE.read_text(encoding="utf-8")
        self.primer = PRIMER.read_text(encoding="utf-8") if PRIMER.exists() else ""

    def replace_between(self, target: str, start: str, end: str, replacement: str, label: str) -> None:
        text = getattr(self, target)
        start_index = text.find(start)
        if start_index < 0:
            raise SystemExit(f"Missing start marker for {label}: {start}")
        end_index = text.find(end, start_index + len(start))
        if end_index < 0:
            raise SystemExit(f"Missing end marker for {label}: {end}")
        setattr(self, target, text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:])
        self.reports.append(EditReport(label, 1))

    def replace_regex(self, target: str, pattern: str, replacement: str, label: str, *, flags: int = re.S) -> None:
        text = getattr(self, target)
        new_text, count = re.subn(pattern, replacement.rstrip() + "\n", text, flags=flags)
        if count == 0:
            raise SystemExit(f"Missing regex match for {label}")
        setattr(self, target, new_text)
        self.reports.append(EditReport(label, count))

    def assert_absent(self, target: str, terms: list[str], label: str) -> None:
        text = getattr(self, target)
        lowered = text.lower()
        for term in terms:
            index = lowered.find(term.lower())
            if index >= 0:
                start = max(0, index - 160)
                end = min(len(text), index + 240)
                print(f"Forbidden term remains in {label}: {term}")
                print(text[start:end])
                raise SystemExit(1)

    def write(self) -> None:
        GUIDE.write_text(self.guide, encoding="utf-8")
        if PRIMER.exists():
            PRIMER.write_text(self.primer, encoding="utf-8")
        for report in self.reports:
            print(f"UPDATED: {report.label} ({report.count})")


def apply_noop_patch(ctx: PatchContext) -> None:
    stage_2a = """
## Stage 2A - Optional Codex worktrees

Codex worktrees are optional. Use them when you want isolated implementation branches, parallel slices, or safer experimentation without disturbing your main local checkout.

Keep repeatable setup and cleanup logic in repo helper scripts or Codex project settings, not in every handoff prompt. A handoff should mention worktree setup only when the task depends on it.

If you use worktrees, see **Optional Codex worktrees** in the reference material for setup and cleanup templates.
"""
    ctx.replace_between(
        "guide",
        "## Stage 2A - Optional Codex worktree setup and cleanup scripts",
        "## Stage 3 - Define the project",
        textwrap.dedent(stage_2a),
        "shorten Stage 2A and move scripts to reference",
    )

    reference_material = r'''
# Reference material

Use this section when the main workflow points you to supporting material. It is deliberately shorter than the old appendices: the main workflow stays actionable, and reference material stays available without becoming a second manual.

## Keep repo docs fresh

Use `docs/current-task.md` as the active work pointer for current status and next action.

Codex should update `docs/current-task.md` after every implementation. Update campaign docs when slice status changes. Update `docs/architecture.md` or `docs/roadmap.md` only when the work changes architecture, routes, services, deployment, milestone status, scope, or sequencing.

ChatGPT should inspect repo docs at the target branch whenever current state matters. Chat memory and prior final reports are orientation only; repo docs are authoritative.

Golden rules:

1. The repo is durable memory. Chats are temporary.
2. Current-state checks beat chat memory.
3. Keep Codex handoffs lean and task-specific.
4. Prefer reviewable slices over vague large changes.
5. Codex updates docs after implementation.
6. The user approves product direction, QA judgment, and merge decisions.
7. Remove stale detail from the hot path instead of letting it bury the next action.

## Documentation delta

Every Codex final report should include a documentation delta.

```md
Documentation delta:
- docs/current-task.md: {{Summarize what changed in docs/current-task.md}}
- campaign doc, if applicable: {{Summarize what changed, or write "not applicable"}}
- docs/architecture.md: {{Summarize what changed, or write "not applicable"}}
- docs/roadmap.md: {{Summarize what changed, or write "not applicable"}}
```

## Docs health check

Run a docs health check after a campaign, before a major campaign, or whenever docs seem stale. Do not make this a weekly chore unless the project is moving quickly.

```md
Create a Codex-ready docs health check handoff.

Target branch:
{{What is the target branch?}}

Reason for audit:
{{Why are you running this docs health check?}}

Goal:
Audit and update project documentation so the hot-path docs accurately reflect the current project state.

Read first from repo docs at the target branch:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- active docs/campaigns/*.md if relevant
- recent git history

Scope:
Documentation only. Do not implement app features.

Tasks:
1. Identify stale, conflicting, or bloated docs.
2. Update docs/current-task.md so it reflects current status and next action.
3. Update the active campaign doc only if slice or campaign status is stale.
4. Update docs/architecture.md only if architecture changed.
5. Update docs/roadmap.md only if roadmap status changed.
6. Remove obsolete detail from hot-path docs when it clearly no longer helps current work.
7. Preserve uncertainty instead of guessing.

Validation:
- Confirm docs agree on the active campaign or active work item.
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

Current situation:
{{Briefly describe why you need a source-of-truth check}}

Target branch:
{{What is the target branch?}}

Please inspect repo docs at the target branch for the latest versions of:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- active docs/campaigns/*.md if relevant

Rules:
- Do not rely on memory or prior chat assumptions.
- Treat repo docs as authoritative.
- If connector access is unavailable or a file is missing, ask me to paste or upload only the specific missing files.
- If the branch is unmerged, do not assume main includes the branch changes.
- If docs conflict, call out the conflict before making recommendations.

After the source-of-truth check, answer my request:
{{What do you want ChatGPT to answer or help with?}}
```

## Minimal Codex handoff shape

Use this as the default structure for normal campaign slices, standalone slices, and patches. Add repo, branch, environment, or worktree details only when the task depends on them or when they are not already configured in Codex.

```md
Goal:
{{What should Codex accomplish?}}

Read first:
- AGENTS.md
- docs/product.md
- docs/architecture.md
- docs/roadmap.md
- docs/current-task.md
- {{Active campaign doc, if applicable}}

Readiness gate:
Before coding, confirm the docs, target branch, and requested scope agree. If they conflict, stop and report the conflict.

Scope:
- {{What is in scope?}}

Non-goals:
- {{What should Codex avoid?}}

Acceptance criteria:
- {{What must be true when the work is complete?}}

Validation:
- {{What commands, tests, preview checks, or manual checks should be run?}}

Documentation delta:
Update docs/current-task.md and any campaign, architecture, or roadmap docs affected by the work.

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
- `docs/roadmap.md` defines milestones, sequencing, campaign backlog, and deferred work. Update it when scope or order changes.
- `docs/current-task.md` defines current status and the next action. Update it after every implementation.
- `docs/campaigns/*.md` tracks active multi-slice efforts. Update the active campaign doc when slice status, acceptance criteria, or follow-up backlog changes.

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

Generic cleanup template:

```powershell
$ErrorActionPreference = "Stop"

Write-Host "Running Codex cleanup script from:" (Get-Location)

$pathsToRemove = @(
  ".next",
  "node_modules",
  "coverage",
  "playwright-report",
  "test-results",
  ".vercel",
  ".turbo"
)

foreach ($path in $pathsToRemove) {
  if (Test-Path $path) {
    Write-Host "Removing disposable path: $path"
    Remove-Item -Recurse -Force $path -ErrorAction SilentlyContinue
  } else {
    Write-Host "Not present, skipping: $path"
  }
}

Write-Host "Codex cleanup complete."
```

Generic setup template:

```powershell
$ErrorActionPreference = "Stop"

# App-specific settings
$SourceEnvPath = "{{Optional path to source .env.local, or leave blank}}"
$RequiredEnvKeys = @(
  "{{OPTIONAL_REQUIRED_ENV_KEY}}"
)
$RequiredRepoFiles = @(
  "package.json"
)
$InstallCommand = "npm install"

Write-Host "Codex Worktree Setup"
Write-Host "Working directory:" (Get-Location)

Write-Host "Tool versions:"
git --version
if (Get-Command node -ErrorAction SilentlyContinue) { node -v }
if (Get-Command npm -ErrorAction SilentlyContinue) { npm -v }
if (Get-Command gh -ErrorAction SilentlyContinue) { gh --version }

Write-Host "Fetching latest Git refs..."
git fetch --all --prune
if ($LASTEXITCODE -ne 0) {
  throw "Git fetch failed. Cannot verify worktree freshness."
}

$head = (git rev-parse HEAD).Trim()
$matchingRefs = @(
  git for-each-ref refs/heads refs/remotes --format='%(refname:short) %(objectname)' |
    Where-Object { -not $_.StartsWith("origin/HEAD ") } |
    ForEach-Object {
      $parts = $_ -split ' '
      if ($parts.Length -ge 2 -and $parts[1] -eq $head) { $parts[0] }
    }
)

if ($matchingRefs.Count -eq 0) {
  git log --oneline --decorate -5
  throw "Stopping setup: this worktree HEAD is not the current tip of any known local or remote branch after fetch."
}

foreach ($file in $RequiredRepoFiles) {
  if (-not (Test-Path $file)) {
    throw "Required repo file not found: $file. Run this script from the project root or update RequiredRepoFiles."
  }
}

$targetEnv = Join-Path (Get-Location) ".env.local"
if (-not (Test-Path $targetEnv) -and -not [string]::IsNullOrWhiteSpace($SourceEnvPath)) {
  if (-not (Test-Path $SourceEnvPath)) {
    throw ".env.local missing in worktree and source path does not exist: $SourceEnvPath"
  }
  Copy-Item $SourceEnvPath $targetEnv -Force -ErrorAction Stop
  Write-Host ".env.local copied into worktree."
}

if ($RequiredEnvKeys.Count -gt 0) {
  if (-not (Test-Path $targetEnv)) {
    throw ".env.local is required but missing."
  }
  foreach ($key in $RequiredEnvKeys) {
    if ([string]::IsNullOrWhiteSpace($key) -or $key.StartsWith("{")) { continue }
    if (-not (Select-String -Path $targetEnv -Pattern "^$key=" -Quiet)) {
      throw "$key missing from .env.local"
    }
  }
  Write-Host ".env.local validation passed."
}

if (-not [string]::IsNullOrWhiteSpace($InstallCommand)) {
  Write-Host "Running dependency install command: $InstallCommand"
  Invoke-Expression $InstallCommand
  if ($LASTEXITCODE -ne 0) { throw "Dependency install command failed." }
}

Write-Host "Codex environment setup complete."
```

## PowerShell cheat sheet

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
git commit -m "{{Short commit message}}"
git push origin {{Branch name}}
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

## Key terms

- **Planning LLM:** The conversational model used for strategy, planning, QA triage, and handoff generation.
- **Coding agent:** The tool that works directly in the repo to edit files, run checks, commit, and push.
- **Source-of-truth docs:** The repo docs that define current product, architecture, roadmap, and active work.
- **Campaign:** A large swath of related work broken into reviewable slices.
- **Slice:** One independently reviewable implementation unit inside a campaign or standalone effort.
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
- Campaign and slice planning prompts
- Codex handoff prompts
- QA review prompts
- Patch prompts
- Docs health check prompts

Rule: save reusable prompts, but keep project-specific truth in repo docs. Do not let a prompt library become a hidden source of truth.
'''
    ctx.replace_regex(
        "guide",
        r"# Documentation freshness system[\s\S]*\Z",
        textwrap.dedent(reference_material),
        "replace post-loop protocols and appendices with compact reference material",
    )
    ctx.assert_absent("guide", ["docs/project-state.json", "project-state", "Appendix A", "Appendix F", "Appendix H", "Appendix I"], "cleaned guide")
    WORKFLOW.write_text(DEFAULT_WORKFLOW, encoding="utf-8")
    HELPER.write_text(DEFAULT_HELPER, encoding="utf-8")
    print("Reset approved patch helper and workflow to defaults.")


def main() -> int:
    ctx = PatchContext()
    apply_noop_patch(ctx)
    ctx.write()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

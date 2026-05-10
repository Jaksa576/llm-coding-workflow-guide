# Guide Maintenance Playbook

This file is the detailed maintenance source for the LLM Coding Workflow Guide project. Keep the ChatGPT Project Instructions short and use this file for detailed workflow rules, validation expectations, troubleshooting, and update policy.

## Purpose

Use this file when maintaining the guide repo, diagnosing generated HTML issues, updating the renderer, or deciding how to handle GitHub Actions failures.

The short ChatGPT Project Instructions should point here instead of trying to contain every maintenance detail.

## Canonical files

Repository: `Jaksa576/llm-coding-workflow-guide`

Default branch: `main`

Core files:

- `llm_coding_workflow_guide.md` — canonical Markdown content source.
- `llm_coding_workflow_guide.html` — generated rendered HTML interface.
- `llm-workflow-primer.md` — compact primer for app-specific ChatGPT Projects.
- `llm_coding_workflow_diagram.png` — visual reference only.
- `tools/render_guide.py` — renderer that generates HTML from Markdown.
- `tools/validate_guide.py` — validation script for generated HTML.
- `tools/apply_approved_guide_patch.py` — reusable helper for approved multi-section guide edits.
- `.github/workflows/build-guide.yml` — GitHub Actions workflow that renders and validates HTML.
- `.github/workflows/apply-guide-patch.yml` — manual workflow for checked-in approved patch helper runs.
- `docs/guide-maintenance.md` — this detailed maintenance playbook.

## Source-of-truth order

Use sources in this order:

1. Current files from GitHub `main`.
2. Files uploaded in the current conversation, only if explicitly requested for comparison, override, recovery, or migration.
3. Older uploaded files, Drive copies, ZIP bundles, DOCX files, or previous versions only when explicitly requested.
4. Prior chat context only as orientation, never as source of truth.

If GitHub `main` conflicts with uploaded files, prefer GitHub `main` and call out the conflict.

## Normal update workflow

For ordinary guide updates:

1. Inspect the latest files on GitHub `main`.
2. Identify the smallest useful change.
3. Update `llm_coding_workflow_guide.md` first for content changes.
4. Update `llm-workflow-primer.md` only when compact reusable workflow rules change.
5. Avoid editing `llm_coding_workflow_guide.html` directly.
6. Commit source/tool changes directly to `main`.
7. Let GitHub Actions regenerate and validate the HTML.
8. Report source commit SHA, generated HTML status, validation status, and anything intentionally not changed.

Do not create a branch or PR by default. Use Git history as the rollback/archive mechanism.

## Approved patch helper workflow

For simple edits, update the source files directly and let `Build guide HTML` regenerate the output.

For large, multi-section, or repetitive approved edits, prefer the checked-in helper instead of temporary one-off workflow YAML:

1. Put the approved text transformations in `tools/apply_approved_guide_patch.py`.
2. Keep the workflow YAML small; do not embed large Markdown replacement blocks in workflow files.
3. Run the helper through `.github/workflows/apply-guide-patch.yml` or locally with Python.
4. The helper workflow should run the patch helper, render the HTML, validate the guide, and commit source plus generated HTML together.
5. After the patch lands, reset the helper to a no-op or leave only reusable helper functions.

This avoids lossy large-file replacement through the connector and prevents brittle YAML failures caused by embedded Markdown, PowerShell, or prompt templates.

## Direct-to-main policy

For this project, direct commits to `main` are preferred after validation.

Only create a branch or PR if:

- the user explicitly asks for one, or
- GitHub blocks direct writes to `main`.

Do not create visible archive snapshots, version folders, backup files, or duplicate guide files unless explicitly requested.

## Generated HTML policy

`llm_coding_workflow_guide.html` is generated output.

For normal content changes, do not manually replace the HTML file through the ChatGPT GitHub connector. Instead:

1. Update Markdown/source/tool files.
2. Let GitHub Actions run `Build guide HTML` or `Apply guide patch`.
3. Let the workflow commit regenerated HTML if it changed.

Manual HTML replacement is a fallback only if automation is broken and the user explicitly asks for manual recovery.

## GitHub Actions workflows

The primary workflow is `.github/workflows/build-guide.yml`.

It should:

1. Check out the repo.
2. Set up Python.
3. Run `python tools/render_guide.py`.
4. Run `python tools/validate_guide.py`.
5. Commit `llm_coding_workflow_guide.html` back to `main` if it changed.

The manual patch workflow is `.github/workflows/apply-guide-patch.yml`.

It should:

1. Check out the repo.
2. Set up Python.
3. Run `python tools/apply_approved_guide_patch.py`.
4. Run `python tools/render_guide.py`.
5. Run `python tools/validate_guide.py`.
6. Commit the source changes, helper changes, primer changes, and generated HTML if they changed.

If a workflow does not run automatically, ask the user to run it manually from Actions on branch `main`.

If a workflow completes but no new generated commit appears, that usually means the rendered HTML did not change.

## Renderer expectations

`tools/render_guide.py` should preserve the existing static guide UX:

- sidebar navigation
- sidebar filtering/search
- collapsible nav groups
- bookmark links
- copy buttons
- key-term tooltips
- prompt/code blocks
- external diagram reference to `llm_coding_workflow_diagram.png`
- generated-guide callout near the top of the HTML

The renderer should not turn the static guide into a larger app. Keep it maintainable and lightweight.

Navigation grouping should be explicit and validated. If section names change, update both the renderer `GROUPS` list and validator expectations so sections do not drift into `Other sections` unexpectedly.

## Validation expectations

`tools/validate_guide.py` is the CI validation source.

It should check:

- sidebar navigation links exist
- every sidebar link points to an existing section ID
- key sections are grouped in the expected sidebar groups, including Loop Step A under Implementation loop
- required UI hooks exist
- required UI classes exist
- copy buttons target existing code blocks
- prompt placeholders use `{{...}}`
- obsolete `[PLACEHOLDER]` placeholders are absent
- routine prompts do not ask for `Connected GitHub repo:`
- Prompt Manager still recommends Awesome Prompts
- the diagram uses the external PNG reference
- JavaScript syntax passes when Node is available
- Liquid-sensitive bare double-brace fragments inside code templates are absent
- removed concepts stay removed when intentionally retired
- the compact primer remains concise

Use behavior markers rather than brittle exact function-name checks when validating JavaScript behavior.

Do not claim browser runtime validation passed unless browser behavior was actually tested.

## Troubleshooting GitHub Actions

When a workflow fails:

1. Inspect the failing step and logs.
2. If render fails, patch `tools/render_guide.py`.
3. If validation fails because the guide is wrong, patch the Markdown/source content.
4. If validation fails because the validator is too strict or checking the wrong thing, patch `tools/validate_guide.py`.
5. If setup or permissions fail, patch `.github/workflows/build-guide.yml` or `.github/workflows/apply-guide-patch.yml`.
6. Make the smallest change that fixes the issue.
7. Commit directly to `main`.
8. Ask the user to rerun the workflow manually if connector commits do not trigger it automatically.

The Node.js deprecation warning is not necessarily a failure. Look for the actual step with exit code 1.

If GitHub Pages/Jekyll fails, check for Liquid-sensitive text in Markdown code blocks. Literal `{{...}}` prompt placeholders are expected, but code that tests for a bare `{{` or `}}` string can be parsed as Liquid before the Markdown fence is respected.

## Prompt and placeholder rules

Preserve the guide’s placeholder style:

- Use `{{VARIABLE_NAME}}` or `{{Plain-language prompt question}}`.
- Do not use `[PLACEHOLDER]`.
- Keep prompt blocks copy-paste ready.
- Avoid asking for `Connected GitHub repo` in routine prompts after a ChatGPT Project is configured with the GitHub connector.
- Keep target branch explicit when current state depends on branch.

Avoid bare double-brace fragments inside code templates, such as checking whether a string contains literal `{{`. Prefer safer alternatives like checking whether a placeholder string starts with `{`.

## GitHub connector guidance

Use the GitHub connector to inspect and update small-to-medium source files on `main`.

Good connector targets:

- Markdown source files
- primer file
- Python renderer/validator scripts
- workflow YAML
- small documentation files
- the approved patch helper script

Avoid using the connector for large generated HTML replacement unless no better option is available.

## Primer rules

Keep `llm-workflow-primer.md` compact.

Update it only when reusable workflow rules change. Do not let it become a copy of the full guide. It should remain suitable as lightweight context inside app-specific ChatGPT Projects.

## Diagram rules

Do not update `llm_coding_workflow_diagram.png` unless:

- the user explicitly asks, or
- the workflow structure changes enough that the diagram becomes misleading.

The generated HTML should reference the PNG externally, not embed it as base64.

## Reporting format

For guide changes, report:

- recommended approach
- what changed
- source commit SHA
- generated HTML commit SHA, if available
- changed files
- validation performed
- generated HTML workflow status
- anything intentionally not changed
- update/archive status
- failed or manual steps, if any

Be explicit about partial completion.

## Honesty rules

Never claim:

- GitHub was updated if the write failed
- `main` was updated if only a branch was updated
- generated HTML was updated if only source files changed and the workflow has not regenerated HTML yet
- validation passed if validation was not actually run
- browser runtime validation passed if browser behavior was not tested
- a PR was created if it was not created

If work is partially completed, say exactly what succeeded, what failed, and what remains.

## Maintenance summary

Preferred maintenance flow:

1. ChatGPT inspects GitHub `main`.
2. ChatGPT updates Markdown, primer, renderer, validator, workflow, or the approved patch helper directly on `main`.
3. For direct source/tool changes, GitHub Actions runs `Build guide HTML`.
4. For large approved patch-helper changes, the user runs `Apply guide patch` manually if needed.
5. GitHub Actions renders and validates the generated guide.
6. GitHub commits the regenerated HTML if it changed.
7. ChatGPT reports source commit, generated HTML status, validation status, and follow-up steps.

This avoids manual large-file replacement while preserving GitHub version history.

# LLM Coding Workflow Guide

Canonical maintenance repo for the LLM Coding Workflow Guide.

This repo stores the source Markdown, generated HTML guide, compact primer, renderer, validator, and maintenance notes for the workflow guide.

## Current live files

- `llm_coding_workflow_guide.md` — canonical Markdown source for the full guide.
- `llm_coding_workflow_guide.html` — generated rendered guide interface.
- `llm-workflow-primer.md` — compact primer for app-specific ChatGPT Projects.
- `llm_coding_workflow_diagram.png` — visual reference.
- `tools/render_guide.py` — Markdown-to-HTML renderer.
- `tools/validate_guide.py` — generated guide validator.
- `.github/workflows/build-guide.yml` — GitHub Actions workflow that renders and validates HTML.
- `docs/guide-maintenance.md` — detailed maintenance playbook.

## Manual edits from GitHub

Use this path for small wording, prompt, or section edits that you want to make directly in the GitHub web UI.

1. Open the repo on GitHub.
2. Make sure you are on the `main` branch.
3. Open `llm_coding_workflow_guide.md`.
4. Click the pencil/edit button.
5. Make the Markdown change.
6. Preserve the guide conventions:
   - keep prompt placeholders in `{{...}}` format;
   - do not use `[PLACEHOLDER]`;
   - avoid renaming major headings unless you expect sidebar/navigation changes;
   - do not manually edit `llm_coding_workflow_guide.html` for normal content edits.
7. Commit the change directly to `main`.
8. Go to **Actions** and check the **Build guide HTML** workflow.
9. If the workflow succeeds and the rendered HTML changed, it should commit `llm_coding_workflow_guide.html` back to `main` automatically.
10. Open the generated HTML guide and confirm the change appears.

## If the workflow does not run

Run it manually:

**Actions → Build guide HTML → Run workflow → branch `main`**

## If validation fails

Review the failed step in GitHub Actions. In most cases, fix the smallest appropriate source file:

- edit `llm_coding_workflow_guide.md` if the guide content or headings caused the issue;
- edit `tools/render_guide.py` if rendering/layout behavior caused the issue;
- edit `tools/validate_guide.py` if validation expectations are outdated or too strict;
- edit `.github/workflows/build-guide.yml` if the workflow setup caused the issue.

Do not replace the generated HTML manually unless automation is broken and manual recovery is intentional.

## Maintenance rules

- Update `llm_coding_workflow_guide.md` first for guide content changes.
- Update `llm-workflow-primer.md` only when compact reusable workflow rules change.
- Let GitHub Actions regenerate `llm_coding_workflow_guide.html`.
- Use `tools/validate_guide.py` as the validation source.
- Use Git history as the rollback/archive mechanism.
- See `docs/guide-maintenance.md` for detailed maintenance rules and troubleshooting.

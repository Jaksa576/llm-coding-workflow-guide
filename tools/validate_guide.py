#!/usr/bin/env python3
"""Validate the rendered LLM Coding Workflow Guide HTML.

This script checks the static behaviors that are practical to validate in CI.
Browser-only behaviors are represented by checking the required DOM hooks and JS behavior markers.
"""
from __future__ import annotations

import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILE = ROOT / "llm_coding_workflow_guide.html"
MD_FILE = ROOT / "llm_coding_workflow_guide.md"
PRIMER_FILE = ROOT / "llm-workflow-primer.md"


class GuideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.nav_hrefs: list[str] = []
        self.nav_groups: dict[str, list[str]] = {}
        self._current_nav_group: str | None = None
        self.copy_targets: list[str] = []
        self.code_ids: set[str] = set()
        self.classes: list[str] = []
        self.scripts: list[str] = []
        self._in_script = False
        self._script_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        if "id" in attr and attr["id"]:
            self.ids.add(attr["id"] or "")
        if "class" in attr and attr["class"]:
            self.classes.extend((attr["class"] or "").split())
        if tag == "details" and attr.get("data-nav-group"):
            self._current_nav_group = attr.get("data-nav-group") or ""
            self.nav_groups.setdefault(self._current_nav_group, [])
        if tag == "a" and "data-nav" in attr and attr.get("href", "").startswith("#"):
            href = attr["href"] or ""
            self.nav_hrefs.append(href)
            if self._current_nav_group:
                self.nav_groups.setdefault(self._current_nav_group, []).append(href)
        if tag == "button" and attr.get("data-copy-target"):
            self.copy_targets.append(attr["data-copy-target"] or "")
        if tag == "code" and attr.get("id"):
            self.code_ids.add(attr["id"] or "")
        if tag == "script":
            self._in_script = True
            self._script_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._in_script:
            self.scripts.append("".join(self._script_parts))
            self._in_script = False
        if tag == "details":
            self._current_nav_group = None

    def handle_data(self, data: str) -> None:
        if self._in_script:
            self._script_parts.append(data)
        self.text_parts.append(data)


def check(condition: bool, message: str, failures: list[str]) -> None:
    if condition:
        print(f"PASS: {message}")
    else:
        print(f"FAIL: {message}")
        failures.append(message)


def find_liquid_sensitive_template_lines(markdown: str) -> list[str]:
    """Find code-template lines that can confuse Jekyll/Liquid.

    The guide intentionally uses {{...}} prompt placeholders. Those should remain.
    This check targets code lines that include a bare {{ or }} fragment inside quotes,
    such as PowerShell string checks like `$key.Contains("{{")`.
    """
    failures: list[str] = []
    in_code = False
    for lineno, line in enumerate(markdown.splitlines(), start=1):
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not in_code:
            continue
        if re.search(r"[\"']\s*\{\{\s*[\"']", line) or re.search(r"[\"']\s*\}\}\s*[\"']", line):
            failures.append(f"line {lineno}: {line.strip()}")
    return failures


def main() -> int:
    html = HTML_FILE.read_text(encoding="utf-8")
    markdown = MD_FILE.read_text(encoding="utf-8")
    parser = GuideParser()
    parser.feed(html)
    text = "\n".join(parser.text_parts)
    failures: list[str] = []

    check(bool(parser.nav_hrefs), "sidebar navigation links exist", failures)
    missing = [href for href in parser.nav_hrefs if href[1:] not in parser.ids]
    check(not missing, f"every sidebar link points to an existing section ID ({len(parser.nav_hrefs)} checked)", failures)

    for required_id in ["navSearch", "expandNav", "collapseNav", "clearNavSearch", "navStatus", "nav", "content"]:
        check(required_id in parser.ids, f"required UI hook exists: {required_id}", failures)

    for required_class in ["nav-group", "copy-btn", "term", "code-card"]:
        check(required_class in parser.classes, f"required UI class exists: {required_class}", failures)
    check("floating-tooltip" in html, "floating tooltip code exists", failures)

    implementation_hrefs = parser.nav_groups.get("Implementation loop", [])
    setup_hrefs = parser.nav_groups.get("One-time setup", [])
    reference_hrefs = parser.nav_groups.get("Reference material", [])
    check("#loop-step-a-ground-a-new-chatgpt-chat-in-the-repo" in implementation_hrefs, "Loop Step A is grouped under Implementation loop", failures)
    check("#stage-2a-optional-codex-worktrees" in setup_hrefs, "Stage 2A worktrees is grouped under One-time setup", failures)
    check("#reference-material" in reference_hrefs, "Reference material top-level section is grouped under Reference material", failures)
    check("#optional-codex-worktrees" in reference_hrefs, "Optional Codex worktrees is grouped under Reference material", failures)
    check("Other sections" not in parser.nav_groups, "Other sections sidebar group is absent", failures)
    check("Appendices" not in parser.nav_groups, "empty Appendices sidebar group is absent", failures)
    check("Docs and protocols" not in parser.nav_groups, "old Docs and protocols sidebar group is absent", failures)

    missing_copy = [target for target in parser.copy_targets if target not in parser.code_ids]
    check(not missing_copy and bool(parser.copy_targets), f"copy buttons target existing code blocks ({len(parser.copy_targets)} checked)", failures)

    check("{{" in html and "}}" in html, "prompt placeholders use double braces", failures)
    check("[PLACEHOLDER]" not in html, "obsolete [PLACEHOLDER] placeholders absent", failures)
    check("Connected GitHub repo:" not in html, "routine Connected GitHub repo prompt field absent", failures)
    check("Awesome Prompts" in text, "Prompt Manager section still recommends Awesome Prompts", failures)
    check("llm_coding_workflow_diagram.png" in html, "diagram uses external PNG reference", failures)
    check("docs/project-state.json" not in html, "docs/project-state.json references absent", failures)
    check("State packet" not in text and "state packet" not in text, "state packet references absent", failures)

    liquid_sensitive_lines = find_liquid_sensitive_template_lines(markdown)
    check(not liquid_sensitive_lines, "Liquid-sensitive bare double-brace code fragments absent", failures)
    if liquid_sensitive_lines:
        for line in liquid_sensitive_lines:
            print(f"Liquid-sensitive line: {line}")

    script = "\n".join(parser.scripts)
    behavior_checks = {
        "copy button clipboard behavior": ["navigator.clipboard.writeText", "copy-btn"],
        "sidebar filter behavior": ["navSearch", "search-hidden", "data-nav"],
        "collapsible navigation controls": ["expandNav", "collapseNav", "nav-group"],
        "tooltip placement behavior": ["floating-tooltip", "getBoundingClientRect", "term"],
        "active section observer behavior": ["IntersectionObserver", "active"],
    }
    for message, snippets in behavior_checks.items():
        check(all(snippet in script for snippet in snippets), f"script includes {message}", failures)

    node = subprocess.run(["bash", "-lc", "command -v node"], capture_output=True, text=True)
    if node.returncode == 0:
        js_file = ROOT / ".tmp-guide-script.js"
        js_file.write_text(script, encoding="utf-8")
        try:
            result = subprocess.run([node.stdout.strip(), "--check", str(js_file)], capture_output=True, text=True)
            check(result.returncode == 0, "JavaScript syntax check passes", failures)
            if result.returncode != 0:
                print(result.stderr)
        finally:
            js_file.unlink(missing_ok=True)
    else:
        print("WARN: node not available; skipped JavaScript syntax check")

    if PRIMER_FILE.exists():
        primer = PRIMER_FILE.read_text(encoding="utf-8")
        check(len(primer) < 6000, "compact primer remains concise", failures)

    if failures:
        print("\nValidation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nValidation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

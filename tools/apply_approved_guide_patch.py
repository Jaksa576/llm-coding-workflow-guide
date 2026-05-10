#!/usr/bin/env python3
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

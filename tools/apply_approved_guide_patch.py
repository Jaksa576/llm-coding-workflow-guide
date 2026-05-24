#!/usr/bin/env python3
from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / 'llm_coding_workflow_guide.md'
DIAGRAM = ROOT / 'llm_coding_workflow_diagram.png'
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
            llm_coding_workflow_diagram.png
            tools/render_guide.py
            tools/apply_approved_guide_patch.py
            .github/workflows/apply-guide-patch.yml
'''


def font(size: int, bold: bool = False):
    from PIL import ImageFont
    candidates = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf',
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def build_diagram() -> None:
    from PIL import Image, ImageDraw

    width, height = 1800, 1000
    image = Image.new('RGB', (width, height), '#f7f7f4')
    draw = ImageDraw.Draw(image)

    title_f = font(56, True)
    subtitle_f = font(28)
    heading_f = font(32, True)
    body_f = font(22)
    tiny_f = font(18)

    ink = '#111827'
    muted = '#4b5563'
    line = '#94a3b8'
    repo_line = '#cbd5e1'
    colors = [
        ('#dbeafe', '#1d4ed8'),
        ('#ede9fe', '#6d28d9'),
        ('#d1fae5', '#047857'),
        ('#fef3c7', '#b45309'),
    ]

    def wrap(text: str, text_font, max_width: int) -> list[str]:
        lines: list[str] = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            current = ''
            for word in words:
                test = word if not current else current + ' ' + word
                if draw.textbbox((0, 0), test, font=text_font)[2] <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
        return lines

    def center_line(x1: int, x2: int, y: int, text: str, text_font, fill: str) -> None:
        text_width = draw.textbbox((0, 0), text, font=text_font)[2]
        draw.text((x1 + (x2 - x1 - text_width) / 2, y), text, font=text_font, fill=fill)

    def centered_text(x1: int, y1: int, x2: int, y2: int, text: str, text_font, fill: str) -> None:
        lines = wrap(text, text_font, x2 - x1 - 40)
        heights = [draw.textbbox((0, 0), line, font=text_font)[3] - draw.textbbox((0, 0), line, font=text_font)[1] for line in lines]
        total_height = sum(heights) + max(0, len(lines) - 1) * 7
        y = y1 + (y2 - y1 - total_height) / 2
        for line_text, line_height in zip(lines, heights):
            line_width = draw.textbbox((0, 0), line_text, font=text_font)[2]
            draw.text((x1 + (x2 - x1 - line_width) / 2, y), line_text, font=text_font, fill=fill)
            y += line_height + 7

    def rounded(box, fill: str, outline: str, radius: int = 28, border_width: int = 3) -> None:
        draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=border_width)

    def arrow(start, end, color: str = line, arrow_width: int = 5) -> None:
        draw.line([start, end], fill=color, width=arrow_width)
        x1, y1 = start
        x2, y2 = end
        angle = math.atan2(y2 - y1, x2 - x1)
        length = 20
        spread = 0.55
        draw.polygon([
            end,
            (x2 - length * math.cos(angle - spread), y2 - length * math.sin(angle - spread)),
            (x2 - length * math.cos(angle + spread), y2 - length * math.sin(angle + spread)),
        ], fill=color)

    draw.text((70, 55), 'LLM Coding Workflow', font=title_f, fill=ink)
    draw.text((72, 125), 'Plan broadly in ChatGPT. Execute narrowly in the repo. Review, patch, and keep docs fresh.', font=subtitle_f, fill=muted)

    draw.arc((260, 165, 1480, 305), start=180, end=360, fill=line, width=4)
    arrow((335, 235), (270, 235), arrow_width=4)

    box_top, box_bottom = 280, 470
    starts = [90, 500, 910, 1320]
    box_width = 330
    data = [
        ('1. Plan', 'ChatGPT turns intent into a campaign, slice, or patch.'),
        ('2. Handoff', 'Lean execution packet: docs, scope, acceptance criteria, validation.'),
        ('3. Implement', 'Coding agent edits the repo, validates, updates docs, commits.'),
        ('4. QA decision', 'User reviews and chooses merge, patch, revise, or stop.'),
    ]
    boxes = []
    for index, (x, (title, body)) in enumerate(zip(starts, data)):
        box = (x, box_top, x + box_width, box_bottom)
        boxes.append(box)
        fill, outline = colors[index]
        rounded(box, fill, outline)
        center_line(x, x + box_width, box_top + 28, title, heading_f, outline)
        draw.line([(x + 35, box_top + 78), (x + box_width - 35, box_top + 78)], fill=outline, width=2)
        centered_text(x + 20, box_top + 88, x + box_width - 20, box_bottom - 20, body, body_f, ink)

    for index in range(3):
        arrow((boxes[index][2] + 16, (box_top + box_bottom) // 2), (boxes[index + 1][0] - 16, (box_top + box_bottom) // 2))

    repo = (170, 685, 1630, 850)
    rounded(repo, '#ffffff', repo_line, radius=30)
    draw.text((215, 715), 'Repo / GitHub source of truth', font=heading_f, fill=ink)
    repo_text = 'AGENTS.md • product • architecture • roadmap • current-task • campaigns • collaboration when group work is active'
    for line_index, line_text in enumerate(wrap(repo_text, body_f, 850)):
        draw.text((215, 770 + line_index * 34), line_text, font=body_f, fill=muted)

    for x1, y1, x2, y2 in boxes:
        center_x = (x1 + x2) // 2
        arrow((center_x, y2 + 16), (center_x, repo[1] - 24), color=repo_line, arrow_width=4)

    group = (1145, 710, 1595, 825)
    rounded(group, '#fee2e2', '#b91c1c', radius=24)
    center_line(group[0], group[2], group[1] + 22, 'Group mode adds', heading_f, '#b91c1c')
    centered_text(group[0] + 20, group[1] + 60, group[2] - 20, group[3] - 12, 'Issue + Draft PR • owner + branch • overlap check', body_f, ink)

    user = (100, 900, 1700, 955)
    rounded(user, '#f1f5f9', repo_line, radius=18, border_width=2)
    centered_text(user[0], user[1], user[2], user[3], 'User owns product direction, QA judgment, merge decisions, and when to simplify.', body_f, ink)
    draw.text((70, 972), 'Default: ChatGPT planning + Codex implementation. Still useful elsewhere, but most token-efficient with separate planning/execution contexts.', font=tiny_f, fill=muted)

    image.save(DIAGRAM, 'PNG', optimize=True)
    print(f'Updated {DIAGRAM.name}')


def fix_markdown_numbering() -> None:
    text = GUIDE.read_text(encoding='utf-8')
    old = '7. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.\n7. Close out campaigns, clean stale context from the hot path, and start a new chat for the next phase when useful.'
    new = '7. Repeat the main loop: plan work -> generate handoff -> implement -> validate -> update docs -> final report -> QA -> merge, patch, revise, or stop.\n8. Close out campaigns, clean stale context from the hot path, and start a new chat for the next phase when useful.'
    if old in text:
        GUIDE.write_text(text.replace(old, new, 1), encoding='utf-8')
        print('Fixed Workflow at a glance numbering.')
    elif new in text:
        print('Workflow at a glance numbering already fixed.')
    else:
        raise SystemExit('Expected Workflow at a glance numbering block not found.')


def main() -> int:
    if not GUIDE.exists():
        raise SystemExit('Guide source not found.')
    fix_markdown_numbering()
    build_diagram()
    SELF.write_text(NOOP, encoding='utf-8')
    WORKFLOW.write_text(MANUAL_WORKFLOW, encoding='utf-8')
    print('Reset patch helper and Apply guide patch workflow to manual no-op state.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render llm_coding_workflow_guide.md into llm_coding_workflow_guide.html."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "llm_coding_workflow_guide.md"
OUT = ROOT / "llm_coding_workflow_guide.html"
TITLE = "LLM Coding Workflow Guide"
GENERATED_NOTE = "This HTML guide is generated from the Markdown source by GitHub Actions."

GROUPS = [
    ("Start here", ["LLM Coding Workflow Guide", "Purpose", "Why this workflow works", "Quick start"], True),
    ("One-time setup", ["Stage 0 - Create the repo and local workspace", "Stage 1 - Create the ChatGPT Project", "Stage 1A - Add the compact workflow primer", "Stage 1B - Configure GitHub source-of-truth access", "Stage 2 - Configure Codex before handoffs", "Stage 2A - Optional Codex worktree setup and cleanup scripts", "Stage 3 - Define the project", "Stage 4 - Generate project-specific ChatGPT instructions", "Stage 5 - Generate the core repo docs", "Stage 6 - Add the core docs to the repo", "Stage 7 - Bootstrap the project", "Stage 8 - Review bootstrap"], False),
    ("Implementation loop", ["Main implementation loop", "Loop Step A - Ground a new ChatGPT chat in the repo", "Loop Step B - Plan the next work item", "Loop Step C - Generate the next Codex handoff", "Loop Step D - Let Codex implement", "Loop Step E - QA and decide merge or patch", "Loop Step F - Patch when needed", "Loop Step G - Close the campaign or phase"], True),
    ("Docs and protocols", ["Documentation freshness system", "Documentation delta", "Docs health check", "Current-state protocol", "Operating rules"], False),
    ("Appendices", ["Appendix A - ChatGPT Project workflow primer", "Appendix B - Key terms", "Appendix C - Standard repo docs", "Appendix D - Codex worktrees", "Appendix E - Common PowerShell commands", "Appendix F - Prompt Manager guidance", "Appendix G - Standard reusable prompts", "Appendix I - Maintenance and versioning"], False),
]

TERMS = {
    "Planning LLM": "The conversational model used for strategy, planning, QA triage, and handoff generation.",
    "Coding agent": "The tool that works directly in the repo to edit files, run checks, commit, and push.",
    "Source-of-truth docs": "The repo docs that define current product, architecture, roadmap, and active work.",
    "Hot context": "The small set of files an agent should read for the current task.",
    "Campaign": "A large swath of related work broken into reviewable slices.",
    "Slice": "One independently reviewable implementation unit inside a campaign or standalone effort.",
    "Patch": "A narrow correction to a specific branch or issue.",
    "Bootstrap": "The first implementation run that creates the working shell, validation path, and initial deploy/run setup.",
    "Readiness gate": "The pre-coding check that confirms docs, branch, and scope agree.",
    "Documentation delta": "The final-report section explaining which docs changed and why.",
    "Docs health check": "A docs-only audit to align current-task, roadmap, architecture, and campaign status.",
    "Source-of-truth check": "A deliberate refresh using the latest repo docs before planning, handoffs, QA, or strategy decisions.",
    "Prompt manager": "A saved-prompt library for reusable prompts. It reduces typing, but does not replace repo docs or project instructions.",
    "Worktree": "A separate working directory connected to the same Git repo, useful for isolated branches.",
}

CSS_FALLBACK = """body{font-family:system-ui;margin:0;background:#f7f7f4;color:#1f2937}.layout{display:grid;grid-template-columns:310px 1fr}.sidebar{position:sticky;top:0;height:100vh;overflow:auto;background:#111827;color:#fff;padding:18px}.content{max-width:1040px;padding:34px 42px}.nav-group{border-top:1px solid #243244;padding:8px 0}.sidebar a{display:block;color:#dbeafe;padding:6px 8px}.code-card{background:#0b1020;border-radius:14px;margin:16px 0;overflow:auto}.code-toolbar{display:flex;justify-content:space-between;color:#cbd5e1;padding:8px 10px}.copy-btn{cursor:pointer}pre{margin:0;padding:16px;color:#e5e7eb}.workflow-diagram{max-width:100%}.term{border-bottom:1px dotted #2563eb}.floating-tooltip{position:fixed;z-index:9999;max-width:360px;background:#111827;color:#fff;padding:10px;border-radius:10px;opacity:0}.floating-tooltip.visible{opacity:1}.search-hidden{display:none!important}"""

JS = r"""
(()=>{
const links=[...document.querySelectorAll('[data-nav]')];
const search=document.getElementById('navSearch');
const status=document.getElementById('navStatus');
function filterNav(){
  const q=(search?.value||'').toLowerCase();
  let shown=0;
  document.querySelectorAll('.nav-group').forEach(group=>{
    let groupShown=false;
    group.querySelectorAll('[data-nav]').forEach(a=>{
      const match=!q||a.textContent.toLowerCase().includes(q);
      a.classList.toggle('search-hidden',!match);
      if(match){shown++;groupShown=true;}
    });
    group.classList.toggle('search-hidden',!groupShown);
    if(q&&groupShown)group.open=true;
  });
  if(status)status.textContent=q?`Showing ${shown} of ${links.length} sections`:'Showing all sections';
}
search?.addEventListener('input',filterNav);
document.getElementById('clearNavSearch')?.addEventListener('click',()=>{search.value='';filterNav();search.focus();});
document.getElementById('expandNav')?.addEventListener('click',()=>document.querySelectorAll('.nav-group').forEach(d=>d.open=true));
document.getElementById('collapseNav')?.addEventListener('click',()=>document.querySelectorAll('.nav-group').forEach(d=>d.open=false));
document.querySelectorAll('.copy-btn').forEach(btn=>btn.addEventListener('click',async()=>{
  const target=document.getElementById(btn.dataset.copyTarget);
  await navigator.clipboard.writeText(target?.innerText||'');
  btn.textContent='Copied';
  setTimeout(()=>btn.textContent='Copy',1200);
}));
const tooltip=document.createElement('div');
tooltip.className='floating-tooltip';
document.body.appendChild(tooltip);
function placeTooltip(el){
  const r=el.getBoundingClientRect();
  tooltip.style.left='0px';
  tooltip.style.top='0px';
  const tr=tooltip.getBoundingClientRect();
  let x=Math.min(Math.max(r.left,14),innerWidth-tr.width-14);
  let y=r.bottom+8;
  if(y+tr.height>innerHeight-14)y=r.top-tr.height-8;
  tooltip.style.left=x+'px';
  tooltip.style.top=Math.max(14,y)+'px';
}
document.querySelectorAll('.term').forEach(el=>{
  el.addEventListener('mouseenter',()=>{tooltip.textContent=el.dataset.tip||'';tooltip.classList.add('visible');placeTooltip(el);});
  el.addEventListener('mouseleave',()=>tooltip.classList.remove('visible'));
});
const observer=new IntersectionObserver(entries=>{
  entries.forEach(entry=>{
    if(entry.isIntersecting){
      links.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+entry.target.id));
    }
  });
},{rootMargin:'-20% 0px -70% 0px',threshold:0});
document.querySelectorAll('main [id]').forEach(el=>observer.observe(el));
filterNav();
})();
"""


def extract_style(old: str) -> str:
    match = re.search(r"<style[^>]*>(.*?)</style>", old, re.S | re.I)
    return match.group(1).strip() if match else CSS_FALLBACK


def slug(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text or "section"


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img class="workflow-diagram" src="{html.escape(m.group(2), quote=True)}" alt="{html.escape(m.group(1), quote=True)}"/>', text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', text)
    stash: list[str] = []
    text = re.sub(r"`([^`]+)`", lambda m: stash.append(f"<code>{m.group(1)}</code>") or f"\0CODE{len(stash)-1}\0", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    for i, value in enumerate(stash):
        text = text.replace(f"\0CODE{i}\0", value)
    return text


def add_terms(rendered: str) -> str:
    parts = re.split(r"(<[^>]+>)", rendered)
    out: list[str] = []
    in_code = False
    for part in parts:
        if part.startswith("<"):
            lower = part.lower()
            if lower.startswith(("<code", "<pre")):
                in_code = True
            elif lower.startswith(("</code", "</pre")):
                in_code = False
            out.append(part)
            continue
        if not in_code:
            for term, tip in sorted(TERMS.items(), key=lambda item: len(item[0]), reverse=True):
                pattern = rf"\b{re.escape(term)}\b"
                replacement = lambda m, tip=tip: f'<span class="term" tabindex="0" data-tip="{html.escape(tip, quote=True)}">{m.group(0)}</span>'
                part = re.sub(pattern, replacement, part, count=1)
        out.append(part)
    return "".join(out)


def parse_markdown(markdown: str) -> tuple[str, list[tuple[int, str, str]]]:
    lines = markdown.splitlines()
    out: list[str] = []
    headings: list[tuple[int, str, str]] = []
    used: dict[str, int] = {}
    list_tag: str | None = None
    i = 0
    code_id = 0

    def close_list() -> None:
        nonlocal list_tag
        if list_tag:
            out.append(f"</{list_tag}>")
            list_tag = None

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            close_list()
            i += 1
            continue
        if line.startswith("```"):
            close_list()
            lang = line[3:].strip() or "text"
            buf: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            code_id += 1
            code = html.escape("\n".join(buf))
            out.append(f'<div class="code-card"><div class="code-toolbar"><span>{html.escape(lang)}</span><button class="copy-btn" type="button" data-copy-target="code-{code_id}">Copy</button></div><pre><code id="code-{code_id}">{code}</code></pre></div>')
            continue
        heading = re.match(r"^(#{1,3})\s+(.*)$", line)
        if heading:
            close_list()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            base = slug(title)
            count = used.get(base, 0)
            used[base] = count + 1
            heading_id = base if count == 0 else f"{base}-{count+1}"
            headings.append((level, title, heading_id))
            out.append(f'<h{level} id="{heading_id}"><a class="heading-anchor" href="#{heading_id}">#</a>{inline(title)}</h{level}>')
            i += 1
            continue
        if line.strip() == "---":
            close_list()
            out.append("<hr/>")
            i += 1
            continue
        item = re.match(r"^\s*([-*]|\d+\.)\s+(.*)$", line)
        if item:
            tag = "ol" if item.group(1).endswith(".") else "ul"
            if list_tag != tag:
                close_list()
                list_tag = tag
                out.append(f"<{tag}>")
            out.append(f"<li>{inline(item.group(2))}</li>")
            i += 1
            continue
        close_list()
        para = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("```") and not re.match(r"^(#{1,3})\s+", lines[i]) and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
            para.append(lines[i].strip())
            i += 1
        rendered = inline(" ".join(para))
        out.append(rendered if rendered.startswith("<img ") else f"<p>{rendered}</p>")
    close_list()
    return add_terms("\n".join(out)), headings


def build_nav(headings: list[tuple[int, str, str]]) -> str:
    by_title = {title: (level, heading_id) for level, title, heading_id in headings}
    used: set[str] = set()
    chunks: list[str] = []
    for group_name, titles, is_open in GROUPS:
        open_attr = " open" if is_open else ""
        chunks.append(f'<details class="nav-group" data-nav-group="{html.escape(group_name)}"{open_attr}><summary>{html.escape(group_name)}</summary>')
        for title in titles:
            if title in by_title:
                level, heading_id = by_title[title]
                used.add(heading_id)
                chunks.append(f'<a data-nav data-level="{level}" href="#{heading_id}">{html.escape(title)}</a>')
        chunks.append("</details>")
    rest = [(level, title, heading_id) for level, title, heading_id in headings if heading_id not in used and level <= 2]
    if rest:
        chunks.append('<details class="nav-group" data-nav-group="Other sections"><summary>Other sections</summary>')
        for level, title, heading_id in rest:
            chunks.append(f'<a data-nav data-level="{level}" href="#{heading_id}">{html.escape(title)}</a>')
        chunks.append("</details>")
    return "\n".join(chunks)


def main() -> int:
    markdown = MD.read_text(encoding="utf-8")
    old_html = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    css = extract_style(old_html)
    body, headings = parse_markdown(markdown)
    nav = build_nav(headings)
    generated_note_html = f'<div class="callout"><strong>Generated guide:</strong> {html.escape(GENERATED_NOTE)}</div>'
    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{TITLE}</title>
<style>
{css}
</style>
</head>
<body>
<div class="layout">
<aside class="sidebar">
<h1>{TITLE}</h1>
<p class="sidebar-subtitle">Jump quickly, collapse groups, or filter sections.</p>
<input aria-label="Filter sections" id="navSearch" placeholder="Filter sections..."/>
<div class="nav-controls"><button id="expandNav" type="button">Expand</button><button id="collapseNav" type="button">Collapse</button><button id="clearNavSearch" type="button">Clear</button></div>
<p class="nav-status" id="navStatus" aria-live="polite">Showing all sections</p>
<nav id="nav">{nav}</nav>
</aside>
<main class="content" id="content">
{generated_note_html}
{body}
</main>
</div>
<script>
{JS}
</script>
</body>
</html>
"""
    OUT.write_text(document, encoding="utf-8")
    print("Rendered llm_coding_workflow_guide.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render llm_coding_workflow_guide.md into llm_coding_workflow_guide.html."""
from __future__ import annotations
import html,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MD=ROOT/'llm_coding_workflow_guide.md'
OUT=ROOT/'llm_coding_workflow_guide.html'
TITLE='LLM Coding Workflow Guide'
GROUPS=[('Start here',['LLM Coding Workflow Guide','Purpose','Why this workflow works','Quick start'],1),('One-time setup',['Stage 0 - Create the repo and local workspace','Stage 1 - Create the ChatGPT Project','Stage 1A - Add the compact workflow primer','Stage 1B - Configure GitHub source-of-truth access','Stage 2 - Configure Codex before handoffs','Stage 3 - Define the project','Stage 4 - Generate project-specific ChatGPT instructions','Stage 5 - Generate the core repo docs','Stage 6 - Add the core docs to the repo','Stage 7 - Bootstrap the project','Stage 8 - Review bootstrap'],0),('Implementation loop',['Main implementation loop','Loop Step A - Start or refresh the ChatGPT chat','Loop Step B - Plan the next work item','Loop Step C - Generate the next Codex handoff','Loop Step D - Let Codex implement','Loop Step E - QA and decide merge or patch','Loop Step F - Patch when needed','Loop Step G - Close the campaign or phase'],1),('Docs and protocols',['Documentation freshness system','Documentation delta','State packet','Docs health check','Current-state protocol','Operating rules'],0),('Appendices',['Appendix A - ChatGPT Project workflow primer','Appendix B - Key terms','Appendix C - Standard repo docs','Appendix D - Codex worktrees','Appendix E - Common PowerShell commands','Appendix F - Prompt Manager guidance','Appendix G - Standard reusable prompts','Appendix H - Lightweight project-state option','Appendix I - Maintenance and versioning'],0)]
TERMS={'Planning LLM':'The conversational model used for strategy, planning, QA triage, and handoff generation.','Coding agent':'The tool that works directly in the repo to edit files, run checks, commit, and push.','Source-of-truth docs':'The repo docs that define current product, architecture, roadmap, and active work.','Hot context':'The small set of files an agent should read for the current task.','Campaign':'A large swath of related work broken into reviewable slices.','Slice':'One independently reviewable implementation unit inside a campaign or standalone effort.','Patch':'A narrow correction to a specific branch or issue.','Bootstrap':'The first implementation run that creates the working shell, validation path, and initial deploy/run setup.','Readiness gate':'The pre-coding check that confirms docs, branch, and scope agree.','Documentation delta':'The final-report section explaining which docs changed and why.','State packet':'A compact final-report summary for the next ChatGPT session. It is not a source of truth.','Docs health check':'A docs-only audit to align current-task, roadmap, architecture, and campaign status.','Source-of-truth check':'A deliberate refresh using the latest repo docs before planning, handoffs, QA, or strategy decisions.','Prompt manager':'A saved-prompt library for reusable prompts. It reduces typing, but does not replace repo docs or project instructions.','Worktree':'A separate working directory connected to the same Git repo, useful for isolated branches.'}
CSS_FALLBACK='body{font-family:system-ui;margin:0;background:#f7f7f4;color:#1f2937}.layout{display:grid;grid-template-columns:310px 1fr}.sidebar{position:sticky;top:0;height:100vh;overflow:auto;background:#111827;color:#fff;padding:18px}.content{max-width:1040px;padding:34px 42px}.nav-group{border-top:1px solid #243244;padding:8px 0}.sidebar a{display:block;color:#dbeafe;padding:6px 8px}.code-card{background:#0b1020;border-radius:14px;margin:16px 0;overflow:auto}.code-toolbar{display:flex;justify-content:space-between;color:#cbd5e1;padding:8px 10px}.copy-btn{cursor:pointer}pre{margin:0;padding:16px;color:#e5e7eb}.workflow-diagram{max-width:100%}.term{border-bottom:1px dotted #2563eb}.floating-tooltip{position:fixed;z-index:9999;max-width:360px;background:#111827;color:#fff;padding:10px;border-radius:10px;opacity:0}.floating-tooltip.visible{opacity:1}.search-hidden{display:none!important}'
JS_FALLBACK="""(()=>{const L=[...document.querySelectorAll('[data-nav]')],s=document.getElementById('navSearch'),st=document.getElementById('navStatus');function f(){const q=(s?.value||'').toLowerCase();let n=0;document.querySelectorAll('.nav-group').forEach(g=>{let v=0;g.querySelectorAll('[data-nav]').forEach(a=>{const m=!q||a.textContent.toLowerCase().includes(q);a.classList.toggle('search-hidden',!m);if(m){n++;v=1}});g.classList.toggle('search-hidden',!v);if(q&&v)g.open=true});if(st)st.textContent=q?`Showing ${n} of ${L.length} sections`:'Showing all sections'}s?.addEventListener('input',f);document.getElementById('clearNavSearch')?.addEventListener('click',()=>{s.value='';f()});document.getElementById('expandNav')?.addEventListener('click',()=>document.querySelectorAll('.nav-group').forEach(d=>d.open=true));document.getElementById('collapseNav')?.addEventListener('click',()=>document.querySelectorAll('.nav-group').forEach(d=>d.open=false));document.querySelectorAll('.copy-btn').forEach(b=>b.addEventListener('click',async()=>{const t=document.getElementById(b.dataset.copyTarget)?.innerText||'';await navigator.clipboard.writeText(t);b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200)}));const tt=document.createElement('div');tt.className='floating-tooltip';document.body.appendChild(tt);function p(e){const r=e.getBoundingClientRect(),w=tt.getBoundingClientRect();let x=Math.min(Math.max(r.left,14),innerWidth-w.width-14),y=r.bottom+8;if(y+w.height>innerHeight-14)y=r.top-w.height-8;tt.style.left=x+'px';tt.style.top=Math.max(14,y)+'px'}document.querySelectorAll('.term').forEach(e=>{e.addEventListener('mouseenter',()=>{tt.textContent=e.dataset.tip||'';tt.classList.add('visible');p(e)});e.addEventListener('mouseleave',()=>tt.classList.remove('visible'))});f()})();"""

def extract(old:str,tag:str,fb:str)->str:
    m=re.search(fr'<{tag}[^>]*>(.*?)</{tag}>',old,re.S|re.I)
    return m.group(1).strip() if m else fb

def slug(t:str)->str:
    s=re.sub(r'[^a-z0-9\s-]','',t.lower());s=re.sub(r'[\s-]+','-',s).strip('-');return s or 'section'

def inline(t:str)->str:
    t=html.escape(t)
    t=re.sub(r'!\[([^\]]*)\]\(([^)]+)\)',lambda m:f'<img class="workflow-diagram" src="{html.escape(m.group(2),quote=True)}" alt="{html.escape(m.group(1),quote=True)}"/>',t)
    t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',lambda m:f'<a href="{html.escape(m.group(2),quote=True)}">{m.group(1)}</a>',t)
    tokens=[]
    t=re.sub(r'`([^`]+)`',lambda m:(tokens.append(f'<code>{m.group(1)}</code>') or f'\0C{len(tokens)-1}\0'),t)
    t=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',t);t=re.sub(r'\*([^*]+)\*',r'<em>\1</em>',t)
    for i,x in enumerate(tokens):t=t.replace(f'\0C{i}\0',x)
    return t

def terms(x:str)->str:
    parts=re.split(r'(<[^>]+>)',x);out=[];incode=False
    for p in parts:
        if p.startswith('<'):
            lo=p.lower();incode=incode or lo.startswith(('<code','<pre'));incode=False if lo.startswith(('</code','</pre')) else incode;out.append(p);continue
        if not incode:
            for term,tip in sorted(TERMS.items(),key=lambda kv:len(kv[0]),reverse=True):
                p=re.sub(rf'\b{re.escape(term)}\b',lambda m:f'<span class="term" tabindex="0" data-tip="{html.escape(tip,quote=True)}">{m.group(0)}</span>',p,count=1)
        out.append(p)
    return ''.join(out)

def parse(md:str):
    lines=md.splitlines();out=[];heads=[];used={};i=0;cid=0;lst=None
    def close():
        nonlocal lst
        if lst: out.append(f'</{lst}>'); lst=None
    while i<len(lines):
        line=lines[i]
        if not line.strip(): close(); i+=1; continue
        if line.startswith('```'):
            close(); lang=line[3:].strip() or 'text'; buf=[]; i+=1
            while i<len(lines) and not lines[i].startswith('```'): buf.append(lines[i]); i+=1
            if i<len(lines): i+=1
            cid+=1; out.append(f'<div class="code-card"><div class="code-toolbar"><span>{html.escape(lang)}</span><button class="copy-btn" type="button" data-copy-target="code-{cid}">Copy</button></div><pre><code id="code-{cid}">{html.escape(chr(10).join(buf))}</code></pre></div>'); continue
        m=re.match(r'^(#{1,3})\s+(.*)$',line)
        if m:
            close(); level=len(m.group(1)); text=m.group(2).strip(); base=slug(text); n=used.get(base,0); used[base]=n+1; hid=base if n==0 else f'{base}-{n+1}'; heads.append((level,text,hid)); out.append(f'<h{level} id="{hid}"><a class="heading-anchor" href="#{hid}">#</a>{inline(text)}</h{level}>'); i+=1; continue
        if line.strip()=='---': close(); out.append('<hr/>'); i+=1; continue
        lm=re.match(r'^\s*([-*]|\d+\.)\s+(.*)$',line)
        if lm:
            kind='ol' if lm.group(1).endswith('.') else 'ul'
            if lst!=kind: close(); lst=kind; out.append(f'<{kind}>')
            out.append(f'<li>{inline(lm.group(2))}</li>'); i+=1; continue
        close(); para=[line.strip()]; i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].startswith('```') and not re.match(r'^(#{1,3})\s+',lines[i]) and not re.match(r'^\s*([-*]|\d+\.)\s+',lines[i]): para.append(lines[i].strip()); i+=1
        r=inline(' '.join(para)); out.append(r if r.startswith('<img ') else f'<p>{r}</p>')
    close(); return terms('\n'.join(out)),heads

def nav(heads):
    by={t:(l,h) for l,t,h in heads};used=set();chunks=[]
    for name,titles,op in GROUPS:
        chunks.append(f'<details class="nav-group"{" open" if op else ""}><summary>{html.escape(name)}</summary>')
        for t in titles:
            if t in by:
                l,h=by[t];used.add(h);chunks.append(f'<a data-nav data-level="{l}" href="#{h}">{html.escape(t)}</a>')
        chunks.append('</details>')
    rest=[(l,t,h) for l,t,h in heads if h not in used and l<=2]
    if rest:
        chunks.append('<details class="nav-group"><summary>Other sections</summary>')
        for l,t,h in rest: chunks.append(f'<a data-nav data-level="{l}" href="#{h}">{html.escape(t)}</a>')
        chunks.append('</details>')
    return '\n'.join(chunks)

old=OUT.read_text(encoding='utf-8') if OUT.exists() else ''
css=extract(old,'style',CSS_FALLBACK); js=extract(old,'script',JS_FALLBACK)
body,heads=parse(MD.read_text(encoding='utf-8'))
OUT.write_text(f'''<!DOCTYPE html>\n<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{TITLE}</title><style>\n{css}\n</style></head><body><div class="layout"><aside class="sidebar"><h1>{TITLE}</h1><p class="sidebar-subtitle">Jump quickly, collapse groups, or filter sections.</p><input aria-label="Filter sections" id="navSearch" placeholder="Filter sections..."/><div class="nav-controls"><button id="expandNav" type="button">Expand</button><button id="collapseNav" type="button">Collapse</button><button id="clearNavSearch" type="button">Clear</button></div><p class="nav-status" id="navStatus" aria-live="polite">Showing all sections</p><nav id="nav">{nav(heads)}</nav></aside><main class="content" id="content">\n{body}\n</main></div><script>\n{js}\n</script></body></html>\n''',encoding='utf-8')
print('Rendered llm_coding_workflow_guide.html')

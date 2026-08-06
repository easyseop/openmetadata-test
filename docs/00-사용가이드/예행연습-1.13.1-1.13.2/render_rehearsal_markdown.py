#!/usr/bin/env python3
"""Render the rehearsal Markdown subset into the shared readable HTML layout."""
from __future__ import annotations
import html,re,sys
from pathlib import Path

def inline(s:str)->str:
    s=html.escape(s,quote=False)
    # The guide uses <br> only inside table cells to keep examples readable.
    s=s.replace("&lt;br&gt;", "<br>")
    s=s.replace("\\*", "*")
    stash=[]
    def code(m): stash.append(f"<code>{m.group(1)}</code>"); return f"@@C{len(stash)-1}@@"
    s=re.sub(r"`([^`]+)`",code,s)
    s=re.sub(r"==(.+?)==",r'<strong class="diff">\1</strong>',s)
    s=re.sub(r"\*\*([^*]+)\*\*",r"<strong>\1</strong>",s)
    s=re.sub(r"\[([^]]+)\]\(([^)]+)\)",r'<a href="\2">\1</a>',s)
    for i,v in enumerate(stash): s=s.replace(f"@@C{i}@@",v)
    return s

def render(md:str)->tuple[str,str]:
    lines=md.splitlines(); out=[]; i=0; title="예행연습 가이드"; first=True
    while i<len(lines):
        line=lines[i]
        if not line.strip(): i+=1; continue
        if line.startswith("# "):
            title=line[2:].strip(); out.append(f'<header class="hero"><h1>{inline(title)}</h1></header>'); first=False; i+=1; continue
        if line.startswith("## "):
            out.append(f'<h2>{inline(line[3:].strip())}</h2>'); i+=1; continue
        if line.startswith("#### "):
            out.append(f'<h4>{inline(line[5:].strip())}</h4>'); i+=1; continue
        if line.startswith("### "):
            out.append(f'<h3>{inline(line[4:].strip())}</h3>'); i+=1; continue
        if line.startswith(":::details "):
            summary=line[len(":::details "):].strip(); buf=[]; i+=1
            while i<len(lines) and lines[i].strip() != ":::": buf.append(lines[i]); i+=1
            if i<len(lines): i+=1
            _,fragment=render("\n".join(buf))
            out.append(
                f'<details class="details"><summary>{inline(summary)}</summary>'
                f'<div class="details-body">{fragment}</div></details>'
            ); continue
        if line.startswith("> "):
            buf=[]
            while i<len(lines) and lines[i].startswith("> "): buf.append(lines[i][2:]); i+=1
            text="<br>".join(inline(x) for x in buf)
            joined=" ".join(buf).replace("\\*", "*")
            cls="core" if "★" in joined else "reference" if "*참고" in joined else "warning" if "주의" in joined else "stop" if "중단" in joined else "note"
            out.append(f'<div class="callout {cls}">{text}</div>'); continue
        if line.startswith("```"):
            lang=line[3:].strip(); buf=[]; i+=1
            while i<len(lines) and not lines[i].startswith("```"): buf.append(lines[i]); i+=1
            i+=1
            out.append(f'<div class="command"><pre><code class="language-{html.escape(lang)}">{html.escape(chr(10).join(buf))}</code></pre></div>'); continue
        image_match=re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)",line.strip())
        if image_match:
            alt,src=image_match.groups()
            out.append(
                f'<figure class="figure"><img src="{html.escape(src,quote=True)}" '
                f'alt="{html.escape(alt,quote=True)}" loading="lazy">'
                f'<figcaption>{inline(alt)}</figcaption></figure>'
            ); i+=1; continue
        if line.startswith("|") and i+1<len(lines) and re.match(r"^\|?\s*:?-+",lines[i+1]):
            rows=[]
            while i<len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i+=1
            head=rows[0]; body=rows[2:]
            out.append('<div class="table-wrap"><table><thead><tr>'+''.join(f'<th>{inline(c)}</th>' for c in head)+'</tr></thead><tbody>')
            out.extend('<tr>'+''.join(f'<td>{inline(c)}</td>' for c in row)+'</tr>' for row in body)
            out.append('</tbody></table></div>'); continue
        if re.match(r"^- ",line):
            items=[]
            while i<len(lines) and re.match(r"^- ",lines[i]): items.append(lines[i][2:]); i+=1
            out.append('<ul>'+''.join(f'<li>{inline(x)}</li>' for x in items)+'</ul>'); continue
        if re.match(r"^\d+\. ",line):
            items=[]
            while i<len(lines) and re.match(r"^\d+\. ",lines[i]): items.append(re.sub(r"^\d+\. ","",lines[i])); i+=1
            out.append('<ol>'+''.join(f'<li>{inline(x)}</li>' for x in items)+'</ol>'); continue
        buf=[line]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r"^(#|>|```|:::details |\||- |\d+\. )",lines[i]): buf.append(lines[i]); i+=1
        text=" ".join(x.strip() for x in buf)
        cls=' class="pager"' if text.startswith("**문서 이동:") else ""
        out.append(f'<p{cls}>{inline(text)}</p>')
    return title,"\n".join(out)

def main():
    for arg in sys.argv[1:]:
        src=Path(arg); title,body=render(src.read_text(encoding="utf-8"))
        doc=f'''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="OM_TEMP_예행연습_공통.css"></head><body><div class="wrap"><main>{body}</main></div></body></html>\n'''
        src.with_suffix('.html').write_text(doc,encoding='utf-8')
if __name__=='__main__': main()

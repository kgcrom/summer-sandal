# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown>=3.6,<4"]
# ///
"""wiki/ 의 markdown 을 site/ 의 HTML 로 바꾼다.

실행: uv run scripts/build_site.py

규칙
- 페이지마다 `# 제목` 이 하나 있어야 한다. 없으면 실패한다.
- 제목 아래 첫 문단은 머리 요약이 된다.
- `## 섹션` 마다 번호가 붙는다. 섹션이 6개 이상이면 왼쪽에 목차가 생긴다.
- 상대 경로 `.md` 링크는 `.html` 로 바뀐다. 대상이 wiki/ 안에 없으면 실패한다.
"""
from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "wiki"
SITE = ROOT / "site"
SITE_NAME = "summer-sandal 위키"
REPO = "kgcrom/summer-sandal"
RAIL_MIN_SECTIONS = 6
NO_NUMBER = {"log.md"}  # 날짜순 기록에는 섹션 번호를 붙이지 않는다

FONTS = (
    "https://fonts.googleapis.com/css2"
    "?family=IBM+Plex+Sans+KR:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
)
EXTRA_CSS = """
.layout.one{grid-template-columns:minmax(0,1fr)}
.eyebrow a{text-decoration-color:var(--ink-4)}
.prose img{max-width:100%;height:auto}
"""
CSS = (Path(__file__).parent / "site" / "base.css").read_text(encoding="utf-8") + EXTRA_CSS

LINK = re.compile(r'href="([^":#]+)\.md(#[^"]*)?"')
TAG = re.compile(r"<[^>]+>")


def render(md: str) -> str:
    out = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    return out.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")


def inline(md: str) -> str:
    return re.sub(r"^<p>|</p>$", "", markdown.markdown(md).strip())


def split_page(text: str) -> tuple[str | None, list[str], list[tuple[str, list[str]]]]:
    """(제목, 제목 아래 머리 줄들, [(섹션 제목, 섹션 줄들)]) 로 나눈다."""
    title: str | None = None
    intro: list[str] = []
    sections: list[tuple[str, list[str]]] = []
    fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        elif not fence and title is None and line.startswith("# "):
            title = line[2:].strip()
            continue
        elif not fence and line.startswith("## "):
            sections.append((line[3:].strip(), []))
            continue
        (sections[-1][1] if sections else intro).append(line)
    return title, intro, sections


def first_paragraph(lines: list[str]) -> tuple[str, str]:
    """머리 줄들을 (첫 문단, 나머지) 로 나눈다. 첫 덩어리가 문단이 아니면 첫 문단은 비운다."""
    text = "\n".join(lines).strip()
    head, _, rest = text.partition("\n\n")
    if not head or head[0] in "-*|>`" or re.match(r"\d+\. ", head):
        return "", text
    return head, rest.strip()


def fix_links(body: str, src: Path, errors: list[str]) -> str:
    def repl(m: re.Match[str]) -> str:
        target = (src.parent / f"{m.group(1)}.md").resolve()
        if not target.is_file() or WIKI not in target.parents:
            errors.append(f"{src.relative_to(ROOT)}: 링크 대상이 wiki/ 에 없다 → {m.group(1)}.md")
        return f'href="{m.group(1)}.html{m.group(2) or ""}"'

    return LINK.sub(repl, body)


def build_page(src: Path, errors: list[str]) -> str | None:
    rel = src.relative_to(WIKI)
    title, intro, sections = split_page(src.read_text(encoding="utf-8"))
    if not title:
        errors.append(f"{src.relative_to(ROOT)}: `# 제목` 이 없다")
        return None

    lead, rest = first_paragraph(intro)
    numbered = rel.as_posix() not in NO_NUMBER
    parts: list[str] = []
    toc: list[tuple[int, str]] = []
    if rest:
        parts.append(f'<section class="sec">\n{render(rest)}\n</section>')
    for i, (head, body) in enumerate(sections, 1):
        head_html = inline(head)
        no = f'<span class="no">{i:02d}</span>' if numbered else ""
        body_html = render("\n".join(body))
        parts.append(f'<section class="sec" id="s{i}">\n<h2>{no}{head_html}</h2>\n{body_html}\n</section>')
        toc.append((i, TAG.sub("", head_html)))

    rail = ""
    if len(toc) >= RAIL_MIN_SECTIONS:
        items = "\n".join(
            f'<li><a href="#s{i}"><span class="br">{"└" if i == len(toc) else "├"}</span>{text}</a></li>'
            for i, text in toc
        )
        rail = f'<nav class="rail" aria-label="목차">\n<div class="th">목차</div>\n<ol>\n{items}\n</ol>\n</nav>\n'

    up = "../" * (len(rel.parts) - 1)
    if rel.as_posix() == "index.md":
        eyebrow = REPO
    else:
        crumbs = "".join(f" · {p}" for p in rel.parts[:-1])
        eyebrow = f'<a href="{up}index.html">{SITE_NAME}</a>{crumbs}'

    title_html = inline(title)
    standfirst = f'<p class="standfirst">{inline(lead)}</p>\n' if lead else ""
    layout = "layout" if rail else "layout one"
    page = f"""<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(TAG.sub("", title_html), quote=False)}</title>
<link rel="stylesheet" href="{FONTS}">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="hero">
<div class="eyebrow">{eyebrow}</div>
<h1>{title_html}</h1>
{standfirst}</header>
<div class="{layout}">
{rail}<main class="prose">
{chr(10).join(parts)}
</main>
</div>
<footer class="foot">원본: wiki/{rel.as_posix()}</footer>
</div>
</body></html>
"""
    return fix_links(page, src, errors)


def main() -> int:
    if not WIKI.is_dir():
        print("wiki/ 폴더가 없다", file=sys.stderr)
        return 1
    errors: list[str] = []
    if SITE.exists():
        shutil.rmtree(SITE)
    count = 0
    for src in sorted(WIKI.rglob("*")):
        if src.is_dir() or src.name.startswith("."):
            continue
        dst = SITE / src.relative_to(WIKI)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix != ".md":
            shutil.copy2(src, dst)
            continue
        page = build_page(src, errors)
        if page:
            dst.with_suffix(".html").write_text(page, encoding="utf-8")
            count += 1
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"{count}개 페이지를 site/ 에 만들었다")
    return 0


if __name__ == "__main__":
    sys.exit(main())

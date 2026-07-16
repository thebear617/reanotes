#!/usr/bin/env python3
"""migrate_cards.py — 一次性：把 replearning.js 里的内联 body: HTML 反推成 .md 源文件。

产出：
    content/replearning/<page>/<slug>.md
        文件头 frontmatter（icon/title/tags/expanded），正文为标准 Markdown。

转换规则（覆盖现有卡片用到的全部结构）：
    <strong>            → **
    <em>               → *
    <span class="code-inline"> / <code>  → `
    <a href="X">Y</a>  → [Y](X)
    $...$ / $$...$$    → 原样保留（交运行时 KaTeX）
    <p> / <h3>         → 段落 / ### 标题
    <ul>/<ol class="nested-list"> → - / 1. 列表
    <div class="example-box"> → > 💡 标题\n> 内容（首行 emoji 即 callout）
        含 <pre> 的复杂 callout → 逐行 > 文本降级
    <table class="comp-table"> → GFM 表格；colspan → 加粗引导行降级
    <p style="...center">$x$</p> → $$x$$（块级居中）

注意：本脚本只负责「生成源文件」，不改 replearning.js。
生成后请手跑 build-cards.py 看结果，再用 cards-diff 校验保真。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# HTML → 节点树
# ---------------------------------------------------------------------------


class _Node:
    __slots__ = ("tag", "attrs", "children", "text")

    def __init__(self, tag=None, attrs=None, children=None, text=None):
        self.tag = tag
        self.attrs = dict(attrs or [])
        self.children = children or []
        self.text = text


class _FragParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node(children=[])
        self.stack = [self.root]
        self._tb: list[str] = []

    def _flush(self):
        if self._tb:
            self.stack[-1].children.append(_Node(text="".join(self._tb)))
            self._tb = []

    def handle_starttag(self, tag, attrs):
        self._flush()
        nd = _Node(tag=tag, attrs=attrs, children=[])
        self.stack[-1].children.append(nd)
        self.stack.append(nd)

    def handle_startendtag(self, tag, attrs):
        self._flush()
        self.stack[-1].children.append(_Node(tag=tag, attrs=attrs, children=[]))

    def handle_endtag(self, tag):
        self._flush()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self._tb.append(data)

    def close(self):
        self._flush()
        super().close()


def _html_to_nodes(html: str) -> list[_Node]:
    p = _FragParser()
    p.feed(html)
    p.close()
    return p.root.children


# ---------------------------------------------------------------------------
# 节点 → Markdown
# ---------------------------------------------------------------------------


def _inline(node: _Node) -> str:
    if node.text is not None:
        return node.text
    cls = node.attrs.get("class", "")
    tag = node.tag
    if tag == "strong":
        return "**" + _inline_children(node) + "**"
    if tag == "em":
        return "*" + _inline_children(node) + "*"
    if tag in ("code", "span") and "code-inline" in cls:
        return "`" + _inline_children(node) + "`"
    if tag == "a":
        return "[" + _inline_children(node) + "](" + node.attrs.get("href", "") + ")"
    if tag == "br":
        return "\n"
    if tag in ("ul", "ol"):
        return "\n" + _list_md(node)
    return _inline_children(node)


def _inline_children(node: _Node) -> str:
    return "".join(_inline(c) for c in node.children)


def _list_md(node: _Node) -> str:
    marker = "- " if node.tag == "ul" else "1. "
    lines = []
    for li in node.children:
        if li.tag != "li":
            continue
        lines.append(marker + _inline_children(li).strip())
    return "\n".join(lines)


def _callout_md(node: _Node) -> str:
    title_node = None
    rest = []
    for c in node.children:
        if c.tag == "div" and "example-box-title" in c.attrs.get("class", ""):
            title_node = c
        else:
            rest.append(c)
    if title_node is None:
        return _inline_children(node)
    title = _inline_children(title_node).strip()
    out = ["> " + title]
    for c in rest:
        if c.tag == "p":
            out.append("> " + _inline_children(c).strip())
        elif c.tag == "pre":
            for line in _inline_children(c).split("\n"):
                out.append("> " + line)
        elif c.text is not None and c.text.strip():
            out.append("> " + c.text.strip())
        else:
            m = _top_md(c)
            if m:
                out.append("> " + m.replace("\n", "\n> "))
    return "\n".join(out)


def _table_md(node: _Node) -> str:
    raw_rows: list[list[tuple[str, int]]] = []
    for tr in node.children:
        if tr.tag != "tr":
            continue
        cells = []
        for c in tr.children:
            if c.tag in ("td", "th"):
                colspan = int(c.attrs.get("colspan", "1") or 1)
                cells.append((_inline_children(c).strip(), colspan))
        if cells:
            raw_rows.append(cells)

    lead_ins: list[str] = []
    table_rows: list[list[str]] = []
    for cells in raw_rows:
        if any(col > 1 for _, col in cells):
            txt = "".join(t for t, _ in cells if t.strip())
            lead_ins.append("**" + txt + "**")
        else:
            table_rows.append([t for t, _ in cells])

    if not table_rows:
        return "\n".join(lead_ins)

    header = table_rows[0]
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("| " + " | ".join("---" for _ in header) + " |")
    for r in table_rows[1:]:
        lines.append("| " + " | ".join(r) + " |")
    body = "\n".join(lines)
    if lead_ins:
        return "\n".join(lead_ins) + "\n\n" + body
    return body


def _top_md(node: _Node) -> str:
    if node.text is not None:
        return node.text.strip()
    tag = node.tag
    cls = node.attrs.get("class", "")
    if tag == "p":
        if node.attrs:
            style = node.attrs.get("style", "")
            inner = _inline_children(node).strip()
            if (
                "center" in style
                and inner.startswith("$")
                and inner.endswith("$")
            ):
                return "$$" + inner[1:-1] + "$$"
            return inner
        return _inline_children(node)
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        return "#" * int(tag[1]) + " " + _inline_children(node).strip()
    if tag in ("ul", "ol"):
        return _list_md(node)
    if tag == "div" and "example-box" in cls:
        return _callout_md(node)
    if tag == "blockquote":
        return "> " + _inline_children(node).strip()
    if tag == "table":
        return _table_md(node)
    if tag == "pre":
        return "```\n" + _inline_children(node) + "\n```"
    if tag == "hr":
        return "---"
    return _inline_children(node)


def html_to_markdown(html: str) -> str:
    nodes = _html_to_nodes(html)
    blocks = []
    for nd in nodes:
        if nd.text is not None:
            if nd.text.strip():
                blocks.append(nd.text.strip())
            continue
        m = _top_md(nd)
        if m:
            m = m.strip("\n")
            if m:
                blocks.append(m)
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# 解析 replearning.js 中的卡片
# ---------------------------------------------------------------------------

_CARD_RE = re.compile(
    r"icon:\s*'([^']*)'\s*,\s*"
    r"title:\s*'([^']*)'\s*,\s*"
    r"tags:\s*\[([^\]]*)\]\s*,\s*"
    r"expanded:\s*(\w+)\s*,\s*"
    r"body:\s*`(.*?)`",
    re.DOTALL,
)

_PAGE_RE = re.compile(r"CONTENT\['(\w[\w-]*)'\]\s*=\s*\{")

_SLUG_UNSAFE = re.compile(r'[\\/:*?"<>|]')


def _slug(title: str, used: set[str]) -> str:
    base = _SLUG_UNSAFE.sub("_", title).strip().strip("_")
    if not base:
        base = "card"
    if base not in used:
        used.add(base)
        return base
    i = 2
    while f"{base}_{i}" in used:
        i += 1
    used.add(f"{base}_{i}")
    return f"{base}_{i}"


def _parse_tags(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    # 形如 '经典' 或 '理念', '总览'
    return [x.strip().strip("'\"") for x in raw.split(",") if x.strip()]


def migrate(reanotes_root: Path):
    src_file = reanotes_root / "js" / "boards" / "replearning.js"
    src = src_file.read_text(encoding="utf-8")

    page_blocks = list(_PAGE_RE.finditer(src))
    total = 0
    for idx, pb in enumerate(page_blocks):
        page = pb.group(1)
        start = pb.end()
        end = page_blocks[idx + 1].start() if idx + 1 < len(page_blocks) else len(src)
        region = src[start:end]
        cm = re.search(r"cards:\s*\[(.*?)\]\s*\n\};", region, re.DOTALL)
        if not cm:
            continue
        cards_region = cm.group(1)

        out_dir = reanotes_root / "content" / "replearning" / page
        out_dir.mkdir(parents=True, exist_ok=True)
        used: set[str] = set()

        for m in _CARD_RE.finditer(cards_region):
            icon, title, tags_raw, expanded, body = m.groups()
            slug = _slug(title, used)
            md = (
                "---\n"
                f"icon: {icon}\n"
                f"title: {title}\n"
                f"tags: [{', '.join(_parse_tags(tags_raw))}]\n"
                f"expanded: {expanded}\n"
                "---\n\n"
                + html_to_markdown(body)
                + "\n"
            )
            (out_dir / f"{slug}.md").write_text(md, encoding="utf-8")
            total += 1
            print(f"  ✅ {page}/{slug}.md  ({title})")

    print(f"\n[migrate] 共生成 {total} 张卡片的 .md 源文件")
    print(f"[migrate] 输出目录: content/replearning/")


def main():
    script_dir = Path(__file__).resolve().parent
    reanotes_root = script_dir.parent
    print(f"[migrate] reanotes 根: {reanotes_root}")
    migrate(reanotes_root)


if __name__ == "__main__":
    main()

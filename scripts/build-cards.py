#!/usr/bin/env python3
"""build-cards.py — 从 content/replearning/**.md 生成 js/boards/replearning.cards.js。

设计目标（与 personal/build-diary.py 同构）：
    Markdown 当源文件，push 前用本脚本把 .md 编译成「内联 HTML 字符串」，
    运行时零依赖、零 fetch、无 file:// 问题，单套渲染逻辑。

约定：
    content/replearning/<page>/<slug>.md   一张卡片一个文件
    文件头 frontmatter：
        ---
        icon: 🏛️
        title: ImageNet 预训练范式
        tags: [经典]
        expanded: true
        ---
    正文用标准 Markdown，支持：
        **加粗** *斜体* `行内代码`
        #/##/### 标题
        - 列表 / 1. 有序列表   → 自动套 .nested-list
        | a | b |               → 自动套 .comp-table
        > 💡 标题\n> 内容      → 自动套 .example-box（首行 emoji 即 callout）
        > 普通引用              → 普通 blockquote
        ```代码块```
        $行内公式$ $$块级公式$$   → 原样保留，交给运行时 KaTeX（renderMathInElement）

用法：
    python3 scripts/build-cards.py            # 生成
    python3 scripts/build-cards.py --dry-run # 只打印统计，不写文件
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from html import escape

# ---------------------------------------------------------------------------
# Markdown → HTML 转换器（复用 build-papers.py 的零依赖实现，math 原样保留）
# ---------------------------------------------------------------------------

_INLINE_TAG_RE = re.compile(r"(\*\*|__)(.+?)\1")            # **bold**
_INLINE_EM_RE  = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)")  # *italic* (not **)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+?)`")                 # `code`
_LINK_RE       = re.compile(r"\[([^\]]*?)\]\(([^)]+?)\)")    # [text](url)
_IMG_RE        = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")     # ![alt](url)
_LATEX_INLINE_RE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")  # $math$
_LATEX_BLOCK_RE  = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)    # $$math$$
_TABLE_SEP_RE  = re.compile(r"^\|[-:\s|]+\|\s*$")           # |---|---|


def _convert_inline(text: str) -> str:
    """转换一行内的 markdown 内联元素为 HTML。math 原样保留。"""
    # 1) 先保护图片（避免被其他规则误匹配）
    imgs = []

    def _save_img(m):
        imgs.append(f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">')
        return f"\x00IMG{len(imgs) - 1}\x00"

    text = _IMG_RE.sub(_save_img, text)

    # 2) 保护 math（$...$ / $$...$$），转换后再原样还原，交给运行时 KaTeX
    math_spans = []

    def _save_math(m):
        math_spans.append(m.group(0))
        return f"\x00MATH{len(math_spans) - 1}\x00"

    text = _LATEX_BLOCK_RE.sub(_save_math, text)
    text = _LATEX_INLINE_RE.sub(_save_math, text)

    # 3) 其他内联规则
    text = _INLINE_TAG_RE.sub(r"<strong>\2</strong>", text)
    text = _INLINE_EM_RE.sub(r"<em>\1</em>", text)
    text = _INLINE_CODE_RE.sub(r"<code>\1</code>", text)
    text = _LINK_RE.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)

    # 4) 还原 math（保持原始 $...$ / $$...$$ 文本，运行时再渲染）
    for i, m in enumerate(math_spans):
        text = text.replace(f"\x00MATH{i}\x00", m)

    # 5) 还原图片
    for i, img in enumerate(imgs):
        text = text.replace(f"\x00IMG{i}\x00", img)

    return text


def _flush_table(rows, output):
    if len(rows) < 2:
        return
    body_rows = [rows[0]]
    for r in rows[1:]:
        if not _TABLE_SEP_RE.match(r):
            body_rows.append(r)
    html_rows = []
    for idx, row in enumerate(body_rows):
        tag = "th" if idx == 0 else "td"
        cells = [
            f"<{tag}>{_convert_inline(c.strip())}</{tag}>"
            for c in row.strip("|").split("|")
        ]
        html_rows.append("<tr>" + "".join(cells) + "</tr>")
    output.append("<table>" + "".join(html_rows) + "</table>")


def _md_to_html(md_text: str) -> str:
    """将 markdown 文本转为 HTML 片段。"""
    lines = md_text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    def flush_buf(buf_type, buf):
        if not buf:
            return
        if buf_type == "p":
            out.append("<p>" + " ".join(buf) + "</p>")
        elif buf_type == "ul":
            items = "".join(f"<li>{li}</li>" for li in buf)
            out.append(f"<ul>{items}</ul>")
        elif buf_type == "ol":
            items = "".join(f"<li>{li}</li>" for li in buf)
            out.append(f"<ol>{items}</ol>")
        elif buf_type == "bq":
            out.append("<blockquote>" + "<br>".join(buf) + "</blockquote>")
        elif buf_type == "code":
            code = "\n".join(buf)
            out.append(f"<pre><code>{escape(code)}</code></pre>")
        elif buf_type == "table":
            _flush_table(buf, out)

    buf_type = None
    buf: list[str] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if stripped == "":
            flush_buf(buf_type, buf)
            buf_type = None
            buf = []
            i += 1
            continue

        if stripped.startswith("```"):
            flush_buf(buf_type, buf)
            buf_type = "code"
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            flush_buf("code", buf)
            buf_type = None
            buf = []
            i += 1
            continue

        h = re.match(r"^(#{1,6})\s+(.+)", stripped)
        if h:
            flush_buf(buf_type, buf)
            level = len(h.group(1))
            out.append(f"<h{level}>{_convert_inline(h.group(2))}</h{level}>")
            buf_type = None
            buf = []
            i += 1
            continue

        ul = re.match(r"^[-*+]\s+(.+)", stripped)
        if ul:
            if buf_type != "ul":
                flush_buf(buf_type, buf)
                buf_type = "ul"
                buf = []
            buf.append(_convert_inline(ul.group(1)))
            i += 1
            continue

        ol = re.match(r"^\d+[.)]\s+(.+)", stripped)
        if ol:
            if buf_type != "ol":
                flush_buf(buf_type, buf)
                buf_type = "ol"
                buf = []
            buf.append(_convert_inline(ol.group(1)))
            i += 1
            continue

        bq = re.match(r"^>\s?(.*)", stripped)
        if bq:
            if buf_type != "bq":
                flush_buf(buf_type, buf)
                buf_type = "bq"
                buf = []
            buf.append(_convert_inline(bq.group(1)))
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            if buf_type != "table":
                flush_buf(buf_type, buf)
                buf_type = "table"
                buf = []
            buf.append(stripped)
            i += 1
            continue

        if re.match(r"^[-*_]{3,}\s*$", stripped):
            flush_buf(buf_type, buf)
            out.append("<hr>")
            buf_type = None
            buf = []
            i += 1
            continue

        if buf_type != "p":
            flush_buf(buf_type, buf)
            buf_type = "p"
            buf = []
        buf.append(_convert_inline(stripped))
        i += 1

    flush_buf(buf_type, buf)
    return "\n".join(out)


# ---------------------------------------------------------------------------
# 设计 class 桥接（让 Markdown 输出套上现有卡片样式）
# ---------------------------------------------------------------------------

def _is_emoji(ch: str) -> bool:
    if not ch:
        return False
    cp = ord(ch)
    return (
        0x1F000 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or 0x2B00 <= cp <= 0x2BFF
        or 0x2300 <= cp <= 0x23FF
        or 0xFE0F == cp
    )


def _callout_bridge(html: str) -> str:
    """把「首行以 emoji 引导的 blockquote」转成 .example-box。"""
    def repl(m):
        inner = m.group(1)
        parts = inner.split("<br>")
        if not parts:
            return m.group(0)
        first_text = re.sub(r"<[^>]+>", "", parts[0]).strip()
        if not first_text or not _is_emoji(first_text[0]):
            return m.group(0)
        title = parts[0]
        rest_lines = [ln for ln in parts[1:] if ln.strip()]
        rest_html = "".join(f"<p>{ln}</p>" for ln in rest_lines)
        return (
            f'<div class="example-box">'
            f'<div class="example-box-title">{title}</div>'
            f"{rest_html}</div>"
        )

    return re.sub(r"<blockquote>(.*?)</blockquote>", repl, html, flags=re.DOTALL)


def _apply_bridge(html: str) -> str:
    # 列表 → nested-list
    html = html.replace("<ul>", '<ul class="nested-list">')
    html = html.replace("<ol>", '<ol class="nested-list">')
    # 表格 → comp-table
    html = html.replace("<table>", '<table class="comp-table">')
    # 行内 code → code-inline（但不影响 <pre> 里的 code）
    html = html.replace("<code>", '<code class="code-inline">')
    html = re.sub(r"<pre><code class=\"code-inline\">", "<pre><code>", html)
    # callout
    html = _callout_bridge(html)
    return html


# ---------------------------------------------------------------------------
# frontmatter 解析
# ---------------------------------------------------------------------------

def _parse_frontmatter(text: str):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.DOTALL)
    if not m:
        return {}, text
    fm, body = m.group(1), m.group(2)
    meta: dict = {}
    for line in fm.split("\n"):
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            meta[k] = [x.strip() for x in inner.split(",") if x.strip()] if inner else []
        elif v.lower() in ("true", "false"):
            meta[k] = v.lower() == "true"
        else:
            meta[k] = v.strip('"').strip("'")
    return meta, body


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="从 content/replearning/**.md 生成卡片 JS")
    parser.add_argument("--dry-run", action="store_true", help="只打印统计，不写文件")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    reanotes_root = script_dir.parent
    content_dir = reanotes_root / "content" / "replearning"
    out_js = reanotes_root / "js" / "boards" / "replearning.cards.js"

    if not content_dir.is_dir():
        print(f"[build-cards] ⚠️ 内容目录不存在: {content_dir}")
        sys.exit(1)

    cards: dict[str, list] = {}
    for page_dir in sorted(content_dir.iterdir()):
        if not page_dir.is_dir():
            continue
        page = page_dir.name
        page_cards = []
        for md_file in sorted(page_dir.glob("*.md")):
            raw = md_file.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(raw)
            html = _md_to_html(body)
            html = _apply_bridge(html)
            card = {
                "icon": meta.get("icon", ""),
                "title": meta.get("title", md_file.stem),
                "tags": meta.get("tags", []),
                "expanded": bool(meta.get("expanded", False)),
                "body": html,
            }
            page_cards.append(card)
        if page_cards:
            cards[page] = page_cards

    total = sum(len(v) for v in cards.values())
    print(f"[build-cards] 扫描到 {len(cards)} 个页面、{total} 张卡片")

    if args.dry_run:
        for page, clist in cards.items():
            print(f"  - {page}: {len(clist)} 张")
        return

    js = (
        "/* ===== 表征学习 · 卡片数据 =====\n"
        " * 由 scripts/build-cards.py 从 content/replearning/**.md 自动生成。\n"
        " * 请勿手改本文件；改 content/ 下的 .md 后重跑 build-cards.py。\n"
        " */\n"
        "window.REPLEARNING_CARDS = "
        + json.dumps(cards, ensure_ascii=False, indent=2)
        + ";\n"
    )
    out_js.parent.mkdir(parents=True, exist_ok=True)
    out_js.write_text(js, encoding="utf-8")
    print(f"[build-cards] ✅ 已生成: {out_js} ({out_js.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

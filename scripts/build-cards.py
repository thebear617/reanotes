#!/usr/bin/env python3
"""build-cards.py — 从 Markdown 内容目录生成表征学习页面数据。

设计目标（与 personal/build-diary.py 同构）：
    Markdown 当源文件，push 前用本脚本把 .md 编译成「内联 HTML 字符串」，
    运行时零依赖、零 fetch、无 file:// 问题，单套渲染逻辑。

约定：
    content/tabs/replearning/pages.json                  页面目录与卡片排列
    content/tabs/replearning/boards/<board>/<slug>.md    一张卡片一个文件
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
    python3 scripts/build-cards.py --check   # 检查生成物是否最新
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

        # 标准 Markdown 允许直接嵌入 HTML。复杂表格、布局和 callout 可用
        # 原生 HTML 表达；编译器保持原样，避免损失 colspan/style 等信息。
        if stripped.startswith("<"):
            flush_buf(buf_type, buf)
            raw_html = [line]
            i += 1
            while i < n and lines[i].strip() != "":
                raw_html.append(lines[i])
                i += 1
            out.append("\n".join(raw_html))
            buf_type = None
            buf = []
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
        rest_html = f"<p>{'<br>'.join(rest_lines)}</p>" if rest_lines else ""
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
    # 行内 code → 现有设计使用的 code-inline span（不影响代码块）
    html = html.replace("<code>", '<span class="code-inline">')
    html = html.replace("</code>", "</span>")
    html = re.sub(r"<pre><span class=\"code-inline\">", "<pre><code>", html)
    html = html.replace("</span></pre>", "</code></pre>")
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

def _fail(message: str):
    print(f"[build-cards] ❌ {message}", file=sys.stderr)
    raise SystemExit(1)


def _load_catalog(content_dir: Path):
    catalog_path = content_dir / "pages.json"
    if not catalog_path.is_file():
        _fail(f"缺少内容目录: {catalog_path}")
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _fail(f"pages.json 格式错误: {exc}")

    pages = catalog.get("pages")
    if not isinstance(pages, list) or not pages:
        _fail("pages.json 必须包含非空 pages 数组")
    return pages


def _build_content(content_dir: Path):
    pages = _load_catalog(content_dir)
    generated: dict[str, dict] = {}
    referenced_files: set[Path] = set()

    for page in pages:
        page_id = page.get("id")
        title = page.get("title")
        desc = page.get("desc")
        card_entries = page.get("cards")
        if not page_id or not title or not isinstance(desc, str):
            _fail("每个页面必须包含 id、title 和 desc")
        if page_id in generated:
            _fail(f"页面 id 重复: {page_id}")
        if not isinstance(card_entries, list) or not card_entries:
            _fail(f"页面 {page_id} 没有 cards")

        page_cards = []
        for entry in card_entries:
            overrides = {}
            if isinstance(entry, str):
                relative_path = entry
            elif isinstance(entry, dict) and isinstance(entry.get("path"), str):
                relative_path = entry["path"]
                overrides = {k: v for k, v in entry.items() if k != "path"}
            else:
                _fail(f"页面 {page_id} 含无效卡片条目: {entry!r}")

            md_file = (content_dir / relative_path).resolve()
            try:
                md_file.relative_to(content_dir.resolve())
            except ValueError:
                _fail(f"卡片路径越出内容目录: {relative_path}")
            if not md_file.is_file() or md_file.suffix != ".md":
                _fail(f"找不到 Markdown 卡片: {relative_path}")
            referenced_files.add(md_file)

            raw = md_file.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(raw)
            if not meta.get("title"):
                _fail(f"卡片缺少 frontmatter title: {relative_path}")
            if not body.strip():
                _fail(f"卡片正文为空: {relative_path}")
            card = {
                "icon": meta.get("icon", ""),
                "title": meta["title"],
                "tags": meta.get("tags", []),
                "expanded": bool(meta.get("expanded", False)),
                "body": _apply_bridge(_md_to_html(body)),
            }
            unknown_overrides = set(overrides) - {"icon", "title", "tags", "expanded"}
            if unknown_overrides:
                _fail(
                    f"卡片 {relative_path} 含未知覆盖字段: "
                    + ", ".join(sorted(unknown_overrides))
                )
            card.update(overrides)
            page_cards.append(card)

        generated[page_id] = {"title": title, "desc": desc, "cards": page_cards}

    boards_dir = content_dir / "boards"
    all_markdown = {path.resolve() for path in boards_dir.rglob("*.md")}
    unreferenced = sorted(all_markdown - referenced_files)
    if unreferenced:
        relative = ", ".join(str(path.relative_to(content_dir)) for path in unreferenced)
        _fail(f"存在未登记的 Markdown 文件: {relative}")

    return generated


def _render_js(content: dict[str, dict]) -> str:
    return (
        "/* ===== 表征学习 · Markdown 编译内容 =====\n"
        " * 由 scripts/build-cards.py 根据 content/tabs/replearning/pages.json 与 Markdown 自动生成。\n"
        " * 请勿手改本文件；编辑 content/ 后重新运行构建脚本。\n"
        " */\n"
        "window.REPLEARNING_CONTENT = "
        + json.dumps(content, ensure_ascii=False, indent=2)
        + ";\n"
    )


def main():
    parser = argparse.ArgumentParser(description="从 Markdown 内容目录生成表征学习页面 JS")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="只打印统计，不写文件")
    mode.add_argument("--check", action="store_true", help="检查生成物是否最新")
    args = parser.parse_args()

    reanotes_root = Path(__file__).resolve().parent.parent
    content_dir = reanotes_root / "content" / "tabs" / "replearning"
    out_js = reanotes_root / "js" / "boards" / "replearning.cards.js"
    if not content_dir.is_dir():
        _fail(f"内容目录不存在: {content_dir}")

    content = _build_content(content_dir)
    total = sum(len(page["cards"]) for page in content.values())
    print(f"[build-cards] 扫描到 {len(content)} 个页面、{total} 个卡片位置")
    if args.dry_run:
        for page_id, page in content.items():
            print(f"  - {page_id}: {len(page['cards'])} 张")
        return

    js = _render_js(content)
    if args.check:
        if not out_js.is_file() or out_js.read_text(encoding="utf-8") != js:
            _fail("生成物已过期，请运行 python3 scripts/build-cards.py")
        print("[build-cards] ✅ 生成物已是最新")
        return

    out_js.parent.mkdir(parents=True, exist_ok=True)
    out_js.write_text(js, encoding="utf-8")
    print(f"[build-cards] ✅ 已生成: {out_js} ({out_js.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

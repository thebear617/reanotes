#!/usr/bin/env python3
"""build-papers.py — 从翻译产物生成 reanotes 论文板块 JS 数据文件。

用法:
    python3 scripts/build-papers.py                    # 扫描 output/translations/
    python3 scripts/build-papers.py --dry-run           # 只打印，不写文件
    python3 scripts/build-papers.py --dir /path/to/translations

产出:
    js/boards/papers-translations.js  — 全局翻译字典（按 arXiv ID 索引）

图片处理:
    宽度超过 MAX_WIDTH(1200px) 的图片自动等比例缩小。MinerU 输出的 JPG
    已高压缩，不做质量重编码。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from html import escape

# ---------------------------------------------------------------------------
# Markdown → HTML 转换器（仅标准库，零依赖）
# ---------------------------------------------------------------------------

_INLINE_TAG_RE = re.compile(r"(\*\*|__)(.+?)\1")          # **bold**
_INLINE_EM_RE  = re.compile(r"(?<!\*)\*([^*\n]+?)\*(?!\*)") # *italic* (not **)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+?)`")              # `code`
_LINK_RE       = re.compile(r"\[([^\]]*?)\]\(([^)]+?)\)")  # [text](url)
_IMG_RE        = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")   # ![alt](url)
_LATEX_INLINE_RE = re.compile(r"(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)")  # $math$
_LATEX_BLOCK_RE  = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)  # $$math$$
_TABLE_SEP_RE  = re.compile(r"^\|[-:\s|]+\|\s*$")          # |---|---|

def _rewrite_img_path(match, paper_rel_path):
    """将 markdown 图片路径改写为相对于 index.html 的路径。"""
    alt = match.group(1)
    path = match.group(2)
    # 已经是绝对路径或外部 URL 的不动
    if path.startswith(("http://", "https://", "/")):
        return f'<img src="{path}" alt="{alt}">'
    # 相对路径 → 相对于 reanotes 根
    full = f"{paper_rel_path}/{path}"
    return f'<img src="{full}" alt="{alt}" loading="lazy">'

def _convert_inline(text: str, paper_rel_path: str = "") -> str:
    """转换一行内的 markdown 内联元素为 HTML。"""
    # 先保护图片（避免被其他规则误匹配）
    imgs = []

    def _save_img(m):
        imgs.append(_rewrite_img_path(m, paper_rel_path))
        return f"\x00IMG{len(imgs)-1}\x00"

    text = _IMG_RE.sub(_save_img, text)
    # LaTeX block
    text = _LATEX_BLOCK_RE.sub(r'<div class="math-block">$$\1$$</div>', text)
    # LaTeX inline
    text = _LATEX_INLINE_RE.sub(r'<span class="math-inline">$\1$</span>', text)
    # Bold
    text = _INLINE_TAG_RE.sub(r"<strong>\2</strong>", text)
    # Italic
    text = _INLINE_EM_RE.sub(r"<em>\1</em>", text)
    # Code
    text = _INLINE_CODE_RE.sub(r"<code>\1</code>", text)
    # Links
    text = _LINK_RE.sub(r'<a href="\2" target="_blank" rel="noopener">\1</a>', text)
    # 还原图片
    for i, img in enumerate(imgs):
        text = text.replace(f"\x00IMG{i}\x00", img)
    return text

def _md_to_html(md_text: str, paper_rel_path: str = "") -> str:
    """将 markdown 文本转为 HTML 片段（不含外层标签）。

    处理: 标题、段落、无序/有序列表、引用块、表格、代码块。
    """
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

    def _flush_table(rows, output):
        if len(rows) < 2:
            return
        # 跳过分隔行
        body_rows = [rows[0]]
        for r in rows[1:]:
            if not _TABLE_SEP_RE.match(r):
                body_rows.append(r)
        html_rows = []
        for idx, row in enumerate(body_rows):
            tag = "th" if idx == 0 else "td"
            cells = [f"<{tag}>{_convert_inline(c.strip(), paper_rel_path)}</{tag}>"
                     for c in row.strip("|").split("|")]
            html_rows.append("<tr>" + "".join(cells) + "</tr>")
        output.append("<table>" + "".join(html_rows) + "</table>")

    buf_type = None
    buf: list[str] = []

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # 空行 → flush
        if stripped == "":
            flush_buf(buf_type, buf)
            buf_type = None
            buf = []
            i += 1
            continue

        # 代码块 ```
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

        # 标题
        h = re.match(r"^(#{1,6})\s+(.+)", stripped)
        if h:
            flush_buf(buf_type, buf)
            level = len(h.group(1))
            content = _convert_inline(h.group(2), paper_rel_path)
            out.append(f"<h{level}>{content}</h{level}>")
            buf_type = None
            buf = []
            i += 1
            continue

        # 无序列表
        ul = re.match(r"^[-*+]\s+(.+)", stripped)
        if ul:
            if buf_type != "ul":
                flush_buf(buf_type, buf)
                buf_type = "ul"
                buf = []
            buf.append(_convert_inline(ul.group(1), paper_rel_path))
            i += 1
            continue

        # 有序列表
        ol = re.match(r"^\d+[.)]\s+(.+)", stripped)
        if ol:
            if buf_type != "ol":
                flush_buf(buf_type, buf)
                buf_type = "ol"
                buf = []
            buf.append(_convert_inline(ol.group(1), paper_rel_path))
            i += 1
            continue

        # 引用块
        bq = re.match(r"^>\s?(.*)", stripped)
        if bq:
            if buf_type != "bq":
                flush_buf(buf_type, buf)
                buf_type = "bq"
                buf = []
            buf.append(_convert_inline(bq.group(1), paper_rel_path))
            i += 1
            continue

        # 表格行
        if stripped.startswith("|") and stripped.endswith("|"):
            if _TABLE_SEP_RE.match(stripped):
                # 表格分隔行也加入 buf，flush 时会跳过
                pass
            if buf_type != "table":
                flush_buf(buf_type, buf)
                buf_type = "table"
                buf = []
            buf.append(stripped)
            i += 1
            continue

        # 水平线
        if re.match(r"^[-*_]{3,}\s*$", stripped):
            flush_buf(buf_type, buf)
            out.append("<hr>")
            buf_type = None
            buf = []
            i += 1
            continue

        # 默认：段落
        if buf_type != "p":
            flush_buf(buf_type, buf)
            buf_type = "p"
            buf = []
        buf.append(_convert_inline(stripped, paper_rel_path))
        i += 1

    flush_buf(buf_type, buf)
    return "\n".join(out)

# ---------------------------------------------------------------------------
# 论文解析
# ---------------------------------------------------------------------------

def _extract_title(body: str) -> tuple[str, str, str]:
    """从 markdown body 提取 (英文标题, 中文题名, 剩余内容)。"""
    lines = body.strip().split("\n")
    start = 0
    while start < len(lines) and lines[start].strip() == "":
        start += 1

    en_title = "Untitled"
    cn_title = ""
    rest_start = start

    # 找第一个 H1
    for i in range(start, len(lines)):
        m = re.match(r"^#\s+(.+)", lines[i].strip())
        if m:
            en_title = m.group(1).strip()
            rest_start = i + 1
            break

    # 跳过 H1 后的空行，检查是否有「> 中文题名：...」blockquote
    j = rest_start
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines):
        bq = re.match(r"^>\s*中文题名[：:]\s*(.+)", lines[j].strip())
        if bq:
            cn_title = bq.group(1).strip()
            j += 1  # 跳过这行
            # 再跳过一个可能的空行
            while j < len(lines) and lines[j].strip() == "":
                j += 1

    rest = "\n".join(lines[j:])
    return en_title, cn_title, rest

def _split_sections(body: str) -> list[tuple[str, str]]:
    """将 markdown 按 ## 标题切分为章节列表 [(标题, 内容), ...]。

    第一个 H2 之前的内容作为「摘要」。
    """
    lines = body.split("\n")
    sections: list[tuple[str, str]] = []
    current_title = "摘要"
    current_lines: list[str] = []

    for line in lines:
        m = re.match(r"^##\s+(.+)", line.strip())
        if m:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = m.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    return sections

# ---------------------------------------------------------------------------
# JS 生成 — 翻译字典（由 litTable 交叉引用）
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 图片优化（压缩体积，不改变文件名）
# ---------------------------------------------------------------------------

MAX_WIDTH = 1200
JPEG_QUALITY = 85

def optimize_images(translations_dir: Path, dry_run: bool = False) -> tuple[int, int]:
    """压缩 oversize 论文图片，返回 (处理数, 节省字节数)。

    仅处理宽度超过 MAX_WIDTH 的图片，等比例缩小。
    MinerU 输出的 JPG 已是高压缩率，不做质量重编码（反而可能变大）。
    """
    try:
        from PIL import Image
    except ImportError:
        print("[build-papers] ⚠️  Pillow 未安装，跳过图片优化 (pip install Pillow)")
        return 0, 0

    processed = 0
    saved = 0
    exts = {".jpg", ".jpeg", ".png"}

    for date_dir in sorted(translations_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        for paper_dir in sorted(date_dir.iterdir()):
            img_dir = paper_dir / "images"
            if not img_dir.is_dir():
                continue
            for img_path in sorted(img_dir.iterdir()):
                if img_path.suffix.lower() not in exts:
                    continue
                try:
                    with Image.open(img_path) as im:
                        w, h = im.size
                        orig_size = img_path.stat().st_size

                        if w <= MAX_WIDTH:
                            continue

                        # 等比例缩到 MAX_WIDTH
                        ratio = MAX_WIDTH / w
                        new_size_tuple = (MAX_WIDTH, int(h * ratio))
                        im = im.resize(new_size_tuple, Image.LANCZOS)

                        # 移除 EXIF，保留原质量
                        save_kwargs = {}
                        if im.format == "JPEG":
                            save_kwargs["quality"] = JPEG_QUALITY
                        if im.format == "PNG":
                            save_kwargs["optimize"] = True

                        if dry_run:
                            print(f"  [DRY RUN] 缩放: {img_path.name}  {w}x{h} → {new_size_tuple[0]}x{new_size_tuple[1]}")
                            processed += 1
                            saved += max(0, orig_size - (orig_size * ratio * ratio * 0.8))
                            continue

                        im.save(img_path, **save_kwargs)
                        new_size = img_path.stat().st_size
                        delta = orig_size - new_size
                        saved += delta
                        processed += 1
                        print(f"  图片缩放: {img_path.name}  {w}x{h} → {new_size_tuple[0]}x{new_size_tuple[1]}, "
                              f"{orig_size//1024}KB → {new_size//1024}KB (-{max(0,delta)//1024}KB)")
                except Exception as e:
                    print(f"  图片优化失败: {img_path.name}: {e}")

    return processed, saved

_JS_ESCAPE_MAP = {
    "\\": "\\\\",
    "'": "\\'",
    "\n": "\\n",
}
_JS_ESCAPE_RE = re.compile(r"[\\'\n]")


_JS_ESCAPE_MAP = {
    "\\": "\\\\",
    "'": "\\'",
    "\n": "\\n",
}
_JS_ESCAPE_RE = re.compile(r"[\\'\n]")

def _js_str(s: str) -> str:
    return "'" + _JS_ESCAPE_RE.sub(lambda m: _JS_ESCAPE_MAP[m.group()], s) + "'"

def _extract_arxiv_id(source_input: str) -> str:
    """从 URL 或路径中提取 arXiv ID。"""
    # 尝试匹配 arXiv URL: arxiv.org/abs/XXXX.XXXXX 或 arxiv.org/pdf/XXXX.XXXXX
    m = re.search(r"arxiv\.org/(?:abs|pdf)/([\d.]+(?:v\d+)?)", source_input)
    if m:
        return m.group(1)
    return ""

def _build_translations_js(papers: list[dict]) -> str:
    """生成 js/boards/papers-translations.js — 全局翻译字典。"""
    entries = []
    for p in papers:
        article_parts = []
        for section_title, section_html in p["sections"]:
            article_parts.append(f"<h2>{section_title}</h2>\n{section_html}")
        full_article = "\n".join(article_parts)

        arxiv_id = p.get("arxiv_id", "")
        if not arxiv_id:
            continue

        entries.append(
            "  " + _js_str(arxiv_id) + ": {\n"
            "    title: " + _js_str(p["title"]) + ",\n"
            "    date: " + _js_str(p["date"]) + ",\n"
            "    article: " + _js_str(full_article) + ",\n"
            "  }"
        )

    return (
        "/* ===== 论文翻译字典 =====\n"
        " * 由 scripts/build-papers.py 自动生成。\n"
        " * key = arXiv ID（如 1706.03762），value = { title, date, article }\n"
        " * 各板块 litTable 渲染时自动检测本字典，已翻译的论文替换为内部跳转链接。\n"
        " */\n"
        "window.PAPER_TRANSLATIONS = {\n"
        + ",\n".join(entries) + "\n"
        "};\n"
    )

# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def collect_papers(translations_dir: Path) -> list[dict]:
    """扫描翻译目录，收集所有论文信息。"""
    papers = []
    if not translations_dir.is_dir():
        print(f"[build-papers] 翻译目录不存在: {translations_dir}")
        return papers

    for date_dir in sorted(translations_dir.iterdir()):
        if not date_dir.is_dir():
            continue
        date_str = date_dir.name

        # 读 summary.json 获取论文名 → arXiv ID 的映射
        arxiv_map = {}
        summary_file = date_dir / "summary.json"
        if summary_file.is_file():
            try:
                summary = json.loads(summary_file.read_text(encoding="utf-8"))
                for item in summary.get("items", []):
                    source = item.get("source", "")
                    arxiv_input = item.get("source_input", "")
                    # 从 item.source 路径提取目录名
                    paper_name = Path(source).parent.name
                    arxiv_id = _extract_arxiv_id(arxiv_input)
                    if paper_name and arxiv_id:
                        arxiv_map[paper_name] = arxiv_id
            except (json.JSONDecodeError, KeyError):
                pass

        for paper_dir in sorted(date_dir.iterdir()):
            if not paper_dir.is_dir():
                continue
            zh_md = paper_dir / "full_zh.md"
            if not zh_md.is_file():
                continue

            arxiv_id = arxiv_map.get(paper_dir.name, "")
            if not arxiv_id:
                print(f"[build-papers] ⚠️  无法确定 arXiv ID: {date_str}/{paper_dir.name}，跳过")
                continue

            print(f"[build-papers] 处理: {date_str}/{paper_dir.name} → {arxiv_id}")
            raw = zh_md.read_text(encoding="utf-8")

            # 提取标题
            en_title, cn_title, body = _extract_title(raw)
            # 截取短标题（用于卡片/导航）
            short_title = cn_title if cn_title else (en_title[:40] + "…" if len(en_title) > 40 else en_title)
            display_title = f"{en_title} — {cn_title}" if cn_title else en_title

            # 论文在 translations 下的相对路径（用于图片路径改写）
            paper_rel = f"output/translations/{date_str}/{paper_dir.name}"

            # 切分章节
            sections = _split_sections(body)

            # 转换每个章节的 markdown 为 HTML
            html_sections = []
            for sec_title, sec_md in sections:
                # 跳过空章节
                if not sec_md.strip():
                    continue
                sec_html = _md_to_html(sec_md, paper_rel)
                if not sec_html.strip():
                    continue
                html_sections.append((sec_title, sec_html))

            papers.append({
                "id": f"paper-{date_str}-{paper_dir.name}",
                "arxiv_id": arxiv_id,
                "date": date_str,
                "en_title": en_title,
                "cn_title": cn_title,
                "title": display_title,
                "short_title": short_title,
                "source": f"output/translations/{date_str}/{paper_dir.name}/full.md",
                "sections": html_sections,
            })

    return papers

def main():
    parser = argparse.ArgumentParser(description="从翻译产物生成 reanotes 论文板块 JS")
    parser.add_argument("--dir", type=Path, default=None,
                        help="翻译产物根目录（默认: output/translations）")
    parser.add_argument("--dry-run", action="store_true",
                        help="只打印，不写文件")
    args = parser.parse_args()

    # 脚本位置: reanotes/scripts/build-papers.py
    script_dir = Path(__file__).resolve().parent
    reanotes_root = script_dir.parent  # reanotes/

    translations_dir = args.dir or (reanotes_root / "output" / "translations")
    output_js = reanotes_root / "js" / "boards" / "papers-translations.js"

    print(f"[build-papers] reanotes 根:  {reanotes_root}")
    print(f"[build-papers] 翻译目录:    {translations_dir}")
    print(f"[build-papers] 输出文件:    {output_js}")

    papers = collect_papers(translations_dir)

    if not papers:
        print("[build-papers] ⚠️  没有找到任何翻译产物（或无法确定 arXiv ID）。先跑 paper_translate.py 吧。")
        return

    print(f"[build-papers] 共 {len(papers)} 篇论文")
    for p in papers:
        print(f"  - [{p['date']}] [{p['arxiv_id']}] {p['title'][:60]}")

    # 压缩 oversize 图片
    opt_count, opt_saved = optimize_images(translations_dir, dry_run=args.dry_run)
    if opt_count > 0:
        print(f"[build-papers] 图片优化: {opt_count} 张, 节省 {opt_saved//1024}KB")

    js_content = _build_translations_js(papers)

    if args.dry_run:
        print("\n[build-papers] --dry-run 模式，不写文件。预览前 500 字符:")
        print(js_content[:500])
        return

    output_js.parent.mkdir(parents=True, exist_ok=True)
    output_js.write_text(js_content, encoding="utf-8")
    print(f"\n[build-papers] ✅ 已生成: {output_js}")
    print(f"[build-papers] 文件大小:   {output_js.stat().st_size:,} bytes")

    # 检查 index.html 是否引用了 papers-translations.js
    index_html = reanotes_root / "index.html"
    if index_html.is_file():
        content = index_html.read_text(encoding="utf-8")
        if "papers-translations.js" not in content:
            print(f"\n[build-papers] ⚠️  index.html 尚未引用 papers-translations.js。")
            print(f"   请在 boards 脚本之前添加：")
            print(f'   <script src="js/boards/papers-translations.js"></script>')
        else:
            print(f"[build-papers] ✅ index.html 已引用 papers-translations.js")


if __name__ == "__main__":
    main()

"""Clean, protect, and post-process academic Markdown before/after translation.

These rules are field-agnostic and were validated on the OVS 113-paper batch.
The pipeline is:

    raw full.md
      → strip_front_matter (drop everything before the first real H1 body)
      → strip_back_matter  (drop refs / appendix / acknowledgements)
      → normalize_html_tables (implemented in normalize_structures.py)
      → protect_html_tables  (placeholder, will be restored after LLM)
      → protect_markdown_images  (placeholder, will be restored after LLM)
      → protect_math  (implemented in placeholders.py)
      → [send to LLM]
      → validate + restore all placeholders
      → apply_title_policy  (keep EN H1, add `> 中文题名：…` line)
      → normalize images + run structural quality checks
      → full_zh.md + translation_report.json
"""

from __future__ import annotations

import re
from typing import Iterable

CHUNK_SIZE_WORDS = 3000

HTML_TABLE_RE = re.compile(r"<table\b[\s\S]*?</table>", re.IGNORECASE)
# Match the image-markdown portion of a line even when followed by caption text.
# The old `$` anchor dropped protection for `![](path)  Figure N. ...` lines,
# which then got mangled by the LLM (e.g. `[[IMAGE_001]]]`). We only require the
# image to start at the line beginning; whatever follows stays put and is
# translated normally.
IMAGE_LINE_RE = re.compile(r"(?m)^\s*!\[[^\]\n]*\]\([^)]+\)")


def split_chunks(text: str, max_words: int = CHUNK_SIZE_WORDS) -> list[str]:
    """Split text into paragraph-aligned chunks bounded by word count."""
    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    current: list[str] = []
    current_words = 0

    for paragraph in paragraphs:
        words = len(paragraph.split())
        if current and current_words + words > max_words:
            chunks.append("\n\n".join(current))
            current = [paragraph]
            current_words = words
        else:
            current.append(paragraph)
            current_words += words

    if current:
        chunks.append("\n\n".join(current))

    return chunks


def strip_front_matter(text: str) -> str:
    """Drop the author block / contents while keeping the first real section.

    Prefer an Abstract marker, then a numbered first section or Introduction.
    Only fall back to the first image when the extraction has no structural
    heading. This avoids dropping early sections in papers without Abstract.
    """
    lines = text.splitlines()
    if not lines:
        return text

    title_idx = next((idx for idx, line in enumerate(lines) if line.startswith("# ")), 0)
    title = lines[title_idx].rstrip()
    after_title = lines[title_idx + 1:]

    def first_matching(pattern: str) -> int | None:
        return next(
            (
                idx
                for idx, line in enumerate(after_title)
                if re.match(pattern, line.strip(), re.IGNORECASE)
            ),
            None,
        )

    abstract_start = first_matching(
        r"^(?:#{1,6}\s*)?abstract(?:\s*[—:-]|\s*$)"
    )
    section_start = first_matching(
        r"^#{2,6}\s+(?:1(?:\.\d+)*[.\s]|introduction\b)"
    )
    image_start = first_matching(r"^!\[.*?\]\(")
    body_start = next(
        (
            candidate
            for candidate in (abstract_start, section_start, image_start)
            if candidate is not None
        ),
        0,
    )

    body = "\n".join([title, ""] + after_title[body_start:]).strip() + "\n"
    body = re.sub(r"(?m)^Abstract\s*[—:-]\s*", "## Abstract\n\n", body)
    return body


def strip_back_matter(text: str) -> str:
    """Drop everything from References / Bibliography / Acknowledgements / Appendix onward."""
    lines = text.splitlines()
    kept: list[str] = []
    stop_re = re.compile(
        r"^#{1,6}\s*(?:\d+(?:\.\d+)*\.?\s*)?"
        r"(references|bibliography|acknowledg(?:e)?ments?|appendix|appendices|supplementary)\b",
        re.IGNORECASE,
    )
    for line in lines:
        if stop_re.match(line.strip()):
            break
        if re.match(r"^\s*ack(?:on)?wledg(?:e)?ments?\b\s*[:.]?", line, re.IGNORECASE):
            break
        kept.append(line)
    return "\n".join(kept).strip() + "\n"


def clean_body(text: str) -> str:
    """Normalize newlines and run front + back stripping."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = strip_front_matter(text)
    text = strip_back_matter(text)
    return text.strip() + "\n"


def protect_html_tables(text: str) -> tuple[str, dict[str, str]]:
    """Replace each <table> block with `[[[HTML_TABLE_NNN]]]` placeholder.

    Returns (protected_text, placeholder_map). The map can be passed to
    `restore_html_tables` to put the original tables back.
    """
    tables: dict[str, str] = {}

    def replace(match: re.Match) -> str:
        placeholder = f"[[[HTML_TABLE_{len(tables):03d}]]]"
        tables[placeholder] = match.group(0)
        return placeholder

    return HTML_TABLE_RE.sub(replace, text), tables


def restore_html_tables(text: str, tables: dict[str, str]) -> str:
    for placeholder, table in tables.items():
        text = text.replace(placeholder, table)
    return text


def protect_markdown_images(text: str) -> tuple[str, dict[str, str]]:
    """Replace each `![](path)` line prefix with `[[[IMAGE_NNN]]]` placeholder.

    Only the image-markdown prefix is protected; whatever caption text follows
    on the same line is left in place so the LLM can translate it normally.
    """
    images: dict[str, str] = {}

    def replace(match: re.Match) -> str:
        placeholder = f"[[[IMAGE_{len(images):03d}]]]"
        images[placeholder] = match.group(0)
        return placeholder

    return IMAGE_LINE_RE.sub(replace, text), images


def restore_markdown_images(text: str, images: dict[str, str]) -> str:
    for placeholder, image in images.items():
        text = text.replace(placeholder, image)
    return text


def apply_title_policy(source_text: str, translated_text: str) -> str:
    """Force a strict title layout: keep the original English H1, then add a
    `> 中文题名：…` line under it. If the LLM already produced a `> 中文题名：`
    line, keep its Chinese title. Otherwise lift the H2 directly after the H1
    (e.g. `## ReCo: …`) into the Chinese title slot — but only when that H2 is
    not `Abstract` / `Introduction` / `摘要` / `引言` / `介绍`.
    """
    source_lines = source_text.splitlines()
    translated_lines = translated_text.splitlines()
    source_title = next((line.strip() for line in source_lines if line.startswith("# ")), "")
    if not source_title:
        return translated_text

    title_idx = next(
        (idx for idx, line in enumerate(translated_lines) if line.startswith("# ")),
        None,
    )
    if title_idx is None:
        return f"{source_title}\n\n{translated_text.strip()}\n"

    existing_idx = title_idx + 1
    if existing_idx < len(translated_lines) and translated_lines[existing_idx].strip() == "":
        existing_idx += 1
    existing_chinese_title = ""
    if existing_idx < len(translated_lines) and translated_lines[existing_idx].startswith("> 中文题名："):
        existing_chinese_title = translated_lines[existing_idx].removeprefix("> 中文题名：").strip()

    translated_h1 = translated_lines[title_idx].removeprefix("# ").strip()
    if existing_chinese_title:
        chinese_title = existing_chinese_title
    elif translated_lines[title_idx].strip() != source_title:
        chinese_title = translated_h1
    else:
        chinese_title = ""
    translated_lines[title_idx] = source_title

    insert_idx = title_idx + 1
    if insert_idx < len(translated_lines) and translated_lines[insert_idx].strip() == "":
        insert_idx += 1

    if not chinese_title and insert_idx < len(translated_lines):
        next_line = translated_lines[insert_idx].strip()
        match = re.match(r"^#{1,6}\s+(.+)$", next_line)
        if match and not re.search(r"\b(abstract|introduction)\b|摘要|引言|介绍", match.group(1), re.IGNORECASE):
            chinese_title = match.group(1).strip()
            del translated_lines[insert_idx]
            if insert_idx < len(translated_lines) and translated_lines[insert_idx].strip() == "":
                del translated_lines[insert_idx]

    if insert_idx < len(translated_lines) and translated_lines[insert_idx].startswith("> 中文题名："):
        if chinese_title:
            translated_lines[insert_idx] = f"> 中文题名：{chinese_title}"
    else:
        if chinese_title:
            translated_lines[insert_idx:insert_idx] = [f"> 中文题名：{chinese_title}", ""]

    return "\n".join(translated_lines).strip() + "\n"

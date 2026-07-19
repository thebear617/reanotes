"""Normalize extracted paper tables and images into publishable Markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


HTML_TABLE_RE = re.compile(r"<table\b[\s\S]*?</table>", re.IGNORECASE)
MARKDOWN_IMAGE_RE = re.compile(
    r"^\s*!\[(?P<alt>[^\]\n]*)\]\((?P<target>[^)\n]+)\)\s*(?P<caption>.*)$"
)
CAPTION_RE = re.compile(
    r"^(?:图\s*\d+[A-Za-z]?|Figure\s+\d+[A-Za-z]?|Fig\.\s*\d+[A-Za-z]?)"
    r"\s*[:：.\-]?\s*.+$",
    re.IGNORECASE,
)
CAPTION_PREFIX_RE = re.compile(
    r"^(?:图\s*\d+[A-Za-z]?|Figure\s+\d+[A-Za-z]?|Fig\.\s*\d+[A-Za-z]?)"
    r"\s*[:：.\-]?\s*",
    re.IGNORECASE,
)


class TableConversionError(ValueError):
    """Raised when an HTML table cannot be flattened without ambiguity."""


@dataclass
class _Cell:
    text: str
    rowspan: int = 1
    colspan: int = 1
    is_header: bool = False


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[_Cell]] = []
        self.current_row: list[_Cell] | None = None
        self.current_parts: list[str] | None = None
        self.current_attrs: dict[str, str] = {}
        self.current_is_header = False
        self.current_link_href: str | None = None
        self.table_depth = 0
        self.nested_table = False
        self.unsupported_tags: set[str] = set()

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        if tag == "table":
            self.table_depth += 1
            if self.table_depth > 1:
                self.nested_table = True
            return
        if self.table_depth != 1:
            return
        if tag == "tr":
            self.current_row = []
        elif tag in {"td", "th"}:
            if self.current_row is None:
                self.current_row = []
            self.current_parts = []
            self.current_attrs = {
                key.lower(): value or "" for key, value in attrs
            }
            self.current_is_header = tag == "th"
        elif tag == "br" and self.current_parts is not None:
            self.current_parts.append("\n")
        elif self.current_parts is not None and tag in {"sup", "sub"}:
            self.current_parts.append(f"<{tag}>")
        elif self.current_parts is not None and tag in {"strong", "b"}:
            self.current_parts.append("**")
        elif self.current_parts is not None and tag in {"em", "i"}:
            self.current_parts.append("*")
        elif self.current_parts is not None and tag == "code":
            self.current_parts.append("`")
        elif self.current_parts is not None and tag == "a":
            attr_map = {key.lower(): value or "" for key, value in attrs}
            self.current_link_href = attr_map.get("href")
            self.current_parts.append("[")
        elif self.current_parts is not None and tag in {"img", "svg"}:
            self.unsupported_tags.add(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "table":
            self.table_depth -= 1
            return
        if self.table_depth != 1:
            return
        if tag in {"td", "th"} and self.current_parts is not None:
            text = _normalize_cell_text("".join(self.current_parts))
            rowspan = _positive_span(self.current_attrs.get("rowspan", "1"))
            colspan = _positive_span(self.current_attrs.get("colspan", "1"))
            if self.current_row is None:
                raise TableConversionError("cell closed outside a table row")
            self.current_row.append(
                _Cell(
                    text=text,
                    rowspan=rowspan,
                    colspan=colspan,
                    is_header=self.current_is_header,
                )
            )
            self.current_parts = None
            self.current_attrs = {}
            self.current_is_header = False
            self.current_link_href = None
        elif self.current_parts is not None and tag in {"sup", "sub"}:
            self.current_parts.append(f"</{tag}>")
        elif self.current_parts is not None and tag in {"strong", "b"}:
            self.current_parts.append("**")
        elif self.current_parts is not None and tag in {"em", "i"}:
            self.current_parts.append("*")
        elif self.current_parts is not None and tag == "code":
            self.current_parts.append("`")
        elif self.current_parts is not None and tag == "a":
            self.current_parts.append(f"]({self.current_link_href or ''})")
            self.current_link_href = None
        elif tag == "tr" and self.current_row is not None:
            if self.current_row:
                self.rows.append(self.current_row)
            self.current_row = None

    def handle_data(self, data: str) -> None:
        if self.table_depth == 1 and self.current_parts is not None:
            self.current_parts.append(data)


def _positive_span(raw: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise TableConversionError(f"invalid table span: {raw!r}") from exc
    if value < 1 or value > 100:
        raise TableConversionError(f"invalid table span: {value}")
    return value


def _normalize_cell_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.splitlines()]
    text = "<br>".join(line for line in lines if line)
    return text.replace("|", r"\|")


def _ensure_grid_row(grid: list[list[str | None]], row_idx: int) -> None:
    while len(grid) <= row_idx:
        grid.append([])


def _ensure_grid_col(row: list[str | None], col_idx: int) -> None:
    while len(row) <= col_idx:
        row.append(None)


def _expand_table(rows: list[list[_Cell]]) -> list[list[str]]:
    grid: list[list[str | None]] = []
    for row_idx, cells in enumerate(rows):
        _ensure_grid_row(grid, row_idx)
        col_idx = 0
        for cell in cells:
            while True:
                _ensure_grid_col(grid[row_idx], col_idx)
                if grid[row_idx][col_idx] is None:
                    break
                col_idx += 1
            for row_offset in range(cell.rowspan):
                target_row_idx = row_idx + row_offset
                _ensure_grid_row(grid, target_row_idx)
                for col_offset in range(cell.colspan):
                    target_col_idx = col_idx + col_offset
                    _ensure_grid_col(grid[target_row_idx], target_col_idx)
                    if grid[target_row_idx][target_col_idx] is not None:
                        raise TableConversionError("overlapping rowspan/colspan cells")
                    grid[target_row_idx][target_col_idx] = cell.text
            col_idx += cell.colspan

    width = max((len(row) for row in grid), default=0)
    if width == 0:
        raise TableConversionError("table has no cells")
    normalized: list[list[str]] = []
    for row in grid:
        normalized.append([(value or "") for value in row] + [""] * (width - len(row)))
    return normalized


def _header_depth(rows: list[list[_Cell]], grid: list[list[str]]) -> int:
    first_row = rows[0]
    depth = max((cell.rowspan for cell in first_row), default=1)
    if any(cell.colspan > 1 for cell in first_row) and len(grid) > 1:
        depth = max(depth, 2)
    return min(max(depth, 1), len(grid))


def _combine_headers(grid: list[list[str]], depth: int) -> list[str]:
    headers: list[str] = []
    for col_idx in range(len(grid[0])):
        parts: list[str] = []
        for row_idx in range(depth):
            value = grid[row_idx][col_idx].strip()
            if value and value not in parts:
                parts.append(value)
        headers.append(" / ".join(parts) or "—")
    return headers


def html_table_to_markdown(table_html: str) -> str:
    parser = _TableParser()
    parser.feed(table_html)
    parser.close()
    if parser.nested_table:
        raise TableConversionError("nested tables are not supported")
    if parser.unsupported_tags:
        raise TableConversionError(
            "unsupported table tags: " + ", ".join(sorted(parser.unsupported_tags))
        )
    if not parser.rows:
        raise TableConversionError("table has no rows")

    grid = _expand_table(parser.rows)
    depth = _header_depth(parser.rows, grid)
    headers = _combine_headers(grid, depth)
    data_rows = grid[depth:]
    delimiter = ["---"] * len(headers)
    markdown_rows = [headers, delimiter, *data_rows]
    return "\n".join("| " + " | ".join(row) + " |" for row in markdown_rows)


def normalize_html_tables(text: str) -> tuple[str, dict[str, Any]]:
    """Convert all representable HTML tables to Markdown before translation."""
    stats: dict[str, Any] = {
        "source_html": 0,
        "converted": 0,
        "fallback_html": 0,
        "issues": [],
    }

    def replace(match: re.Match[str]) -> str:
        table_index = stats["source_html"]
        stats["source_html"] += 1
        try:
            markdown = html_table_to_markdown(match.group(0))
        except (TableConversionError, AssertionError) as exc:
            stats["fallback_html"] += 1
            stats["issues"].append(
                {"table": table_index, "message": str(exc)}
            )
            return match.group(0)
        stats["converted"] += 1
        return f"\n\n{markdown}\n\n"

    return HTML_TABLE_RE.sub(replace, text), stats


def _split_markdown_row(line: str) -> list[str]:
    stripped = line.strip().strip("|")
    return [part.strip() for part in re.split(r"(?<!\\)\|", stripped)]


def validate_markdown_tables(text: str) -> dict[str, Any]:
    """Check that Markdown table rows remain rectangular after translation."""
    lines = text.splitlines()
    table_count = 0
    issues: list[dict[str, Any]] = []
    idx = 0
    while idx + 1 < len(lines):
        if not lines[idx].lstrip().startswith("|"):
            idx += 1
            continue
        header = _split_markdown_row(lines[idx])
        delimiter = _split_markdown_row(lines[idx + 1])
        if not delimiter or not all(
            re.fullmatch(r":?-{3,}:?", cell) for cell in delimiter
        ):
            idx += 1
            continue
        table_count += 1
        expected = len(header)
        if len(delimiter) != expected:
            issues.append(
                {
                    "table": table_count - 1,
                    "row": 1,
                    "expected_columns": expected,
                    "actual_columns": len(delimiter),
                }
            )
        row_offset = 2
        idx += 2
        while idx < len(lines) and lines[idx].lstrip().startswith("|"):
            actual = len(_split_markdown_row(lines[idx]))
            if actual != expected:
                issues.append(
                    {
                        "table": table_count - 1,
                        "row": row_offset,
                        "expected_columns": expected,
                        "actual_columns": actual,
                    }
                )
            idx += 1
            row_offset += 1
    return {"count": table_count, "issues": issues}


def _caption_to_alt(caption: str) -> str:
    alt = CAPTION_PREFIX_RE.sub("", caption).strip()
    alt = re.sub(r"\$[^$\n]*\$", " ", alt)
    alt = re.sub(r"<[^>]+>", "", alt)
    alt = re.sub(r"[*_`]+", "", alt)
    alt = alt.replace("\\[", "").replace("\\]", "")
    alt = alt.replace("[", "").replace("]", "")
    alt = re.sub(r"\s+", " ", alt).strip(" .。:：")
    return alt[:120]


def _image_path(target: str) -> str:
    target = target.strip()
    if target.startswith("<") and ">" in target:
        return target[1:target.index(">")]
    return target.split(maxsplit=1)[0]


def _normalize_image_target(target: str) -> str:
    """Make local image references explicit for VuePress/Vite resolution."""
    target = target.strip()
    path_text = _image_path(target)
    if re.match(r"^(?:https?:|data:|/|\./|\.\./)", path_text):
        return target
    return f"./{target}"


def _following_group_caption(lines: list[str], start_idx: int) -> str:
    """Find a shared caption after a short run of multi-panel images."""
    for line in lines[start_idx + 1 : start_idx + 31]:
        stripped = line.strip()
        if not stripped:
            continue
        image_match = MARKDOWN_IMAGE_RE.match(line)
        if image_match:
            inline_caption = image_match.group("caption").strip()
            if inline_caption and CAPTION_RE.match(inline_caption):
                return inline_caption
            continue
        if re.fullmatch(r"\(?[A-Za-z0-9]+\)?[.:]?", stripped):
            continue
        if CAPTION_RE.match(stripped):
            return stripped
        break
    return ""


def normalize_images_and_captions(
    text: str,
    *,
    image_base_dir: Path,
) -> tuple[str, dict[str, Any]]:
    """Add image alt text, separate inline captions, and check local files."""
    lines = text.splitlines()
    output: list[str] = []
    stats: dict[str, Any] = {
        "referenced": 0,
        "generated_alt": 0,
        "fallback_alt": 0,
        "captions_normalized": 0,
        "missing": [],
    }
    idx = 0
    while idx < len(lines):
        match = MARKDOWN_IMAGE_RE.match(lines[idx])
        if not match:
            output.append(lines[idx].rstrip())
            idx += 1
            continue

        stats["referenced"] += 1
        alt = match.group("alt").strip()
        target = _normalize_image_target(match.group("target"))
        caption = match.group("caption").strip()
        consumed = 1
        if not caption:
            next_idx = idx + 1
            if next_idx < len(lines) and not lines[next_idx].strip():
                next_idx += 1
            if next_idx < len(lines) and CAPTION_RE.match(lines[next_idx].strip()):
                caption = lines[next_idx].strip()
                consumed = next_idx - idx + 1

        if not alt:
            alt_caption = caption or _following_group_caption(lines, idx)
            alt = _caption_to_alt(alt_caption) if alt_caption else ""
            if alt:
                stats["generated_alt"] += 1
            else:
                alt = "论文插图"
                stats["fallback_alt"] += 1

        output.append(f"![{alt}]({target})")
        if caption:
            output.extend(["", caption])
            stats["captions_normalized"] += 1

        path_text = _image_path(target)
        if not re.match(r"^(?:https?:|data:|/)", path_text):
            image_path = image_base_dir / path_text
            if not image_path.is_file():
                stats["missing"].append(path_text)

        idx += consumed

    return "\n".join(output).strip() + "\n", stats

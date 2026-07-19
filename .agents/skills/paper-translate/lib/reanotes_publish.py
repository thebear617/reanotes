"""Publish a quality-gated translation into the ReaNotes literature library."""

from __future__ import annotations

import datetime as dt
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


H1_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
ZH_TITLE_RE = re.compile(r"^>\s*中文题名[：:]\s*(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ARXIV_ID_RE = re.compile(r"\b(\d{2})(\d{2})\.\d{4,5}(?:v\d+)?\b")
BAD_HTML_MARKERS = (
    "katex-error",
    "Invalid variant:",
    "MathJax retry -- an asynchronous action is required",
    "[[[MATH_",
    "[[[IMAGE_",
    "[[[HTML_TABLE_",
)


class ReaNotesPublishError(RuntimeError):
    """Raised when a translation cannot safely enter the ReaNotes library."""


def discover_reanotes_root(skill_root: Path, cwd: Path | None = None) -> Path:
    """Find a ReaNotes checkout after either repo-local or legacy installation."""
    current_dir = (cwd or Path.cwd()).resolve()
    candidates = [
        *skill_root.resolve().parents,
        current_dir,
        current_dir / "reanotes",
    ]
    for candidate in candidates:
        if (
            (candidate / "package.json").is_file()
            and (candidate / "docs/literature/papers.md").is_file()
        ):
            return candidate
    return current_dir / "reanotes"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9._-]+", "-", value.lower()).strip("-.")
    if not slug:
        raise ReaNotesPublishError(f"publication slug is empty after sanitizing: {value!r}")
    return slug


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReaNotesPublishError(f"cannot read JSON file {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReaNotesPublishError(f"expected a JSON object in {path}")
    return value


def _paper_titles(markdown: str) -> tuple[str, str | None]:
    title_match = H1_RE.search(markdown)
    if not title_match:
        raise ReaNotesPublishError("full_zh.md has no H1 paper title")
    zh_match = ZH_TITLE_RE.search(markdown)
    return title_match.group(1).strip(), (zh_match.group(1).strip() if zh_match else None)


def _publication_month(source_input: str) -> str:
    match = ARXIV_ID_RE.search(source_input)
    if not match:
        return "待补充"
    year = 2000 + int(match.group(1))
    return f"{year:04d}-{match.group(2)}"


def _escape_cell(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).replace("|", r"\|")


def _default_index_fields(source_input: str) -> dict[str, str]:
    return {
        "date": _publication_month(source_input),
        "venue": "arXiv 预印本" if "arxiv.org" in source_input.lower() else "待补充",
        "area": "待分类",
        "tags": "已翻译",
        "reading_status": "未读",
        "focus": "中文译文已收录；建议结合原文阅读。",
    }


def update_literature_index(
    index_path: Path,
    *,
    title: str,
    source_input: str,
    relative_link: str,
    fields: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Point an existing paper row to the translation, or append a new row."""
    original = index_path.read_text(encoding="utf-8")
    lines = original.splitlines()
    matched_line: int | None = None
    source_canonical = re.sub(r"v\d+(?=$|[?#])", "", source_input)

    for idx, line in enumerate(lines):
        if not line.lstrip().startswith("|"):
            continue
        link_match = LINK_RE.search(line)
        if not link_match:
            continue
        row_title, row_link = link_match.groups()
        row_canonical = re.sub(r"v\d+(?=$|[?#])", "", row_link)
        if row_title.casefold() == title.casefold() or (
            source_input and row_canonical == source_canonical
        ):
            lines[idx] = line[: link_match.start(2)] + relative_link + line[link_match.end(2) :]
            matched_line = idx
            break

    action = "updated"
    if matched_line is None:
        values = _default_index_fields(source_input)
        values.update(fields or {})
        new_row = (
            f"| [{_escape_cell(title)}]({relative_link}) | "
            f"{_escape_cell(values['date'])} | {_escape_cell(values['venue'])} | "
            f"{_escape_cell(values['area'])} | {_escape_cell(values['tags'])} | "
            f"{_escape_cell(values['reading_status'])} | {_escape_cell(values['focus'])} |"
        )
        last_table_line = max(
            (idx for idx, line in enumerate(lines) if line.lstrip().startswith("|")),
            default=-1,
        )
        if last_table_line < 1:
            raise ReaNotesPublishError(f"literature index table not found: {index_path}")
        lines.insert(last_table_line + 1, new_row)
        matched_line = last_table_line + 1
        action = "added"

    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"action": action, "line": matched_line + 1, "link": relative_link}


def _validate_source_images(markdown: str, paper_dir: Path) -> list[str]:
    issues: list[str] = []
    for target in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", markdown):
        raw_target = target.strip()
        if raw_target.startswith("<") and ">" in raw_target:
            path_text = raw_target[1 : raw_target.index(">")]
        else:
            path_text = raw_target.split(maxsplit=1)[0]
        if re.match(r"^[a-z][a-z0-9+.-]*://", path_text, re.IGNORECASE):
            continue
        candidate = (paper_dir / path_text).resolve()
        images_root = (paper_dir / "images").resolve()
        try:
            candidate.relative_to(images_root)
        except ValueError:
            issues.append(f"outside images/: {path_text}")
            continue
        if not candidate.is_file():
            issues.append(path_text)
    return sorted(set(issues))


def publish_paper(
    paper_dir: Path,
    reanotes_root: Path,
    *,
    slug: str | None = None,
    source_input: str = "",
    allow_needs_review: bool = False,
    force: bool = False,
    index_fields: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Copy only the Chinese article and its assets into ReaNotes."""
    paper_dir = paper_dir.resolve()
    reanotes_root = reanotes_root.resolve()
    translated_path = paper_dir / "full_zh.md"
    report_path = paper_dir / "translation_report.json"
    if not translated_path.is_file() or not report_path.is_file():
        raise ReaNotesPublishError(
            f"publication requires full_zh.md and translation_report.json in {paper_dir}"
        )

    report = _read_json(report_path)
    quality_status = report.get("status")
    allowed = {"publishable"}
    if allow_needs_review:
        allowed.add("needs_review")
    if quality_status not in allowed or not report.get("output_written"):
        raise ReaNotesPublishError(
            f"quality gate rejected publication: status={quality_status!r}"
        )

    markdown = translated_path.read_text(encoding="utf-8")
    title, zh_title = _paper_titles(markdown)
    missing_images = _validate_source_images(markdown, paper_dir)
    if missing_images:
        raise ReaNotesPublishError(
            "publication source has missing images: " + ", ".join(missing_images)
        )

    safe_slug = slugify(slug or paper_dir.name)
    translations_root = reanotes_root / "docs/literature/translations"
    index_path = reanotes_root / "docs/literature/papers.md"
    package_path = reanotes_root / "package.json"
    if not index_path.is_file() or not package_path.is_file():
        raise ReaNotesPublishError(f"not a ReaNotes repository: {reanotes_root}")

    translations_root.mkdir(parents=True, exist_ok=True)
    target_dir = translations_root / safe_slug
    if target_dir.exists() and not force:
        raise ReaNotesPublishError(
            f"publication target already exists: {target_dir}; use --publish-force to replace it"
        )

    original_index = index_path.read_text(encoding="utf-8")
    backup_dir: Path | None = None
    if target_dir.exists():
        backup_dir = Path(tempfile.mkdtemp(prefix=f".{safe_slug}-backup-", dir=translations_root))
        backup_dir.rmdir()
        target_dir.rename(backup_dir)

    staging_dir = Path(tempfile.mkdtemp(prefix=f".{safe_slug}-staging-", dir=translations_root))
    try:
        shutil.copy2(translated_path, staging_dir / "README.md")
        source_images = paper_dir / "images"
        if source_images.is_dir():
            shutil.copytree(source_images, staging_dir / "images")
        shutil.copy2(report_path, staging_dir / "translation-report.json")
        metadata = {
            "schema_version": 1,
            "title": title,
            "zh_title": zh_title,
            "source_input": source_input,
            "quality_status": quality_status,
            "published_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "translation_model": "deepseek-chat",
            "translation_report": "translation-report.json",
        }
        (staging_dir / "translation-metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        staging_dir.rename(target_dir)
        index_result = update_literature_index(
            index_path,
            title=title,
            source_input=source_input,
            relative_link=f"translations/{safe_slug}/",
            fields=index_fields,
        )
    except Exception:
        index_path.write_text(original_index, encoding="utf-8")
        if target_dir.exists():
            shutil.rmtree(target_dir)
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        if backup_dir is not None and backup_dir.exists():
            backup_dir.rename(target_dir)
        raise
    else:
        if backup_dir is not None and backup_dir.exists():
            shutil.rmtree(backup_dir)

    return {
        "status": "published",
        "slug": safe_slug,
        "title": title,
        "quality_status": quality_status,
        "target": str(target_dir),
        "index": index_result,
    }


def validate_reanotes_publications(
    reanotes_root: Path,
    publications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Format the index, build the site, and inspect each generated page."""
    if not publications:
        return {"status": "not_run", "commands": [], "pages": []}

    commands = [
        ["pnpm", "exec", "prettier", "--write", "docs/literature/papers.md"],
        ["pnpm", "lint"],
        ["pnpm", "docs:build"],
    ]
    command_reports: list[dict[str, Any]] = []
    for command in commands:
        try:
            proc = subprocess.run(
                command,
                cwd=reanotes_root,
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            command_reports.append(
                {
                    "command": " ".join(command),
                    "returncode": None,
                    "stdout_tail": "",
                    "stderr_tail": f"{type(exc).__name__}: {exc}",
                }
            )
            return {
                "status": "failed",
                "commands": command_reports,
                "pages": [],
            }
        command_reports.append(
            {
                "command": " ".join(command),
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            }
        )
        if proc.returncode != 0:
            return {
                "status": "failed",
                "commands": command_reports,
                "pages": [],
            }

    page_reports: list[dict[str, Any]] = []
    for publication in publications:
        slug = publication["slug"]
        page_path = reanotes_root / "dist/literature/translations" / slug / "index.html"
        issues: list[str] = []
        if not page_path.is_file():
            issues.append("built_page_missing")
        else:
            html = page_path.read_text(encoding="utf-8", errors="replace")
            for marker in BAD_HTML_MARKERS:
                if marker in html:
                    issues.append(f"built_html_contains:{marker}")
        page_reports.append(
            {"slug": slug, "path": str(page_path), "issues": issues}
        )

    return {
        "status": "passed" if all(not page["issues"] for page in page_reports) else "failed",
        "commands": command_reports,
        "pages": page_reports,
    }

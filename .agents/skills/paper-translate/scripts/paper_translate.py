#!/usr/bin/env python3
"""End-to-end paper translation: URL / local PDF → MinerU → DeepSeek → full_zh.md.

Per-paper output lives at:

    {out_root}/{date}/{name}/
        full.md         (MinerU English Markdown)
        images/         (extracted figures)
        full_zh.md      (DeepSeek Chinese translation, final)

Where:
- `{out_root}` defaults to `reanotes/output/translations/` (under the htmls project root)
- `{date}` is the run date in `YYYY-MM-DD` form
- `{name}` is:
    * `{arXiv-ID}-{YYYYMMDD}` for arXiv papers (year-month from ID; day from arXiv API)
    * `{user-chosen-short-name}-{YYYYMMDD}` for local PDFs (prompts interactively)
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

# Bootstrap lib/ onto sys.path so `import deepseek_translate` / `import clean_markdown` work.
_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _SCRIPT_DIR.parent
_LIB_DIR = _SKILL_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from env_loader import load_skill_env  # noqa: E402
import deepseek_translate  # noqa: E402
from reanotes_publish import (  # noqa: E402
    ReaNotesPublishError,
    discover_reanotes_root,
    publish_paper,
    validate_reanotes_publications,
)


load_skill_env(_SKILL_ROOT)


DEFAULT_REANOTES_ROOT = discover_reanotes_root(_SKILL_ROOT)
DEFAULT_OUT_ROOT = DEFAULT_REANOTES_ROOT / "output" / "translations"
DEFAULT_MINERU_SCRIPT = Path.home() / "Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py"
DEFAULT_GLOSSARY = _SKILL_ROOT / "glossary" / "general-ovs-cv-nlp.md"
DEFAULT_MINERU_MODEL = "pipeline"
DEFAULT_MINERU_TIMEOUT = 600

ARXIV_ID_RE = re.compile(r"\b(\d{4}\.\d{4,5}(?:v\d+)?|[a-z\-]+(?:\.[A-Z]{2})?/\d{7}(?:v\d+)?)\b", re.IGNORECASE)
ARXIV_NEW_ID_RE = re.compile(r"^(\d{2})(\d{2})\.(\d{4,5})(?:v(\d+))?$")
ARXIV_OLD_ID_RE = re.compile(r"^([a-z\-]+(?:\.[A-Z]{2})?)/(\d{2})(\d{2})(\d{3})(?:v(\d+))?$", re.IGNORECASE)
ARXIV_API_URL = "http://export.arxiv.org/api/query"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("sources", nargs="*", type=str, help="URL(s) or local PDF path(s).")
    p.add_argument("--sources-file", type=Path, help="UTF-8 file with one source per line.")
    p.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT, help="Per-paper output root.")
    p.add_argument("--date", type=str, default=None, help="Override run date (YYYY-MM-DD).")
    p.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY, help="Glossary markdown path.")
    p.add_argument("--mineru-script", type=Path, default=DEFAULT_MINERU_SCRIPT)
    p.add_argument("--mineru-model", type=str, default=DEFAULT_MINERU_MODEL)
    p.add_argument("--mineru-timeout", type=int, default=DEFAULT_MINERU_TIMEOUT)
    p.add_argument("--force", action="store_true", help="Re-translate even if full_zh.md exists.")
    p.add_argument(
        "--force-extract",
        action="store_true",
        help="Run MinerU again even when the planned target already has full.md.",
    )
    p.add_argument("--name", action="append", default=None,
                   help="Per-source folder name (repeatable, in source order). "
                        "Skips the pre-run prompt for that source.")
    p.add_argument("--non-interactive", action="store_true",
                   help="Skip ALL pre-run name prompts. arXiv papers fall back to auto-name; "
                        "other sources use their default.")
    p.add_argument("--dry-run", action="store_true", help="Print the plan, do not run MinerU or DeepSeek.")
    p.add_argument(
        "--publish",
        action="store_true",
        help="Publish quality-gated translations into the ReaNotes literature library.",
    )
    p.add_argument(
        "--reanotes-root",
        type=Path,
        default=DEFAULT_REANOTES_ROOT,
        help="ReaNotes repository root used by --publish.",
    )
    p.add_argument(
        "--publish-needs-review",
        action="store_true",
        help="Explicitly allow needs_review outputs to publish (publishable only by default).",
    )
    p.add_argument(
        "--publish-force",
        action="store_true",
        help="Replace an existing ReaNotes translation directory.",
    )
    return p.parse_args()


def collect_sources(args: argparse.Namespace) -> list[str]:
    out = list(args.sources)
    if args.sources_file:
        for line in args.sources_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            out.append(stripped)
    if not out:
        print("No sources provided. Use positional args or --sources-file.", file=sys.stderr)
        sys.exit(2)
    return out


def is_url(s: str) -> bool:
    return s.startswith("http://") or s.startswith("https://")


def is_local_pdf(s: str) -> bool:
    p = Path(s)
    return p.is_file() and p.suffix.lower() == ".pdf"


def extract_arxiv_id(text: str) -> str | None:
    m = ARXIV_ID_RE.search(text)
    if not m:
        return None
    raw = m.group(1)
    if ARXIV_NEW_ID_RE.match(raw) or ARXIV_OLD_ID_RE.match(raw):
        return raw
    return None


def arxiv_id_date(arxiv_id: str) -> str:
    """Return the arXiv submission date for the given ID in YYYYMMDD form.

    Strategy:
    1. Hit the arXiv API to get the exact `<published>` date.
    2. Fall back to year-month encoded in the ID (day = 01).
    """
    base = arxiv_id
    m_new = ARXIV_NEW_ID_RE.match(arxiv_id)
    m_old = ARXIV_OLD_ID_RE.match(arxiv_id)
    if m_new:
        yy, mm, _seq, _ver = m_new.groups()
        fallback = f"{int(yy) + 2000:04d}{int(mm):02d}01"
    elif m_old:
        _subj, yy, mm, _seq, _ver = m_old.groups()
        fallback = f"{int(yy) + 2000:04d}{int(mm):02d}01"
    else:
        return "00000000"

    try:
        url = f"{ARXIV_API_URL}?id_list={base}"
        with urllib.request.urlopen(url, timeout=15) as resp:
            xml = resp.read().decode("utf-8")
        m_pub = re.search(r"<published>(\d{4})-(\d{2})-(\d{2})", xml)
        if m_pub:
            return f"{m_pub.group(1)}{m_pub.group(2)}{m_pub.group(3)}"
    except (urllib.error.URLError, TimeoutError, OSError, ConnectionError):
        pass

    return fallback


def arxiv_canonical_id(arxiv_id: str) -> str:
    """Strip the version suffix from an arXiv ID."""
    return re.sub(r"v\d+$", "", arxiv_id, flags=re.IGNORECASE)


def _sanitize_folder_name(name: str) -> str:
    """Lowercase letters, digits, '.', '_', '-'; collapse runs of others to '-'."""
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-")


def _subkind_for(source: str) -> str:
    if is_url(source):
        if "arxiv.org" in source.lower():
            return "arxiv"
        return "url"
    if is_local_pdf(source):
        return "local_pdf"
    raise ValueError(f"Unrecognized source (not a URL and not an existing .pdf): {source}")


def name_for_source(
    source: str,
    allow_prompt: bool,
    pre_supplied_name: str | None = None,
) -> tuple[str, str]:
    """Return (folder_name, subkind) for a given source.

    `subkind` is one of: "arxiv", "url", "local_pdf".

    Args:
        source: the URL or local PDF path.
        allow_prompt: if True, prompt the user for a name (when no
            pre_supplied_name is given). If False, use auto-defaults
            silently — including falling back to the arXiv auto-name
            when the user would have been required to type.
        pre_supplied_name: if provided (from --name), use this as the
            folder name (after sanitization) and skip the prompt.

    Prompt rules:
        - arXiv: NO default. Empty input is a hard error (script exits 2).
        - generic URL: default = `url-YYYYMMDD`. Enter accepts the default.
        - local PDF: default = file stem. Enter accepts the default.
    """
    subkind = _subkind_for(source)

    if pre_supplied_name is not None:
        safe = _sanitize_folder_name(pre_supplied_name)
        if not safe:
            raise ValueError(f"--name '{pre_supplied_name}' sanitizes to empty string")
        return safe, subkind

    if subkind == "arxiv":
        arxiv_id = extract_arxiv_id(source)
        if not arxiv_id:
            raise ValueError(f"Looks like an arXiv URL but no arXiv ID found: {source}")
        date = arxiv_id_date(arxiv_id)
        canon = arxiv_canonical_id(arxiv_id)
        auto_name = f"{canon}-{date}"
        if not allow_prompt:
            return auto_name, "arxiv"
        try:
            user = input(f"Folder name for {arxiv_id} (no default, must type): ").strip()
        except EOFError:
            user = ""
        if not user:
            print(f"  ✗ arXiv paper {arxiv_id} requires a folder name; aborting.", file=sys.stderr)
            sys.exit(2)
        return _sanitize_folder_name(user), "arxiv"

    if subkind == "url":
        auto_name = f"url-{dt.date.today():%Y%m%d}"
        if not allow_prompt:
            return auto_name, "url"
        try:
            user = input(f"Folder name for {source} (default: {auto_name}): ").strip()
        except EOFError:
            user = ""
        if not user:
            return auto_name, "url"
        safe = _sanitize_folder_name(user)
        return safe or auto_name, "url"

    # local_pdf
    stem = Path(source).stem
    auto_name = f"{stem}-{dt.date.today():%Y%m%d}"
    if not allow_prompt:
        return auto_name, "local_pdf"
    try:
        user = input(f"Short name for {Path(source).name} (default: {stem}): ").strip()
    except EOFError:
        user = ""
    if not user:
        return auto_name, "local_pdf"
    safe = _sanitize_folder_name(user)
    if not safe:
        return auto_name, "local_pdf"
    return f"{safe}-{dt.date.today():%Y%m%d}", "local_pdf"


def run_mineru(source: str, date_dir: Path, args: argparse.Namespace) -> Path | None:
    """Invoke mineru_extract_batch.py and return the actual out_dir it created.

    Returns None if MinerU failed or returned no usable out_dir.

    arXiv abs URLs (HTML) are auto-rewritten to the corresponding PDF URL so
    that the default `pipeline` model can parse them. Other URLs are passed
    through as-is.
    """
    mineru_source = source
    m_abs = re.search(r"arxiv\.org/abs/(\d{4}\.\d{4,5}(?:v\d+)?)", source)
    if m_abs:
        mineru_source = f"https://arxiv.org/pdf/{m_abs.group(1)}"
        if mineru_source != source:
            print(f"  (rewrote abs → pdf for MinerU: {mineru_source})")

    cmd = [
        "python3",
        str(args.mineru_script),
        "--model", args.mineru_model,
        "--timeout", str(args.mineru_timeout),
        "--out", str(date_dir),
        mineru_source,
    ]
    print(f"\n→ MinerU: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=Path.cwd(), capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"  ✗ MinerU failed (rc={proc.returncode})", file=sys.stderr)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return None

    # MinerU prints a JSON summary on its last stdout line. Parse it to find
    # the exact out_dir it just created — never guess from sibling scan.
    out_dir: Path | None = None
    for line in reversed(proc.stdout.splitlines()):
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        items = payload.get("items") or []
        for item in items:
            candidate = item.get("out_dir")
            if candidate and (Path(candidate) / "full.md").exists():
                out_dir = Path(candidate)
                break
        if out_dir:
            break
    if out_dir is None:
        print("  ✗ MinerU returned no usable out_dir", file=sys.stderr)
    return out_dir


def rename_paper_dir(actual_dir: Path, target_name: str, parent: Path) -> Path:
    target = parent / target_name
    if target == actual_dir:
        return actual_dir
    if target.exists():
        # If the target is an empty placeholder (e.g. left over from a previous
        # failed run), remove it so the rename can succeed. Otherwise, leave it
        # alone and return the actual_dir as-is.
        if target.is_dir() and not any(target.iterdir()):
            target.rmdir()
        else:
            print(f"  target exists already, leaving as-is: {target.name}", file=sys.stderr)
            return actual_dir
    actual_dir.rename(target)
    return target


def append_ledger(ledger: Path, date: str, results: list[dict], total_cost_cny: float,
                  total_prompt: int, total_completion: int, total_cache_hit: int,
                  total_cache_miss: int, elapsed_s: float) -> None:
    ledger.parent.mkdir(parents=True, exist_ok=True)
    header_needed = not ledger.exists()
    with ledger.open("a", encoding="utf-8") as f:
        if header_needed:
            f.write("# Paper Translate 用量台账\n\n")
            f.write("> 每行一次运行汇总；明细见同目录 `summary.json`。\n\n")
        f.write(f"## {date} {dt.datetime.now():%H:%M:%S}\n\n")
        f.write(f"- 篇数：{len(results)}\n")
        f.write(f"- prompt_tokens：{total_prompt:,}\n")
        f.write(f"- prompt_cache_hit_tokens：{total_cache_hit:,}\n")
        f.write(f"- prompt_cache_miss_tokens：{total_cache_miss:,}\n")
        f.write(f"- completion_tokens：{total_completion:,}\n")
        f.write(f"- cost_cny：{total_cost_cny:.6f}\n")
        f.write(f"- elapsed_s：{elapsed_s:.1f}\n")
        f.write("- 论文清单：\n")
        for r in results:
            f.write(f"  - {Path(r.get('output', '')).parent.name} — {r.get('status', '?')}\n")
        f.write("\n")


def main() -> int:
    args = parse_args()
    sources = collect_sources(args)
    run_date = args.date or dt.date.today().isoformat()
    out_root: Path = args.out_root
    date_dir = out_root / run_date

    # Phase 1: resolve target folder names.
    #   - is_batch: more than one source → silent, no prompts
    #   - allow_prompt: single source + not --non-interactive + not --dry-run → prompt
    #   - pre_names: --name flags, mapped 1:1 onto sources by position
    is_batch = len(sources) > 1
    allow_prompt = not is_batch and not args.non_interactive and not args.dry_run
    pre_names: list[str] = list(args.name or [])

    plan: list[dict] = []
    for i, source in enumerate(sources):
        pre_name = pre_names[i] if i < len(pre_names) else None
        try:
            name, subkind = name_for_source(source, allow_prompt, pre_name)
        except (ValueError, RuntimeError) as exc:
            print(f"  ✗ {source}: {exc}", file=sys.stderr)
            continue
        plan.append({"source": source, "name": name, "subkind": subkind,
                     "target_dir": date_dir / name})

    if not plan:
        print("No valid sources after resolution.", file=sys.stderr)
        return 1

    # Phase 2: dry-run preview.
    print(f"\n=== Plan ({len(plan)} papers) ===")
    print(f"  out_root: {out_root}")
    print(f"  date_dir: {date_dir}")
    print(f"  glossary: {args.glossary}")
    if args.publish:
        print(f"  publish_to: {args.reanotes_root / 'docs/literature/translations'}")
        print(
            "  publish_gate: "
            + ("publishable + needs_review" if args.publish_needs_review else "publishable only")
        )
    for item in plan:
        print(f"  - [{item['subkind']}] {item['source']} → {item['target_dir']}")

    if args.dry_run:
        print("\nDry run — exiting before MinerU / DeepSeek.")
        return 0

    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print(
            "DEEPSEEK_API_KEY is required "
            "(put it in the paper-translate skill's .env).",
            file=sys.stderr,
        )
        return 2

    # Phase 3: MinerU per paper.
    date_dir.mkdir(parents=True, exist_ok=True)
    for item in plan:
        print(f"\n=== {item['name']} ===")
        existing_full_md = item["target_dir"] / "full.md"
        if existing_full_md.is_file() and not args.force_extract:
            print(f"  (reusing existing MinerU extraction: {existing_full_md})")
            continue
        actual = run_mineru(item["source"], date_dir, args)
        if actual is None:
            print(f"  ✗ MinerU failed for {item['source']}", file=sys.stderr)
            continue
        if actual.name != item["name"]:
            renamed = rename_paper_dir(actual, item["name"], date_dir)
            item["target_dir"] = renamed
        else:
            item["target_dir"] = actual

    # Sweep empty directories left behind by failed MinerU attempts. We only
    # remove dirs that are empty AND not one of the planned targets.
    planned_names = {item["name"] for item in plan}
    for entry in sorted(date_dir.iterdir()):
        if not entry.is_dir() or entry.name in planned_names:
            continue
        try:
            is_empty = not any(entry.iterdir())
        except OSError:
            continue
        if is_empty:
            try:
                entry.rmdir()
                print(f"  (cleaned empty leftover: {entry.name})")
            except OSError:
                pass

    # Phase 4: translate full.md → full_zh.md per paper.
    system_prompt = deepseek_translate.build_system_prompt(args.glossary)
    results: list[dict] = []
    t0_total = dt.datetime.now()
    for item in plan:
        paper_dir = item["target_dir"]
        full_md = paper_dir / "full.md"
        full_zh = paper_dir / "full_zh.md"
        if not full_md.exists():
            print(f"  ✗ missing full.md at {full_md}, skipping translation")
            results.append({"source": item["source"], "output": str(full_zh), "status": "missing_full_md"})
            continue
        result = deepseek_translate.translate_file(
            api_key, system_prompt, full_md, full_zh, force=args.force
        )
        result["source_input"] = item["source"]
        result["subkind"] = item["subkind"]
        results.append(result)

    elapsed_total = (dt.datetime.now() - t0_total).total_seconds()

    # Phase 5: quality-gated ReaNotes publication. The adapter deliberately
    # copies only full_zh.md, images, and machine-readable provenance; full.md
    # never enters the public literature library.
    publications: list[dict] = []
    if args.publish:
        for item, result in zip(plan, results):
            paper_dir = Path(result.get("output", item["target_dir"] / "full_zh.md")).parent
            try:
                publication = publish_paper(
                    paper_dir,
                    args.reanotes_root,
                    slug=item["name"],
                    source_input=item["source"],
                    allow_needs_review=args.publish_needs_review,
                    force=args.publish_force,
                )
            except ReaNotesPublishError as exc:
                publication = {
                    "status": "publish_failed",
                    "slug": item["name"],
                    "error": str(exc),
                }
                print(f"  publish blocked: {item['name']}: {exc}", file=sys.stderr)
            except Exception as exc:
                publication = {
                    "status": "publish_failed",
                    "slug": item["name"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
                print(
                    f"  publish failed: {item['name']}: {type(exc).__name__}: {exc}",
                    file=sys.stderr,
                )
            result["publication"] = publication
            if publication.get("status") == "published":
                publications.append(publication)
                print(f"  published: {publication['target']}")

    publication_validation = validate_reanotes_publications(
        args.reanotes_root, publications
    ) if args.publish else {"status": "not_requested", "commands": [], "pages": []}

    summary = {
        "date": run_date,
        "out_root": str(out_root),
        "glossary": str(args.glossary),
        "model": deepseek_translate.MODEL,
        "pricing": {
            "input_cache_hit_usd_per_1m": deepseek_translate.INPUT_CACHE_HIT_USD_PER_M,
            "input_cache_miss_usd_per_1m": deepseek_translate.INPUT_CACHE_MISS_USD_PER_M,
            "output_usd_per_1m": deepseek_translate.OUTPUT_USD_PER_M,
            "usd_to_cny": deepseek_translate.USD_TO_CNY,
        },
        "totals": {
            "files": len(results),
            "translated": sum(1 for r in results if r.get("status") == "translated"),
            "publishable": sum(
                1 for r in results if r.get("quality_status") == "publishable"
            ),
            "needs_review": sum(
                1 for r in results if r.get("quality_status") == "needs_review"
            ),
            "published": sum(
                1
                for r in results
                if r.get("publication", {}).get("status") == "published"
            ),
            "publish_failed": sum(
                1
                for r in results
                if r.get("publication", {}).get("status") == "publish_failed"
            ),
            "skipped_exists": sum(1 for r in results if r.get("status") == "skipped_exists"),
            "validation_failed": sum(
                1 for r in results if r.get("status") == "validation_failed"
            ),
            "translation_failed": sum(
                1 for r in results if r.get("status") == "translation_failed"
            ),
            "elapsed_s": elapsed_total,
            "prompt_tokens": sum(r.get("prompt_tokens", 0) for r in results),
            "completion_tokens": sum(r.get("completion_tokens", 0) for r in results),
            "prompt_cache_hit_tokens": sum(r.get("prompt_cache_hit_tokens", 0) for r in results),
            "prompt_cache_miss_tokens": sum(r.get("prompt_cache_miss_tokens", 0) for r in results),
            "cost_usd": sum(r.get("cost_usd", 0) for r in results),
            "cost_cny": sum(r.get("cost_cny", 0) for r in results),
        },
        "publication_validation": publication_validation,
        "items": results,
    }
    summary_path = date_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    append_ledger(
        date_dir / "usage_ledger.md",
        run_date,
        results,
        summary["totals"]["cost_cny"],
        summary["totals"]["prompt_tokens"],
        summary["totals"]["completion_tokens"],
        summary["totals"]["prompt_cache_hit_tokens"],
        summary["totals"]["prompt_cache_miss_tokens"],
        elapsed_total,
    )
    print(f"\nSummary: {summary_path}")
    print(f"Translated: {summary['totals']['translated']}, "
          f"Publishable: {summary['totals']['publishable']}, "
          f"Needs review: {summary['totals']['needs_review']}, "
          f"Published: {summary['totals']['published']}, "
          f"Publish failed: {summary['totals']['publish_failed']}, "
          f"Skipped (exists): {summary['totals']['skipped_exists']}, "
          f"Total cost: ¥{summary['totals']['cost_cny']:.4f}, "
          f"Elapsed: {elapsed_total:.1f}s")
    if args.publish and (
        summary["totals"]["publish_failed"]
        or publication_validation.get("status") == "failed"
    ):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

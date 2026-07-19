#!/usr/bin/env python3
"""Publish existing paper-translate output folders into ReaNotes."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILL_ROOT = _SCRIPT_DIR.parent
_LIB_DIR = _SKILL_ROOT / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))

from reanotes_publish import (  # noqa: E402
    ReaNotesPublishError,
    discover_reanotes_root,
    publish_paper,
    validate_reanotes_publications,
)


DEFAULT_REANOTES_ROOT = discover_reanotes_root(_SKILL_ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "paper_dirs",
        nargs="+",
        type=Path,
        help="Folder(s) containing full_zh.md and translation_report.json.",
    )
    parser.add_argument("--reanotes-root", type=Path, default=DEFAULT_REANOTES_ROOT)
    parser.add_argument(
        "--slug",
        action="append",
        default=[],
        help="Publication slug, repeatable in paper_dirs order.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Original paper URL/path, repeatable in paper_dirs order.",
    )
    parser.add_argument("--allow-needs-review", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip ReaNotes prettier, lint, build, and generated-page checks.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    publications: list[dict] = []
    failures: list[dict] = []
    for idx, paper_dir in enumerate(args.paper_dirs):
        slug = args.slug[idx] if idx < len(args.slug) else None
        source_input = args.source[idx] if idx < len(args.source) else ""
        try:
            result = publish_paper(
                paper_dir,
                args.reanotes_root,
                slug=slug,
                source_input=source_input,
                allow_needs_review=args.allow_needs_review,
                force=args.force,
            )
        except ReaNotesPublishError as exc:
            failures.append({"paper_dir": str(paper_dir), "error": str(exc)})
            print(f"publish blocked: {paper_dir}: {exc}", file=sys.stderr)
            continue
        publications.append(result)
        print(f"published: {result['target']}")

    validation = (
        {"status": "skipped", "commands": [], "pages": []}
        if args.no_validate
        else validate_reanotes_publications(args.reanotes_root, publications)
    )
    summary = {
        "published": publications,
        "failures": failures,
        "validation": validation,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if failures or validation.get("status") == "failed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

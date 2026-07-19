from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = SKILL_ROOT / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from reanotes_publish import (  # noqa: E402
    ReaNotesPublishError,
    discover_reanotes_root,
    publish_paper,
    update_literature_index,
    validate_reanotes_publications,
)


INDEX = """---
title: 文献索引
---

| 文献 | 发表时间 | 会刊 | 领域 | 标签 | 状态 | 建议重点读 |
| --- | --- | --- | --- | --- | --- | --- |
| [Example Paper](https://arxiv.org/abs/2401.12345) | 2024-01 | arXiv 预印本 | 表征学习 | 必读 | 未读 | 看摘要。 |
"""


def make_reanotes(root: Path) -> Path:
    repo = root / "reanotes"
    (repo / "docs/literature/translations").mkdir(parents=True)
    (repo / "docs/literature/papers.md").write_text(INDEX, encoding="utf-8")
    (repo / "package.json").write_text('{"name":"reanotes"}\n', encoding="utf-8")
    return repo


def make_paper(root: Path, status: str = "publishable") -> Path:
    paper = root / "paper-output"
    (paper / "images").mkdir(parents=True)
    (paper / "images/figure.jpg").write_bytes(b"image")
    (paper / "full.md").write_text("# English extraction\n", encoding="utf-8")
    (paper / "full_zh.md").write_text(
        "# Example Paper\n\n> 中文题名：示例论文\n\n"
        "正文。\n\n![示意图](images/figure.jpg)\n",
        encoding="utf-8",
    )
    (paper / "translation_report.json").write_text(
        json.dumps(
            {
                "schema_version": 2,
                "status": status,
                "output_written": True,
                "checks": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return paper


class ReaNotesPublicationTests(unittest.TestCase):
    def test_discovers_repo_root_from_repo_local_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_reanotes(Path(tmp))
            skill_root = repo / ".agents/skills/paper-translate"
            skill_root.mkdir(parents=True)

            self.assertEqual(discover_reanotes_root(skill_root), repo.resolve())

    def test_publishable_copy_updates_existing_index_and_excludes_english(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_reanotes(root)
            paper = make_paper(root)

            result = publish_paper(
                paper,
                repo,
                slug="Example-Paper",
                source_input="https://arxiv.org/abs/2401.12345",
            )

            target = repo / "docs/literature/translations/example-paper"
            self.assertEqual(result["status"], "published")
            self.assertEqual(result["index"]["action"], "updated")
            self.assertTrue((target / "README.md").is_file())
            self.assertTrue((target / "images/figure.jpg").is_file())
            self.assertTrue((target / "translation-report.json").is_file())
            self.assertFalse((target / "full.md").exists())
            self.assertIn(
                "[Example Paper](translations/example-paper/)",
                (repo / "docs/literature/papers.md").read_text(encoding="utf-8"),
            )
            metadata = json.loads(
                (target / "translation-metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["zh_title"], "示例论文")
            self.assertEqual(metadata["quality_status"], "publishable")

    def test_needs_review_requires_explicit_override(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_reanotes(root)
            paper = make_paper(root, status="needs_review")

            with self.assertRaises(ReaNotesPublishError):
                publish_paper(paper, repo, slug="example-paper")

            result = publish_paper(
                paper,
                repo,
                slug="example-paper",
                allow_needs_review=True,
            )
            self.assertEqual(result["quality_status"], "needs_review")

    def test_missing_image_is_rejected_even_with_publishable_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_reanotes(root)
            paper = make_paper(root)
            (paper / "images/figure.jpg").unlink()

            with self.assertRaisesRegex(ReaNotesPublishError, "missing images"):
                publish_paper(paper, repo, slug="example-paper")

    def test_new_paper_gets_a_complete_default_index_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index = root / "papers.md"
            index.write_text(INDEX, encoding="utf-8")

            result = update_literature_index(
                index,
                title="New Paper",
                source_input="https://arxiv.org/abs/2506.00001",
                relative_link="translations/new-paper/",
            )

            text = index.read_text(encoding="utf-8")
            self.assertEqual(result["action"], "added")
            self.assertIn(
                "| [New Paper](translations/new-paper/) | 2025-06 | arXiv 预印本 | "
                "待分类 | 已翻译 | 未读 | 中文译文已收录；建议结合原文阅读。 |",
                text,
            )

    def test_existing_target_requires_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = make_reanotes(root)
            paper = make_paper(root)
            target = repo / "docs/literature/translations/example-paper"
            target.mkdir()
            (target / "README.md").write_text("old", encoding="utf-8")

            with self.assertRaisesRegex(ReaNotesPublishError, "already exists"):
                publish_paper(paper, repo, slug="example-paper")

            result = publish_paper(
                paper,
                repo,
                slug="example-paper",
                source_input="https://arxiv.org/abs/2401.12345",
                force=True,
            )
            self.assertEqual(result["status"], "published")
            self.assertIn(
                "# Example Paper",
                (target / "README.md").read_text(encoding="utf-8"),
            )

    def test_validation_builds_and_rejects_known_mathjax_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = make_reanotes(Path(tmp))
            page = repo / "dist/literature/translations/example-paper/index.html"
            page.parent.mkdir(parents=True)
            page.write_text("<html>Invalid variant: -bboldx</html>", encoding="utf-8")

            with patch(
                "reanotes_publish.subprocess.run",
                return_value=CompletedProcess([], 0, "ok", ""),
            ) as run:
                result = validate_reanotes_publications(
                    repo, [{"slug": "example-paper"}]
                )

            self.assertEqual(run.call_count, 3)
            self.assertEqual(result["status"], "failed")
            self.assertIn(
                "built_html_contains:Invalid variant:",
                result["pages"][0]["issues"],
            )


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = SKILL_ROOT / "lib"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from normalize_structures import (  # noqa: E402
    html_table_to_markdown,
    normalize_html_tables,
    normalize_images_and_captions,
    validate_markdown_tables,
)
import deepseek_translate  # noqa: E402
from clean_markdown import strip_front_matter  # noqa: E402
from placeholders import protect_math  # noqa: E402
from quality_checks import (  # noqa: E402
    detect_suspicious_math,
    normalize_high_confidence_math_ocr,
)


class FrontMatterNormalizationTests(unittest.TestCase):
    def test_paper_without_abstract_starts_at_first_numbered_section(self) -> None:
        source = """# A Cookbook

Authors and affiliations

## Contents

1 Introduction
2 Methods

## 1 What is SSL?

First section body.

![](images/later.jpg)
"""

        cleaned = strip_front_matter(source)

        self.assertIn("# A Cookbook", cleaned)
        self.assertIn("## 1 What is SSL?", cleaned)
        self.assertIn("First section body.", cleaned)
        self.assertNotIn("Authors and affiliations", cleaned)
        self.assertNotIn("## Contents", cleaned)


class HtmlTableNormalizationTests(unittest.TestCase):
    def test_expands_rowspan_and_colspan_into_rectangular_markdown(self) -> None:
        source = (
            '<table><tr><td rowspan="2">Model</td><td colspan="2">BLEU</td></tr>'
            "<tr><td>EN-DE</td><td>EN-FR</td></tr>"
            "<tr><td>Transformer</td><td>$27.3$</td><td>$38.1$</td></tr></table>"
        )

        markdown = html_table_to_markdown(source)

        self.assertIn("| Model | BLEU / EN-DE | BLEU / EN-FR |", markdown)
        self.assertIn("| Transformer | $27.3$ | $38.1$ |", markdown)
        self.assertEqual(validate_markdown_tables(markdown)["issues"], [])

    def test_nested_table_falls_back_and_records_issue(self) -> None:
        source = "<table><tr><td><table><tr><td>x</td></tr></table></td></tr></table>"

        normalized, stats = normalize_html_tables(source)

        self.assertEqual(normalized, source)
        self.assertEqual(stats["fallback_html"], 1)
        self.assertEqual(len(stats["issues"]), 1)

    def test_detects_markdown_table_column_drift(self) -> None:
        markdown = "| A | B |\n| --- | --- |\n| one | two | extra |"
        result = validate_markdown_tables(markdown)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["issues"][0]["actual_columns"], 3)


class ImageNormalizationTests(unittest.TestCase):
    def test_generates_alt_and_separates_inline_caption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "images").mkdir()
            (root / "images" / "figure.jpg").write_bytes(b"image")
            source = (
                "![](images/figure.jpg) "
                "图 2：缩放点积注意力与多头注意力。"
            )

            normalized, stats = normalize_images_and_captions(
                source, image_base_dir=root
            )

            self.assertIn(
                "![缩放点积注意力与多头注意力](./images/figure.jpg)",
                normalized,
            )
            self.assertIn("\n\n图 2：", normalized)
            self.assertEqual(stats["generated_alt"], 1)
            self.assertEqual(stats["missing"], [])

    def test_missing_image_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            _normalized, stats = normalize_images_and_captions(
                "![Figure](images/missing.jpg)",
                image_base_dir=Path(tmp),
            )
            self.assertEqual(stats["missing"], ["./images/missing.jpg"])

    def test_multi_panel_images_share_following_caption_alt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "images").mkdir()
            for name in ("a.jpg", "b.jpg"):
                (root / "images" / name).write_bytes(b"image")
            source = """![](images/a.jpg)

(a)

![](images/b.jpg)

(b)
图 12：不同主干网络输出维度的比较，指标为 $x-y$。
"""

            normalized, stats = normalize_images_and_captions(
                source, image_base_dir=root
            )

            self.assertEqual(stats["fallback_alt"], 0)
            self.assertEqual(stats["generated_alt"], 2)
            self.assertNotIn("论文插图", normalized)
            self.assertEqual(normalized.count("图 12："), 1)
            self.assertNotIn("$x-y$", normalized.splitlines()[0])


class MathOcrNormalizationTests(unittest.TestCase):
    def test_collapses_only_high_confidence_latex_identifiers(self) -> None:
        source = (
            r"$$\operatorname* { m i n }_x f(x) + "
            r"\mathrm { R a n k M e }(Z) + 1 0 ^ {-3} + \mathbb { R }$$"
        )

        normalized, stats = normalize_high_confidence_math_ocr(source)

        self.assertIn(r"\operatorname*{min}", normalized)
        self.assertIn(r"\mathrm{RankMe}", normalized)
        self.assertIn(r"10^", normalized)
        self.assertIn(r"\mathrm{R}", normalized)
        self.assertNotIn(r"\mathbb", normalized)
        self.assertEqual(stats["count"], 4)
        self.assertEqual(detect_suspicious_math(normalized)["issues"], [])


class AttentionRegressionTests(unittest.TestCase):
    def test_problematic_attention_snippet_is_normalized_and_flagged(self) -> None:
        source = (FIXTURE_DIR / "attention-problematic.md").read_text(
            encoding="utf-8"
        )

        normalized, table_stats = normalize_html_tables(source)
        protected, formulas = protect_math(normalized)
        math_quality = detect_suspicious_math(normalized)

        self.assertEqual(table_stats["converted"], 1)
        self.assertEqual(table_stats["fallback_html"], 0)
        self.assertNotIn("<table", normalized)
        self.assertIn("BLEU / EN-DE", normalized)
        self.assertEqual(len(formulas), 3)
        self.assertIn("[[[MATH_000]]]", protected)
        issue_types = {issue["type"] for issue in math_quality["issues"]}
        self.assertIn("spaced_math_keyword", issue_types)
        self.assertIn("spaced_power_of_ten", issue_types)
        self.assertIn("spaced_mathrm_identifier", issue_types)

    def test_attention_quality_report_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "full.md"
            output = root / "full_zh.md"
            source.write_text(
                (FIXTURE_DIR / "attention-problematic.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            (root / "images").mkdir()
            (root / "images" / "attention.jpg").write_bytes(b"image")

            def fake_request(
                _api_key: str, _system_prompt: str, chunk: str, retries: int = 3
            ) -> deepseek_translate.TranslationChunkResult:
                del retries
                content = chunk.replace(
                    "Figure 2: Scaled dot-product and multi-head attention.",
                    "图 2：缩放点积注意力与多头注意力。",
                )
                return deepseek_translate.TranslationChunkResult(
                    content=content,
                    usage={},
                    finish_reason="stop",
                    attempts=1,
                )

            with patch.object(
                deepseek_translate, "request_translation", side_effect=fake_request
            ):
                result = deepseek_translate.translate_file(
                    "test-key", "prompt", source, output
                )

            report = json.loads(
                (root / "translation_report.json").read_text(encoding="utf-8")
            )
            translated = output.read_text(encoding="utf-8")
            self.assertEqual(result["quality_status"], "needs_review")
            self.assertEqual(report["status"], "needs_review")
            self.assertNotIn("<table", translated)
            self.assertIn("BLEU / EN-DE", translated)
            self.assertIn(
                "![缩放点积注意力与多头注意力](./images/attention.jpg)",
                translated,
            )
            self.assertEqual(
                report["checks"]["table_normalization"]["converted"], 1
            )
            self.assertEqual(
                report["checks"]["markdown_tables"]["missing_converted"], 0
            )
            self.assertGreater(len(report["checks"]["math_ocr"]["issues"]), 0)


if __name__ == "__main__":
    unittest.main()

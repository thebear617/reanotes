from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = SKILL_ROOT / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

import deepseek_translate  # noqa: E402
from placeholders import PlaceholderDiff, PlaceholderIntegrityError  # noqa: E402


class ApiValidationTests(unittest.TestCase):
    def test_accepts_complete_response_with_exact_placeholders(self) -> None:
        source = "Equation [[[MATH_000]]]"
        payload = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "公式 [[[MATH_000]]]"},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

        content, usage, finish_reason = deepseek_translate._validate_api_result(
            payload, source
        )

        self.assertEqual(content, "公式 [[[MATH_000]]]")
        self.assertEqual(usage["completion_tokens"], 5)
        self.assertEqual(finish_reason, "stop")

    def test_rejects_length_truncation(self) -> None:
        payload = {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "被截断"},
                }
            ]
        }
        with self.assertRaises(deepseek_translate.TranslationResponseError):
            deepseek_translate._validate_api_result(payload, "source")

    def test_rejects_placeholder_corruption(self) -> None:
        payload = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "公式 [[[MATH_001]]]"},
                }
            ]
        }
        with self.assertRaises(PlaceholderIntegrityError):
            deepseek_translate._validate_api_result(
                payload, "Equation [[[MATH_000]]]"
            )

    def test_request_retries_truncated_response(self) -> None:
        class FakeResponse:
            def __init__(self, payload: dict):
                self.payload = payload

            def __enter__(self) -> "FakeResponse":
                return self

            def __exit__(self, *_args: object) -> None:
                return None

            def read(self) -> bytes:
                return json.dumps(self.payload).encode("utf-8")

        truncated = {
            "choices": [
                {
                    "finish_reason": "length",
                    "message": {"content": "截断 [[[MATH_000]]]"},
                }
            ]
        }
        complete = {
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": "公式 [[[MATH_000]]]"},
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }

        with patch.object(
            deepseek_translate.urllib.request,
            "urlopen",
            side_effect=[FakeResponse(truncated), FakeResponse(complete)],
        ), patch.object(deepseek_translate.time, "sleep"):
            result = deepseek_translate.request_translation(
                "test-key",
                "prompt",
                "Equation [[[MATH_000]]]",
                retries=2,
            )

        self.assertEqual(result.finish_reason, "stop")
        self.assertEqual(result.attempts, 2)


class TranslateFileQualityGateTests(unittest.TestCase):
    SOURCE = """# Example Paper

## Abstract

Equation $x+y$.

![](images/figure.jpg) Figure 1: Example architecture.

<table><tr><td>$z$</td></tr></table>

## References

[1] Omitted.
"""

    def test_success_writes_translation_and_publishable_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "full.md"
            output = root / "full_zh.md"
            source.write_text(self.SOURCE, encoding="utf-8")
            (root / "images").mkdir()
            (root / "images" / "figure.jpg").write_bytes(b"test-image")

            def fake_request(
                _api_key: str, _system_prompt: str, chunk: str, retries: int = 3
            ) -> deepseek_translate.TranslationChunkResult:
                del retries
                return deepseek_translate.TranslationChunkResult(
                    content=chunk.replace("Equation", "公式"),
                    usage={"prompt_tokens": 10, "completion_tokens": 5},
                    finish_reason="stop",
                    attempts=1,
                )

            with patch.object(
                deepseek_translate, "request_translation", side_effect=fake_request
            ):
                result = deepseek_translate.translate_file(
                    "test-key", "prompt", source, output
                )

            report_path = root / "translation_report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            translated = output.read_text(encoding="utf-8")
            self.assertEqual(result["status"], "translated")
            self.assertEqual(report["status"], "publishable")
            self.assertTrue(report["output_written"])
            self.assertEqual(
                report["checks"]["placeholder_integrity"]["protected"],
                {"html_tables": 0, "images": 1, "math": 2},
            )
            self.assertIn("$x+y$", translated)
            self.assertIn(
            "![Example architecture](./images/figure.jpg)", translated
            )
            self.assertNotIn("[[[", translated)

    def test_validation_failure_blocks_output_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "full.md"
            output = root / "full_zh.md"
            source.write_text(self.SOURCE, encoding="utf-8")

            with patch.object(
                deepseek_translate,
                "request_translation",
                side_effect=PlaceholderIntegrityError(
                    PlaceholderDiff(
                        missing=("[[[MATH_000]]]",), unexpected=()
                    )
                ),
            ):
                result = deepseek_translate.translate_file(
                    "test-key", "prompt", source, output
                )

            report = json.loads(
                (root / "translation_report.json").read_text(encoding="utf-8")
            )
            self.assertEqual(result["status"], "validation_failed")
            self.assertEqual(report["status"], "blocked")
            self.assertFalse(report["output_written"])
            self.assertEqual(
                report["checks"]["placeholder_integrity"]["missing"],
                ["[[[MATH_000]]]"],
            )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()

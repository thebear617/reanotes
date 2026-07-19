from __future__ import annotations

import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
LIB_DIR = SKILL_ROOT / "lib"
if str(LIB_DIR) not in sys.path:
    sys.path.insert(0, str(LIB_DIR))

from placeholders import (  # noqa: E402
    PlaceholderIntegrityError,
    compare_placeholders,
    protect_math,
    restore_placeholders,
    validate_placeholder_integrity,
)


class MathProtectionTests(unittest.TestCase):
    def test_protects_and_restores_supported_math_delimiters(self) -> None:
        source = (
            "Inline $x+y$ and display $$z = x^2$$.\n\n"
            "Also \\(a+b\\) and:\n\\[c=d\\]\n"
            "Escaped currency \\$5 stays text."
        )

        protected, formulas = protect_math(source)

        self.assertEqual(len(formulas), 4)
        self.assertIn("[[[MATH_000]]]", protected)
        self.assertIn("\\$5", protected)
        self.assertEqual(restore_placeholders(protected, formulas), source)

    def test_strict_restore_rejects_missing_math_placeholder(self) -> None:
        with self.assertRaises(PlaceholderIntegrityError):
            restore_placeholders("no placeholder", {"[[[MATH_000]]]": "$x$"})


class PlaceholderIntegrityTests(unittest.TestCase):
    def test_exact_multiset_passes(self) -> None:
        source = "[[[IMAGE_000]]] [[[MATH_000]]] [[[MATH_000]]]"
        translated = "文本 [[[MATH_000]]] [[[IMAGE_000]]] [[[MATH_000]]]"
        validate_placeholder_integrity(source, translated)

    def test_missing_and_unexpected_are_reported(self) -> None:
        diff = compare_placeholders(
            "[[[IMAGE_000]]] [[[MATH_000]]]",
            "[[[IMAGE_000]]] [[[MATH_001]]]",
        )
        self.assertEqual(diff.missing, ("[[[MATH_000]]]",))
        self.assertEqual(diff.unexpected, ("[[[MATH_001]]]",))
        with self.assertRaises(PlaceholderIntegrityError):
            validate_placeholder_integrity(
                "[[[IMAGE_000]]] [[[MATH_000]]]",
                "[[[IMAGE_000]]] [[[MATH_001]]]",
            )


if __name__ == "__main__":
    unittest.main()

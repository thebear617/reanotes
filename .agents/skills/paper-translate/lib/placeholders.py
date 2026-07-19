"""Protect fragile Markdown structures and validate translation placeholders."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass


PLACEHOLDER_RE = re.compile(r"\[\[\[(?:HTML_TABLE|IMAGE|MATH)_\d{3}\]\]\]")
MATH_RE = re.compile(
    r"(?<!\\)\$\$[\s\S]*?(?<!\\)\$\$"
    r"|\\\[[\s\S]*?\\\]"
    r"|\\\([\s\S]*?\\\)"
    r"|(?<!\\)\$(?!\$)(?:\\.|[^$\n])+?(?<!\\)\$"
)


@dataclass(frozen=True)
class PlaceholderDiff:
    """Difference between placeholders expected in a chunk and model output."""

    missing: tuple[str, ...]
    unexpected: tuple[str, ...]

    @property
    def is_valid(self) -> bool:
        return not self.missing and not self.unexpected


class PlaceholderIntegrityError(ValueError):
    """Raised when a translated chunk changes a protected placeholder."""

    def __init__(self, diff: PlaceholderDiff):
        self.diff = diff
        details: list[str] = []
        if diff.missing:
            details.append(f"missing={list(diff.missing)}")
        if diff.unexpected:
            details.append(f"unexpected={list(diff.unexpected)}")
        super().__init__("placeholder integrity failed: " + ", ".join(details))


def extract_placeholders(text: str) -> list[str]:
    """Return protected placeholders in source order, including duplicates."""
    return PLACEHOLDER_RE.findall(text)


def count_placeholders(text: str) -> Counter[str]:
    return Counter(extract_placeholders(text))


def compare_placeholders(source_text: str, translated_text: str) -> PlaceholderDiff:
    """Compare exact placeholder multisets between source and translation."""
    expected = count_placeholders(source_text)
    actual = count_placeholders(translated_text)
    missing = tuple(sorted((expected - actual).elements()))
    unexpected = tuple(sorted((actual - expected).elements()))
    return PlaceholderDiff(missing=missing, unexpected=unexpected)


def validate_placeholder_integrity(source_text: str, translated_text: str) -> None:
    diff = compare_placeholders(source_text, translated_text)
    if not diff.is_valid:
        raise PlaceholderIntegrityError(diff)


def protect_math(text: str) -> tuple[str, dict[str, str]]:
    """Replace LaTeX math spans with stable placeholders.

    Supports `$...$`, `$$...$$`, `\\(...\\)`, and `\\[...\\]`. HTML tables
    should be protected before this function so their raw contents remain one
    independent protected unit until the table-normalization phase is added.
    """
    formulas: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        placeholder = f"[[[MATH_{len(formulas):03d}]]]"
        formulas[placeholder] = match.group(0)
        return placeholder

    return MATH_RE.sub(replace, text), formulas


def restore_placeholders(
    text: str,
    replacements: dict[str, str],
    *,
    strict: bool = True,
) -> str:
    """Restore one placeholder map and optionally reject missing entries."""
    if strict:
        missing = tuple(key for key in replacements if text.count(key) != 1)
        if missing:
            raise PlaceholderIntegrityError(
                PlaceholderDiff(missing=missing, unexpected=())
            )
    for placeholder, value in replacements.items():
        text = text.replace(placeholder, value)
    return text


def placeholder_type_counts(text: str) -> dict[str, int]:
    """Return aggregate counts suitable for quality reports."""
    counts = {"html_tables": 0, "images": 0, "math": 0}
    for placeholder in extract_placeholders(text):
        if placeholder.startswith("[[[HTML_TABLE_"):
            counts["html_tables"] += 1
        elif placeholder.startswith("[[[IMAGE_"):
            counts["images"] += 1
        elif placeholder.startswith("[[[MATH_"):
            counts["math"] += 1
    return counts

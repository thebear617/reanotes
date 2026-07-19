"""Build and persist machine-readable translation quality reports."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from placeholders import MATH_RE


REPORT_SCHEMA_VERSION = 2
OCR_MATH_PATTERNS = (
    (
        "spaced_math_keyword",
        re.compile(
            r"\b(?:l\s+r\s+a\s+t\s+e|l\s+o\s+g|m\s+i\s+n|m\s+a\s+x|"
            r"s\s+i\s+n|c\s+o\s+s)\b",
            re.IGNORECASE,
        ),
    ),
    ("spaced_power_of_ten", re.compile(r"(?<!\d)1\s+0\s*\^")),
    (
        "spaced_mathrm_identifier",
        re.compile(r"\\mathrm\s*\{\s*(?:[A-Za-z]\s+){2,}[A-Za-z]\s*\}"),
    ),
)
SPACED_COMMAND_IDENTIFIER_RE = re.compile(
    r"\\(?P<command>mathrm|operatorname)(?P<star>\s*\*)?\s*\{\s*"
    r"(?P<letters>(?:[A-Za-z]\s+){2,}[A-Za-z])\s*\}"
)


def normalize_high_confidence_math_ocr(text: str) -> tuple[str, dict[str, Any]]:
    """Fix unambiguous spaced identifiers inside LaTeX and report each fix."""
    fixes: list[dict[str, Any]] = []
    formula_index = 0

    def normalize_formula(match: re.Match[str]) -> str:
        nonlocal formula_index
        formula = match.group(0)

        def collapse_identifier(identifier_match: re.Match[str]) -> str:
            before = identifier_match.group(0)
            letters = re.sub(r"\s+", "", identifier_match.group("letters"))
            star = "*" if identifier_match.group("star") else ""
            after = f"\\{identifier_match.group('command')}{star}{{{letters}}}"
            fixes.append(
                {
                    "formula": formula_index,
                    "type": "spaced_command_identifier",
                    "before": before,
                    "after": after,
                }
            )
            return after

        normalized = SPACED_COMMAND_IDENTIFIER_RE.sub(collapse_identifier, formula)

        def collapse_power(power_match: re.Match[str]) -> str:
            fixes.append(
                {
                    "formula": formula_index,
                    "type": "spaced_power_of_ten",
                    "before": power_match.group(0),
                    "after": "10",
                }
            )
            return "10"

        normalized = re.sub(r"(?<!\d)1\s+0\s*(?=\^)", collapse_power, normalized)

        def replace_mathbb(mathbb_match: re.Match[str]) -> str:
            before = mathbb_match.group(0)
            after = f"\\mathrm{{{mathbb_match.group('symbol')}}}"
            fixes.append(
                {
                    "formula": formula_index,
                    "type": "mathbb_render_fallback",
                    "before": before,
                    "after": after,
                }
            )
            return after

        normalized = re.sub(
            r"\\mathbb\s*\{\s*(?P<symbol>[A-Za-z])\s*\}",
            replace_mathbb,
            normalized,
        )
        formula_index += 1
        return normalized

    normalized_text = MATH_RE.sub(normalize_formula, text)
    return normalized_text, {"count": len(fixes), "fixes": fixes}


def detect_suspicious_math(text: str) -> dict[str, Any]:
    """Report high-confidence MinerU/OCR artifacts without changing formulas."""
    issues: list[dict[str, Any]] = []
    formulas = [match.group(0) for match in MATH_RE.finditer(text)]
    for formula_index, formula in enumerate(formulas):
        for issue_type, pattern in OCR_MATH_PATTERNS:
            if pattern.search(formula):
                issues.append(
                    {
                        "formula": formula_index,
                        "type": issue_type,
                        "snippet": re.sub(r"\s+", " ", formula)[:180],
                    }
                )
    return {"count": len(formulas), "issues": issues}


def build_translation_report(
    *,
    source: Path,
    output: Path,
    status: str,
    protected_counts: dict[str, int],
    chunks: list[dict[str, Any]],
    remaining_placeholders: list[str] | None = None,
    missing_placeholders: list[str] | None = None,
    unexpected_placeholders: list[str] | None = None,
    table_normalization: dict[str, Any] | None = None,
    markdown_tables: dict[str, Any] | None = None,
    image_normalization: dict[str, Any] | None = None,
    math_quality: dict[str, Any] | None = None,
    error: str | None = None,
    output_written: bool = False,
) -> dict[str, Any]:
    """Create the first-stage quality report contract."""
    remaining = sorted(remaining_placeholders or [])
    missing = sorted(missing_placeholders or [])
    unexpected = sorted(unexpected_placeholders or [])
    if status in {"publishable", "needs_review"} and not remaining and not missing and not unexpected:
        placeholder_status = "passed"
    elif remaining or missing or unexpected:
        placeholder_status = "failed"
    else:
        placeholder_status = "not_completed"
    completion_status = (
        "passed"
        if chunks and all(chunk.get("finish_reason") == "stop" for chunk in chunks)
        else "failed"
    )
    report: dict[str, Any] = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": status,
        "source": str(source),
        "output": str(output),
        "output_written": output_written,
        "checks": {
            "placeholder_integrity": {
                "status": placeholder_status,
                "protected": protected_counts,
                "missing": missing,
                "unexpected": unexpected,
                "remaining": remaining,
            },
            "api_completion": {
                "status": completion_status,
                "chunks": chunks,
            },
            "math_protection": {
                "status": "passed",
                "protected": protected_counts.get("math", 0),
            },
            "table_normalization": table_normalization or {},
            "markdown_tables": markdown_tables or {},
            "image_normalization": image_normalization or {},
            "math_ocr": math_quality or {},
        },
    }
    if error:
        report["error"] = error
    return report


def write_translation_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

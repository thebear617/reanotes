"""DeepSeek translation core — library, no CLI, no env loading, no hardcoded paths.

Pipeline (in-memory, no `body.md` written to disk):

    full.md
      → clean_body
      → normalize_html_tables
      → protect_html_tables / protect_markdown_images / protect_math
      → split_chunks → request_translation → validate each chunk
      → restore placeholders
      → apply_title_policy → normalize images → structural checks
      → full_zh.md + translation_report.json

Caller responsibilities:
- load `DEEPSEEK_API_KEY` into os.environ (use `lib/env_loader.py`)
- pass `glossary_path` explicitly (no DEFAULT — use the skill's built-in
  `glossary/general-ovs-cv-nlp.md` or a project-specific one)
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

# Allow `import deepseek_translate` whether called from scripts/ or lib/.
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from clean_markdown import (  # noqa: E402
    apply_title_policy,
    clean_body,
    protect_html_tables,
    protect_markdown_images,
    split_chunks,
)
from placeholders import (  # noqa: E402
    PlaceholderIntegrityError,
    extract_placeholders,
    placeholder_type_counts,
    protect_math,
    restore_placeholders,
    validate_placeholder_integrity,
)
from normalize_structures import (  # noqa: E402
    normalize_html_tables,
    normalize_images_and_captions,
    validate_markdown_tables,
)
from quality_checks import (  # noqa: E402
    build_translation_report,
    detect_suspicious_math,
    normalize_high_confidence_math_ocr,
    write_translation_report,
)


URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
USD_TO_CNY = 7.25

# Official DeepSeek-V4-Flash prices, per 1M tokens. `deepseek-chat` maps to
# non-thinking DeepSeek-V4-Flash for compatibility.
INPUT_CACHE_HIT_USD_PER_M = 0.0028
INPUT_CACHE_MISS_USD_PER_M = 0.14
OUTPUT_USD_PER_M = 0.28

SYSTEM_PROMPT_TEMPLATE = """You are a professional academic translator specializing in computer vision and machine learning.
Translate the following cleaned English academic-paper markdown to Simplified Chinese (zh-CN).

STRICT RULES:
1. Output ONLY the translated markdown. No explanations, preamble, notes, or reasoning.
2. Preserve markdown syntax: headings, lists, emphasis, links, image refs ![](path), LaTeX ($...$, $$...$$), citation numbers [N].
3. Preserve every placeholder like [[[HTML_TABLE_000]]], [[[IMAGE_000]]], or [[[MATH_000]]] exactly. Do not translate, delete, split, wrap, or punctuate placeholders.
4. Preserve model/method/dataset names and metric names in English unless there is a standard Chinese term.
5. Translate figure/table captions in place. Use professional Chinese academic style.
6. Keep the first H1 paper title in English when possible, and provide a Chinese title line under it.
7. Follow this glossary with highest priority:

{glossary}
"""


def load_glossary(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Glossary not found: {path}")
    return path.read_text(encoding="utf-8")


def build_system_prompt(glossary_path: Path) -> str:
    return SYSTEM_PROMPT_TEMPLATE.format(glossary=load_glossary(glossary_path))


@dataclass(frozen=True)
class TranslationChunkResult:
    content: str
    usage: dict
    finish_reason: str
    attempts: int


class TranslationResponseError(ValueError):
    """Raised when the API returns incomplete or structurally invalid output."""


def _validate_api_result(result: dict, source_chunk: str) -> tuple[str, dict, str]:
    """Validate one API payload before it is accepted as translated Markdown."""
    try:
        choice = result["choices"][0]
        finish_reason = choice.get("finish_reason") or ""
        content = choice["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        raise TranslationResponseError("malformed API response") from exc

    if finish_reason != "stop":
        raise TranslationResponseError(
            f"incomplete API response: finish_reason={finish_reason or 'missing'}"
        )
    if not content:
        raise TranslationResponseError("empty translation response")
    validate_placeholder_integrity(source_chunk, content)
    return content, result.get("usage", {}), finish_reason


def request_translation(
    api_key: str,
    system_prompt: str,
    chunk: str,
    retries: int = 3,
) -> TranslationChunkResult:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": chunk},
        ],
        "temperature": 0.1,
        "max_tokens": 8192,
        "stream": False,
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            content, usage, finish_reason = _validate_api_result(result, chunk)
            return TranslationChunkResult(
                content=content,
                usage=usage,
                finish_reason=finish_reason,
                attempts=attempt,
            )
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            json.JSONDecodeError,
            TranslationResponseError,
            PlaceholderIntegrityError,
        ) as exc:
            if attempt == retries:
                raise
            wait_s = 2 * attempt
            print(f"    retry {attempt}/{retries} after {type(exc).__name__}; wait {wait_s}s")
            time.sleep(wait_s)

    raise RuntimeError("unreachable")


def compute_cost(usage_totals: dict) -> dict:
    prompt_tokens = usage_totals.get("prompt_tokens", 0)
    completion_tokens = usage_totals.get("completion_tokens", 0)
    cache_hit_tokens = usage_totals.get("prompt_cache_hit_tokens", 0)
    cache_miss_tokens = usage_totals.get(
        "prompt_cache_miss_tokens", prompt_tokens - cache_hit_tokens
    )

    cost_usd = (
        cache_hit_tokens / 1_000_000 * INPUT_CACHE_HIT_USD_PER_M
        + cache_miss_tokens / 1_000_000 * INPUT_CACHE_MISS_USD_PER_M
        + completion_tokens / 1_000_000 * OUTPUT_USD_PER_M
    )
    return {
        "cost_usd": cost_usd,
        "cost_cny": cost_usd * USD_TO_CNY,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "prompt_cache_hit_tokens": cache_hit_tokens,
        "prompt_cache_miss_tokens": cache_miss_tokens,
    }


def translate_file(
    api_key: str,
    system_prompt: str,
    source: Path,
    output: Path,
    force: bool = False,
    report_path: Path | None = None,
) -> dict:
    """Translate one Markdown file. Returns a result dict with usage + cost."""
    if output.exists() and not force:
        return {
            "source": str(source),
            "output": str(output),
            "status": "skipped_exists",
        }

    report_path = report_path or output.parent / "translation_report.json"
    text = clean_body(source.read_text(encoding="utf-8"))
    text, table_normalization = normalize_html_tables(text)
    protected_text, html_tables = protect_html_tables(text)
    protected_text, markdown_images = protect_markdown_images(protected_text)
    protected_text, math_formulas = protect_math(protected_text)
    protected_counts = placeholder_type_counts(protected_text)
    chunks = split_chunks(protected_text)
    usage_totals = {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "prompt_cache_hit_tokens": 0,
        "prompt_cache_miss_tokens": 0,
    }
    translated_chunks: list[str] = []
    chunk_reports: list[dict] = []
    t0 = time.time()

    print(f"▶ {source.parent.name}: {len(chunks)} chunks")
    try:
        for idx, chunk in enumerate(chunks, 1):
            print(f"  [{idx}/{len(chunks)}] translating...", flush=True)
            try:
                chunk_result = request_translation(api_key, system_prompt, chunk)
            except Exception:
                chunk_reports.append(
                    {
                        "index": idx,
                        "finish_reason": "failed",
                        "attempts": 3,
                        "placeholders": len(extract_placeholders(chunk)),
                    }
                )
                raise
            translated_chunks.append(chunk_result.content)
            chunk_reports.append(
                {
                    "index": idx,
                    "finish_reason": chunk_result.finish_reason,
                    "attempts": chunk_result.attempts,
                    "placeholders": len(extract_placeholders(chunk)),
                }
            )
            for key in usage_totals:
                usage_totals[key] += chunk_result.usage.get(key, 0)
            if (
                "prompt_cache_miss_tokens" not in chunk_result.usage
                and "prompt_tokens" in chunk_result.usage
            ):
                usage_totals["prompt_cache_miss_tokens"] = (
                    usage_totals["prompt_tokens"]
                    - usage_totals["prompt_cache_hit_tokens"]
                )

        translated_text = "\n\n".join(translated_chunks)
        translated_text = restore_placeholders(translated_text, math_formulas)
        translated_text = restore_placeholders(translated_text, markdown_images)
        translated_text = restore_placeholders(translated_text, html_tables)
        remaining_placeholders = extract_placeholders(translated_text)
        if remaining_placeholders:
            raise TranslationResponseError(
                f"unrestored placeholders: {remaining_placeholders}"
            )
        translated_text = apply_title_policy(text, translated_text)
        translated_text, image_normalization = normalize_images_and_captions(
            translated_text,
            image_base_dir=source.parent,
        )
        translated_text, math_ocr_normalization = normalize_high_confidence_math_ocr(
            translated_text
        )
        markdown_tables = validate_markdown_tables(translated_text)
        markdown_tables["expected_from_html"] = table_normalization["converted"]
        markdown_tables["missing_converted"] = max(
            table_normalization["converted"] - markdown_tables["count"],
            0,
        )
        math_quality = detect_suspicious_math(translated_text)
        math_quality["normalization"] = math_ocr_normalization
    except Exception as exc:  # per-paper failure must not abort the entire batch
        status = (
            "validation_failed"
            if isinstance(
                exc,
                (PlaceholderIntegrityError, TranslationResponseError),
            )
            else "translation_failed"
        )
        placeholder_diff = (
            exc.diff
            if isinstance(exc, PlaceholderIntegrityError)
            else None
        )
        report = build_translation_report(
            source=source,
            output=output,
            status="blocked",
            protected_counts=protected_counts,
            chunks=chunk_reports,
            remaining_placeholders=[],
            missing_placeholders=(
                list(placeholder_diff.missing) if placeholder_diff else []
            ),
            unexpected_placeholders=(
                list(placeholder_diff.unexpected) if placeholder_diff else []
            ),
            error=f"{type(exc).__name__}: {exc}",
            output_written=False,
            table_normalization=table_normalization,
        )
        write_translation_report(report_path, report)
        print(f"  blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return {
            "source": str(source),
            "output": str(output),
            "report": str(report_path),
            "status": status,
            "chunks": len(chunks),
            "elapsed_s": time.time() - t0,
        }

    quality_status = "publishable"
    if (
        table_normalization["fallback_html"]
        or table_normalization["issues"]
        or markdown_tables["issues"]
        or markdown_tables["missing_converted"]
        or image_normalization["missing"]
        or image_normalization["fallback_alt"]
        or math_quality["issues"]
    ):
        quality_status = "needs_review"

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(translated_text.rstrip() + "\n", encoding="utf-8")
    report = build_translation_report(
        source=source,
        output=output,
        status=quality_status,
        protected_counts=protected_counts,
        chunks=chunk_reports,
        remaining_placeholders=[],
        output_written=True,
        table_normalization=table_normalization,
        markdown_tables=markdown_tables,
        image_normalization=image_normalization,
        math_quality=math_quality,
    )
    write_translation_report(report_path, report)
    elapsed_s = time.time() - t0
    cost = compute_cost(usage_totals)
    result = {
        "source": str(source),
        "output": str(output),
        "status": "translated",
        "quality_status": quality_status,
        "report": str(report_path),
        "chunks": len(chunks),
        "elapsed_s": elapsed_s,
        **cost,
    }
    print(
        f"  done: {elapsed_s:.1f}s, "
        f"in={cost['prompt_tokens']}, out={cost['completion_tokens']}, "
        f"cost=¥{cost['cost_cny']:.4f}"
    )
    return result

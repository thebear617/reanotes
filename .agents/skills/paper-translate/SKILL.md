---
name: paper-translate
description: "Translate an academic paper PDF or URL to quality-gated Simplified Chinese Markdown and optionally publish it directly into the ReaNotes literature library. End-to-end: MinerU extraction, DeepSeek in-memory translation, table/image/math checks, and ReaNotes index/build validation. Use for new paper translation or publishing an existing paper-translate output. Field-agnostic; defaults to an OVS / CV / NLP-flavoured glossary."
---

# Paper Translate

End-to-end paper translation, field-agnostic. Single command takes a URL or a local PDF and produces a clean `full_zh.md` next to the MinerU-produced `full.md`.

Pipeline:

```
URL / local PDF
   → MinerU (via ~/Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py)
   → {out_root}/{date}/{name}/full.md + images/
   → clean_body → HTML tables to Markdown → protect remaining HTML / images / LaTeX math
   → split_chunks → DeepSeek per chunk → validate placeholders + finish_reason
   → restore placeholders → normalize image captions + alt → structural quality checks
   → {out_root}/{date}/{name}/full_zh.md + translation_report.json
   → optional --publish quality gate → ReaNotes README.md + images + index
```

Cleaning happens in memory. **No `body.md` is written to disk.**

## When to invoke

- User gives a paper PDF or arXiv URL and asks for a Chinese translation.
- User wants to batch-translate a `sources.txt` of papers.
- User asks for a deep-dive into a paper that requires a clean zh reference alongside the original.

## When NOT to invoke

- User only wants MinerU extraction without translation → use `mineru-extract` directly.
- User wants English cleanup / reformatting only → use `mineru-extract` and a custom script.
- Source is a webpage (blog, news) — this skill assumes paper-like structure with refs / appendix.

## Inputs

- **Positional**: one or more URLs or local `.pdf` paths
- **`--sources-file <path>`**: UTF-8 file with one source per line (`#` for comments)
- **`--out-root <path>`**: defaults to `reanotes/output/translations/`
- **`--date YYYY-MM-DD`**: defaults to today
- **`--glossary <path>`**: defaults to `glossary/general-ovs-cv-nlp.md` (skill-internal fallback)
- **`--mineru-script <path>`**: defaults to `~/Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py`
- **`--mineru-model`**: `pipeline | vlm | MinerU-HTML` (default `pipeline`)
- **`--mineru-timeout`**: seconds (default 600)
- **`--force`**: re-translate even if `full_zh.md` already exists
- **`--force-extract`**: run MinerU again even when the planned target already contains `full.md`; without it retries reuse the existing extraction.
- **`--name <name>`**: per-source folder name, repeatable. Skips the pre-run prompt for that source. **When invoking from an agent, pass this to avoid blocking on `input()`.**
- **`--non-interactive`**: skip ALL pre-run name prompts. arXiv papers fall back to `{arxiv-id}-{YYYYMMDD}`; URLs fall back to `url-{YYYYMMDD}`; local PDFs fall back to `{stem}-{YYYYMMDD}`.
- **`--dry-run`**: print the plan, do not invoke MinerU or DeepSeek. Prompting is disabled (uses auto-names) so the run never blocks on stdin.
- **`--publish`**: publish accepted translations to the ReaNotes literature library, update its index, then run Prettier, lint, build, and generated-page checks.
- **`--reanotes-root <path>`**: ReaNotes repository root used by `--publish`.
- **`--publish-needs-review`**: explicitly allow `needs_review`; without it the publication gate accepts only `publishable`.
- **`--publish-force`**: replace an existing published translation directory.

## Configuration

`DEEPSEEK_API_KEY` must be in `paper-translate/.env` (skill root) or already in the process environment. Format:

```
DEEPSEEK_API_KEY=sk-...
```

The skill auto-loads `<skill_root>/.env` and `<skill_root>/scripts/.env` on import.

## Folder naming — the pre-run prompt

**Naming happens BEFORE the pipeline starts**, not after. The decision matrix:

| Source          | Single run (default)                                                                              | Batch run (`>1` source)              | `--non-interactive`                  |
| --------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------ |
| **arXiv URL**   | `Folder name for {id} (no default, must type): ` — empty input → `exit 2`                         | silent auto-name `{id}-{YYYYMMDD}`   | silent auto-name `{id}-{YYYYMMDD}`   |
| **Generic URL** | `Folder name for {url} (default: url-{YYYYMMDD}): ` — Enter accepts default                       | silent auto-name `url-{YYYYMMDD}`    | silent auto-name `url-{YYYYMMDD}`    |
| **Local PDF**   | `Short name for {file} (default: {stem}): ` — Enter accepts default (gets `-{YYYYMMDD}` appended) | silent auto-name `{stem}-{YYYYMMDD}` | silent auto-name `{stem}-{YYYYMMDD}` |

When invoking from an agent (Claude Code), **ask the user up front** for the folder name and pass it via `--name`. This avoids `input()` blocking the script. Example:

```bash
# Agent gets "translate https://arxiv.org/abs/2504.09480 and call it DINO-Soars"
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "DINO-Soars" https://arxiv.org/abs/2504.09480
```

For batch with multiple custom names, repeat `--name` in source order:

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "PaperA" https://arxiv.org/abs/1 \
  --name "PaperB" https://arxiv.org/abs/2 \
  --name "PaperC" https://arxiv.org/abs/3
```

Folder names are sanitized (only `[A-Za-z0-9._-]`, others collapsed to `-`). The date suffix is added by the script for local PDF and URL auto-names; for arXiv auto-names the date comes from the arXiv API (or year-month fallback with day = 01 if API is unreachable).

## Usage

### Single arXiv paper

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  https://arxiv.org/abs/2311.12345
```

Will prompt `Folder name for 2311.12345 (no default, must type):` — type any name. To skip the prompt, pass `--name`.

### Single local PDF

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "reco-paper" ~/Downloads/reco.pdf
```

### Batch

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --sources-file sources.txt \
  --glossary /path/to/my-project-glossary.md
```

Batch mode is silent (no prompts) — uses auto-defaults for every source.

### Dry run

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --sources-file sources.txt --dry-run
```

Prints the plan (target dirs, glossary, counts) without hitting the network. Always uses auto-names (no prompt) so it never blocks on stdin.

### Translate and publish to ReaNotes

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "attention-is-all-you-need" --publish \
  https://arxiv.org/abs/1706.03762
```

The public library receives only the Chinese `README.md`, `images/`, the quality report, and portable translation metadata. English `full.md` stays in the private translation workspace. Existing index rows are relinked in place; papers absent from the index get a complete default row for later refinement.

To publish an existing output without invoking MinerU or DeepSeek again:

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/publish_reanotes.py \
  --source https://arxiv.org/abs/1706.03762 \
  /path/to/translation-output/attention-is-all-you-need
```

## Output contract

For each input paper, the skill produces **one folder**:

```
{out_root}/{date}/{name}/
├── full.md           # MinerU English Markdown
├── images/           # extracted figures
├── full_zh.md        # DeepSeek Chinese translation (only written after validation)
└── translation_report.json # per-paper quality-gate result
```

Per-run aggregates live in `{out_root}/{date}/`:

- `summary.json` — per-paper status, `publishable` / `needs_review` totals, token counts, cost
- `usage_ledger.md` — append-only cost log across runs

With `--publish`, each accepted paper also produces:

```
reanotes/docs/literature/translations/{slug}/
├── README.md                    # Chinese translation only
├── images/                      # local figures used by README.md
├── translation-report.json     # quality-gate evidence
└── translation-metadata.json   # title, source, model, status, publication time
```

Publication updates `reanotes/docs/literature/papers.md`. Per-paper publication results and the final `publication_validation` are stored in `summary.json`.

## Cleaning rules (validated on OVS 113-paper batch)

- Normalize newlines to `\n`.
- Strip author block / arXiv watermark before the first body line. Prefer the abstract, then the first numbered section / Introduction, and use the first image only as a final fallback.
- Strip everything from References / Bibliography / Acknowledgements / Appendix onward.
- Protect `<table>…</table>` blocks with `[[[HTML_TABLE_NNN]]]` placeholders, restore after LLM.
- Before protection, convert representable HTML tables to rectangular Markdown tables. Expand `rowspan` and `colspan`, combine multi-row headers, and leave unsupported nested tables as protected HTML with a report warning.
- Protect `![](path)` line prefixes with `[[[IMAGE_NNN]]]` placeholders (caption text on the same line is left for the LLM to translate).
- Protect `$...$`, `$$...$$`, `\(...\)`, and `\[...\]` LaTeX with `[[[MATH_NNN]]]` placeholders.
- Validate the exact placeholder multiset and API `finish_reason` for every chunk. Retry invalid or truncated chunks up to 3 times.
- Write `full_zh.md` only when all chunks pass. Always write `translation_report.json` for a completed or blocked translation attempt.
- After translation, derive missing image alt text from translated captions (including shared multi-panel captions), put inline captions on their own paragraph, normalize local targets to `./images/...` for VuePress/Vite, and report missing files.
- Validate Markdown table column counts. Normalize high-confidence OCR artifacts inside LaTeX commands (for example spaced `\operatorname`, `\mathrm`, and `1 0 ^`) and record every change. Replace single-symbol `\mathbb` with the site's stable `\mathrm` fallback to avoid static-renderer font failures. Continue to flag uncertain formulas such as `l r a t e` without rewriting them.
- Set report status to `publishable` when structural checks pass, `needs_review` for recoverable table/image/math warnings, or `blocked` when translation integrity fails.
- Title policy: keep the original English H1, insert `> 中文题名：…` line under it. If the LLM already produced a `> 中文题名：…` line, keep its content.

## Title policy detail

The first H1 is forced to match the source H1 (so `检索` is never substituted for the English title). Under the H1, a single `> 中文题名：…` line carries the Chinese title.

If the LLM's translation puts a heading right after the H1 (e.g. `## ReCo: 检索协同分割`), the script lifts that into the `> 中文题名：…` slot — but only when the heading is not `Abstract` / `Introduction` / `摘要` / `引言` / `介绍`.

## Failure modes & fallbacks

- **MinerU fails for a URL** (anti-bot / geo / login): the script prints the failure and continues with the next paper. Re-run with a local PDF or a long screenshot.
- **arXiv abs URL auto-rewritten to PDF URL**: `pipeline` model can't parse HTML, so the script always passes the PDF URL to MinerU when the input is `arxiv.org/abs/<id>`. The plan still shows the original abs URL.
- **DeepSeek rate limit / timeout**: `lib/deepseek_translate.py` retries 3 times with backoff (2s, 4s, 6s). After that the paper is marked failed in `summary.json`.
- **Placeholder changed or output truncated**: retry the affected chunk up to 3 times. If it still fails, do not write `full_zh.md`; write a blocked `translation_report.json` and continue the batch.
- **Unsupported table, missing image, or suspicious OCR math**: keep `full_zh.md`, set `translation_report.json` to `needs_review`, and require review before publishing.
- **ReaNotes publication rejected**: `--publish` accepts only `publishable` by default. Use `--publish-needs-review` only after an explicit human review decision.
- **Published target already exists**: use `--publish-force` only when replacement is intended. The adapter restores the previous target if index updating fails.
- **ReaNotes validation fails**: the run exits non-zero and records command output plus generated-page findings under `publication_validation`.
- **arXiv API unreachable for date lookup**: falls back to year-month from the ID; folder name will use day = 01.
- **arXiv single run, empty stdin** (no `--name`, no interactive input): the script exits with code 2 and message `arXiv paper {id} requires a folder name; aborting.` Agents must pass `--name` to avoid this.
- **Local PDF, no `--name`, no stdin input**: falls back to `{stem}-{YYYYMMDD}` (silent in batch and `--non-interactive`).
- **MinerU smart-name folder collision** (e.g. you already have a `DINO-2026/` from a previous run): MinerU auto-appends `-2`, `-3`, etc. The script auto-renames to the planned name in Phase 3 (deletes an empty placeholder if present). No post-run prompt.

## Pricing

Hardcoded in `lib/deepseek_translate.py` for `deepseek-chat` (non-thinking DeepSeek-V4-Flash):

- Input (cache hit): $0.0028 / 1M tokens
- Input (cache miss): $0.14 / 1M tokens
- Output: $0.28 / 1M tokens
- USD → CNY: 7.25

Update the constants if DeepSeek pricing changes.

## References

- DeepSeek API: https://api-docs.deepseek.com/
- arXiv API: https://info.arxiv.org/help/api/basics.html
- Upstream parser: `~/Documents/notes/.claude/skills/mineru-extract/SKILL.md`
- Migrated from: `02-Areas/领域研究/OVS/pipeline/scripts/` (now deprecated and removed in 2026-06-08 directory restructure)

## Migration notes

The OVS 113-paper batch was translated under the old `02-Areas/领域研究/OVS/pipeline/` driver (entire `02-Areas/领域研究/` tree removed in 2026-06-08 restructure). That driver was OVS-specific (read `OVS-文献索引.md`, wrote `body.md` + `body_zh_deepseek.md` per paper, tracked a usage ledger by date). The new skill is field-agnostic and writes only `full_zh.md` per paper.

Old OVS artefacts under `04-Archives/文献原文md/未分类/2026-05-22/` are left as legacy — they still have `body.md` and `body_zh_deepseek.md` files. New runs go to `未分类/{today}/` with only `full.md` + `images/` + `full_zh.md`.

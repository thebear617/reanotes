# paper-translate skill — 迁移 Handoff

> 目标读者：另一台电脑、另一个用户下的 Agent。读完应能：把 skill 跑起来；知道哪些路径/密钥必须改；知道出错时看哪里。

## 1. 这个 skill 做什么

端到端学术论文翻译。输入 arXiv URL 或本地 PDF，串起 **MinerU 解析 → DeepSeek 翻译**两步，输出中文 Markdown。

```
URL / 本地 PDF
   → MinerU 抽取英文 Markdown（不写 body.md 到磁盘，全部在内存里清洗）
   → DeepSeek 按 chunk 翻译
   → {out_root}/{date}/{name}/full_zh.md
   → 可选：质量闸门后发布到 ReaNotes 文献库
```

领域无关（任何 arXiv / 本地 PDF 都行）。默认术语表 `glossary/general-ovs-cv-nlp.md` 偏向 OVS / CV / NLP；可通过 `--glossary <path>` 替换。

## 2. 文件结构

```
paper-translate/
├── SKILL.md                          # 暴露给 WorkBuddy 的 skill 描述
├── .env.example                      # API 密钥模板（复制为 .env 并填入真实密钥）
├── .gitignore                        # 排除 .env 和 __pycache__
├── HANDOFF.md                        # 本文件
├── scripts/
│   ├── paper_translate.py            # 翻译主 CLI，可用 --publish 直接发布
│   └── publish_reanotes.py            # 已有译文的独立发布入口，不调用 API
├── lib/
│   ├── clean_markdown.py             # 内存清洗规则：front-matter / back-matter / HTML 表格 / 图片占位 / 标题策略
│   ├── normalize_structures.py        # HTML 表格转 Markdown、合并单元格展开、图片与图注规范化
│   ├── placeholders.py               # 公式保护、通用占位符恢复和完整性校验
│   ├── quality_checks.py              # OCR 公式检测与 translation_report.json 质量报告
│   ├── reanotes_publish.py             # 中文正文/图片复制、索引更新、构建验证
│   ├── deepseek_translate.py         # DeepSeek 客户端：API 调用 + 3 次重试 + token/费用统计
│   └── env_loader.py                 # 读取 skill 根目录的 .env
└── glossary/
    └── general-ovs-cv-nlp.md         # 默认术语表（~150 条）
```

只用 Python 标准库（argparse、urllib、subprocess、pathlib、json 等），不需要 pip install。

## 3. 依赖

- **同级 skill：`mineru-extract`**（位于 `~/Documents/notes/.claude/skills/mineru-extract/`）。本 skill 用 `subprocess` 调 `python3 ~/Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py`。
- **外部服务**：
  - DeepSeek API（`https://api.deepseek.com`）— 密钥见 §4
  - MinerU API（`https://mineru.net`）— 密钥在 mineru-extract 的 `.env` 里，**不归本 skill 管**
  - arXiv API（`https://info.arxiv.org`）— 公开无鉴权，仅用于查 arXiv 论文公开日期
- **Python ≥ 3.10**（用到 `from __future__ import annotations`、`Iterable`、PEP 604 union 写法）
- **`python3` 在 PATH 里**
- **运行 cwd 建议为项目根**（`/Users/mokaiche/Documents/htmls`），CLI 使用绝对路径或相对于项目根

## 4. 迁移到新电脑必须改的地方

按顺序执行，每一步都可独立验证。

### 4.1 放置目录

把整个 `paper-translate/` 目录放到 ReaNotes 仓库的 `.agents/skills/paper-translate/`。如需兼容 WorkBuddy，在工作区的 `.workbuddy/skills/` 下建立指向它的软链接。`mineru-extract` 保持在 `~/Documents/notes/.claude/skills/mineru-extract/`（独立于本项目）。

### 4.2 配 API 密钥

- **`paper-translate/.env`**（一行）：
  ```bash
  DEEPSEEK_API_KEY=sk-你的密钥
  ```
- **`mineru-extract/.env`**（一行）：
  ```bash
  MINERU_TOKEN=你的token
  ```
  （这是 mineru-extract 自己读的，本 skill 不需要改它。）

`.env` 不要写进任何 prompt 输出或 commit 信息。

### 4.3 检查 vault 路径默认值

`scripts/paper_translate.py` 会从 Skill 所在目录向上查找 ReaNotes 仓库：

```python
DEFAULT_REANOTES_ROOT = discover_reanotes_root(_SKILL_ROOT)
DEFAULT_OUT_ROOT = DEFAULT_REANOTES_ROOT / "output" / "translations"
DEFAULT_MINERU_SCRIPT = Path.home() / "Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py"
```

- 默认推荐把 Skill 放在 `reanotes/.agents/skills/paper-translate/`，脚本会自动找到仓库根目录。
- 旧的 `.workbuddy/skills/paper-translate` 可以保留为指向上述目录的兼容软链接。
- 如果输出目录不是 `reanotes/output/translations/`，用 `--out-root` 覆盖。
- 如果 ReaNotes 仓库不在默认位置，用 `--reanotes-root` 覆盖。
- `mineru-extract` 默认路径指向 `~/Documents/notes/.claude/skills/mineru-extract/`，否则也要改或者用 `--mineru-script` 覆盖。

### 4.4 （可选）换术语表

如果用户研究的不是 OVS / CV / NLP，把 `glossary/general-ovs-cv-nlp.md` 替换或加一份新文件，每次跑用 `--glossary <path>` 指向它。

## 5. 怎么跑

CLI 默认 cwd 是项目根（`/Users/mokaiche/Documents/htmls`）。**Agent 调用必须带 `--name`**，否则 arXiv 论文会卡在 `input()` 上。

```bash
# 单篇 arXiv
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --name "MyPaper" https://arxiv.org/abs/2504.09480

# 翻译后直接进入 ReaNotes（默认只接受 publishable）
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --name "my-paper" --publish https://arxiv.org/abs/2504.09480

# 发布已有翻译结果，不重新调用 MinerU / DeepSeek
python3 .agents/skills/paper-translate/scripts/publish_reanotes.py \
  --source https://arxiv.org/abs/2504.09480 \
  reanotes/output/translations/2026-07-19/my-paper

# 单个本地 PDF
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --name "mypdf" ~/Downloads/paper.pdf

# 批量（从 sources.txt 读，UTF-8，每行一个源，# 开头是注释）
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --sources-file sources.txt --non-interactive

# 干跑（不调 API，只打印计划）
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --dry-run --non-interactive https://arxiv.org/abs/2411.19331
```

## 6. 迁移后如何验证

按这 4 步走，逐步加压。

### Step 1 — 语法检查（无网络）

```bash
python3 -m py_compile .agents/skills/paper-translate/scripts/paper_translate.py
python3 -m py_compile .agents/skills/paper-translate/lib/*.py
```

应当静默通过。

### Step 2 — dry-run

```bash
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --dry-run --non-interactive https://arxiv.org/abs/2411.19331
```

应打印：

```
=== Plan (1 papers) ===
  out_root: .../htmls/reanotes/output/translations
  date_dir: .../htmls/reanotes/output/translations/<today>
  glossary: .../glossary/general-ovs-cv-nlp.md
  - [arxiv] https://arxiv.org/abs/2411.19331 → ...
```

如果报 `Missing DEEPSEEK_API_KEY`，说明 `.env` 没读到，回到 §4.2。

### Step 3 — MinerU 单独跑通

```bash
python3 ~/Documents/notes/.claude/skills/mineru-extract/scripts/mineru_extract_batch.py \
  --model pipeline --timeout 600 --out /tmp/mineru-test \
  https://arxiv.org/pdf/2411.19331
```

应在 `/tmp/mineru-test/<date>/<name>/` 下出现 `full.md` + `images/`。如果 MinerU 报 `Unauthorized` 或 `token invalid`，回到 §4.2 检查 `mineru-extract/.env`。

### Step 4 — 端到端

```bash
python3 .agents/skills/paper-translate/scripts/paper_translate.py \
  --name "smoketest" https://arxiv.org/abs/2411.19331
```

应当看到：

- 控制台：`done: Ns, in=N, out=N, cost=¥X.XXXX`
- 目录 `reanotes/output/translations/<today>/smoketest/` 出现 `full.md` + `images/` + `full_zh.md` + `translation_report.json`
- `translation_report.json` 的 `status` 为 `publishable`
- 如果状态为 `needs_review`，检查报告中的 `table_normalization`、`image_normalization` 和 `math_ocr`
- 同级 `summary.json` 记录这次 run 的 token 和费用

## 7. 输出契约

每篇论文一个目录：

```
{out_root}/{YYYY-MM-DD}/{name}/
├── full.md            # 英文 MinerU 输出
├── images/            # 提取的图片
├── full_zh.md         # 中文 DeepSeek 翻译（质量门禁通过后才写入）
└── translation_report.json # 占位符、公式保护和 API 完整性报告
```

`translation_report.json` 有三种状态：

- `publishable`：翻译及结构检查通过
- `needs_review`：译文已写出，但存在无法自动确认的表格、图片或公式风险
- `blocked`：翻译完整性失败，没有写出新的译文

`--publish` 的额外契约：

- 默认只发布 `publishable`；`needs_review` 必须显式传 `--publish-needs-review`
- 文献库只接收中文 `README.md`、`images/`、质量报告和元数据，不接收英文 `full.md`
- 自动更新 `docs/literature/papers.md`
- 自动运行 Prettier、lint、VuePress build，并检查生成页面是否缺失或包含 KaTeX、MathJax、占位符异常
- 发布结果和验证结果写入当次 `summary.json`

每次 run 还会产出聚合文件：

- `{out_root}/{YYYY-MM-DD}/summary.json` — 每篇论文的状态、token、费用
- `{out_root}/{YYYY-MM-DD}/usage_ledger.md` — 跨 run 追加式费用日志

## 8. 出错时去哪里查

- **整篇失败 / 卡死**：`summary.json` 看每篇的 `status` 和 `error` 字段
- **DeepSeek 报错**：`lib/deepseek_translate.py` 有 3 次重试（间隔 2s/4s/6s），超过后该篇标记 `failed`
- **译文被截断或占位符被改坏**：查看该论文目录的 `translation_report.json`；状态为 `blocked` 时不会写出新的 `full_zh.md`
- **表格、图片或公式告警**：报告状态为 `needs_review`；正文仍保留，发布前按报告逐项检查
- **重新翻译已有输出**：使用 `--force` 时默认复用现有 `full.md`；只有源 PDF 或 MinerU 结果需要刷新时才加 `--force-extract`
- **发布失败**：查看 `summary.json` 中每篇的 `publication` 和顶层 `publication_validation`
- **MinerU 失败**：错误是透传的，看 mineru-extract 那边的日志
- **arXiv 拿不到日期**：`scripts/paper_translate.py` 会回退到 arXiv ID 的 YYMM，文件夹名用 day=01

关键代码定位：

- `scripts/paper_translate.py` 顶部 — 默认输出、ReaNotes 和 MinerU 路径
- `scripts/paper_translate.py` 全文 — 编排、命名、subprocess 调用
- `lib/clean_markdown.py` — 清洗规则（HTML 表格、图片占位、参考文献/附录剥离、标题策略）
- `lib/deepseek_translate.py` — DeepSeek 客户端、token/费用

## 9. 已知边界（不要承诺超出以下能力）

- 不支持并发翻译（单进程串行）
- 失败论文没有 `--retry-failed` 自动重跑，需要手动重跑该源
- arXiv abs URL 会被自动改写成 `https://arxiv.org/pdf/{id}` 给 MinerU（HTML 解析不了）
- 单跑 arXiv 缺 `--name` 时会 `exit 2`，**Agent 必须传 `--name`**
- 不支持网页（非 arXiv）的源；那是 `content-extract` / `defuddle` 的活

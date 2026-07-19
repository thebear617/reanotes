# Paper Translate 使用说明

把论文 PDF 或 arXiv 地址解析、翻译并发布到 ReaNotes 文献库。

完整流程：

```text
MinerU 解析 → DeepSeek 翻译 → 表格/图片/公式检查
→ 写入 ReaNotes → 更新文献索引 → lint/build 验证
```

## 使用前准备

需要配置两个密钥：

- DeepSeek：写入本目录的 `.env`

  ```text
  DEEPSEEK_API_KEY=你的密钥
  ```

- MinerU：由 `mineru-extract` Skill 自己的 `.env` 管理。

本机还需要能够运行 `python3` 和 `pnpm`。

## 翻译并发布一篇论文

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "论文目录名" \
  --publish \
  https://arxiv.org/abs/论文编号
```

目录名建议使用小写英文和短横线，例如：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "attention-is-all-you-need" \
  --publish \
  https://arxiv.org/abs/1706.03762
```

命令会自动调用 MinerU 和 DeepSeek API。退出码为 `0` 表示翻译、发布和站点构建全部通过。

## 翻译本地 PDF

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "论文目录名" \
  --publish \
  /绝对路径/paper.pdf
```

## 只预览执行计划

不会调用 MinerU 或 DeepSeek，也不会产生 API 费用：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "论文目录名" \
  --publish \
  --dry-run \
  https://arxiv.org/abs/论文编号
```

## 发布已有译文

已有 `full_zh.md` 和 `translation_report.json` 时，不必重新调用 API：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/publish_reanotes.py \
  --source https://arxiv.org/abs/论文编号 \
  /绝对路径/翻译结果目录
```

## 质量状态

- `publishable`：自动发布到 ReaNotes。
- `needs_review`：译文已生成，但发现可疑公式、表格或图片，默认停止发布。
- `blocked`：翻译完整性检查失败，不生成新的可发布译文。

人工检查确认 `needs_review` 没有问题后，可以显式允许发布：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/publish_reanotes.py \
  --allow-needs-review \
  --source https://arxiv.org/abs/论文编号 \
  /绝对路径/翻译结果目录
```

## 更新已经发布的论文

默认不会覆盖现有文献目录。确定需要替换时使用：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "论文目录名" \
  --publish \
  --publish-force \
  https://arxiv.org/abs/论文编号
```

翻译工作区保留英文 `full.md`；公开文献库只接收中文正文、图片、质量报告和来源元数据。

重新翻译时，脚本默认复用已经存在的 MinerU `full.md`，避免重复支付解析成本：

```bash
python3 /Users/mokaiche/Documents/htmls/reanotes/.agents/skills/paper-translate/scripts/paper_translate.py \
  --name "论文目录名" \
  --force \
  --publish \
  https://arxiv.org/abs/论文编号
```

只有确定需要重新解析 PDF 时才额外使用 `--force-extract`。

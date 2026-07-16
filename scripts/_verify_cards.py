#!/usr/bin/env python3
"""临时校验：生成的卡片 HTML 与原 replearning.js 内联 body 逐卡比对。"""
import json
import re
from pathlib import Path

ROOT = Path("/Users/mokaiche/Documents/htmls/reanotes")
SRC = ROOT / "js/boards/replearning.js"
GEN = ROOT / "js/boards/replearning.cards.js"

CARD_RE = re.compile(
    r"icon:\s*'([^']*)'\s*,\s*title:\s*'([^']*)'\s*,\s*tags:\s*\[([^\]]*)\]\s*,\s*"
    r"expanded:\s*(\w+)\s*,\s*body:\s*`(.*?)`",
    re.DOTALL,
)
PAGE_RE = re.compile(r"CONTENT\['(\w[\w-]*)'\]\s*=\s*\{")

def norm(s):
    s = re.sub(r">\s+<", "><", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

# 原 body
src = SRC.read_text(encoding="utf-8")
orig = {}  # page -> {title: body}
page_blocks = list(PAGE_RE.finditer(src))
for idx, pb in enumerate(page_blocks):
    page = pb.group(1)
    start = pb.end()
    end = page_blocks[idx + 1].start() if idx + 1 < len(page_blocks) else len(src)
    region = src[start:end]
    cm = re.search(r"cards:\s*\[(.*?)\]\s*\n\};", region, re.DOTALL)
    if not cm:
        continue
    for m in CARD_RE.finditer(cm.group(1)):
        title = m.group(2)
        orig.setdefault(page, {})[title] = m.group(5)

# 生成 body
gen_text = GEN.read_text(encoding="utf-8")
i = gen_text.index("window.REPLEARNING_CARDS")
j = gen_text.index("{", i)
k = gen_text.rfind("}")
gen = json.loads(gen_text[j : k + 1])

total = 0
mism = 0
for page, cards in gen.items():
    for card in cards:
        total += 1
        title = card["title"]
        new_body = card["body"]
        old_body = orig.get(page, {}).get(title)
        if old_body is None:
            print(f"[{page}] ⚠️ 原文件找不到匹配标题: {title}")
            mism += 1
            continue
        if norm(old_body) != norm(new_body):
            mism += 1
            print(f"\n=== MISMATCH [{page}] {title} ===")
            print("ORIG:", norm(old_body)[:600])
            print("NEW :", norm(new_body)[:600])

print(f"\n总计 {total} 张，差异 {mism} 张")

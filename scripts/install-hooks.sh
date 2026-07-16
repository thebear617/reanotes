#!/bin/sh
set -eu

ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

if ! command -v pnpm >/dev/null 2>&1; then
  echo "未找到 pnpm，请先安装 pnpm 10。" >&2
  exit 1
fi

pnpm install
chmod +x .husky/pre-commit

echo "Git hooks 已启用：$(git config --get core.hooksPath)/pre-commit"

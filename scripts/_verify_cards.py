#!/usr/bin/env python3
"""兼容入口：校验 Markdown 编译生成物是否与内容目录一致。"""

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent


def main():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build-cards.py"), "--check"],
        cwd=ROOT,
        check=False,
    )
    raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

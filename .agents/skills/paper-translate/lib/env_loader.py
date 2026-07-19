"""Load KEY=VAL pairs from a .env file into os.environ.

Mirrors the dotenv pattern used by mineru-extract: read line-by-line, skip
comments and blank lines, do not override existing env vars.
"""

from __future__ import annotations

import os
import shlex
from pathlib import Path


def load_dotenv(path: Path) -> bool:
    """Load a .env file. Returns True if the file existed and was read."""
    if not path.exists():
        return False
    for token in shlex.split(path.read_text(encoding="utf-8")):
        if "=" not in token:
            continue
        key, _, value = token.partition("=")
        if key and key not in os.environ:
            os.environ[key] = value
    return True


def load_skill_env(skill_root: Path) -> list[Path]:
    """Load `.env` from skill root and script dir, in that order.

    Returns the list of paths that were successfully read.
    """
    loaded: list[Path] = []
    if load_dotenv(skill_root / ".env"):
        loaded.append(skill_root / ".env")
    scripts_env = skill_root / "scripts" / ".env"
    if load_dotenv(scripts_env):
        loaded.append(scripts_env)
    return loaded

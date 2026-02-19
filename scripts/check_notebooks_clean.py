#!/usr/bin/env python3
"""Fail if notebooks contain execution outputs/counts."""

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"


def iter_notebooks() -> list[Path]:
    return sorted(
        p
        for p in LESSONS_DIR.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in p.parts
    )


def is_enforced_notebook(path: Path) -> bool:
    rel = path.relative_to(REPO_ROOT).as_posix()
    return rel.startswith("lessons/2026/") or rel.startswith("lessons/classic/")


def main() -> int:
    offenders: list[str] = []
    for notebook in iter_notebooks():
        if not is_enforced_notebook(notebook):
            continue
        data = json.loads(notebook.read_text(encoding="utf-8"))
        for idx, cell in enumerate(data.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue

            has_outputs = bool(cell.get("outputs"))
            has_count = cell.get("execution_count") is not None
            if has_outputs or has_count:
                rel = notebook.relative_to(REPO_ROOT).as_posix()
                offenders.append(f"{rel}#cell{idx}")

    if offenders:
        print("Notebook cleanliness check failed. Clear outputs before commit:")
        for offender in offenders:
            print(f"  - {offender}")
        print("Run: make notebooks-clean")
        return 1

    print("Notebook cleanliness check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Strip notebook outputs and execution counts for clean git diffs."""

from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"


def iter_notebooks() -> list[Path]:
    return sorted(
        p
        for p in LESSONS_DIR.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in p.parts
    )


def clean_notebook(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = False

    for cell in data.get("cells", []):
        if cell.get("cell_type") != "code":
            continue

        if cell.get("execution_count") is not None:
            cell["execution_count"] = None
            changed = True

        if cell.get("outputs"):
            cell["outputs"] = []
            changed = True

    if changed:
        path.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def main() -> int:
    notebooks = iter_notebooks()
    changed = [p for p in notebooks if clean_notebook(p)]
    print(f"Scanned: {len(notebooks)} notebooks")
    print(f"Cleaned: {len(changed)} notebooks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

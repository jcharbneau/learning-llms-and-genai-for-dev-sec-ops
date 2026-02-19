#!/usr/bin/env python3
"""Validate Launcher and index-notebook click-through navigation contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"
LAUNCHER_YAML = REPO_ROOT / "jupyter_app_launcher" / "jp_app_launcher_lessons.yaml"

HOME_INDEX = LESSONS_DIR / "00-home.ipynb"
ECOSYSTEM_INDEX = LESSONS_DIR / "2026" / "00-ecosystem-index.ipynb"
TRACK_INDEXES = {
    "langchain": LESSONS_DIR / "2026" / "langchain" / "00-modern-track-index.ipynb",
    "litellm": LESSONS_DIR / "2026" / "litellm" / "00-track-index.ipynb",
    "llamaindex": LESSONS_DIR / "2026" / "llamaindex" / "00-track-index.ipynb",
    "dspy": LESSONS_DIR / "2026" / "dspy" / "00-track-index.ipynb",
    "agent-clis": LESSONS_DIR / "2026" / "agent-clis" / "00-track-index.ipynb",
    "openclaw": LESSONS_DIR / "2026" / "openclaw" / "00-track-index.ipynb",
}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+\.ipynb)\)")
PATH_RE = re.compile(r"^\s*path:\s*(.+?)\s*$")


def _read_markdown(notebook: Path) -> str:
    data = json.loads(notebook.read_text(encoding="utf-8"))
    return "\n".join(
        "".join(cell.get("source", []))
        for cell in data.get("cells", [])
        if cell.get("cell_type") == "markdown"
    )


def _extract_notebook_links(notebook: Path) -> set[str]:
    markdown = _read_markdown(notebook)
    return {m.group(1).strip() for m in LINK_RE.finditer(markdown)}


def _resolve_link(base_notebook: Path, link: str) -> Path:
    return (base_notebook.parent / link).resolve()


def _expected_lessons(track: str, index_path: Path) -> set[str]:
    if track == "langchain":
        return {
            p.name
            for p in index_path.parent.glob("*.ipynb")
            if p.name != "00-modern-track-index.ipynb"
        }
    return {
        p.name
        for p in index_path.parent.glob("0[1-9]-*.ipynb")
        if p.name != "00-track-index.ipynb"
    }


def _launcher_paths() -> list[str]:
    paths: list[str] = []
    for line in LAUNCHER_YAML.read_text(encoding="utf-8").splitlines():
        match = PATH_RE.match(line)
        if match:
            paths.append(match.group(1))
    return paths


def validate() -> list[str]:
    errors: list[str] = []

    if not HOME_INDEX.exists():
        errors.append("missing lessons home index: lessons/00-home.ipynb")
    if not ECOSYSTEM_INDEX.exists():
        errors.append("missing ecosystem index: lessons/2026/00-ecosystem-index.ipynb")

    if LAUNCHER_YAML.exists():
        for raw in _launcher_paths():
            path = (LESSONS_DIR / raw).resolve()
            if not path.exists():
                errors.append(f"launcher path is missing: {raw}")
    else:
        errors.append("missing launcher config: jupyter_app_launcher/jp_app_launcher_lessons.yaml")

    index_notebooks = [HOME_INDEX, ECOSYSTEM_INDEX] + list(TRACK_INDEXES.values())
    for notebook in index_notebooks:
        if not notebook.exists():
            continue
        rel = notebook.relative_to(REPO_ROOT).as_posix()
        links = _extract_notebook_links(notebook)
        if not links:
            errors.append(f"{rel}: no notebook links found")
            continue
        for link in links:
            target = _resolve_link(notebook, link)
            if not target.exists():
                errors.append(f"{rel}: broken notebook link: {link}")

    for track, index_path in TRACK_INDEXES.items():
        if not index_path.exists():
            continue
        rel = index_path.relative_to(REPO_ROOT).as_posix()
        links = {Path(link).name for link in _extract_notebook_links(index_path)}
        expected = _expected_lessons(track, index_path)
        missing = sorted(expected - links)
        if missing:
            errors.append(f"{rel}: missing lesson links: {missing}")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Navigation contract check failed:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("Navigation contract check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Validate 2026 curriculum notebooks against lesson contract requirements."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TRACKS = ("litellm", "llamaindex", "dspy", "agent-clis", "openclaw")
REQUIRED_HEADINGS = (
    "What This Lesson Is",
    "Scientific Lens",
    "How It Works",
    "Code Walkthrough",
    "Applied Labs",
    "Validation Checklist",
    "Further Reading",
)


def lesson_notebooks() -> list[Path]:
    paths: list[Path] = []
    for track in TRACKS:
        paths.extend(sorted((REPO_ROOT / "lessons" / "2026" / track).glob("0[1-8]-*.ipynb")))
    # LangChain modern track uses domain-prefixed filenames instead of 01..08 naming.
    paths.extend(
        sorted(
            p
            for p in (REPO_ROOT / "lessons" / "2026" / "langchain").glob("*.ipynb")
            if p.name != "00-modern-track-index.ipynb"
        )
    )
    return paths


def _extract_section_block(markdown: str, start: str, end: str) -> str:
    if start not in markdown or end not in markdown:
        return ""
    return markdown.split(start, 1)[1].split(end, 1)[0].strip()


def validate() -> list[str]:
    errors: list[str] = []
    lab_hashes: dict[str, list[str]] = {}
    check_hashes: dict[str, list[str]] = {}

    for path in lesson_notebooks():
        rel = path.relative_to(REPO_ROOT).as_posix()
        data = json.loads(path.read_text(encoding="utf-8"))

        markdown = "\n".join(
            "".join(c.get("source", []))
            for c in data.get("cells", [])
            if c.get("cell_type") == "markdown"
        )
        code = "\n".join(
            "".join(c.get("source", []))
            for c in data.get("cells", [])
            if c.get("cell_type") == "code"
        )

        for heading in REQUIRED_HEADINGS:
            if heading not in markdown:
                errors.append(f"{rel}: missing heading '{heading}'")

        for required_lens in ("- Concept:", "- Measure:", "- Validity Limit:"):
            if required_lens not in markdown:
                errors.append(f"{rel}: missing scientific lens field '{required_lens}'")

        if "# Deterministic Demo" not in code:
            errors.append(f"{rel}: missing deterministic demo code marker")
        if "# Live Demo" not in code:
            errors.append(f"{rel}: missing live demo code marker")

        labs = _extract_section_block(markdown, "## Applied Labs", "## Validation Checklist")
        checks = _extract_section_block(markdown, "## Validation Checklist", "## Further Reading")

        if not labs:
            errors.append(f"{rel}: empty Applied Labs section")
        if not checks:
            errors.append(f"{rel}: empty Validation Checklist section")

        lab_key = hashlib.sha1(labs.encode("utf-8")).hexdigest()
        check_key = hashlib.sha1(checks.encode("utf-8")).hexdigest()
        lab_hashes.setdefault(lab_key, []).append(rel)
        check_hashes.setdefault(check_key, []).append(rel)

    for group in lab_hashes.values():
        if len(group) > 1:
            errors.append(f"duplicate Applied Labs block across notebooks: {group}")
    for group in check_hashes.values():
        if len(group) > 1:
            errors.append(f"duplicate Validation Checklist block across notebooks: {group}")

    return errors


def main() -> int:
    errs = validate()
    if errs:
        print("Curriculum contract check failed:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("Curriculum contract check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

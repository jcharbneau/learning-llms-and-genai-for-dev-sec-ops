#!/usr/bin/env python3
"""Execute Jupyter notebooks end-to-end with provider-aware preflight checks."""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"
DEFAULT_OUTPUT_DIR = REPO_ROOT / ".artifacts" / "executed-notebooks"
DEFAULT_OLLAMA_ALLOWED_MODELS = (
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:7b",
)


@dataclass
class NotebookRequirements:
    needs_network: bool = False
    needs_openai: bool = False
    needs_azure: bool = False
    needs_langsmith: bool = False
    needs_ollama: bool = False
    ollama_models: set[str] = field(default_factory=set)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-network",
        action="store_true",
        help="Execute notebooks that appear to require network/API access.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        default=[],
        help="Glob pattern(s) relative to repo root (default: lessons/**/*.ipynb).",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Per-cell timeout in seconds (default: 300).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directory for executed notebook artifacts (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first execution failure.",
    )
    return parser.parse_args()


def discover_notebooks(patterns: list[str]) -> list[Path]:
    if not patterns:
        patterns = ["lessons/**/*.ipynb"]

    notebooks: set[Path] = set()
    for path in LESSONS_DIR.rglob("*.ipynb"):
        if ".ipynb_checkpoints" in path.parts:
            continue
        if path.name.startswith("Untitled"):
            continue

        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(fnmatch.fnmatch(rel, p) for p in patterns):
            notebooks.add(path)

    return sorted(notebooks)


def resolve_cmd(candidates: list[list[str]]) -> list[str] | None:
    for candidate in candidates:
        try:
            proc = subprocess.run([*candidate, "--version"], capture_output=True, text=True)
        except FileNotFoundError:
            continue
        if proc.returncode == 0:
            return candidate
    return None


def resolve_jupyter_cmd() -> list[str] | None:
    return resolve_cmd([[sys.executable, "-m", "jupyter"], ["jupyter"]])


def resolve_ollama_cmd() -> list[str] | None:
    return resolve_cmd([["ollama"]])


def inspect_notebook_requirements(path: Path) -> NotebookRequirements:
    text = path.read_text(encoding="utf-8")
    req = NotebookRequirements()

    req.needs_azure = any(
        marker in text
        for marker in (
            "AZURE_OPENAI",
            "AzureChatOpenAI",
            "AZURE_VISION_DEPLOYMENT",
        )
    )
    req.needs_openai = bool(
        re.search(r"\b(OpenAI\(|ChatOpenAI\(|OpenAIEmbeddings\()", text)
    ) and not req.needs_azure
    req.needs_langsmith = "langsmith" in text.lower() or "hub.pull(" in text
    req.needs_ollama = any(
        marker in text for marker in ("ChatOllama", "OllamaEmbeddings", "ollama")
    )
    req.needs_network = (
        req.needs_openai
        or req.needs_azure
        or req.needs_langsmith
        or req.needs_ollama
        or any(
            marker in text
            for marker in ("duckduckgo", "RequestsWrapper", "create_openapi_agent")
        )
    )

    if req.needs_ollama:
        model_patterns = (
            r"ChatOllama\([^\)]*model\s*=\s*[\"']([^\"']+)",
            r"OllamaEmbeddings\([^\)]*model\s*=\s*[\"']([^\"']+)",
        )
        for pattern in model_patterns:
            for match in re.findall(pattern, text, flags=re.DOTALL):
                req.ollama_models.add(match.strip())

    return req


def parse_ollama_allowed_models() -> set[str]:
    raw = os.getenv("OLLAMA_ALLOWED_MODELS")
    if raw:
        return {item.strip() for item in raw.split(",") if item.strip()}
    return set(DEFAULT_OLLAMA_ALLOWED_MODELS)


def parse_ollama_models_list(ollama_cmd: list[str]) -> set[str]:
    proc = subprocess.run([*ollama_cmd, "list"], capture_output=True, text=True)
    if proc.returncode != 0:
        return set()

    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if len(lines) <= 1:
        return set()

    models: set[str] = set()
    for line in lines[1:]:
        models.add(line.split()[0])
    return models


def preflight_skip_reason(
    req: NotebookRequirements,
    include_network: bool,
    ollama_cmd: list[str] | None,
    ollama_models_available: set[str] | None,
) -> str | None:
    if not include_network and req.needs_network:
        return "network/API markers detected (use --include-network to run)"

    if req.needs_openai and not os.getenv("OPENAI_API_KEY"):
        return "OPENAI_API_KEY is not set"

    if req.needs_azure:
        missing = [
            key
            for key in (
                "AZURE_OPENAI_API_KEY",
                "AZURE_OPENAI_ENDPOINT",
                "AZURE_VISION_DEPLOYMENT",
            )
            if not os.getenv(key)
        ]
        if missing:
            return f"Azure config missing: {', '.join(missing)}"

    if req.needs_langsmith and not os.getenv("LANGCHAIN_API_KEY"):
        return "LANGCHAIN_API_KEY is not set (required for LangSmith/Hub notebooks)"

    if req.needs_ollama:
        if ollama_cmd is None:
            return "ollama command not available"

        allowed = parse_ollama_allowed_models()
        if req.ollama_models:
            disallowed = sorted(model for model in req.ollama_models if model not in allowed)
            if disallowed:
                return (
                    "Ollama models not in allowed small-model set: "
                    + ", ".join(disallowed)
                    + f" (allowed: {', '.join(sorted(allowed))})"
                )

            available = ollama_models_available or set()
            missing = sorted(model for model in req.ollama_models if model not in available)
            if missing:
                return "Ollama models not installed locally: " + ", ".join(missing)

    return None


def runtime_skip_reason(error_text: str) -> str | None:
    checks = (
        ("OPENAI_API_KEY", "OPENAI_API_KEY missing at runtime"),
        ("AZURE_OPENAI_API_KEY", "AZURE_OPENAI_API_KEY missing at runtime"),
        ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_ENDPOINT missing at runtime"),
        ("AZURE_VISION_DEPLOYMENT", "AZURE_VISION_DEPLOYMENT missing at runtime"),
    )
    lowered = error_text.lower()
    for marker, reason in checks:
        if marker.lower() in lowered:
            return reason
    return None


def summarize_error(error_text: str, max_lines: int = 30) -> str:
    lines = [line for line in error_text.splitlines() if line.strip()]
    if not lines:
        return "<no error details>"
    tail = lines[-max_lines:]
    return "\n".join(tail)


def execute_notebook(
    path: Path, output_dir: Path, timeout: int, jupyter_cmd: list[str]
) -> tuple[bool, str]:
    rel = path.relative_to(REPO_ROOT)
    target_dir = output_dir / rel.parent
    target_dir.mkdir(parents=True, exist_ok=True)

    error_dir = output_dir / "_errors"
    error_dir.mkdir(parents=True, exist_ok=True)
    err_path = error_dir / f"{rel.as_posix().replace('/', '__')}.log"

    cmd = [
        *jupyter_cmd,
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(path),
        f"--ExecutePreprocessor.timeout={timeout}",
        "--output",
        path.name,
        "--output-dir",
        str(target_dir),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode == 0:
        return True, ""

    stderr = (proc.stderr or "").strip()
    stdout = (proc.stdout or "").strip()
    detail = stderr if stderr else stdout
    err_path.write_text(detail, encoding="utf-8")
    summary = summarize_error(detail)
    return False, f"{summary}\n[full log] {err_path}"


def main() -> int:
    args = parse_args()
    jupyter_cmd = resolve_jupyter_cmd()
    if jupyter_cmd is None:
        print(
            "jupyter is not available. Install notebook dependencies locally "
            "or run this command inside the docker notebooks container."
        )
        return 2

    notebooks = discover_notebooks(args.pattern)
    if not notebooks:
        print("No notebooks matched the provided patterns.")
        return 1

    output_dir = Path(args.output_dir)
    ollama_cmd = resolve_ollama_cmd()
    ollama_models_available = (
        parse_ollama_models_list(ollama_cmd) if ollama_cmd is not None else None
    )

    passed: list[Path] = []
    failed: list[tuple[Path, str]] = []
    skipped: list[tuple[Path, str]] = []

    for notebook in notebooks:
        req = inspect_notebook_requirements(notebook)
        skip_reason = preflight_skip_reason(
            req,
            include_network=args.include_network,
            ollama_cmd=ollama_cmd,
            ollama_models_available=ollama_models_available,
        )
        if skip_reason:
            skipped.append((notebook, skip_reason))
            print(f"SKIP {notebook.relative_to(REPO_ROOT)} ({skip_reason})")
            continue

        print(f"RUN  {notebook.relative_to(REPO_ROOT)}")
        ok, detail = execute_notebook(
            notebook,
            output_dir=output_dir,
            timeout=args.timeout,
            jupyter_cmd=jupyter_cmd,
        )
        if ok:
            passed.append(notebook)
            continue

        runtime_skip = runtime_skip_reason(detail)
        if runtime_skip:
            skipped.append((notebook, runtime_skip))
            print(f"SKIP {notebook.relative_to(REPO_ROOT)} ({runtime_skip})")
            continue

        failed.append((notebook, detail))
        print(f"FAIL {notebook.relative_to(REPO_ROOT)}: {detail}")
        if args.fail_fast:
            break

    print("\nNotebook E2E summary")
    print(f"  passed:  {len(passed)}")
    print(f"  failed:  {len(failed)}")
    print(f"  skipped: {len(skipped)}")
    print(f"  artifacts: {output_dir}")

    if skipped:
        print("\nSkipped:")
        for notebook, reason in skipped:
            print(f"  - {notebook.relative_to(REPO_ROOT)}: {reason}")

    if failed:
        print("\nFailures:")
        for notebook, error in failed:
            print(f"  - {notebook.relative_to(REPO_ROOT)}")
            print(f"    {error}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

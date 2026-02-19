import json
import importlib.util
import py_compile
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _iter_notebooks() -> list[Path]:
    return sorted(
        p
        for p in LESSONS_DIR.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in p.parts
    )


def _normalize_source(source: object) -> str:
    if isinstance(source, list):
        return "".join(source)
    if isinstance(source, str):
        return source
    return ""


def _sanitize_for_compile(code: str) -> str:
    lines = code.splitlines()
    if any(line.strip().startswith("%%") for line in lines):
        return ""

    kept: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("%") or stripped.startswith("!"):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


class RepoSmokeTests(unittest.TestCase):
    def test_navigation_contract(self) -> None:
        module_path = SCRIPTS_DIR / "check_navigation_contract.py"
        spec = importlib.util.spec_from_file_location("check_navigation_contract", module_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        errors = module.validate()
        self.assertEqual([], errors, f"Navigation contract violations: {errors}")

    def test_classic_notebooks_live_under_lessons_classic(self) -> None:
        notebooks = _iter_notebooks()
        classic_named = [p for p in notebooks if p.name.endswith("-classic.ipynb")]
        self.assertGreater(len(classic_named), 0, "No classic notebooks found.")

        for notebook in classic_named:
            rel = notebook.relative_to(REPO_ROOT).as_posix()
            with self.subTest(notebook=rel):
                self.assertTrue(
                    rel.startswith("lessons/classic/"),
                    "Classic notebooks must live under lessons/classic/.",
                )

    def test_lessons_classic_notebooks_have_preflight_block(self) -> None:
        notebooks = sorted(
            p
            for p in (LESSONS_DIR / "classic").rglob("*.ipynb")
            if ".ipynb_checkpoints" not in p.parts and p.name != "00-classic-track-index.ipynb"
        )
        self.assertGreater(len(notebooks), 0, "No notebooks found under lessons/classic.")

        for notebook in notebooks:
            rel = notebook.relative_to(REPO_ROOT).as_posix()
            data = json.loads(notebook.read_text(encoding="utf-8"))
            cells = data.get("cells", [])
            self.assertGreaterEqual(len(cells), 2, f"{rel} should have preflight markdown+code cells.")

            first_md = _normalize_source(cells[0].get("source", "")) if cells else ""
            first_code = _normalize_source(cells[1].get("source", "")) if len(cells) > 1 else ""
            with self.subTest(notebook=rel):
                self.assertIn("Classic Environment Preflight", first_md)
                self.assertIn("CLASSIC=1 make notebooks-build", first_code)
                self.assertIn("import langchain", first_code)

    def test_notebooks_are_valid_json_and_have_cells(self) -> None:
        notebooks = _iter_notebooks()
        self.assertGreater(len(notebooks), 0, "No notebooks found under lessons/")

        for notebook in notebooks:
            with self.subTest(notebook=str(notebook)):
                data = json.loads(notebook.read_text(encoding="utf-8"))
                self.assertIn("cells", data)
                self.assertIsInstance(data["cells"], list)
                self.assertGreater(len(data["cells"]), 0)

    def test_notebook_code_cells_compile_after_sanitizing_magics(self) -> None:
        notebooks = _iter_notebooks()

        for notebook in notebooks:
            data = json.loads(notebook.read_text(encoding="utf-8"))
            for idx, cell in enumerate(data.get("cells", [])):
                if cell.get("cell_type") != "code":
                    continue

                source = _normalize_source(cell.get("source", ""))
                sanitized = _sanitize_for_compile(source)
                if not sanitized:
                    continue

                with self.subTest(notebook=str(notebook), cell_index=idx):
                    compile(sanitized, f"{notebook}#cell{idx}", "exec")

    def test_python_scripts_compile(self) -> None:
        scripts = sorted(LESSONS_DIR.rglob("*.py"))
        self.assertGreater(len(scripts), 0, "No python scripts found under lessons/")

        for script in scripts:
            with self.subTest(script=str(script)):
                py_compile.compile(str(script), doraise=True)

    def test_repo_scripts_compile(self) -> None:
        scripts = sorted(SCRIPTS_DIR.rglob("*.py"))
        self.assertGreater(len(scripts), 0, "No python scripts found under scripts/")

        for script in scripts:
            with self.subTest(script=str(script)):
                py_compile.compile(str(script), doraise=True)

    def test_notebooks_avoid_deprecated_run_calls(self) -> None:
        notebooks = _iter_notebooks()
        deprecated = re.compile(r"(?<!subprocess)\.run\(")

        for notebook in notebooks:
            data = json.loads(notebook.read_text(encoding="utf-8"))
            for idx, cell in enumerate(data.get("cells", [])):
                if cell.get("cell_type") != "code":
                    continue

                source = _normalize_source(cell.get("source", ""))
                with self.subTest(notebook=str(notebook), cell_index=idx):
                    self.assertIsNone(
                        deprecated.search(source),
                        "Found deprecated .run(...) pattern; use invoke(...) instead.",
                    )

    def test_ollama_notebooks_require_explicit_base_url(self) -> None:
        notebooks = _iter_notebooks()

        for notebook in notebooks:
            data = json.loads(notebook.read_text(encoding="utf-8"))
            for idx, cell in enumerate(data.get("cells", [])):
                if cell.get("cell_type") != "code":
                    continue

                source = _normalize_source(cell.get("source", ""))
                if "ChatOllama(" in source:
                    with self.subTest(notebook=str(notebook), cell_index=idx, type="ChatOllama"):
                        self.assertIn(
                            "base_url=",
                            source,
                            "ChatOllama must set base_url from OLLAMA_BASE_URL for Docker host routing.",
                        )
                if "OllamaEmbeddings(" in source:
                    with self.subTest(notebook=str(notebook), cell_index=idx, type="OllamaEmbeddings"):
                        self.assertIn(
                            "base_url=",
                            source,
                            "OllamaEmbeddings must set base_url from OLLAMA_BASE_URL for Docker host routing.",
                        )


if __name__ == "__main__":
    unittest.main()

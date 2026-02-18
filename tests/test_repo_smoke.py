import json
import py_compile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = REPO_ROOT / "lessons"


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
    def test_notebooks_are_valid_json_and_have_cells(self) -> None:
        notebooks = sorted(LESSONS_DIR.rglob("*.ipynb"))
        self.assertGreater(len(notebooks), 0, "No notebooks found under lessons/")

        for notebook in notebooks:
            with self.subTest(notebook=str(notebook)):
                data = json.loads(notebook.read_text(encoding="utf-8"))
                self.assertIn("cells", data)
                self.assertIsInstance(data["cells"], list)
                self.assertGreater(len(data["cells"]), 0)

    def test_notebook_code_cells_compile_after_sanitizing_magics(self) -> None:
        notebooks = sorted(LESSONS_DIR.rglob("*.ipynb"))

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


if __name__ == "__main__":
    unittest.main()

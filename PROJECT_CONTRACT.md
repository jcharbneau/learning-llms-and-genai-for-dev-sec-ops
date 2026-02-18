# PROJECT CONTRACT

## Goal
- Keep this repository runnable as a notebook-first learning project with reliable local and Docker workflows.
- Prefer small, targeted changes that improve lesson stability and reproducibility.

## Technology Baseline
- Python: `3.12` (`.python-version`)
- Runtime deps: `requirements-notebooks.txt`
- Notebook runtime: JupyterLab in Docker (`Dockerfile`, `compose.yaml`, `Makefile`)
- Key LLM integrations:
  - OpenAI (`langchain-openai`, `openai`)
  - Azure OpenAI (vision lesson)
  - Ollama (local models, host-routed from Docker via `OLLAMA_BASE_URL`)
- Data/vector tooling: `chromadb`, `langchain-community`

## Change Standards
- Keep diffs minimal and focused; avoid unrelated refactors.
- Prefer forward-compatible APIs (current `langchain`/`langchain-openai` imports and `invoke` patterns).
- Do not hardcode secrets or real keys.
- Prefer graceful handling for optional dependencies/services:
  - Skip cleanly with clear message if env vars/tools are missing.
  - Do not crash entire notebook test runs for missing optional providers.
- For local-model lessons, default to smaller Ollama models.

## Notebook Standards
- Notebook cells must be valid JSON and syntactically valid Python.
- Avoid brittle environment assumptions (`__file__`, unavailable CLIs, legacy imports).
- Handle expected demo failures explicitly (e.g., `try/except` around intentionally malformed parser examples).
- If a lesson depends on external services, include prerequisite checks in the notebook.

## Testing Standards
- Required before completion:
  1. `make test-smoke`
  2. `make test-e2e-notebooks-full`
- `test-e2e-notebooks-full` is considered healthy when:
  - `failed: 0`
  - skips are only explicit prerequisite skips (e.g. missing `LANGCHAIN_API_KEY`, Azure vars, or Ollama access).
- Use generated error logs for diagnosis:
  - `.artifacts/executed-notebooks/_errors/*.log`

## Environment Expectations
- Docker-to-host Ollama routing:
  - `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- Common provider env vars:
  - `OPENAI_API_KEY`
  - `LANGCHAIN_API_KEY` (LangSmith/Hub lessons)
  - `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_VISION_DEPLOYMENT`

## Definition Of Done
- Changes are scoped and documented.
- Smoke tests pass.
- Full notebook E2E run has zero failures (with graceful prerequisite skips).
- README and/or lesson notes updated when workflow behavior changes.

# Learning llms and genai for Dev,Sec,Ops
## What is this repo about ?
This repo aims to structure various information about LLMs and GenAi in a **lesson narrative** that is easily understood by traditional software engineering. It highlights the aspects you need to understand from development, operations and security perspective. While there is a lot of material out there, I found myself explaining the same things over and over again and developed a narrative.

The lessons are mainly based on the [Langchain](https://github.com/langchain-ai/langchain) framework and expects a bit of familiarity with the Python programming language. Many examples have been borrowed from documentation pages and attribution is given where possible. Kudos to Langchain for collection so much material !

## Lessons overview
### Tracks
- `lessons/<area>/*-classic.ipynb`: legacy/classic LangChain-era demonstrations kept for comparison and evaluation
- `lessons/2026/langchain/*.ipynb`: modern 2026 equivalents using current Runnable/LCEL-style patterns
- `lessons/2026/<batch>/*.ipynb`: new ecosystem lessons grouped by 2026 topic batches (LiteLLM, LlamaIndex, DSPy, agent CLIs, ...)

### Developer
- Calling a simple LLM using OpenAI
- Looking at debugging in Langchain
- Chatting with OpenAI as model
- Using prompt templates
- Use of Docloader to read your local files and prepare them for the LLM
- Explain the calculation and use of embeddings
- Understand how splitting and chunking is important
- Loading embeddings and documents in a vector database
- Use a chain for Questions and Answers to implement the RAG pattern (Retrieval Augmented Generation)
- Show the use of OpenAI documentation to have the llm generate calls to find realtime information
- Implement an Agent and provide it with tools to get more realtime information

## Operations
- Find out how much tokens you are using and the cost
- How to cache your calls to an LLM using exact matching or embeddings
- How to cache the calculation of embeddings and run the calculation locally
- Run your own local LLM (using Ollama)
- Track your calls and log them to a file (using a callback handler)
- Impose output structure (as JSON) and have the LLM retry if it's not correct

## Security
- Explain the OWASP top 10 for LLMS
- Show how simple prompt injection works and some mitigation strategies
- How to detect prompt injection using a 3rd party model from Hugginface
- Detect project injection by using a prompt
- Check the answer llms provide and reflect if it ok
- Use a huggingface model to detect if an LLM output was toxic
- Show a simple prompt for asking the llm's opinon on Kubernetes and Trivy vulnerabilities

Jump right in <https://github.com/jedi4ever/learning-llms-and-genai-for-dev-sec-ops/tree/main/lessons>
For modernized equivalents, start at `lessons/2026/langchain/00-modern-track-index.ipynb`.
For 2026 ecosystem batches (LangChain + non-LangChain), start at `lessons/2026/00-ecosystem-index.ipynb`.
More to come !

## History of this repo
- The initial lessons structure was formed during a [GenAI hackaton](https://www.linkedin.com/feed/update/urn:li:activity:7101235295735488512/) graceously hosted by [Techstrong/MediaOps](https://techstronggroup.com/)
- The lessons were refined for a presentation at the [London Devops Meetup group](https://www.meetup.com/london-devops/events/294948985/?utm_medium=referral&utm_campaign=share-btn_savedevents_share_modal).
- [Others are making plans](https://x.com/devopsdaysATL/status/1699833229795291609?) to run their own version of it

## How can you help ?
- Let us know what topic you'd like to see a lesson on ? Open a github issue to ask it
- Submit new lessons, send us corrections etc.. to improve it.

- Run your own meetup/hackaton using this repo as base and report back ! We love to hear those stories, send us pictures or videos ! 
- Send thankyou tweet to [@patrickdebois](https://twitter.com/patrick.debois)

## Modernization updates (2026-02-18)

This repository was updated to improve reproducibility and make local/container workflows consistent again.

### What changed
- Standardized runtime to Python 3.12 (`.python-version`)
- Added a consolidated notebook dependency baseline (`requirements-notebooks.txt`)
- Replaced the old Docker implementation with a Python 3.12 + virtualenv image (`Dockerfile`)
- Added Docker Compose workflow for JupyterLab (`compose.yaml`)
- Added environment template for model credentials (`.env.example`)
- Updated devcontainer interpreter settings to use the container venv (`.devcontainer/devcontainer.json`)
- Hardened `.gitignore` to avoid syncing local caches, notebook artifacts, envs, and local DB files

### Why this matters
- You can run the lessons with fewer manual fixes and less dependency drift
- Local development and container execution now use the same dependency source
- Notebook startup and authentication behavior are now explicit and documented

### Current status
- Docker build and Jupyter startup have been validated
- Core repo setup is modernized; notebook-by-notebook LangChain API migration is still in progress

## Requirements to run this repo

### Python version
- Target runtime: Python 3.12 (`.python-version` is set to `3.12`)

### Run it locally (recommended: virtual environment)
Use a local `venv` so notebook installs do not leak into your system Python:

```shell
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-notebooks.txt
python -m ipykernel install --user --name learning-llms --display-name "learning-llms"
```

If you need model provider credentials:

```shell
cp .env.example .env
```

### Run it with Docker Compose
This starts JupyterLab on [http://localhost:8888](http://localhost:8888):

```shell
make notebooks-build
make notebooks-up
```

The notebook image includes the `openclaw` CLI so OpenClaw lesson cells can run inside Docker.
The container runs as an unprivileged `notebook` user (uid/gid `1000`) and stores runtime state under `/home/notebook` (not `/root`).
It also installs separate Jupyter kernels for split notebook tracks:
- `Python 3 (classic-langchain)` (`python3-classic`) for `*-classic.ipynb`
- `Python 3 (modern-langchain)` (`python3-modern`) for `lessons/2026/langchain/*.ipynb`
- `Python 3 (modern-langchain)` (`python3`) as the default kernel

Jupyter runs with token auth enabled by default. Get the login URL with:

```shell
make notebooks-url
```

Open in your browser automatically:

```shell
make notebooks-open
```

Stop containers:

```shell
make notebooks-down
```

Use host Ollama from Docker (macOS). Compose defaults `OLLAMA_BASE_URL` to this value:

```shell
export OLLAMA_BASE_URL="http://host.docker.internal:11434"
```

Inside Docker, `localhost` points to the container itself. `host.docker.internal` routes to your Mac host where Ollama is running.

### Ollama setup (host machine)
For Docker notebooks, run Ollama on your host and keep `OLLAMA_BASE_URL=http://host.docker.internal:11434`.

Install (macOS/Homebrew):

```shell
brew install ollama
```

Start Ollama service (or open the Ollama desktop app):

```shell
ollama serve
```

Pull a smaller model (recommended for laptops):

```shell
ollama pull qwen2.5-coder:1.5b
```

Verify:

```shell
ollama list
curl http://localhost:11434/api/tags
```

### OpenClaw prerequisites
- Docker workflow: `openclaw` CLI is preinstalled in the notebook image (`Dockerfile`)
- OpenAI use cases: set `OPENAI_API_KEY` in `.env` (or shell env before `make notebooks-up`)
- Ollama use cases from Docker:
  - Run Ollama on your host machine
  - Keep `OLLAMA_BASE_URL=http://host.docker.internal:11434` (default in `compose.yaml`)
  - Prefer smaller models for laptop stability, for example `qwen2.5-coder:1.5b`
- Local (non-Docker) workflow:
  - Install OpenClaw CLI from upstream docs: https://docs.openclaw.ai
  - If you use Ollama locally, `OLLAMA_BASE_URL` can usually be `http://localhost:11434`
- Note for containers: `openclaw gateway status` may warn about missing `systemd`; this is expected in Docker and does not block provider configuration cells.

### Automated notebook tests
Run lightweight offline checks:

```shell
make test-smoke
```

Run notebook end-to-end execution (skips network/API notebooks unless enabled):

```shell
make test-e2e-notebooks
```

Run full notebook E2E execution:

```shell
make test-e2e-notebooks-full
```

`test-e2e-notebooks-full` will skip notebooks cleanly when required configuration is missing:
- `LANGCHAIN_API_KEY` for LangSmith/Hub notebooks
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_VISION_DEPLOYMENT` for Azure vision notebook
- both `OLLAMA_BASE_URL` and `ollama` CLI are unavailable for Ollama notebooks

Optional local model controls for Ollama notebooks:

```shell
export OLLAMA_MODEL="qwen2.5-coder:1.5b"
export OLLAMA_ALLOWED_MODELS="qwen2.5-coder:1.5b,qwen2.5-coder:7b"
```

### Notebook git hygiene (recommended)
Notebook outputs tend to create noisy diffs. This repo supports an output-free workflow:

```shell
make dev-tools-install
make notebooks-clean
make notebooks-check-clean
```

What this provides:
- `pre-commit` + `nbstripout`: strips notebook outputs before commit
- `jupytext` support: optional pairing for text-first notebook editing
  - `make notebooks-pair NOTEBOOK=lessons/path/notebook.ipynb`
- CI enforcement: GitHub Actions checks that notebooks are output-clean

### Run it using a devcontainer
This project includes a devcontainer definition that uses the project Dockerfile.
You can also run notebooks in Colab if preferred.

### VS Code setup
- Install extensions: Python + Jupyter
- Select interpreter: `.venv/bin/python` for local, or `/opt/venv-modern/bin/python` in container
- Open notebooks from the `lessons/` folder and pick the matching kernel:
  - `Python 3 (classic-langchain)` for `*-classic.ipynb`
  - `Python 3 (modern-langchain)` for `lessons/2026/langchain/*.ipynb`

## Changelog 
- 0.1 version with initial langchain syntax
- 0.2 version adapted to new langchain-community , langchain-openai and new syntax
- 0.3 modernization baseline: Python 3.12 target, venv-first local workflow, refreshed Docker/Compose runtime, and repository hygiene updates

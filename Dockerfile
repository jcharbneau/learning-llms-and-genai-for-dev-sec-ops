FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    VENV_MODERN=/opt/venv-modern \
    VENV_CLASSIC=/opt/venv-classic \
    PATH="/opt/venv-modern/bin:$PATH" \
    HOME=/home/notebook

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    build-essential \
    curl \
    git \
    jq \
    nodejs \
    npm \
    ripgrep \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-notebooks.txt requirements-notebooks-classic.txt ./
RUN python -m venv "$VENV_MODERN" \
    && "$VENV_MODERN/bin/pip" install --upgrade pip setuptools wheel \
    && "$VENV_MODERN/bin/pip" install -r requirements-notebooks.txt \
    && python -m venv "$VENV_CLASSIC" \
    && "$VENV_CLASSIC/bin/pip" install --upgrade pip setuptools wheel \
    && "$VENV_CLASSIC/bin/pip" install -r requirements-notebooks-classic.txt \
    && "$VENV_MODERN/bin/python" -m ipykernel install --prefix /usr/local --name python3 --display-name "Python 3 (modern-langchain)" \
    && "$VENV_MODERN/bin/python" -m ipykernel install --prefix /usr/local --name python3-modern --display-name "Python 3 (modern-langchain)" \
    && "$VENV_CLASSIC/bin/python" -m ipykernel install --prefix /usr/local --name python3-classic --display-name "Python 3 (classic-langchain)"

# Install OpenClaw CLI in-container for notebook exercises.
RUN curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install-cli.sh \
    | bash -s -- --prefix /opt/openclaw --no-onboard \
    && ln -s /opt/openclaw/bin/openclaw /usr/local/bin/openclaw

# Install optional agent CLIs used by 2026 agent-clis lessons.
# These are best-effort because package names and distribution channels may change.
RUN npm install -g @openai/codex @anthropic-ai/claude-code opencode-ai || true

RUN groupadd --gid 1000 notebook \
    && useradd --uid 1000 --gid notebook --create-home --shell /bin/bash notebook \
    && mkdir -p /workspace \
    && chown -R notebook:notebook /workspace /home/notebook

USER notebook

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser"]

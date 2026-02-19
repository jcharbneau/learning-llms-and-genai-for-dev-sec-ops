# 2026 Curriculum Spec (Non-LangChain Tracks)

This file is the implementation contract for 2026 lesson tracks:
- `lessons/2026/litellm`
- `lessons/2026/llamaindex`
- `lessons/2026/dspy`
- `lessons/2026/agent-clis`

## Global Notebook Contract
Each `01..08` notebook must include these exact headings:
- `What This Lesson Is`
- `Scientific Lens`
- `How It Works`
- `Code Walkthrough`
- `Applied Labs`
- `Validation Checklist`
- `Further Reading`

Each notebook must include:
- `Deterministic Demo` code cell (runs without provider credentials)
- `Live Demo` code cell (provider/CLI backed, with graceful skip)
- topic-specific labs and checklist text (no template duplication)

## Difficulty Progression Pattern
- `01-02`: fundamentals and base abstractions
- `03-04`: composition and intermediate tradeoffs
- `05-06`: evaluation/quality/reliability controls
- `07-08`: productionization, governance, and operations

## Track Progression Matrix

### LiteLLM
1. Provider routing fundamentals
2. Cost-latency policy routing
3. Retries/timeouts/circuit-breakers
4. Structured output portability
5. Caching and idempotency keys
6. Observability and telemetry
7. Failure drills and recovery validation
8. Security and governance guardrails

### LlamaIndex
1. Minimal RAG architecture
2. Chunking and metadata strategies
3. Hybrid retrieval fundamentals
4. Reranking pipelines
5. Router retrievers by intent/domain
6. Retrieval evaluation metrics (hit@k/MRR)
7. Index persistence and refresh lifecycle
8. Cost-performance tuning and tradeoff analysis

### DSPy
1. Signatures and typed contracts
2. Composable modules
3. Optimizers and training/eval set design
4. Constraint-driven structured outputs
5. Tool-augmented programs
6. Regression test harness design
7. Error taxonomy and remediation loops
8. Production handoff and release gates

### Agent CLIs
1. Capability benchmarking across CLIs
2. Safe repo mutation workflow
3. Approval/sandbox policy enforcement
4. Prompt-to-PR quality rubricing
5. Resilience under execution failures
6. Security posture checks for generated changes
7. Latency-cost-success benchmarking
8. Team adoption rollout and governance operations

## Mini Spec Per Notebook

### LiteLLM
- `01-provider-routing-and-fallback.ipynb`
  - Deterministic: fallback router simulation with provider failure states.
  - Live: execute primary+fallback model chain via LiteLLM.
- `02-cost-latency-routing.ipynb`
  - Deterministic: weighted routing score over synthetic latency/cost data.
  - Live: compare model calls and capture latency + token usage.
- `03-retries-timeouts-circuit-breakers.ipynb`
  - Deterministic: retry/backoff state machine.
  - Live: timeout-bound calls with retry policy and terminal fail path.
- `04-structured-output-portability.ipynb`
  - Deterministic: schema validation parser and repair path.
  - Live: provider output normalized to one schema.
- `05-caching-and-idempotency.ipynb`
  - Deterministic: idempotency key hashing and cache-hit semantics.
  - Live: cache-wrapped LLM calls showing first/memoized behavior.
- `06-observability-and-metrics.ipynb`
  - Deterministic: compute p50/p95/error-rate from event stream.
  - Live: instrument request metrics from real calls.
- `07-failure-drills.ipynb`
  - Deterministic: scenario table with expected behavior assertions.
  - Live: scripted drill harness for degraded provider path.
- `08-security-governance.ipynb`
  - Deterministic: model allowlist + secret redaction checks.
  - Live: policy-gated call execution with blocked/allowed traces.

### LlamaIndex
- `01-rag-minimal-modern.ipynb`
  - Deterministic: tiny corpus retrieval reasoning.
  - Live: query engine call and grounding validation.
- `02-chunking-and-metadata-strategy.ipynb`
  - Deterministic: chunk-size/metadata comparison table.
  - Live: retrieval differences for chunking strategies.
- `03-hybrid-retrieval.ipynb`
  - Deterministic: lexical + semantic score fusion.
  - Live: hybrid retrieval result inspection.
- `04-reranking-pipeline.ipynb`
  - Deterministic: first-pass vs reranked order deltas.
  - Live: rerank-enabled query comparison.
- `05-router-retrievers.ipynb`
  - Deterministic: intent router over query set.
  - Live: route-specific retriever execution.
- `06-evaluating-retrieval-quality.ipynb`
  - Deterministic: hit@k/MRR over labeled set.
  - Live: retrieval outputs scored against rubric.
- `07-index-persistence-refresh.ipynb`
  - Deterministic: persist/reload/update lifecycle simulation.
  - Live: storage-backed index reload and query.
- `08-cost-performance-tuning.ipynb`
  - Deterministic: Pareto tradeoff scoring.
  - Live: top_k/strategy sweep with latency-quality snapshots.

### DSPy
- `01-signatures-and-programs.ipynb`
  - Deterministic: typed signature contract checks.
  - Live: run `Predict` with configured LM.
- `02-composable-modules.ipynb`
  - Deterministic: module pipeline with explicit interfaces.
  - Live: multi-module DSPy execution.
- `03-optimizers-and-training-sets.ipynb`
  - Deterministic: candidate score comparison on eval set.
  - Live: optimizer/eval preview with LM configured.
- `04-constraints-and-structured-output.ipynb`
  - Deterministic: constraint checker and invalid case detection.
  - Live: constrained DSPy output generation.
- `05-tool-augmented-programs.ipynb`
  - Deterministic: tool dispatcher with safe interfaces.
  - Live: tool-augmented DSPy flow.
- `06-regression-testing.ipynb`
  - Deterministic: golden tests for parser/program behavior.
  - Live: run live outputs through regression checks.
- `07-error-analysis-loop.ipynb`
  - Deterministic: classify failure modes to remediations.
  - Live: generate remediation proposals and evaluate.
- `08-production-hand-off.ipynb`
  - Deterministic: release manifest + gate checks.
  - Live: generate concise release notes from manifest.

### Agent CLIs
- `01-opencode-codex-claudecode-playbook.ipynb`
  - Deterministic: capability matrix with measured criteria.
  - Live: run one non-interactive prompt on available CLI.
- `02-safe-repo-mutation-workflow.ipynb`
  - Deterministic: mutation workflow gate simulation.
  - Live: CLI-generated safe plan checked against policy rules.
- `03-approval-and-sandbox-policies.ipynb`
  - Deterministic: command risk classification engine.
  - Live: CLI policy proposal validated by classifier.
- `04-prompt-to-pr-quality.ipynb`
  - Deterministic: rubric scoring for PR summary quality.
  - Live: CLI-generated PR summary scored by rubric.
- `05-resilience-under-failure.ipynb`
  - Deterministic: retry/fallback executor simulation.
  - Live: CLI execution with controlled retry harness.
- `06-security-posture-checks.ipynb`
  - Deterministic: static checks for secrets/unsafe shell usage.
  - Live: CLI output scanned by security checks.
- `07-latency-and-cost-benchmarking.ipynb`
  - Deterministic: benchmark aggregation + ranking formula.
  - Live: timed CLI runs captured to benchmark table.
- `08-team-adoption-playbook.ipynb`
  - Deterministic: phased rollout plan generator.
  - Live: CLI-generated rollout draft validated against governance checklist.

## References Policy
`Further Reading` in each notebook should use primary sources where possible:
- Official framework docs (LiteLLM, LlamaIndex, DSPy, tool vendor docs)
- Official API docs (OpenAI, Ollama)
- Peer-reviewed or canonical references for metrics/evaluation concepts

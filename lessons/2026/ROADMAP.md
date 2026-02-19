# 2026 Ecosystem Roadmap

This roadmap defines the lesson scope for 2026 batches beyond the classic track.

## LangChain
- Location: `lessons/2026/langchain/`
- Status: Broad modern coverage already in place.

## LiteLLM
- Location: `lessons/2026/litellm/`
- Lessons:
  - `01-provider-routing-and-fallback.ipynb`
  - `02-cost-latency-routing.ipynb`
  - `03-retries-timeouts-circuit-breakers.ipynb`
  - `04-structured-output-portability.ipynb`
  - `05-caching-and-idempotency.ipynb`
  - `06-observability-and-metrics.ipynb`
  - `07-failure-drills.ipynb`
  - `08-security-governance.ipynb`

## LlamaIndex
- Location: `lessons/2026/llamaindex/`
- Lessons:
  - `01-rag-minimal-modern.ipynb`
  - `02-chunking-and-metadata-strategy.ipynb`
  - `03-hybrid-retrieval.ipynb`
  - `04-reranking-pipeline.ipynb`
  - `05-router-retrievers.ipynb`
  - `06-evaluating-retrieval-quality.ipynb`
  - `07-index-persistence-refresh.ipynb`
  - `08-cost-performance-tuning.ipynb`

## DSPy
- Location: `lessons/2026/dspy/`
- Lessons:
  - `01-signatures-and-programs.ipynb`
  - `02-composable-modules.ipynb`
  - `03-optimizers-and-training-sets.ipynb`
  - `04-constraints-and-structured-output.ipynb`
  - `05-tool-augmented-programs.ipynb`
  - `06-regression-testing.ipynb`
  - `07-error-analysis-loop.ipynb`
  - `08-production-hand-off.ipynb`

## Agent CLIs
- Location: `lessons/2026/agent-clis/`
- Lessons:
  - `01-opencode-codex-claudecode-playbook.ipynb`
  - `02-safe-repo-mutation-workflow.ipynb`
  - `03-approval-and-sandbox-policies.ipynb`
  - `04-prompt-to-pr-quality.ipynb`
  - `05-resilience-under-failure.ipynb`
  - `06-security-posture-checks.ipynb`
  - `07-latency-and-cost-benchmarking.ipynb`
  - `08-team-adoption-playbook.ipynb`

## Curriculum Standards (Locked)
- Scope in this pass: `litellm`, `llamaindex`, `dspy`, `agent-clis` only.
- Each `01..08` notebook must include:
  - `What This Lesson Is`
  - `Scientific Lens` (Concept, Measure, Validity Limit)
  - `How It Works`
  - `Code Walkthrough`
  - `Applied Labs` (unique per notebook)
  - `Validation Checklist` (unique per notebook)
  - `Further Reading` (official/primary sources)
- Runtime pattern per notebook:
  - deterministic demo path (always runnable)
  - live demo path (provider/CLI backed with graceful skip)
- Progression requirement: `01` to `08` increases in complexity and operational realism.

See `lessons/2026/CURRICULUM_SPEC.md` for the full per-notebook spec.

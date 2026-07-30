# Research Source Map

> Status: reference map for future ADRs and methodology. Sources inform target
> design; they are not dependencies or implemented integrations.

Re-check primary documentation when an issue relies on it.

## R1 — OpenAI Codex and AGENTS.md

- https://openai.com/index/introducing-codex/
- https://openai.com/index/running-codex-safely/

Repository instructions, reliable tests, bounded execution, approvals, network
policy, and telemetry informed the governance approach.

## R2 — OpenAI Evals and graders

- https://platform.openai.com/docs/api-reference/evals
- https://platform.openai.com/docs/api-reference/graders
- https://github.com/openai/evals/blob/main/docs/build-eval.md

Relevant concepts include separation of eval definitions and runs,
data-source schemas, grader types, and reusable templates.

## R3 — PaperBench

- https://openai.com/index/paperbench/
- https://evals.openai.com/

Relevant concepts include hierarchical gradable rubrics, domain-expert rubric
development, and evaluating a judge as a benchmark.

## R4 — NIST AI RMF and TEVV

- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- https://www.nist.gov/ai-test-evaluation-validation-and-verification-tev

Relevant concepts include lifecycle evaluation, validity, risk, limitations,
documentation, and governance.

## R5 — Inspect AI

- https://inspect.aisi.org.uk/
- https://inspect.aisi.org.uk/tasks.html
- https://inspect.aisi.org.uk/scorers.html
- https://inspect.aisi.org.uk/solvers.html

Relevant concepts include composable datasets/tasks, solvers/agents, scorers,
sandboxes, and model-independent packages.

## R6 — LangSmith evaluation concepts

- https://docs.langchain.com/langsmith/evaluation
- https://docs.langchain.com/langsmith/evaluate-pairwise
- https://docs.langchain.com/langsmith/manage-datasets

Relevant concepts include offline/online loops, versioned datasets and
experiments, randomized pairwise comparison, and failure promotion.

## R7 — SWE-bench

- https://github.com/SWE-bench/SWE-bench

Relevant concepts include repository patch tasks, Docker evaluation, gold
validation, verified subsets, and item-level logs.

## R8 — Inter-annotator agreement

- Artstein & Poesio, “Inter-Coder Agreement for Computational Linguistics.”
- https://www.aclweb.org/portal/node/9
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.cohen_kappa_score.html

Choose coefficients based on scale/design and interpret them with prevalence,
sample size, and case analysis.

## R9 — Calibration and uncertainty

- https://scikit-learn.org/stable/modules/calibration.html
- https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html
- https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html

Relevant concepts include reliability diagrams, proper scoring rules, and
paired bootstrap intervals.

## R10 — Judge reliability

- “Trust or Escalate: LLM Judges with Provable Guarantees for Human Agreement”
  — https://arxiv.org/abs/2407.18370
- “Humans or LLMs as the Judge? A Study on Judgement Biases”
  — https://arxiv.org/abs/2402.10669

Relevant concepts include confidence-aware selection, escalation, and bias
testing.

## R11 — Contamination

- https://aclanthology.org/2024.naacl-long.482/
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/e4a46394ba5378b3f9a186a5b4c650d1-Abstract-Conference.html
- https://aclanthology.org/2025.acl-long.656/

Relevant concepts include public benchmark contamination, hidden/dynamic or
temporal components, and cross-language leakage.

## R12 — Agent security

- https://genai.owasp.org/resource/securing-agentic-applications-guide-1-0/
- https://docs.docker.com/engine/containers/run/

Relevant concepts include least privilege, controlled tools, isolation, and
resource/network boundaries.

## Usage rule

When a design choice relies on a source, cite it in the owning ADR or
methodology. Do not copy large passages. Implement the principle only through
the issue responsible for that capability.

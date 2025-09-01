Title: Knowledge Gaps Research — 30 Questions, Rubric, and POCs
Last updated: 2025-09-02

Purpose: Identify knowledge gaps and external capabilities that would most improve delivery quality, velocity, and safety. Drive high‑ROI, low‑bloat integrations.

Rubric (score 1–5)
- Impact: Effect on accuracy, trust, developer velocity, or reliability
- Ease: Integration complexity, maintenance cost, team familiarity
- Maturity: Stability, docs, ecosystem, licensing
- Alignment: Fit with agentic loops, adapters, CI/CD, and governance
- Cost: Financial/runtime cost (invert: lower cost = higher score)

Process
1) Draft 30 research questions across domains (below)
2) Build candidate list (tools/services/frameworks/repos) per question
3) Score with rubric; shortlist top 10; pick 5 for micro‑POCs
4) Run POCs (≤1 day each); record metrics and decision
5) Write ADRs for adopted items; integrate behind adapters/flags

Research Questions (revised 1–30)
1. Agent strategies: Which planner strategies (test‑first, scaffold+fix, refactor‑then‑feature) yield higher win‑rates and lower reverts under time/cost budgets?
2. Safety policies: Which checks (allowlists, path guards, dry‑runs, rate limits) most reduce revert rate with minimal latency impact?
3. Agent memory: Which summarization/embedding policy improves plan quality per token ($) spent for our repo scale?
4. Agent evals: What eval set composition (task mix/difficulty/size) best predicts PR success and low revert rate?
5. NeSy rules: LNN vs simple Python rules vs JSON‑Schema—precision, maintainability, and CI performance trade‑offs?
6. Gap detection: ESG‑BERT vs ESGSenticNet vs heuristics—F1, latency, and cost with calibrated thresholds?
7. Calibration: Which method (temperature/Platt/quantile) stabilizes promotions while minimizing false positives?
8. Prompt/model registry: File‑based in‑repo vs hosted—versioning semantics, eval gates, and rollback ergonomics?
9. Canary strategy: What PR/nightly canary size and thresholds catch regressions early with low cost/noise?
10. Validators: Great Expectations vs pydantic‑core—speed, ergonomics, and maintenance for our data checks?
11. Determinism: Canonical JSON policy (orjson vs stdlib) across OS/Python—newline/encoding/sorting stability?
12. Compiled validation: Pydantic v2 compiled validators and fastjsonschema—measured speedups and correctness parity?
13. Dataframes: Polars vs pandas for our transforms—rewrite cost vs speed/memory gains; hybrid patterns?
14. Heavy joins: When to use DuckDB—memory footprint, throughput, and integration complexity for large joins?
15. Caching: Content‑hash key design (inputs/config/env), invalidation strategy, and HTTP caching (ETag) ROI?
16. Concurrency: Multiprocessing vs asyncio/httpx vs joblib—determinism, throughput, and resource ceilings; auto‑tune limits?
17. Logging/metrics: orjson logging overhead, sampling strategies; which histograms (P50/P95/P99) yield highest diagnostic value?
18. Tracing: Which spans (pipeline stages, external calls) most improve MTTR vs overhead; OTel sampling config?
19. Static analysis: Curated semgrep + Bandit rules that maximize true positives and minimize triage burden?
20. Supply chain: SBOM (syft) + Trivy policy—what to gate vs report; break‑glass criteria and signing roadmap?
21. CI gating: Advisory→enforced cadence, time budgets, flaky quarantine; pytest‑xdist impact on stability/speed?
22. Test ROI: Which mutation/fuzz targets deliver best defect discovery per CI minute; nightly vs weekly schedule?
23. Formal methods: Where do CrossHair + contracts find real bugs with acceptable modeling effort (pure mapping utilities)?
24. FinOps: Which API/LLM calls benefit most from caching or deferral; cost telemetry fields and dashboards?
25. Adapter interface: Minimal portable interface for LLM/NeSy providers; parity test design; error/timeout handling?
26. Docs effectiveness: Which runbooks/quickstarts/templates reduce time‑to‑fix and support requests the most?
27. A11y/i18n: Which automated/manual checks catch the most impactful accessibility issues; i18n early hooks to avoid rework?
28. Incident readiness: Most probable failure scenarios; drill cadence; automations (repro packs) to meet RTO/RPO?
29. Golden data: Best approach to version and store golden datasets/snapshots (e.g., Git LFS/DVC) without bloat?
30. Coverage metrics: How to set and ratchet type/line/mutation coverage thresholds to maximize signal without blocking progress?

Refined Plan per Question (v2)
Note: For each question below, approach is designed to be low‑bloat, evidence‑first, and reproducible.

1) Agent strategies
- Split: (a) win‑rate vs task type; (b) revert rate; (c) planning latency.
- Sources: OpenAI/Google agent papers, ReAct/Reflexion; vendor blogs with code; our trace logs.
- Method: A/B strategies on low‑risk tasks; log success/reverts/time; 7‑day stability.
- Metrics: win‑rate, reverts <1%, P95 plan time; cost per task.
- Tools: agent_core traces; CI eval harness; nightly job.

2) Safety policies
- Split: allowlists, path guards, dry‑runs, rate limits.
- Sources: OWASP, OpenSSF guides; vendor agent safety write‑ups.
- Method: Enable policies incrementally; measure revert rate and latency delta.
- Metrics: revert delta, false blocks, added latency.

3) Agent memory
- Split: summarization vs embeddings; context window cost/benefit.
- Sources: LLM retrieval best practices; model provider docs.
- Method: Compare summary lengths/embedding sizes on planning quality.
- Metrics: plan quality proxy (win‑rate), token $, latency.

4) Agent evals
- Split: task taxonomy; size/difficulty balance.
- Sources: evaluation frameworks; Papers with Code task taxonomies.
- Method: Curate eval set; correlate eval outcomes with PR success.
- Metrics: correlation coefficient; predictive power vs cost.

5) NeSy rules engines
- Split: LNN vs Python rules vs JSON‑Schema.
- Sources: IBM LNN repo/papers; JSON‑Schema draft; Python rule examples.
- Method: Implement same constraints in all; compare precision, maintainability, CI time.
- Metrics: FP/FN, rule code LOC/complexity, CI runtime.

6) Gap detection models
- Split: ESG‑BERT vs ESGSenticNet vs heuristics.
- Sources: ESG‑BERT repo; ESGSenticNet docs; SenticNet.
- Method: Eval on labeled gaps; calibrate thresholds for stable promotions.
- Metrics: F1, P95 latency, cost/sample; explanation acceptance rate.

7) Calibration
- Split: temperature vs Platt vs quantile.
- Sources: calibration literature; sklearn; ML blogs.
- Method: Calibrate on validation; test stability over 7 days.
- Metrics: ECE/Brier; promotion FP rate.

8) Prompt/model registry
- Split: in‑repo file registry vs hosted.
- Sources: MLOps best practices; model registry docs.
- Method: Prototype file‑based registry with CI eval hooks.
- Metrics: time to rollback; change traceability; setup cost.

9) Canary strategy
- Split: PR vs nightly; sample sizes.
- Sources: CI/CD canary literature; internal metrics.
- Method: Simulate regressions; tune thresholds to minimize noise.
- Metrics: precision/recall of canary alerts; CI time impact.

10) Validators
- Split: Great Expectations vs pydantic‑core.
- Sources: GE docs; Pydantic v2 docs.
- Method: Implement identical checks; measure speed/maintainability.
- Metrics: runtime, LOC, onboarding time.

11) Determinism
- Split: orjson vs stdlib; newline/encoding/sorting.
- Sources: orjson docs; Python json docs; OS/Python differences.
- Method: Cross‑OS/Python snapshot tests; choose canonical settings.
- Metrics: snapshot pass rate; performance delta.

12) Compiled validation
- Split: Pydantic v2 compiled vs fastjsonschema.
- Sources: Pydantic v2 perf notes; fastjsonschema docs.
- Method: Bench identical schemas; verify parity on tricky cases.
- Metrics: speedup %, memory; correctness parity.

13) Dataframes
- Split: Polars vs pandas; hybrid patterns.
- Sources: Polars/pandas docs; community benchmarks.
- Method: Port one heavy transform; measure speed/memory; estimate rewrite cost.
- Metrics: speedup %, memory; code diff size.

14) Heavy joins
- Split: DuckDB vs pandas joins; streaming.
- Sources: DuckDB docs; best practices.
- Method: Prototype large join; measure memory, throughput, complexity.
- Metrics: peak RSS, rows/s; code complexity.

15) Caching
- Split: key design; invalidation; HTTP (ETag).
- Sources: HTTP caching RFCs; content‑hashing patterns.
- Method: Implement content‑hash + HTTP caching; measure hit rate.
- Metrics: hit rate %, runtime saved; staleness incidents.

16) Concurrency
- Split: multiprocessing vs asyncio/httpx vs joblib.
- Sources: Python concurrency guides; httpx docs.
- Method: Implement both for representative tasks; compare determinism/throughput.
- Metrics: speedup vs serial; error rate; CPU/mem.

17) Logging/metrics
- Split: logging format perf; histogram design.
- Sources: orjson docs; Prometheus best practices.
- Method: Measure logging overhead; select key histograms with exemplars.
- Metrics: logging overhead <5%; metric diagnostic value.

18) Tracing
- Split: span selection; sampling configuration.
- Sources: OpenTelemetry specs; SRE MTTR case studies.
- Method: Add spans to pipeline stages; measure MTTR impact on drills.
- Metrics: MTTR delta; tracing overhead.

19) Static analysis
- Split: semgrep/Bandit rule sets.
- Sources: official rulesets; community curated profiles.
- Method: Tune to maximize true positives; track triage time.
- Metrics: TP rate; triage minutes/week.

20) Supply chain
- Split: SBOM policy; Trivy gating; signing roadmap.
- Sources: SLSA, OpenSSF, CycloneDX, SPDX.
- Method: Run weekly SBOM+Trivy; define break‑glass criteria.
- Metrics: high/critical count; remediation SLA.

21) CI gating
- Split: cadence; flaky quarantine; xdist effects.
- Sources: CI best practices; pytest‑xdist docs.
- Method: Enable xdist; add flaky quarantine; measure stability/time.
- Metrics: CI duration; flake rate; developer wait times.

22) Test ROI
- Split: mutation vs fuzz targets; schedule.
- Sources: mutmut/atheris docs; case studies.
- Method: Target core mappers; measure defect finds per minute.
- Metrics: defects found / CI minute; false positives.

23) Formal methods
- Split: pure mapping utilities; contract style.
- Sources: CrossHair; design by contract literature.
- Method: Apply to curated list; track real bugs found.
- Metrics: bugs found; modeling effort hours.

24) FinOps
- Split: caching vs nightly; telemetry fields.
- Sources: FinOps guides; provider pricing.
- Method: Log cost fields; pilot caching/nightly deferral.
- Metrics: $/1k items; cache hit rate; cost trend.

25) Adapter interface
- Split: LLM vs NeSy; parity tests.
- Sources: provider SDKs; adapter patterns.
- Method: Define minimal interface; add parity tests across providers.
- Metrics: switch latency; behavior parity; error handling coverage.

26) Docs effectiveness
- Split: runbooks vs quickstarts vs templates.
- Sources: internal support logs; industry docs patterns.
- Method: A/B docs sets; measure time‑to‑fix/onboarding.
- Metrics: minutes to complete tasks; support requests.

27) A11y/i18n
- Split: automated vs manual checks; early hooks.
- Sources: WCAG, axe‑core, i18n guides.
- Method: Run axe; manual passes; externalize strings.
- Metrics: critical issues count; retrofit cost avoided.

28) Incident readiness
- Split: scenarios; drill cadence; repro packs.
- Sources: SRE books; incident postmortems.
- Method: Run drills; measure RTO/RPO; generate repro packs.
- Metrics: RTO/RPO met; action items closed.

29) Golden data
- Split: LFS/DVC vs plain git; storage constraints.
- Sources: DVC docs; Git LFS; data versioning best practices.
- Method: Pilot small golden datasets; watch repo size & flows.
- Metrics: repo bloat; ease of use; CI time.

30) Coverage ratcheting
- Split: type/line/mutation; ratchet policy.
- Sources: coverage.py/mypy/mutmut docs; case studies.
- Method: Start at current levels; ratchet up on green weeks.
- Metrics: trend lines; failure noise.

Initial Findings & New Gaps (Triage)
- Determinism likely needs orjson + explicit newline/encoding policies; cross‑OS tests required.
- Compiled validation (Pydantic v2, fastjsonschema) expected to yield double‑digit % speedups; verify parity on edge cases.
- Polars/DuckDB promising for heavy joins; integration cost must be balanced with maintainability.
- CI stability depends on flaky quarantine and xdist tuning; measure before gating.
- New gaps: baseline labeled datasets for gap detection; golden dataset/versioning policy; minimal parity test harness for adapters.

Candidates & Shortlist (to be populated)
- Table listing: name, category, link, license, costs, notes, scores

Micro‑POCs (≤1 day each)
- Template: goal, hypothesis, setup, dataset, metrics, result, decision, follow‑ups

Decisions & ADR Links
- List adopted tools/methods with ADR IDs and rationale

Acceptance
- 30 questions completed; ≥10 shortlisted; ≥5 POCs with metrics; ≥3 ADRs adopted; integrations behind adapters/flags; ROI rationale recorded.

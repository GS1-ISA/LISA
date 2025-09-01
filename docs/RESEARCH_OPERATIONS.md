Title: Research Operations — From Learning to Adoption (R2P)

Goal: Convert research into high‑impact, low‑bloat improvements via a repeatable Research‑to‑Production (R2P) pipeline with strong evidence standards and measurable ROI.

R2P Pipeline (10 Steps)
1) Question: Select a research question from docs/RESEARCH_KNOWLEDGE_GAPS.md.
2) Systematic Search: Generate queries (keywords/synonyms), search multiple sources (standards, peer‑reviewed, reputable industry, official repos/docs). Log queries and hits in a search ledger.
3) Candidate Set: Build a shortlist of tools/services/repos with license, cost, maturity, maintenance metrics.
4) Evidence Grading: Score each candidate with the rubric (Impact, Ease, Maturity, Alignment, Cost). Add evidence levels (see Evidence Ladder below).
5) Pre‑Reg Protocol: Write a micro‑POC plan (hypothesis, metrics, dataset, env, seeds) to avoid p‑hacking.
6) Run POC: Execute under pinned environment; collect metrics (accuracy/F1, latency, cost, dev time saved), logs, and artifacts.
7) Replication: Re‑run POC on a second machine or container to confirm determinism; document any drift.
8) Decision: Adopt/Hold/Reject with rationale. Create an ADR for adopted items and a tracking issue for holds.
9) Integration: Add behind an adapter and feature flag; shadow (A/B) in nightly. No PR‑CI coupling until stability is proven.
10) Promotion & Retirement: Promote to PR‑CI only if passing thresholds for 7 consecutive days; periodically review and retire low‑value integrations.

Evidence Ladder (Highest → Lowest)
- Tier A: Peer‑reviewed papers with code + reproducible results; official standards/specs; security advisories (NVD/CVE).
- Tier B: Official vendor docs, SDKs, or reference implementations; widely used OSS with active maintenance and strong tests.
- Tier C: Industry whitepapers, conference talks with demos; large community benchmarks (Papers with Code) with verified results.
- Tier D: Blog posts and tutorials with working code samples; preliminary research without code.
- Tier E: Marketing materials; unverified claims; closed results without detail.

Source Vetting Checklist
- Authority: Standards bodies (GS1, EU, NIST, OWASP, W3C), major research venues (NeurIPS/ICLR/ACL), official vendor docs.
- Recency: Prefer last 2–3 years; note when older sources remain canonical.
- Reproducibility: Code available, versioned, runnable; datasets accessible; CI badges, tests, coverage.
- Maintenance: Commit frequency, issue responsiveness, release cadence.
- Licensing/Cost: Permissive licenses; transparent pricing; TCO estimates.
- Independence: Conflicts of interest disclosed; triangulate with at least two independent sources.

Best‑in‑Class Sources (Non‑Exhaustive)
- Standards/Policy: GS1 GDSN, EU CSRD/EUDR, W3C, NIST, OWASP, OpenSSF.
- Research: arXiv, ACL Anthology, IEEE, ACM DL, NeurIPS; Papers with Code for benchmarks.
- Engineering: Google SRE Book, AWS Well‑Architected, CNCF TAGs, OpenTelemetry.
- Security/Supply Chain: NVD/CVE/NIST NVD, OpenSSF Scorecards, SLSA, CycloneDX/SPDX.
- See also: docs/RESEARCH_SOURCES.md for a curated list to seed search ledgers.

Experiment Design (Micro‑POC)
- Hypothesis: Specific, falsifiable statement tied to metrics.
- Dataset: Fixed version with licenses; train/test split or holdout; seeds fixed.
- Metrics: Task‑appropriate (e.g., gap detection F1, validator FP/FN, latency P95, $/1k items, dev time saved).
- Environment: Devcontainer or pinned requirements; record CPU/RAM; capture seeds.
- Analysis: Report means, stdev, confidence where applicable; include failure analysis.

Enhancements (v2)
- Power Analysis: Estimate needed sample sizes to detect target effects; avoid underpowered POCs (template: docs/templates/power_analysis_template.md).
- Threats to Validity: Document internal/external/construct threats and mitigations (template: docs/templates/threats_to_validity_template.md).
- SPC/Control Charts: Track key metrics over time to detect drift (template: docs/templates/control_chart_template.md).
- Pre‑registration: Link protocol before running; include stop/kill criteria and budget caps.

Adoption Criteria (Promote → Gate)
- Replicable: POC results reproduce within tolerance on second run/environment.
- ROI: Clear benefit vs. baseline (e.g., ≥10% F1 lift; −20% latency; −30% dev time).
- Stability: Nightly shadow runs meet thresholds for 7 days; flakiness <1%.
- Safety/Legal: License compatible; security review passed; privacy OK.
- Integration: Adapterized; feature flag default OFF; ADR merged.

Retrospectives & Learning
- After each POC and promotion, write a short retrospective: what worked, what didn’t, next bets.
- Update the reward model priors for agentic strategies based on measured outcomes.

Artifacts & Traceability
- Keep POC notebooks/scripts, configs, logs, and reports under version control.
- Link all decisions to ADRs; include metrics and references.

Acceptance
- For each adopted research output: ADR exists; adapter and flag merged; nightly shadow metrics green for 7 days; promotion logged; rollback plan documented.
\n+POC Results Index (Examples)
- Q11 Determinism (orjson vs stdlib): docs/research/q11_orjson_determinism/results.md
- Q12 Compiled Validators: docs/research/q12_compiled_validators/results.md

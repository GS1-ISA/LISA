Title: NeSy (NeuroSymbolic) Roadmap — TODOs and Acceptance Criteria

Note: This file is the NeSy-specific tracker. For the full program checklist, see docs/TODO.md.

Status Legend: [ ] pending  [~] in-progress  [x] done  [!] blocked

Scope: All NeSy integrations for GS1 ESG gap-analysis. Keep adapters modular, feature-flagged, and evaluated via A/B before promotion to gates. Avoid bloat — prioritize high-ROI items.

0) Foundations
- [ ] Create `nesy` adapters package layout (no heavy deps): `ISA_SuperApp/src/nesy/`
- [ ] Define common `NeSyAdapter` interface (predict(), explain(), metadata())
- [ ] Add feature flags in config: `NESY_{ESG_BERT,LNN,SENTICNET,ESGSENTICNET,DEPPROB,NEURASP,DON}`
- [ ] Seed evaluation dataset for gaps (labeled) under `artifacts/nesy_eval/`
- [ ] Eval harness: precision/recall/F1, latency, cost per adapter; JSONL report
Acceptance:
- Adapters implement the interface; flags are typed and documented; eval harness runs locally and in nightly CI.

1) ESG‑BERT + Symbolic Post‑Processors (NOW)
- [ ] Adapter stub wrapping model API or local weights
- [ ] Symbolic materiality/rule layer (simple Python rules)
- [ ] Unit + integration tests with goldens and explanations
- [ ] CI job: run adapter on small sample (advisory report)
Acceptance:
- ≥10% precision/recall lift vs. baseline keyword rules on eval set; explanations pass reviewer spot-checks (≥80% acceptance).

2) LNN Rules Engine (NOW)
- [~] Rule library MVP (e.g., EUDR geolocation precision ≥ 6 decimals)
- [x] LNN integration module and deterministic validator endpoint `/validate`
- [x] Tests with seeded violations; zero false positives on green data
- [ ] Wire into PR CI (gate when stable)
Acceptance:
- Catches 100% seeded violations; 0 FPs on clean fixtures; adds <5% to CI time.

3) SenticNet 7 REST (NOW — Optional)
- [ ] REST client with retries and caching; rate-limit guards
- [ ] Dedupe/precision filters; reviewer queue integration
- [ ] Nightly advisory report of top N candidate attributes per sector
Acceptance:
- ≥5 high‑value candidates/sector with <10% spam; budget respected.

4) ESGSenticNet (Pilot)
- [ ] Verify availability/licensing and API/schema stability
- [ ] Adapter + A/B vs. ESG‑BERT; confidence thresholds
- [ ] Nightly eval, shadow mode only
Acceptance:
- Beats ESG‑BERT on recall without >1.5× false positives; cost within cap.

5) DeepProbLog (Pilot, Narrow)
- [ ] Define one focused question: P(audit pass | evidence)
- [ ] Micro‑module or service; training data prep; calibration check
- [ ] Nightly advisory probability outputs for reviewer feedback
Acceptance:
- Calibrated probabilities (Brier score improvement vs. naive baseline) on ≥20 cases.

6) Weave.AI Spectrum (Pilot UI)
- [ ] Map our JSON outputs to Spectrum widgets; no vendor‑locked logic
- [ ] Demo dashboard; export JSON for parity with SuperApp UI
Acceptance:
- Pilot demo loads in <5 minutes; identical insights render in SuperApp.

7) NeurASP (Later / Research)
- [ ] What‑if simulation prototype for one attribute set
- [ ] Correlate with historical adoption; offline only
Acceptance:
- Produces plausible deltas that correlate with outcomes on a holdout.

8) Deep Ontological Networks (Later / Research)
- [ ] Offline prototype for cross‑sector mapping suggestions
- [ ] SME validation workflow; export explainable rules
Acceptance:
- Validated explainable mappings outperform simple heuristics on a sample.

9) Cross‑Cutting Guardrails
- [ ] All adapters behind feature flags; default OFF in PR CI
- [ ] A/B by default (shadow mode); promote only with eval wins and SME sign‑off
- [ ] External API budgets and caching; fail closed on rate limits
Acceptance:
- No PR CI failures due to external API; reproducible nightly reports.

10) Metrics & Promotion
- [ ] Eval metrics: P/R/F1, latency P95, cost/sample, explanation acceptance
- [ ] Nightly trend dashboards (JSON → Grafana via pushgateway or artifact review)
- [ ] Promotion checklist per adapter (criteria + SME sign‑off)
Acceptance:
- Promotion occurs only when metrics meet thresholds for 7 consecutive days.

11) Documentation
- [ ] `docs/nesy/overview.md` (architecture, adapters, flags, evals)
- [ ] `docs/nesy/adapters/*.md` per adapter with inputs/outputs/schemas
- [ ] Playbook for adding a new NeSy component
Acceptance:
- A new engineer can add an adapter and run evals in ≤60 minutes.

Appendix — Backlog (Optional Enhancements)
- [ ] Ensembling: simple rank fusion across ESG‑BERT/ESGSenticNet/SenticNet
- [ ] Active learning loop with reviewer feedback to retrain thresholds
- [ ] Explanation store and similarity search for reuse across sectors

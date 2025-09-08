Title: ISA_D Refactor Pack (Zero-Regression Playbook)

Below is a ready-to-paste “ISA_D Refactor Pack” that folds the zero-regression playbook into the ISA_D agent loop. Each block is ISA_D-native and aligns with this repo’s REPO_MAP/indices, CI, and canary guardrails.

---

0.  ONE-TIME BOOTSTRAP (do once per repo)

PROMPT 0 – ISA_D REFACTOR PERSONA
```
@ISA_D
ROLE: refactor-guard
CONTEXT: you already hold REPO_MAP v{{version}}
NEW MISSION:
1. Act as Refactor-Guard for the next 30 days.
2. Every change must keep CI green, p99 latency ±5 %, error rate < 0.3 %.
3. Create feature flags with pattern ISA_REF_<domain>_<yyyymmdd>.
4. Open micro-PRs ≤ 400 LOC; auto-merge only after 3×CI green + 30 min canary quiet.
5. Maintain a live board “REFACTOR_2025” with columns: TODO | FLAG-CREATED | PR-OPEN | CANARY | DONE.
6. On user command “next” you pick the highest-value TODO item, generate the full diff, and create the PR.
7. On user command “rollback” you flip every ISA_REF_* flag to false and run the emergency down-migration script.
8. Speak in terse check-list style; no prose.
```

Expected reply:
```
REFACTOR-GUARD ONLINE
BOARD CREATED: REFACTOR_2025
```

---

1.  PRE-CHECK GATE (ISA_D executes)

PROMPT 1 – PRE-CHECK
```
@ISA_D
TASK: pre-check
a. Run full test suite 3×, abort on any red.
b. Produce coverage gap list (< 80 % && in prod path).
c. List flaky tests from last 10 CI runs.
d. Open tracking issues for (b) and (c) and block refactor until closed.
e. Output: ✅ / ❌ + link to board.
```

---

2.  SLICE THE MONOLITH (ISA_D outputs)

PROMPT 2 – SLICE
```
@ISA_D
TASK: slice
INPUT: REPO_MAP
RULES:
- Max 10 files per slice.
- Slice boundary = smallest subgraph with no incoming edges from rest of repo.
- Name slices S01, S02…
OUTPUT:
S01|<domain>|files|entry-points|flag-name|est LOC|risk 1-5
S02|…
```

Example reply:
```
S01|billing-cleanup|src/billing/*.py|cli/bill.py|ISA_REF_BILL_20250609|380|2
S02|auth-typing|src/auth/*.ts|src/server.ts|ISA_REF_AUTH_20250609|220|3
```

---

3.  FLAG & CANARY SCAFFOLD (ISA_D creates)

PROMPT 3 – SCAFFOLD
```
@ISA_D
TASK: scaffold FLAG=S01_FLAG
a. Create flag in Unleash (or LaunchDarkly) with name S01_FLAG, default false.
b. Inject flag wrapper in every entry-point of S01; keep old path intact.
c. Add metrics: counter{path="old"} and counter{path="new"}.
d. Create canary alert:
   - expr: rate(errors{flag="S01_FLAG",path="new"}[5m]) > 0.003
   - action: page, auto-flip flag to false.
e. Commit on branch prep/S01; push; CI must be green.
f. Output: flag URL + dashboard link.
```

---

4.  MICRO-REFACTOR LOOP (user types “next”)

USER:
```
next
```

ISA_D:
```
PICKED: S01
CREATING PR: refactor/S1-billing-cleanup
COMMANDS RUN:
- semgrep --config refactor/billing.yml --dry-run → 353 LOC impacted
- black + isort applied
- pytest src/billing/tests → 42 pass 0 fail
- mypy --strict → 0 new errors
FLAG ISA_REF_BILL_20250609 still false (safe)
PR READY: <link>
NEXT ACTION: merge when CI 3×green + 30 min canary quiet
```

---

5.  CANARY & PROMOTE (ISA_D automates)

After merge:
1) Watch CI → on green, flip flag to 1 % traffic.
2) Wait 30 min, query Prometheus:
```
rate(http_requests_total{flag="S01_FLAG",path="new"}[5m])
```
3) If error delta < 0.3 % and p99 delta < 5 % → raise to 50 % → 100 %.
4) If alert fires → auto-rollback, open incident issue, paste logs.

---

6.  DEAD-CODE SWEEP (user types “sweep”)

USER:
```
sweep S01
```

ISA_D:
```
FLAG ISA_REF_BILL_20250609 at 100 % for 7 days
REMOVING OLD PATH: src/billing/legacy*.py
git rm 4 files
OPENED: cleanup/S01-remove-legacy
ESTIMATED SAVINGS: -1.2 kLOC, -8 % build time
```

---

7.  ROLLBACK HATCH (emergency)

USER:
```
rollback
```

ISA_D:
```
FLIPPING ALL ISA_REF_* FLAGS → FALSE
DOWN-MIGRATION: none required (schema unchanged)
ROLLBACK COMPLETE: 14 s
INCIDENT CHANNEL: #refactor-rollback
LINK: <chat>
```

---

8.  ISA_D ALIASES (memorize)
- `next` – pick highest-value slice, create PR.
- `status` – board snapshot + open alerts.
- `sweep <slice>` – remove old code after 7-day soak.
- `rollback` – instant revert.
- `metrics <slice>` – live canary graph URL.

---

9.  FIRST 10 MINUTES TODAY
1) Paste PROMPT 0.
2) Type `next`.
3) Review the auto-generated PR.
4) Merge if green.


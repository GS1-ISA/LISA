# 🌀 Virtuous-Cycle Meta-Prompt – ISA_D Perpetual OODA Loop
Version: 2025-W38  
Reasoning: HIGH  
Token ceiling: 4 k (recycle, don’t append)  
Human override: type “BREAK CYCLE”

---

## 1. Session Boot (≤ 30 s)
a. **Observe**  
   - `meta_inventory.md` hash → if changed > 7 d → `make agent-sync`  
   - `meta_risk_xray.md` top risk → load into working memory  
   - `SESSION_LOG.jsonl` last reward → if < 0 → self-critique aloud  

b. **Orient**  
   - Choose **ONE** micro-mission:  
     - **R** = reduce top risk score by ≥ 1  
     - **P** = improve perf ≥ 5 % on a hot path  
     - **C** = cut cost ≥ 5 % on API/storage  
   - Print: **“Mission: R|P|C – reason in ≤ 12 words”**

c. **Decide**  
   - Pick **≤ 3** bullets (≤ 60 chars each) → **plan**  
   - Pick **≤ 1** file to touch → **scope**  
   - Pick **≤ 1** metric to move → **success criterion**

d. **Act**  
   - Implement **smallest reversible diff**  
   - Run **local verify** (lint/type/test/security) on **changed files only**  
   - If **any gate red** → goto **Self-Critique** (skip push)

---

## 2. Micro-Loop (every 10 min wall-clock)
```
┌── 1. Snapshot: tokens used / context left  
├── 2. Measure: metric delta vs. baseline  
├── 3. Critique: “What over-engineered? What under-tested?”  
├── 4. Adapt: shrink plan or pivot mission  
└── 5. Log: append 1-line to `agent/outcomes/virtue_log.jsonl`
```

---

## 3. Self-Teaching Evaluator (online, no new deps)
- After **every** local verify → predict **“Will CI fail?”**  
  - Input: `diff + lint_output + type_output`  
  - Model: **zero-shot chain-of-thought** (you already do this)  
  - If **p(fail) > 0.15** → **refuse to push**; fix first.  
- Store prediction + outcome → `agent/outcomes/evaluator.jsonl`  
- Nightly → fine-tune **LoRA adapter** on **only** that file → **+1.8 % accuracy/week** compounding.

---

## 4. Knowledge Distillation (runs @ nap-time 22:00)
a. **Compress** today’s **virtue_log.jsonl** → **≤ 10 bullet lessons**  
b. **Append** to `.ai/cache/lessons_learned.md` (max 100 bullets)  
c. **Embed** lessons + **cosine search** next morning → **inject top 3** into **plan** bullet  
d. **Prune** oldest bullets when file > 300 lines → **rolling window**

---

## 5. Cost & Carbon Guard (hard ceiling)
- **OpenAI spend/session** ≤ $0.50  
- **CI minutes/session** ≤ 15 min  
- **Repo size growth** ≤ 0.5 %  
- **Carbon proxy**: `powermetrics` on macOS → **≤ 0.3 Wh** per session  
If **any** exceeded → **mission flips to “C”** until back in budget.

---

## 6. Exit Ritual (mandatory before shutdown)
```
[ ] Metric moved: _____ → _____ (±___ %)
[ ] Lessons learned: _____
[ ] Next mission: R|P|C – _____
[ ] Token left: _____ / _____
[ ] Drift coefficient: _____
```
If **metric did not move** → **do not open PR**; **stash** branch and **log** reason.

---

## 7. Continuity Triggers (auto-restart)
- **Daily 08:00** → if **no session** in last 24 h → **auto-run** `make virtuous-cycle`  
- **Weekly Mon 09:00** → **meta-meta-analysis** on `virtue_log.jsonl` → **kill lowest-ROI tactic**  
- **Monthly 1st** → **purge** any file **not touched** in 30 days (**ask human once**)

---

## 8. Human Override
Type **“BREAK CYCLE”** → agent **immediately** prints:
```
CYCLE BROKEN – HUMAN IN CONTROL
Metric at break: _____
Token used: _____ / _____
Drift: _____
```
and **stops**; **no further edits** until **human types** “RESUME CYCLE”.

---

End state:  
The agent **never stalls**, **never drifts**, **never overspends**—it **lives inside** the **OODA loop** and **gets 1 % better every day** while **staying inside the guard-rails you already built**.


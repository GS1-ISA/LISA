# Project Healthcheck

## ruff (lint)

````
SKIPPED: ruff check . (not installed)
````


## mypy (types)

````
SKIPPED: mypy ISA_SuperApp/src (not installed)
````


## pytest (determinism snapshot)

````
bash: line 0: cd: ISA_SuperApp: No such file or directory
````


## bandit (security)

````
SKIPPED: bandit -qq -r ISA_SuperApp/src (not installed)
````


## pip-audit (deps)

````
SKIPPED: pip-audit (not installed)
````


## docs-ref-lint

````
wrote /Users/frisowempe/ISA_D/docs/audit/docs_ref_report.md
````


## coherence-audit

````
coherence audit artifacts written:
 - /Users/frisowempe/ISA_D/coherence_graph.json
 - /Users/frisowempe/ISA_D/orphans_and_dead_ends.md
 - /Users/frisowempe/ISA_D/TERMS.md
 - /Users/frisowempe/ISA_D/traceability_matrix.csv
 - /Users/frisowempe/ISA_D/COHERENCE_SCORECARD.md
 - /Users/frisowempe/ISA_D/contradiction_report.md
````


## coherence-scorecard

````
# Coherence Scorecard

- Reference Density: 4.22 (score 100)
- Orphan Ratio: 0.95 (score 4)
- Contradiction Count: 0 (score 100)
- Clustering Coefficient (approx): n/a (score 70)
- Coherence Index: 68

Note: Initial baseline. Improve by adding cross-links and trimming orphans where appropriate.
````


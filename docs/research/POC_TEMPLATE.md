# Micro-POC Template

## Goal

What is the specific research question or feature you're validating?

## Hypothesis

What do you expect to find or prove?

## Timebox

How long will this take? (default: ≤1 day)

## Owner

Who runs it and who is reviewer?

## Inputs

- Data sources, manifests, queries

## Scripts to run

- scripts/research/run_poc.py --manifest data/ingestion_manifests/isa_docs_v1_manifest.yaml --out artifacts/{run_id}

## Expected metrics

- metric: target

## Acceptance criteria

- Quantitative pass/fail rules

## Artifacts produced

- artifacts/{run_id}/raw
- artifacts/{run_id}/processed
- experiments/{run_id}.yaml

## Notes

- Privacy, blockers, follow-ups

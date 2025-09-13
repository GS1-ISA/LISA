# Model Card: evaluator-v1

## Model Details

- Name: evaluator-v1
- Version: 0.1.0
- Description: Lightweight evaluation model used to score mapping correctness and retrieval relevance in QA/eval harness.
- Owner: data-science

## Intended Use

- Primary: automated evaluation of candidate mappings and retrieval rank.
- Out-of-scope: production user-facing inference for decisions without human review.

## Datasets & Training

- Training data: curated mapping examples (internal), synthetic augmentations.
- Validation: holdout set from golden_mappings_v1.

## Evaluation Metrics

- Accuracy: mapping correctness on holdout
- Precision@10 for retrieval relevance
- Latency: median inference time per example

## Limitations

- Small training set; may not generalize to unseen edge cases.
- Not audited for fairness or privacy; avoid direct PII inputs.

## Reproducibility

- Model artifact: n/a (placeholder)
- Random seed: documented per experiment in experiments/{run_id}.yaml

## Governance

- Review cadence: monthly
- Responsible AI notes: see docs/AI_PROJECT_CHARTER.md

## Contact

- <data-science@example.com>

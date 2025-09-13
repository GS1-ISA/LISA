# Model Card Template

Use this template to create a model card for every production model used by ISA.

- Model name:
- Model version:
- Model type / architecture:
- Model license:
- Date built:
- Contact / Owner:

## Intended use

- Primary use cases:
- Out-of-scope / disallowed uses:

## Training & Evaluation Data

- Training datasets (versioned):
- Evaluation datasets (versioned):
- Data provenance links (data_catalog entries):

## Metrics

- Primary metrics (e.g., retrieval P@5, answer faithfulness human score):
- Disaggregated metrics (by document type, complexity):

## Limitations & Known Failure Modes

-

## Ethical Considerations & Bias Mitigation

- Steps taken to mitigate bias:
- Open questions:

## Model I/O

- Input schema (JSON):
- Output schema (JSON):

## Versioning & Reproducibility

- Training script commit: (git sha)
- Experiment tracking link (MLflow/W&B):
- Model artifact location:

## Contact & Governance

- Model owner:
- Review cadence:

---

Create `docs/model_cards/<model>-v<version>.md` from this template and link from the release notes.

# Phase 6 — temporal KG-context experiment

## Research objective

Evaluate whether historical organization-project participation context adds value
to graph-only Adamic–Adar ranking for predicting first observed collaborations.
The prototype uses a **typed, dated bipartite KG** with
`organization -> participates_in -> project` relationships.

The model scores a candidate pair with Adamic–Adar plus a weighted sum of
historical project-activity features of their shared collaboration partners.
It is an interpretable contextual heuristic, **not** a demonstrated novel
machine-learning algorithm or a publication-ready contribution.

## Reproduce

```bash
python -m unittest -v test_kg_model.py
python prepare_cordis.py
python kg_model.py --queries 250
```

The script requires the official downloaded archive and prepared edge files.
It writes `data/processed/kg_model_results.json`. GitHub Actions runs the same
code and uploads the aggregate JSON artifact.

## Temporal protocol

- Organizations must be known by 2023-12-31.
- Validation ranks new collaborations in 2024 from a graph frozen at 2023-12-31.
- Candidate generation uses only graph features and deterministic hash exploration.
- Select the KG context coefficient from [0, .25, .5, 1] using 2024 observed-positive Recall@10.
- Test 2025 only once with the frozen coefficient, updating historical graph and
  project context to 2024-12-31.
- Use independent deterministic query samples with seeds 11, 23, 37, and report
  candidate coverage, observed-positive Recall@10, and per-seed comparisons.

## Interpretation limits

This uses a *retrospective current archive* and project start dates; it does not
prove project details were public at the cutoff. Unknown collaborations are
unlabeled. Multiple seeds on one network do not imply independent populations.
Only 250 queries per seed are evaluated; confidence intervals must account for
query dependence and overlapping samples. Project-size filtering may bias results.
No claim of improvement, statistical significance, or journal readiness is
warranted until real-data results and uncertainty checks are inspected.

## Remaining research requirements

- Audit historical publication timestamps or reconstruct point-in-time snapshots.
- Verify organization identifier stability and project-size exclusion impact.
- Develop and compare against strong typed-KG and temporal graph baselines.
- Conduct larger, prespecified cohorts, multiple seeds, ablations, and uncertainty analysis.
- Draft the manuscript with exactly two figures and two editable tables using
  measured results only; verify references and journal submission requirements.
